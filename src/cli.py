"""
NepaliCode Command Line Interface
=================================

    nepali run main.np        Run a .np program
    nepali                    Start the interactive REPL
    nepali check main.np      Parse a file without running it
    nepali new myapp          Scaffold a new project
    nepali --vm main.np       (Experimental) run on the bytecode VM
    nepali --version          Version information

The `nepali`, `nepali.exe` and `nepali.cmd` shims all end up here.
"""

from __future__ import annotations

import io
import os
import sys

# Ensure UTF-8 output on Windows consoles.
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                      errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8",
                                      errors="replace")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.errors import NpError, NpSyntaxError  # noqa: E402
from src.interpreter import Interpreter  # noqa: E402

VERSION = "0.1.0-alpha"
BANNER = rf"""
  _   _                 _    _          _
 | \ | | ___ _   _  ___| | _| |__   ___| |
 |  \| |/ _ \ \ | | / __| |/ / '_ \ / _ \ |
 | |\  |  __/\ \| |/ __|   <| |_) |  __/ |
 |_| \_|\___| \__/ |\___|_|\_\_.__/ \___|_|
              |___/
  NepaliCode {VERSION} — swagat chha! 🇳🇵
""".replace("\\", "")

REPL_HELP = """
Commands:
  exit / bida      Leave the REPL
  help             Show this message
  Everything else is evaluated as NepaliCode.
"""


def _print_error(err: NpError) -> None:
    print(err.render(), file=sys.stderr)


def cmd_run(path: str, vm: bool = False) -> int:
    if not os.path.isfile(path):
        print(f"Error: file '{path}' not found.")
        return 1
    with open(path, "r", encoding="utf-8") as handle:
        source = handle.read()

    if vm:
        return _run_vm(source, path)

    interp = Interpreter()
    interp.search_paths = [os.path.dirname(os.path.abspath(path))]
    try:
        interp.run_source(source, file=path)
    except NpSyntaxError as err:
        _print_error(err)
        return 65
    except NpError as err:
        _print_error(err)
        return 70
    except KeyboardInterrupt:
        print("\nInterrupted.")
        return 130
    return 0


def _run_vm(source: str, path: str) -> int:
    from src.bytecode import compile_to_bytecode, BytecodeVM

    from src.lexer import tokenize
    from src.parser import parse

    try:
        tokens = tokenize(source, file=path)
        ast = parse(tokens, file=path, source_lines=source.splitlines())
        code = compile_to_bytecode(ast, name=os.path.basename(path))
        vm = BytecodeVM(code)
        vm.run()
    except NpError as err:
        _print_error(err)
        return 70
    print("\n[note] The bytecode VM is experimental; the tree-walking "
          "interpreter is the reference engine.")
    return 0


def cmd_check(path: str) -> int:
    if not os.path.isfile(path):
        print(f"Error: file '{path}' not found.")
        return 1
    with open(path, "r", encoding="utf-8") as handle:
        source = handle.read()
    from src.lexer import tokenize
    from src.parser import parse

    try:
        tokens = tokenize(source, file=path)
        statements = parse(tokens, file=path, source_lines=source.splitlines())
    except NpSyntaxError as err:
        _print_error(err)
        return 65
    print(f"OK {path} — {len(tokens)} tokens, {len(statements)} statements.")
    return 0


def cmd_new(name: str) -> int:
    if os.path.exists(name):
        print(f"Error: '{name}' already exists.")
        return 1
    os.makedirs(os.path.join(name, "lib"), exist_ok=True)
    os.makedirs(os.path.join(name, "tests"), exist_ok=True)

    with open(os.path.join(name, "main.np"), "w", encoding="utf-8") as handle:
        handle.write(
            "# namaste!\n"
            'print("Namaste, sansar!")\n'
            "\n"
            "kaam greet(name):\n"
            '    firta f"Namaste {name}!"\n'
            "\n"
            'print(greet("Nepal"))\n'
        )
    with open(os.path.join(name, "nepali.toml"), "w", encoding="utf-8") as handle:
        handle.write(
            f'[project]\n'
            f'name = "{os.path.basename(name)}"\n'
            f'version = "0.1.0"\n'
            f'entry = "main.np"\n'
            f'author = "Your Name"\n'
            f'license = "MIT"\n'
        )
    with open(os.path.join(name, "README.md"), "w", encoding="utf-8") as handle:
        handle.write(f"# {os.path.basename(name)}\n\nRun with:\n\n    nepali run main.np\n")
    with open(os.path.join(name, "tests", "test_main.np"), "w", encoding="utf-8") as handle:
        handle.write(
            "# A tiny smoke test.\n"
            "yedi 1 + 1 != 2:\n"
            '    uthau "math broke"\n'
            'print("tests passed")\n'
        )
    print(f"Created project '{name}'.")
    print(f"  cd {name}")
    print("  nepali run main.np")
    return 0


