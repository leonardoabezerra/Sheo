import sys


def main():
    # TODO: Uncomment the code below to pass the first stage
    while(1):
        sys.stdout.write("$ ")

        command = input()
        if command is 'exit':
            break

        print(f"{command}: command not found")

    pass


if __name__ == "__main__":
    main()
