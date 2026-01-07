import sys, os, subprocess


def main():
    # TODO: Uncomment the code below to pass the first stage
    builtIns = ['echo', 'exit', 'pwd', 'cd', 'type']
    PATH = os.environ['PATH']
    while(1):
        sys.stdout.write("$ ")

        command = input()
        command, _, command_content = command.partition(" ")
        if command == 'exit':
            break
        elif command == 'echo':
            print(f"{command_content}")
            continue
        elif command == 'pwd':
            print(os.getcwd())
            continue
        elif command == 'cd':
            if command_content == "":
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
