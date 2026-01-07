import sys, os


def main():
    # TODO: Uncomment the code below to pass the first stage
    builtIns = ['echo', 'exit', 'type']
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

        print(f"{command}: command not found")

    pass


if __name__ == "__main__":
    main()
