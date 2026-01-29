<img width="1800" height="920" alt="Sheo_" src="https://github.com/user-attachments/assets/3199e201-3520-4296-b5a2-e283f85190b1" />

<br>

# About the Project
Sheo is a simple shell application I created based on Unix shells. This application was created as a way of better comprehending command-line interpreters and how operating systems handle processes, memory and file streams while practicing some Python programming. I constructed it with the help of code crafters, which I used to test the code and as a guide to which functionalities I should develop in this project to optimize my learning experience.

<br>

# Sheo, a linux-based python-written shell application
This custom comand-line interface (CLI) built with Python replicates core Unix shell functionalities. This project demonstrates low-level systems programming concepts, including **process management, file descriptor manipulation, and inter-process communication (IPC)**.

<br>

## Key features
- **Command Execution & Lifecycle:** Implements a full REPL (Read-Eval-Print Loop) using `os.fork()` and `os.execv()` to manage child processes for external binaries.
- **Advanced Piping & Redirection:** Supports complex command chaining through `os.pipe()`. Includes output redirection for `stdout` and `stderr`, supporting both overwrite (`>`) and append (`>>`) modes.
- **Dynamic Tab-Autocompletion & History:** Supports autocompletion for system binaries and built-in commands, as well as command history navigation through arrow up (`↑`) and down (`↓`). Also includes history file management through the `history` command and environment variables.
- **Internaa Built-Ins:** Custom implementation of essential shell commands.
- **Robust Parsing:** Ensures correct handling of quotes, escapes and complex arguments.

<br>

## Technical Deep Dive
- **Process Synchronization:** Managed parent-child process relationship through `os.waitpid()` to avoid "zombie" processes.
- **Environment Handling:** Dynamically crawls the system `$PATH` to index executables for autocompletion and command execution.
- **File Descriptor Logic:** Implemented `os.dup2` to conduct the transfer of data between piped processes and files.

<br>

## How to run the code
### Prerequisites
- Python 3
- Unix-based OS (Like linux or macOS)

### Running the Shell
1. Clone this repository:
   ```sh
   git clone https://github.com/leonardoabezerra/Sheo.git
   cd Sheo
   ```
2. Launch the Shell:
   ```sh
   python3 app/main.py
   ```
   
### Example usage
```sh
$ ls -la | grep ".py" > python_files.txt
$ cat python_files.txt
$ history 5
```

<br>

# Thanks!
#### I really appreciate your time taking a look at my project. Please, feel free to explore my portfolio to check out my other projects!

```
    ___           _________     _________
   /\  \         /\   ______\  /\   ____  \
   \ \  \        \ \   ___\ /  \ \  \__/\  \
    \ \  \______  \ \  \_/____  \ \  \___\  \    ___
     \ \_________\ \ \_________\ \ \_________\  /\__\
      \/_________/  \/_________/  \/_________/  \/__/


    Developed by: Leonardo Alves Bezerra.
```

<div>
<a href="https://www.linkedin.com/in/leonardoabezerra" target="_blank" rel="noopener noreferrer">
    <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn Badge"/>
</a>
<a href="mailto:leonardoalvesbezerra@gmail.com" target="_blank" rel="noopener noreferrer">
    <img src="https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Gmail Badge"/>
</a>
<a href="https://leonardoabezerra.github.io/my-portfolio" target="_blank" rel="noopener noreferrer">
    <img src="https://img.shields.io/badge/Portfolio-brightgreen?style=for-the-badge&logo=github"/>
</a>
</div>
