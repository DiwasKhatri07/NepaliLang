# Quick Start Guide

## 1. Running NepaliLang Files

### Option A: From Project Directory
```bash
cd "C:\Users\Diwas\Desktop\.np lannguage"
nepali.bat examples\hello.np
```

### Option B: Add to System PATH
```bash
# Run this to add nepali to your PATH
setup_path.bat
```

Then you can run from anywhere:
```bash
nepali.bat "C:\Users\Diwas\Desktop\.np lannguage\examples\hello.np"
```

### Option C: Using Python directly
```bash
python "C:\Users\Diwas\Desktop\.np lannguage\main.py" examples\hello.np
```

## 2. Using NepaliCode Editor

```bash
cd "C:\Users\Diwas\Desktop\.np lannguage"
nepalicode.bat
```

This opens the built-in editor with:
- Syntax highlighting
- Run button (F5)
- File operations
- Output display

## 3. VS Code Extension Setup

### Quick Installation (No npm required)

1. **Copy extension folder to VS Code extensions:**
```bash
# Navigate to VS Code extensions folder
# Windows: %USERPROFILE%\.vscode\extensions
# Example: C:\Users\Diwas\.vscode\extensions

# Create folder
mkdir nepalilang-0.1.0

# Copy all files from vscode-extension to this folder
```

2. **Restart VS Code**

3. **Test it:**
   - Create a file `test.np`
   - You should see the NP logo
   - Syntax highlighting should work
   - Press F5 to run

### Alternative: Using npm

```bash
cd vscode-extension
npm install -g @vscode/vsce
vsce package
```

Then install the `.vsix` file in VS Code.

## 4. Common Issues

### "nepali command not found"
- Use full path: `nepali.bat` from project directory
- Or run `setup_path.bat` to add to PATH

### VS Code extension not working
- Make sure you copied the entire vscode-extension folder
- Restart VS Code completely
- Check that the file extension is `.np`

### Editor not opening
- Make sure Python is installed
- Run from the project directory

## 5. Testing Your Setup

Run these commands to verify everything works:

```bash
# Test CLI
nepali.bat examples\hello.np

# Test Editor
nepalicode.bat

# Test VS Code
# Create test.np in VS Code and check for syntax highlighting
```

## 6. Next Steps

- Read the full documentation in `docs/` folder
- Try the examples in `examples/` folder
- Explore the standard library
- Build your own NepaliLang programs!