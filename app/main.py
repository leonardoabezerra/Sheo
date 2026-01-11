import sys, os, subprocess, shlex

def main():
    PATH = os.environ['PATH']
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    builtIns = ['echo', 'exit', 'pwd', 'cd', 'type']
    redirectors = ['>', '1>', '2>']

    while True:
        sys.stdout.write("$ ")

        # Handle command input
        input_line = input()
        full_command = shlex.split(input_line)

        if not full_command: 
            continue

        command = full_command[0]
        args = full_command[1:]

        args_str = " ".join(args)

        # Handle output redirection
        redirect_filename = None
        redirect_index = None
        if any(r in args for r in redirectors):
            if '2>' in args:
                redirect_index = args.index('2>')
            elif '1>' in args:
                redirect_index = args.index('1>')
            elif '>' in args:
                redirect_index = args.index('>')

            if redirect_index is not None and redirect_index + 1 < len(args):
                redirect_filename = args[redirect_index + 1]

                if (args[redirect_index] == '2>'):
                    sys.stderr = open(redirect_filename, 'w')
                else:
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
            for x in builtIns:
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
