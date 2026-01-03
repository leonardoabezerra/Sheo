import sys


def main():
    # TODO: Uncomment the code below to pass the first stage
    while(1):
        sys.stdout.write("$ ")

        command = input()
        if command == 'exit':
            break
        elif command[:4] == 'echo':
            print(f"{command[4:]}")
            continue


        print(f"{command}: command not found")

    pass


if __name__ == "__main__":
    main()
