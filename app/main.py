import sys, os, shlex, readline

PATH = os.environ['PATH']
BUILTINS = ['echo', 'exit', 'pwd', 'cd', 'type']
REDIRECTORS = ['>', '1>', '2>', '>>', '1>>', '2>>']


def activate_autocompletion():
    path_executables = set()
    paths = PATH.split(os.pathsep)

    for path in paths:
        if os.path.isdir(path):
            try:
                for file in os.listdir(path):
                    path_executables.add(file)
            except PermissionError:
                continue
    
    all_commands = sorted(list(set(BUILTINS) | path_executables))

    def complete(text, state):
        options = [command for command in all_commands if command.startswith(text)]

        if state < len(options):
            matches = options[state]
            
            if len(options) == 1:
                return matches + " "
            return matches

        return None
    
    readline.set_completer(complete)    
    readline.parse_and_bind('tab: complete')


def execute_builtin(command, args):

        args_str = " ".join(args)

        # Execute built-in commands or external programs
        if command == 'exit':
            sys.exit(0)
        elif command == 'echo':
            print(f"{args_str}")
            return True

        elif command == 'pwd':
            print(os.getcwd())
            return True

        elif command == 'cd':
            if args_str == "" or args_str == "~":
                os.chdir(os.path.expanduser("~"))
            else:
                try:
                    os.chdir(args_str)
                except FileNotFoundError:
                    sys.stderr.write(f"cd: {args_str}: No such file or directory\n")
            return True

        elif command == 'type':
            found = False
            for x in BUILTINS:
                if x == args_str:
                    print(f'{args_str} is a shell builtin')
                    found = True
                    break

            if not found:
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
            
        else:
            return False  # Not a built-in command



def main():
    activate_autocompletion()

    original_stdout = sys.stdout
    original_stderr = sys.stderr

    while True:
        try:
            input_line = input("$ ")
        except (EOFError, KeyboardInterrupt):
            break

        if not input_line: continue

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
            
            if cmd_name in ['cd', 'exit']:
                execute_builtin(cmd_name, cmd_args)
                continue

        # Pipeline execution
        input_fd = 0
        pids = []

        for i, cmd_parts in enumerate(command_chain):
            
            cmd_name = cmd_parts[0]
            cmd_args = cmd_parts[1:]

            # Handle output redirection
            redirect_filename = None
            redirect_index = None
            redirect_type = None

            if any(r in cmd_args for r in REDIRECTORS):
                if '2>>' in cmd_args:
                    redirect_index = cmd_args.index('2>>')
                    redirect_type = '2>>'
                elif '1>>' in cmd_args:
                    redirect_index = cmd_args.index('1>>')
                    redirect_type = '1>>'
                elif '>>' in cmd_args:
                    redirect_index = cmd_args.index('>>')
                    redirect_type = '1>>'
                elif '2>' in cmd_args:
                    redirect_index = cmd_args.index('2>')
                    redirect_type = '2>'
                elif '1>' in cmd_args:
                    redirect_index = cmd_args.index('1>')
                    redirect_type = '1>'
                elif '>' in cmd_args:
                    redirect_index = cmd_args.index('>')
                    redirect_type = '1>'

                if redirect_index is not None and redirect_index + 1 < len(cmd_args):
                    redirect_filename = cmd_args[redirect_index + 1]

                    if (redirect_type == '2>>'):
                        sys.stderr = open(redirect_filename, 'a')
                    elif (redirect_type ==  '1>>'):
                        sys.stdout = open(redirect_filename, 'a')
                    elif (redirect_type == '2>'):
                        sys.stderr = open(redirect_filename, 'w')
                    elif (redirect_type == '1>'):
                        sys.stdout = open(redirect_filename, 'w')
                    
                    cmd_args = cmd_args[:redirect_index]
            
            is_last = (i == len(command_chain) - 1)
            r, w = 0, 0

            if not is_last:
                r, w = os.pipe()

            pid = os.fork()

            if pid == 0:  # Child
                if input_fd != 0:
                    os.dup2(input_fd, 0)
                    os.close(input_fd)

                if not is_last:
                    os.dup2(w, 1)
                    os.close(w)
                    os.close(r)

                if execute_builtin(cmd_name, cmd_args): 
                    os._exit(0) # kill child 

                found_path = None

                if os.sep in cmd_name:
                    if os.access(cmd_name, os.X_OK):
                        found_path = cmd_name
                else:
                    split_paths = PATH.split(os.pathsep)
                    for folder_path in split_paths:
                        file_path = folder_path + "/" + cmd_name
                        if os.access(file_path, os.X_OK):
                            found_path = file_path
                            break       
                    
                if found_path:
                    try:
                        os.execv(found_path, cmd_parts)
                    except Exception as err:
                        sys.stderr.write(f"Error executing {cmd_name}: {err}\n")
                        os._exit(1)
                else:
                    sys.stderr.write(f"{cmd_name}: command not found\n")
                    os._exit(1)

            else: # Parent
                pids.append(pid)

                if input_fd != 0:
                    os.close(input_fd)

                if not is_last:
                    os.close(w)
                    input_fd = r

        # Wait for children to finish
        for pid in pids:
            try:
                os.waitpid(pid, 0)
            except ChildProcessError:
                pass

        # Reset redirection
        if redirect_filename:
            sys.stdout.flush()
            sys.stderr.flush()
            if sys.stdout != original_stdout:
                sys.stdout.close()
                sys.stdout = original_stdout
            if sys.stderr != original_stderr:
                sys.stderr.close()
                sys.stderr = original_stderr

if __name__ == "__main__":
    main()
