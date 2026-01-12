import sys, os, subprocess, shlex, readline, rlcompleter

BUILTINS = ['echo', 'exit', 'pwd', 'cd', 'type']
PATH = os.environ['PATH']


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

            if len(matches) == 1:
                return matches + " "
            return matches

        return None
    
    readline.set_completer_delims('\t\n`@$><=;|&{(')  # Remove space from delimiters
    readline.set_completer(complete)
    readline.parse_and_bind('tab: complete')

def main():
    activate_autocompletion()

    original_stdout = sys.stdout
    original_stderr = sys.stderr

    redirectors = ['>', '1>', '2>', '>>', '1>>', '2>>']

    while True:
        try:
            input_line = input("$ ")
        except (EOFError, KeyboardInterrupt):
            break

        # Handle command input
        full_command = shlex.split(input_line)

        if not full_command: 
            continue

        command = full_command[0]
        args = full_command[1:]

        args_str = " ".join(args)

        # Handle output redirection
        redirect_filename = None
        redirect_index = None
        redirect_type = None

        if any(r in args for r in redirectors):
            if '2>>' in args:
                redirect_index = args.index('2>>')
                redirect_type = '2>>'
            elif '1>>' in args:
                redirect_index = args.index('1>>')
                redirect_type = '1>>'
            elif '>>' in args:
                redirect_index = args.index('>>')
                redirect_type = '1>>'
            elif '2>' in args:
                redirect_index = args.index('2>')
                redirect_type = '2>'
            elif '1>' in args:
                redirect_index = args.index('1>')
                redirect_type = '1>'
            elif '>' in args:
                redirect_index = args.index('>')
                redirect_type = '1>'

            if redirect_index is not None and redirect_index + 1 < len(args):
                redirect_filename = args[redirect_index + 1]

                if (redirect_type == '2>>'):
                    sys.stderr = open(redirect_filename, 'a')
                elif (redirect_type ==  '1>>'):
                    sys.stdout = open(redirect_filename, 'a')
                elif (redirect_type == '2>'):
                    sys.stderr = open(redirect_filename, 'w')
                elif (redirect_type == '1>'):
                    sys.stdout = open(redirect_filename, 'w')
                
                args = args[:redirect_index]
                args_str = " ".join(args)


        # Execute built-in commands or external programs
        if command == 'exit':
            break
        elif command == 'echo':
            print(f"{args_str}")

        elif command == 'pwd':
            print(os.getcwd())

        elif command == 'cd':
            if args_str == "" or args_str == "~":
                os.chdir(os.path.expanduser("~"))
            else:
                try:
                    os.chdir(args_str)
                except FileNotFoundError:
                    sys.stderr.write(f"cd: {args_str}: No such file or directory\n")

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
            
        else:
            found = False
            split_paths = PATH.split(os.pathsep)
            for folder_path in split_paths:
                file_path = folder_path + "/" + command
                if os.access(file_path, os.X_OK):
                    result = subprocess.run([command] + args, capture_output=True, text=True)

                    sys.stdout.write(result.stdout)
                    sys.stderr.write(result.stderr)

                    found = True
                    break       
            
            if not found:
                print(f"{command}: command not found")

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
