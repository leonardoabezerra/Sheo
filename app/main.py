import sys, os, subprocess, shlex

def main():
    PATH = os.environ['PATH']
    original_stdout = sys.stdout
    builtIns = ['echo', 'exit', 'pwd', 'cd', 'type']

    while True:
        sys.stdout.write("$ ")

        # Handle command input
        input_line = input()
        command, _, command_content = input_line.partition(" ")

        # Strip quotes from arguments and handle empty commands
        split_command_content = shlex.split(command_content) 
        if not split_command_content: # Reset loop if command is empty "[]"
            continue
        
        command_content = " ".join(split_command_content)

        # Handle output redirection
        redirect_filename = None
        if '>' in split_command_content or '1>' in split_command_content:
            if '>' in split_command_content:
                redirect_index = split_command_content.index('>')
            else:
                redirect_index = split_command_content.index('1>')

            if redirect_index + 1 < len(split_command_content):
                redirect_filename = split_command_content[redirect_index + 1]
                sys.stdout = open(redirect_filename, 'w')

                command_content = " ".join(split_command_content[:redirect_index])


        # Execute built-in commands or external programs
        if command == 'exit':
            break
        elif command == 'echo':
            print(f"{command_content}")

        elif command == 'pwd':
            print(os.getcwd())

        elif command == 'cd':
            if command_content == "" or command_content == "~":
                os.chdir(os.path.expanduser("~"))
            else:
                try:
                    os.chdir(command_content)
                except FileNotFoundError:
                    print(f"cd: {command_content}: No such file or directory")

        elif command == 'type':
            found = False
            for x in builtIns:
                if x == command_content:
                    print(f'{command_content} is a shell builtin')
                    found = True
                    break

            if not found:
                split_paths = PATH.split(os.pathsep)

                for folder_path in split_paths:
                    file_path = folder_path +  "/" + command_content
                    if os.access(file_path, os.X_OK):
                        print(f'{command_content} is {file_path}')
                        found = True
                        break
                
                if not found:
                    print(f'{command_content}: not found')     
            
        else:
            found = False
            split_paths = PATH.split(os.pathsep)
            for folder_path in split_paths:
                file_path = folder_path + "/" + command
                if os.access(file_path, os.X_OK):
                    result = subprocess.run([command] + command_content.split(" "), capture_output=True, text=True)

                    sys.stdout.write(result.stdout)
                    sys.stderr.write(result.stderr)

                    found = True
                    break       
            
            if not found:
                print(f"{command}: command not found")

        if redirect_filename:
            sys.stdout.close()
            sys.stdout = original_stdout


if __name__ == "__main__":
    main()
