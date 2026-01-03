import sys


def main():
    # TODO: Uncomment the code below to pass the first stage
    builtIns = ['echo', 'exit', 'type']
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
                command = command_content       

        print(f"{command}: command not found")

    pass


if __name__ == "__main__":
    main()
