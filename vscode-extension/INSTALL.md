# NepaliLang VS Code Extension Installation

## Option 1: Manual Installation (Recommended)

### Step 1: Create Extension Folder
```bash
# In VS Code
# 1. Go to File > Preferences > Extensions
# 2. Click the three dots menu
# 3. Select "Install from VSIX..."
```

### Step 2: Package the Extension
Since we have a simple JavaScript extension, you can install it directly:

1. **Install vsce globally** (first time only):
```bash
npm install -g @vscode/vsce
```

2. **Package the extension**:
```bash
cd vscode-extension
vsce package
```

This will create a `nepalilang-0.1.0.vsix` file.

### Step 3: Install in VS Code
1. Open VS Code
2. Go to Extensions
3. Click the three dots (⋮) in the top right
4. Select "Install from VSIX..."
5. Choose the `nepalilang-0.1.0.vsix` file
6. Reload VS Code when prompted

## Option 2: Development Installation

### Step 1: Navigate to Extension Folder
```bash
cd vscode-extension
```

### Step 2: Install Dependencies (if needed)
```bash
npm install
```

### Step 3: Build the Extension
```bash
# Since we're using JavaScript instead of TypeScript, no build is needed
# The extension is ready to use as-is
```

### Step 4: Install in Development Mode
1. Open VS Code
2. Press `F5` to open a new VS Code window with the extension loaded
3. Or go to Run and Debug in VS Code and select "Run Extension"

## Option 3: Direct Folder Installation

### Step 1: Copy Extension Folder
```bash
# Navigate to your VS Code extensions folder
# Windows: %USERPROFILE%\.vscode\extensions
# macOS/Linux: ~/.vscode/extensions

# Create a folder named nepalilang-0.1.0
# Copy the entire vscode-extension folder contents there
```

### Step 2: Reload VS Code
1. Restart VS Code
2. The extension should be automatically loaded

## Verification

After installation, you should see:

1. **File Icon**: NP logo with Nepal colors for `.np` files
2. **Syntax Highlighting**: Colored keywords and strings
3. **Code Snippets**: Type `print` + Tab for snippets
4. **Commands**: F5 to run .np files
5. **Language**: "NepaliLang" in the language selector

## Configuration

The extension adds these settings to your VS Code settings:

```json
{
  "nepalilang.executablePath": "nepali",
  "nepalilang.enableLinting": true
}
```

## Troubleshooting

### Extension not loading
- Check VS Code output for errors
- Ensure all files are in the correct locations
- Try reloading VS Code

### Syntax highlighting not working
- Make sure the file extension is `.np`
- Check that the language is set to "NepaliLang"
- Reload the window

### Run command not working
- Ensure the nepali executable is in your PATH
- Configure the executable path in settings
- Check the terminal output for errors

## Features After Installation

✅ **File Icons**: NP logo for .np files  
✅ **Syntax Highlighting**: Full color coding  
✅ **Code Snippets**: Quick code templates  
✅ **Run Integration**: F5 to execute files  
✅ **Language Support**: Full .np file support  

## Next Steps

1. Create a test file: `test.np`
2. Write some NepaliLang code
3. Try running it with F5
4. Explore the syntax highlighting and snippets