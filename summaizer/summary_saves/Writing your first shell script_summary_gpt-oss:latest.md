# Summary (gpt-oss:latest)

- **Introduction to Bash scripting**
  - Tutorial covers the basics of writing a bash script.
  - Target audience: beginners and intermediate users wanting to reinforce fundamentals.
  - Core concepts highlighted: variables, if statements, case statements, and functions.

- **Script file and shebang**
  - Create a file named `video.sh` (or any name ending in `.sh`).
  - First line: `#!/usr/bin/env bash` to let the system locate the Bash interpreter.
  - Alternative common shebang: `#!/bin/bash`.

- **Basic commands and execution**
  - Bash executes each line as a shell command by default.
  - Example: `echo "hello world"` prints text to stdout.
  - Run script via:
    - `sh video.sh` (invokes default shell).
    - `bash video.sh` (explicitly uses Bash).
    - `./video.sh` (requires executable permission).

- **Setting executable permission**
  - Use `chmod +x video.sh` to make the script executable.
  - After this, `./video.sh` runs directly.

- **Using PATH for scripts**
  - If script directory is in `$PATH`, you can run it without `./`.
  - Example: place `video.sh` in a `$PATH` directory → run `video.sh` from any location.

- **Variables**
  - Syntax: `name=value` (no spaces around `=`).
  - Example: `myvar="text"` or `myvar=$(date)` (command substitution).
  - Reference variable: `echo $myvar`.
  - Command substitution can use `$()` or backticks `` `command` ``.

- **If statements**
  - Basic syntax:
    ```bash
    if [ "$var" -gt 80 ]; then
        echo "Disk is nearly full!"
    else
        echo "Disk has space left!"
    fi
    ```
  - Comparison operators:
    - `-gt` (greater than)
    - `-lt` (less than)
    - `=` (equal)
    - `!=` (not equal)
  - Conditional expression must be enclosed in `[` `]` (test).

- **Case statements**
  - Syntax:
    ```bash
    case "$1" in
        disk) echo "disk selected" ;;
        mem) echo "memory selected" ;;
        *) echo "pick disk or memory" ;;
    esac
    ```
  - `$1` refers to the first command‑line argument to the script.
  - Patterns can be simple strings or glob patterns.
  - `*` is the default (matches anything).

- **Functions**
  - Define a function:
    ```bash
    check_disk() {
        # commands
    }
    ```
  - Call the function by name: `check_disk`.
  - Functions can use local variables and return status via `return`.

- **Example script: disk usage check**
  - Retrieve disk usage percent:
    ```bash
    myvar=$(df -h / | awk '/^\/dev/ {print $5}' | tr -d '%')
    ```
    - `df -h /` shows disk usage for the root filesystem.
    - `awk '/^\/dev/ {print $5}'` extracts the fifth field of the line starting with `/dev`.
    - `tr -d '%'` removes the `%` character, leaving a number.
  - Use an if statement to compare against a threshold (e.g., 80 or 90).
  - Output:
    - `"Disk is nearly full!"` if usage > threshold.
    - `"Disk has space left!"` otherwise.

- **Example script: memory usage check**
  - Retrieve used memory:
    ```bash
    mem_used=$(free -h | awk '/^Mem:/ {print $3}')
    ```
    - `free -h` shows memory usage in human‑readable format.
    - `awk '/^Mem:/ {print $3}'` prints the third field (used memory) of the line starting with `Mem:`.
  - Define a function `check_mem` that echoes the used memory:
    ```bash
    check_mem() {
        echo "Memory used: $mem_used"
    }
    ```

- **Integrating case with functions**
  - Main script uses case to dispatch to the appropriate function:
    ```bash
    case "$1" in
        disk) check_disk ;;
        mem) check_mem ;;
        *) echo "pick disk or memory" ;;
    esac
    ```
  - Running `./video.sh disk` prints disk status.
  - Running `./video.sh mem` prints memory usage.

- **Miscellaneous script elements**
  - Comments start with `#` and are ignored by the shell.
  - Commands can be piped (`|`) to feed output into the next command.
  - Substitutions inside variables or commands use `$()` or backticks.

- **Summary of covered fundamentals**
  - Shebang to specify interpreter.
  - Variables: assignment, referencing, command substitution.
  - Conditional logic: if statements with comparison operators.
  - Argument handling: case statements for simple menus or options.
  - Encapsulation: functions to group related commands and reuse logic.

These points capture the key ideas and concrete example code used in the transcript for learning basic Bash scripting.