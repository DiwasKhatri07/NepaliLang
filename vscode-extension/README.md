# NepaliLang VS Code Extension

Official VS Code extension for NepaliLang programming language.

## Features

- **Syntax Highlighting**: Full syntax highlighting for .np files
- **Code Snippets**: Useful code snippets for common patterns
- **File Icon**: Custom file icon for .np files
- **Run Integration**: Run .np files directly from VS Code (F5)
- **Syntax Checking**: Basic syntax validation
- **Auto-completion**: Basic keyword completion

## Installation

### Manual Installation

1. Build the extension:
```bash
cd vscode-extension
npm install
npm run compile
```

2. Package the extension:
```bash
vsce package
```

3. Install the .vsix file in VS Code:
   - Open VS Code
   - Go to Extensions → Install from VSIX
   - Select the generated .vsix file

### Development

```bash
cd vscode-extension
npm install
npm run watch
```

Then press F5 in VS Code to launch a new instance with the extension loaded.

## Features in Detail

### Syntax Highlighting
- Keywords (English and Nepali)
- Strings and comments
- Numbers and operators
- Function calls
- Built-in functions

### Code Snippets
- `print` → print statement
- `if` → if statement
- `def` → function definition
- `kaam` → Nepali function definition
- `yedi` → Nepali if statement
- And many more...

### Keyboard Shortcuts
- `F5` - Run current .np file

## Configuration

```json
{
  "nepalilang.executablePath": "nepali",
  "nepalilang.enableLinting": true
}
```

## Contributing

Contributions welcome! Please read the main project documentation.

## License

MIT License - see LICENSE file for details.