def repl() -> int:
    print(BANNER)
    print('Type "help" for help, "exit" to quit.')
    print()

    interp = Interpreter()
    interp.current_file = "<repl>"
    buffer: list = []
    prompt = ">>> "

    while True:
        try:
            line = input(prompt)
        except EOFError:
            print()
            return 0
        except KeyboardInterrupt:
            print("\n(use 'exit' to quit)")
            buffer = []
            prompt = ">>> "
            continue

        if not buffer:
            stripped = line.strip()
            if stripped in ("exit", "bida"):
                return 0
            if stripped == "help":
                print(REPL_HELP)
                continue
            if stripped == "":
                continue

        buffer.append(line)
        source = "\n".join(buffer)

        # Keep collecting when lines/brackets are still open.
        if _incomplete(source):
            prompt = "... "
            continue
        buffer = []
        prompt = ">>> "

        try:
            interp.run_source(source, file="<repl>")
        except NpSyntaxError as err:
            _print_error(err)
        except NpError as err:
            _print_error(err)
        except KeyboardInterrupt:
            print("\nInterrupted.")
        print()


def _incomplete(source: str) -> bool:
    """Heuristic multi-line detection: unbalanced brackets or hanging colon."""
    depth = 0
    last_meaningful = ""
    in_string = False
    quote = ""
    i = 0
    while i < len(source):
        ch = source[i]
        if in_string:
            if ch == "\\" and i + 1 < len(source):
                i += 2
                continue
            if ch == quote:
                in_string = False
            i += 1
            continue
        if ch in "\"'":
            in_string = True
            quote = ch
        elif ch == "#":
            while i < len(source) and source[i] != "\n":
                i += 1
            continue
        elif ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif ch not in " \t\r\n":
            last_meaningful = ch
        i += 1
    if depth > 0:
        return True
    # A line ending with ':' starts a block.
    stripped_lines = [ln for ln in source.splitlines() if ln.strip()
                      and not ln.strip().startswith("#")]
    return bool(stripped_lines and stripped_lines[-1].rstrip().endswith(":"))


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    if not argv:
        return repl()

    command = argv[0]

    if command in ("--version", "-v", "version"):
        print(f"NepaliCode {VERSION}")
        print(f"Runtime {VERSION} (tree-walking interpreter)")
        print(f"nppm {VERSION} (planned)")
        return 0

    if command in ("--help", "-h", "help"):
        print("NepaliCode — a programming language from Nepal")
        print()
        print("Usage:")
        print("  nepali                 Start the REPL")
        print("  nepali run <file.np>   Run a .np program")
        print("  nepali check <file.np> Parse a file without running it")
        print("  nepali new <name>      Scaffold a new project")
        print("  nepali repl            Start the REPL")
        print("  nepali --vm <file.np>  Run on the experimental bytecode VM")
        print("  nepali --version       Show version information")
        return 0

    if command == "repl":
        return repl()

    if command == "run":
        if len(argv) < 2:
            print("Usage: nepali run <file.np>")
            return 2
        return cmd_run(argv[1])

    if command == "check":
        if len(argv) < 2:
            print("Usage: nepali check <file.np>")
            return 2
        return cmd_check(argv[1])

    if command == "new":
        if len(argv) < 2:
            print("Usage: nepali new <project-name>")
            return 2
        return cmd_new(argv[1])

    if command == "--vm":
        if len(argv) < 2:
            print("Usage: nepali --vm <file.np>")
            return 2
        return cmd_run(argv[1], vm=True)

    # Bare filename: nepali main.np
    if command.endswith(".np"):
        return cmd_run(command)

    print(f"Unknown command: {command}\nTry 'nepali --help'.")
    return 2


if __name__ == "__main__":
    sys.exit(main())
