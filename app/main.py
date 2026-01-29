import sys, os, shlex, readline, pwd

PATH = os.environ['PATH']
HISTFILE = os.environ['HISTFILE'] if 'HISTFILE' in os.environ else ""
BUILTINS = ['echo', 'exit', 'pwd', 'cd', 'type', 'history']
REDIRECTORS = ['>', '1>', '2>', '>>', '1>>', '2>>']
SHELL_STATE_ARGS = ['-r', '-w', '-a']

history = []
history_append = []

# Terminal colors
class Colors:
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    ERROR = '\033[91m'
    RESET = '\033[0m'


def activate_autocompletion():
    path_executables = set()
    paths = PATH.split(os.pathsep)

    # Collect all executable files in PATH directories
    for path in paths:
        if os.path.isdir(path):
            try:
                for file in os.listdir(path):
                    path_executables.add(file)
            except PermissionError:
                continue
    
    all_commands = sorted(list(set(BUILTINS) | path_executables))

    def complete(text, state):
        # Generate possible matches
        options = [command for command in all_commands if command.startswith(text)]

        if state < len(options):
            matches = options[state]
            
            if len(options) == 1:
                return matches + " "
            return matches

        return None

    # Configure readline for tab completion    
    readline.set_completer(complete)    
    readline.parse_and_bind('tab: complete')


# Load history from HISTFILE
def load_histfile():
    try:
        with open(HISTFILE, 'r') as hfile:
            for line in hfile:
                line = line.strip()
                if line:
                    readline.add_history(line) # Necessary for arrow navigation
                    history.append(line)
                    history_append.append(line)
    except FileNotFoundError:
        pass  # HISTFILE environment variable is not necessary
    except Exception as err:
        sys.stderr.write(f'{Colors.ERROR}Error loading history file: {err}\n')


# Update HISTFILE with current history
def update_histfile():
    try:
        with open(HISTFILE, 'w') as hfile: # Overwrite existing history with current session history
            joined_history = '\n'.join(history)
            hfile.write(joined_history)
            hfile.write('\n')
    except FileNotFoundError:
        pass # HISTFILE environment variable is not necessary
    except Exception as err:
        sys.stderr.write(f'{Colors.ERROR}Error updating history file: {err}\n')


def execute_builtin(command, args):  # Returns True if executed
        args_str = " ".join(args)

        # Execute built-in commands
        if command == 'exit':  # Exit shell
            update_histfile()
            print(f"{Colors.CYAN}Sheo{Colors.RESET}$ Bye :D")
            sys.exit(0)

        elif command == 'echo':  # Print arguments
            print(f"{args_str}")
            return True

        elif command == 'pwd':  # Print working directory
            print(os.getcwd())
            return True

        elif command == 'cd':  # Change directory
            if args_str == "" or args_str == "~":
                os.chdir(os.path.expanduser("~"))
            else:
                try:
                    os.chdir(args_str)
                except FileNotFoundError:
                    sys.stderr.write(f"cd: {args_str}: No such file or directory\n")
            return True

        elif command == 'type':  # Identify command type
            found = False
            for x in BUILTINS:
                if x == args_str:
                    print(f'{args_str} is a shell builtin')
                    found = True
                    break

            if not found:  # Check in PATH for external binaries
                split_paths = PATH.split(os.pathsep)

                for folder_path in split_paths:
                    file_path = folder_path +  "/" + args_str
                    if os.access(file_path, os.X_OK):
                        print(f'{args_str} is {file_path}')
                        found = True
                        break
                
                if not found:
                    print(f'{args_str}: not found')     
            return True
        
        elif command == 'history':  # Show command history
            if len(args) > 1 and args[0] == '-r':  # Read history from file
                path_to_hfile = args[1]
                try:
                    with open(path_to_hfile, 'r') as hfile:
                        for line in hfile:
                            line = line.strip()
                            if line:
                                readline.add_history(line) # Necessary for arrow navigation
                                history.append(line)     
                                history_append.append(line)
                        return True
                except FileNotFoundError:
                    sys.stderr.write(f'history: {path_to_hfile}: No such file or directory\n')
                    return True
                except Exception as err:
                    sys.stderr.write(f'{Colors.ERROR}history: {path_to_hfile}: {err}\n')
                    return True

            elif len(args) > 1 and args[0] == '-w':  # Write history to file
                path_to_hfile = args[1]
                try:
                    with open(path_to_hfile, 'w') as hfile:
                        joined_history = '\n'.join(history)
                        hfile.write(joined_history)
                        hfile.write('\n')
                        return True
                except FileNotFoundError:
                    sys.stderr.write(f'history: {path_to_hfile}: No such file or directory\n')
                    return True
                except Exception as err:
                    sys.stderr.write(f'{Colors.ERROR}history: {path_to_hfile}: {err}\n')
                    return True
            
            elif len(args) > 1 and args[0] == '-a':  # Append recent history to file
                path_to_hfile = args[1]
                try:
                    with open(path_to_hfile, 'a') as hfile:
                        joined_history = '\n'.join(history_append)
                        hfile.write(joined_history)
                        hfile.write('\n')
                        history_append.clear()  # Clear recent history after appending
                        return True
                except FileNotFoundError:
                    sys.stderr.write(f'history: {path_to_hfile}: No such file or directory\n')
                    return True
                except Exception as err:
                    sys.stderr.write(f'{Colors.ERROR}history: {path_to_hfile}: {err}\n')
                    return True

            # Default: print history
            for index, cmd in enumerate(history):
                if len(args) > 0 and args[0].isdigit():
                    if index >= len(history) - int(args[0]):
                        print(f'    {index + 1} {cmd}')
                else:
                    print(f'    {index + 1} {cmd}')
            return True
            
        else:
            return False  # Not a built-in command


