import sys, os, subprocess

def main():
    PATH = os.environ['PATH']
    original_stdout = sys.stdout
    builtIns = ['echo', 'exit', 'pwd', 'cd', 'type']

    while(1):
        sys.stdout = original_stdout
        sys.stdout.write("$ ")

        # Handle command input
        command = input()
        command, _, command_content = command.partition(" ")
        split_command_content = command_content.split(" ")

        # Strip quotes from arguments
        for quoted_arg in split_command_content:
            if (quoted_arg.startswith('"') and quoted_arg.endswith('"')) or \
               (quoted_arg.startswith("'") and quoted_arg.endswith("'")):
                command_content[split_command_content.index(quoted_arg)] = quoted_arg[1:-1] 

        # Handle output redirection
        if '>' in split_command_content or '1>' in split_command_content:
            if '>' in split_command_content:
                redirect_index = split_command_content.index('>')
            else:
                redirect_index = split_command_content.index('1>')

            redirect_filename = split_command_content[redirect_index + 1]
            sys.stdout = open(redirect_filename, 'w')

            command_content = " ".join(split_command_content[:redirect_index])

        # Execute built-in commands or external programs
        if command == 'exit':
            break
        elif command == 'echo':
            print(f"{command_content}")
            continue
        elif command == 'pwd':
            print(os.getcwd())
            continue
        elif command == 'cd':
            if command_content == "" or command_content == "~":
                os.chdir(os.path.expanduser("~"))
            else:
                try:
                    os.chdir(command_content)
                    continue
                except FileNotFoundError:
                    print(f"cd: {command_content}: No such file or directory")
                    continue
        elif command == 'type':
            found = False
            for x in builtIns:
                if x == command_content:
                    print(f'{command_content} is a shell builtin')
                    found = True
                    break
            if found:
                continue 
            else:
                split_paths = PATH.split(os.pathsep)

                for folder_path in split_paths:
                    file_path = folder_path +  "/" + command_content
                    if os.access(file_path, os.X_OK):
                        print(f'{command_content} is {file_path}')
                        found = True
                        break
                
                if found:
                    continue
                else:
                    print(f'{command_content}: not found')     
                    continue

        else:
            found = False
            split_paths = PATH.split(os.pathsep)
            for folder_path in split_paths:
                file_path = folder_path + "/" + command
                if os.access(file_path, os.X_OK):
                    try:
                        result = subprocess.run([command] + command_content.split(" "), check=True, capture_output=True, text=True)
                        sys.stdout.write(result.stdout)
                        found = True
                        break
                    except subprocess.CalledProcessError as err:
                        print(f'Program failed to run with return code {err.returncode}:\n{err.stderr}')
                        found = True
                        break
                else:
                    continue       
            
            if found:
                continue
            else:
                print(f"{command}: command not found")

    pass


if __name__ == "__main__":
    main()
