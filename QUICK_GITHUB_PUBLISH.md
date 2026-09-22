# Quick GitHub Publishing Commands

## Step-by-Step Commands to Publish NepaliCode

Run these commands in PowerShell or Command Prompt:

### 1. Navigate to Project Directory
```bash
cd "C:\Users\Diwas\Desktop\.np lannguage"
```

### 2. Initialize Git Repository
```bash
git init
```

### 3. Configure Your Identity
```bash
git config user.name "Diwas Khatri"
git config user.email "diwas@nepalcode.com"
```

### 4. Add All Files
```bash
git add .
```

### 5. Create Initial Commit
```bash
git commit -m "Initial commit: NepaliCode v0.1.0-alpha

- Complete language implementation with lexer, parser, interpreter
- Bytecode VM with stack-based execution
- Professional module system with 10+ standard libraries
- 50+ comprehensive examples covering all features
- VS Code extension with syntax highlighting
- Standalone Windows executable
- Full documentation and README
- MIT License - Open source

Made with ❤️ in Nepal by Diwas Khatri - NepaliSource"
```

### 6. Create GitHub Repository (Manual Step)

**IMPORTANT:** Before running the next commands, you need to create the repository on GitHub:

1. Go to https://github.com/new
2. Repository name: `NepaliCode`
3. Description: `A modern, simple programming language from Nepal`
4. Set as **Public**
5. **Do NOT** initialize with README (we already have one)
6. Click "Create repository"

### 7. Add Remote Repository
```bash
git remote add origin https://github.com/NepaliSource/NepaliCode.git
```

*Note: Replace `NepaliSource` with your GitHub username if you're not using an organization*

### 8. Push to GitHub
```bash
git branch -M main
git push -u origin main
```

### 9. Verify

Visit your repository at:
https://github.com/NepaliSource/NepaliCode

You should see all your files, README, and documentation!

## Alternative: Using GitHub CLI (if installed)

```bash
# Create and push in one command
gh repo create NepaliSource/NepaliCode --public --source=. --remote=origin --push
```

## Authentication

If Git asks for authentication:
- Use your GitHub username and password
- Or use a Personal Access Token (recommended)
- Create token at: https://github.com/settings/tokens

## Troubleshooting

### If push fails with authentication error:
```bash
# Use personal access token
git remote set-url origin https://YOUR_TOKEN@github.com/NepaliSource/NepaliCode.git
```

### If large files cause issues:
```bash
# Install Git LFS
git lfs install
git lfs track "*.exe"
git lfs track "*.vsix"
git add .gitattributes
git commit -m "Add Git LFS tracking"
git push
```

## Success!

After successful push:
- ✅ Repository is live on GitHub
- ✅ All code is open source
- ✅ MIT License is applied
- ✅ README is displayed
- ✅ Ready for contributions!

---

**Your NepaliCode project is now open source on GitHub! 🎉🇳🇵**
