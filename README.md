# NepaliCode 🇳🇵

**A modern, simple programming language from Nepal that makes programming and automation easy to understand.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.1.0--alpha-blue)](https://github.com/NepaliSource/NepaliCode)
[![Python](https://img.shields.io/badge/python-3.6+-green.svg)](https://www.python.org/)

## 🌟 Mission

> **"Programming should be simple enough that a Nepali beginner can understand what the code is doing."**

NepaliCode is designed to be:
- **Simple** - Easy to learn and write
- **Expressive** - Clean, natural syntax
- **Nepali** - Native Nepali keywords and identity
- **Professional** - Production-ready features
- **Beginner-Friendly** - Accessible to everyone

## 🎯 Key Features

### Language Features
- ✅ **Python-like syntax** - Familiar and intuitive
- ✅ **Nepali keywords** - `yedi` (if), `kaam` (def), `firta` (return)
- ✅ **Full Unicode support** - Nepali text and identifiers
- ✅ **Bytecode VM** - Stack-based virtual machine
- ✅ **Module system** - Professional Python-like imports
- ✅ **OOP support** - Classes, inheritance, methods
- ✅ **Error handling** - Try/except with Nepali keywords
- ✅ **Async foundation** - async/await patterns

### Standard Library
- ✅ **ganit** - Mathematics operations
- ✅ **samaya** - Date and time functions
- ✅ **randomlib** - Random number generation
- ✅ **jsonlib** - JSON parsing and stringifying
- ✅ **file** - File operations
- ✅ **database** - SQLite database support
- ✅ **anurodh** - HTTP requests (requests-like API)
- ✅ **asyn** - Async programming foundation
- ✅ **telegram** - Telegram bot foundation
- ✅ **browser** - Browser automation foundation

### Developer Tools
- ✅ **CLI** - Command-line interface with REPL
- ✅ **VS Code Extension** - Syntax highlighting, run/debug
- ✅ **50+ Examples** - Comprehensive learning resources
- ✅ **Bytecode compiler** - Compile .np to bytecode
- ✅ **Interpreter** - Fallback for complex features

## 🚀 Quick Start

### Installation

**Option 1: Using Python (Development)**
```bash
git clone https://github.com/NepaliSource/NepaliCode.git
cd NepaliCode
python main.py examples/01_hello_world.np
```

**Option 2: Standalone Executable (Windows)**
```bash
# Download nepali.exe from releases
nepali.exe examples/01_hello_world.np
```

**Option 3: VS Code Extension**
```bash
# Install from VS Code Marketplace
# Search "NepaliCode" and install
```

### First Program

Create `hello.np`:
```np
print("Namaste Nepal!")
```

Run it:
```bash
python main.py hello.np
```

## 📚 Syntax Examples

### Variables and Types
```np
name = "Diwas"
age = 21
is_student = sacho
items = [1, 2, 3, 4, 5]
user = {"name": "Diwas", "age": 21}
```

### Control Flow
```np
# English keywords
yedi age >= 18:
    print("Adult")
natra:
    print("Minor")

# Nepali keywords
yedi umar >= 18:
    print("Adult")
natra:
    print("Minor")
```

### Loops
```np
# For loop
ko_lagi item ma items:
    print(item)

# While loop
jabasamma count < 10:
    count += 1
```

### Functions
```np
kaam add(a, b):
    firta a + b

kaam greet(name="World"):
    print(f"Namaste {name}!")

print(add(10, 20))
greet("Diwas")
```

### Classes
```np
kakshya Person:
    kaam __init__(self, name, age):
        self.name = name
        self.age = age
    
    kaam greet(self):
        firta f"Namaste, I am {self.name}"

user = Person("Diwas", 21)
print(user.greet())
```

### Error Handling
```np
koshish:
    data = file.read("data.json")
samau error:
    print(f"Error: {error}")
antya:
    print("Finished")
```

### Module System
```np
lyau ganit
lyau jsonlib
lyau file

print(ganit.jod(5, 3))
data = jsonlib.parse('{"name": "Diwas"}')
content = file.read("file.txt")
```

## 📖 Documentation

### Core Concepts
- [Installation Guide](docs/installation.md)
- [First Program](docs/first_program.md)
- [Syntax Reference](docs/syntax.md)
- [Standard Library](docs/stdlib.md)

### Examples
- [50+ Comprehensive Examples](examples/EXAMPLES_INDEX.md)
- Covering: basics, OOP, modules, libraries, advanced topics

### Advanced
- [Bytecode VM Documentation](BYTECODE_VM_IMPLEMENTATION.md)
- [Module System](MODULE_SYSTEM_INTEGRATED.txt)
- [Upgrade Summary](UPGRADE_COMPLETE.md)

## 🏗️ Architecture

```
.np source
  ↓
Lexer (src/lexer.py)
  ↓
Parser (src/parser.py)
  ↓
AST
  ↓
Bytecode Compiler (src/bytecode.py)
  ↓
Bytecode Instructions
  ↓
Bytecode VM (src/bytecode.py)
  ↓
Runtime Output
```

## 📁 Project Structure

```
NepaliCode/
├── src/                    # Core language implementation
│   ├── lexer.py           # Lexical analysis
│   ├── parser.py          # Parsing and AST
│   ├── interpreter.py     # Interpreter
│   ├── bytecode.py        # Bytecode VM
│   └── cli.py             # Command-line interface
├── stdlib/                # Standard library modules
│   ├── ganit.py          # Mathematics
│   ├── samaya.py         # Time
│   ├── randomlib.py      # Random
│   ├── jsonlib.py        # JSON
│   ├── file.py           # File operations
│   ├── database.py       # SQLite
│   ├── anurodh.py        # HTTP
│   └── ...
├── examples/              # 50+ example programs
│   ├── 01_hello_world.np
│   ├── 02_variables_and_types.np
│   └── ...
├── tests/                 # Test suite
├── vscode-extension/      # VS Code extension
├── dist/                  # Build artifacts
│   ├── nepali.exe        # Standalone executable
│   └── NepaliLang_Setup.exe
├── docs/                  # Documentation
└── README.md
```

## 🛠️ Development

### Setup Development Environment
```bash
# Clone repository
git clone https://github.com/NepaliSource/NepaliCode.git
cd NepaliCode

# Run tests
python tests/run_all_tests.py

# Run REPL
python main.py

# Run example
python main.py examples/01_hello_world.np
```

### Building Executable
```bash
# Using PyInstaller
pyinstaller --onefile --name nepali main.py

# Output: dist/nepali.exe
```

### VS Code Extension Development
```bash
cd vscode-extension
npm install
npm run build
vsce package
```

## 🧪 Testing

```bash
# Run all tests
python tests/run_all_tests.py

# Run specific test
python tests/test_bytecode.py

# Run examples
python main.py examples/01_hello_world.np
```

## 🌍 Nepali Keywords

| English | Nepali | Meaning |
|---------|--------|---------|
| def | kaam | function |
| return | firta | return |
| if | yedi | if |
| else | natra | else |
| elif | athawa | elif |
| for | ko_lagi | for |
| while | jabasamma | while |
| in | ma | in |
| class | kakshya | class |
| import | lyau | import |
| from | bata | from |
| try | koshish | try |
| except | samau | except |
| finally | antya | finally |
| raise | uthau | raise |
| with | bhitra | with |
| and | ra | and |
| or | wa | or |
| not | hoina | not |
| True | sacho | true |
| False | jhut | false |
| None | khali | none |
| break | rok | break |
| continue | agadi | continue |

## 🗺️ Roadmap

### ✅ Phase 1: Complete (Current)
- [x] Language core (lexer, parser, interpreter)
- [x] Bytecode VM
- [x] Module system
- [x] Standard library (10+ modules)
- [x] CLI and REPL
- [x] VS Code extension
- [x] 50+ examples
- [x] Documentation

### 🚧 Phase 2: In Progress
- [ ] Enhanced HTTP library
- [ ] Async runtime improvements
- [ ] Type system foundation
- [ ] Package manager foundation

### 🔮 Phase 3: Future
- [ ] Native runtime (no Python dependency)
- [ ] Full LSP implementation
- [ ] Formatter and linter
- [ ] Advanced compiler optimizations
- [ ] Package manager (nppm)
- [ ] Cloud tools and integrations

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Guidelines
- Follow the existing code style
- Add tests for new features
- Update documentation
- Use meaningful commit messages
- Be respectful and inclusive

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Author

**Diwas Khatri**
- [GitHub](https://github.com/DiwasKhatri)
- [Organization](https://github.com/NepaliSource)

## 🙏 Acknowledgments

- Inspired by Python's simplicity and elegance
- Built with love for the Nepali programming community
- Thanks to all contributors and supporters

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/NepaliSource/NepaliCode/issues)
- **Discussions**: [GitHub Discussions](https://github.com/NepaliSource/NepaliCode/discussions)
- **Email**: dev@nepalcode.com

## 🌐 Links

- **Website**: https://nepalcode.com
- **Documentation**: https://docs.nepalcode.com
- **VS Code Extension**: [Marketplace](https://marketplace.visualstudio.com/items?itemName=NepaliSource.nepalcode)

---

**Made with ❤️ in Nepal**

*NepaliCode - Programming from Nepal, for the World* 🇳🇵