def main():
    activate_autocompletion()
    load_histfile()

    # Main shell loop (REPL)
    while True:

        # Prepare input prompt
        current_user = pwd.getpwuid(os.getuid()).pw_name
        current_wd = os.getcwd()
        split_cwd = current_wd.split(os.sep)

        if current_user in split_cwd and len(split_cwd) > 1:
            user_index = split_cwd.index(current_user)
            current_wd = '~' + os.sep + os.sep.join(split_cwd[user_index + 1:])
        
        try:
            input_line = input(f"{Colors.CYAN}{current_user}@sheo:{Colors.BLUE}{current_wd}{Colors.RESET}$ ")
        except (EOFError, KeyboardInterrupt):
            break

        if not input_line: continue

        history.append(input_line) # Add input to history
        history_append.append(input_line) # Recent history for -a option

        # Handle command input
        full_command = shlex.split(input_line)

        if not full_command: 
            continue 

        # Separate commands by pipes
        current_command = []
        command_chain = []
        for i in full_command:
            if i == '|':
                if current_command:
                    command_chain.append(current_command)
                current_command = []
            else:
                current_command.append(i)
        if current_command:
            command_chain.append(current_command)            

        # Handle built-in commands without forking
        if len(command_chain) == 1:
            cmd_name = command_chain[0][0]
            cmd_args = command_chain[0][1:]
            
            # Built-in commands that affect shell state
            if cmd_name in ['cd', 'exit'] or (cmd_name == 'history' and (len(cmd_args) > 0 and cmd_args[0] in SHELL_STATE_ARGS)):
                execute_builtin(cmd_name, cmd_args)
                continue

        # Pipeline execution
        input_fd = 0
        pids = []

        # Create processes for each command in the pipeline
        for i, cmd_parts in enumerate(command_chain):
            
            is_last = (i == len(command_chain) - 1)
            r, w = 0, 0  # Initialize pipe fds

            if not is_last:
                r, w = os.pipe()

            pid = os.fork()

            if pid == 0:  # Child
                # Setup input from previous command
                if input_fd != 0:
                    os.dup2(input_fd, 0)
                    os.close(input_fd)

                # Setup output to next command
                if not is_last:
                    os.dup2(w, 1)
                    os.close(w)
                    os.close(r)

                cmd_name = cmd_parts[0]
                cmd_args = cmd_parts[1:]
                
                # Handle output redirection
                redirect_filename = None
                
                for redirector in REDIRECTORS:
                        if redirector in cmd_args:
                            redirect_index = cmd_args.index(redirector)

                            # Ensure there is a filename after the redirector
                            if redirect_index + 1 < len(cmd_args):
                                redirect_filename = cmd_args[redirect_index + 1]                
                                rmode = 'a' if '>>' in redirector else 'w'
                                rtarget = 2 if '2' in redirector else 1

                                # Perform redirection
                                f = open(redirect_filename, rmode)
                                os.dup2(f.fileno(), rtarget)
                                f.close()

                                cmd_args = cmd_args[:redirect_index]
                                break


                # Execute command                    
                if execute_builtin(cmd_name, cmd_args): 
                    os._exit(0) # kill child 

                # Search for external command in PATH
                found_path = None

                if os.sep in cmd_name:
                    if os.access(cmd_name, os.X_OK):
                        found_path = cmd_name
                else:  #  Search in PATH
                    split_paths = PATH.split(os.pathsep)
                    for folder_path in split_paths:
                        file_path = folder_path + "/" + cmd_name
                        if os.access(file_path, os.X_OK):
                            found_path = file_path
                            break       
                    
                if found_path:
                    try:
                        os.execv(found_path, [cmd_name] + cmd_args)  # Execute external command
                    except Exception as err:
                        sys.stderr.write(f"{Colors.ERROR}Error executing {cmd_name}: {err}\n")
                        os._exit(1)
                else:
                    sys.stderr.write(f"{cmd_name}: command not found\n")
                    os._exit(1)

            else: # Parent
                pids.append(pid)

                # Close unused fds
                if input_fd != 0:
                    os.close(input_fd)

                # Setup input for next command
                if not is_last:
                    os.close(w)
                    input_fd = r

        # Wait for children to finish
        for pid in pids:
            try:
                os.waitpid(pid, 0)
            except ChildProcessError:
                pass

if __name__ == "__main__":
    main()


#
#    ___           _________     _________
#   /\  \         /\   ______\  /\   ____  \
#   \ \  \        \ \   ___\ /  \ \  \__/\  \
#    \ \  \______  \ \  \_/____  \ \  \___\  \    ___
#     \ \_________\ \ \_________\ \ \_________\  /\__\
#      \/_________/  \/_________/  \/_________/  \/__/
#
#
#   Developed by: Leonardo Alves Bezerra.
#