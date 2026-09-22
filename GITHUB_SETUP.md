# GitHub Publishing Guide for NepaliCode

This guide will help you publish NepaliCode to GitHub as an open source project.

## Prerequisites

1. **Git installed**: Download from https://git-scm.com/
2. **GitHub account**: Create at https://github.com/
3. **GitHub CLI (optional)**: For easier GitHub operations

## Step-by-Step Setup

### 1. Initialize Git Repository

Open PowerShell or Command Prompt in the project directory:

```bash
cd "C:\Users\Diwas\Desktop\.np lannguage"
git init
```

### 2. Configure Git

Set your identity (if not already configured):

```bash
git config user.name "Diwas Khatri"
git config user.email "diwas@nepalcode.com"
```

### 3. Create GitHub Repository

Option A: Using GitHub Website
1. Go to https://github.com/new
2. Repository name: `NepaliCode`
3. Description: `A modern, simple programming language from Nepal`
4. Set as Public
5. Don't initialize with README (we have one)
6. Click "Create repository"

Option B: Using GitHub CLI
```bash
gh repo create NepaliSource/NepaliCode --public --description "A modern, simple programming language from Nepal"
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

### 6. Add Remote Repository

```bash
git remote add origin https://github.com/NepaliSource/NepaliCode.git
```

### 7. Push to GitHub

```bash
git branch -M main
git push -u origin main
```

## Verification

After pushing, visit your repository at:
https://github.com/NepaliSource/NepaliCode

You should see:
- ✅ README.md displayed
- ✅ All source files
- ✅ Examples directory
- ✅ Documentation
- ✅ LICENSE file

## Repository Settings

### 1. Enable Features
Go to Settings → Options:
- ✅ Set "NepaliCode" as repository name
- ✅ Add description
- ✅ Set website to: https://nepalcode.com
- ✅ Enable Topics: `programming-language`, `nepal`, `python`, `interpreter`, `bytecode`

### 2. Protection Rules
Settings → Branches → Add rule:
- Branch name pattern: `main`
- Require pull request reviews: ✅
- Require status checks: ✅
- Restrict who can push: ✅ (only maintainers)

### 3. Collaborators
Settings → Collaborators:
- Add collaborators as needed
- Set permissions (maintain, write, read)

## Organization Setup (Optional)

If you want to use the NepaliSource organization:

1. Create organization at https://github.com/organizations/new
2. Organization name: `NepaliSource`
3. Create repository under organization
4. Update remote:
```bash
git remote set-url origin https://github.com/NepaliSource/NepaliCode.git
git push -u origin main
```

## Post-Publishing Steps

### 1. Create Release
- Go to Releases → Create new release
- Tag version: `v0.1.0-alpha`
- Release title: `NepaliCode v0.1.0-alpha - Initial Release`
- Description: Use release notes from CHANGELOG
- Attach binaries: `dist/nepali.exe`, `dist/NepaliLang_Setup.exe`

### 2. Add GitHub Topics
Add topics to improve discoverability:
- `programming-language`
- `nepal`
- `python`
- `interpreter`
- `bytecode`
- `compiler`
- `vscode-extension`
- `open-source`

### 3. Setup GitHub Pages (Optional)
Settings → Pages:
- Source: `main` branch
- Folder: `/docs`
- This will host documentation at: https://nepalisource.github.io/NepaliCode/

### 4. Enable Discussions
Settings → General → Features:
- Enable Discussions for community support

### 5. Setup Issue Templates
Create `.github/ISSUE_TEMPLATE/`:
- `bug_report.md`
- `feature_request.md`
- `question.md`

### 6. Setup Pull Request Template
Create `.github/pull_request_template.md`

## Future Commit Guidelines

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

Examples:
```
feat(math): add trigonometric functions

Add sin, cos, tan functions to ganit module
with proper degree/radian conversion.

Closes #123
```

```
fix(parser): handle nested expressions correctly

Fixed parsing of nested mathematical expressions
that were causing syntax errors in complex formulas.

Fixes #456
```

## Branch Strategy

- `main`: Stable releases
- `develop`: Development branch
- `feature/*`: Feature branches
- `bugfix/*`: Bug fix branches
- `hotfix/*`: Emergency fixes

## Publishing Workflow

1. Develop on feature branch
2. Create pull request to `develop`
3. Review and merge
4. Test on `develop`
5. Create release branch from `develop`
6. Merge to `main`
7. Tag release
8. Push tag to trigger release automation

## Security Considerations

- Never commit secrets (API keys, passwords)
- Use `.env` files and add to `.gitignore`
- Use GitHub Secrets for CI/CD
- Enable security advisories
- Regular dependency updates

## Community Guidelines

### Code of Conduct
Create `CODE_OF_CONDUCT.md` with community guidelines.

### Contributing Guide
Enhance `CONTRIBUTING.md` with detailed contribution guidelines.

### License Enforcement
Ensure all contributions include proper license headers.

## Success Indicators

Your repository is successfully published when:
- ✅ Repository is accessible at GitHub URL
- ✅ README displays correctly
- ✅ All files are present
- ✅ License is visible
- ✅ CI/CD is working (if configured)
- ✅ First release is published
- ✅ Issues and Discussions are enabled

## Troubleshooting

### Authentication Issues
```bash
# Use personal access token
git remote set-url origin https://YOUR_TOKEN@github.com/NepaliSource/NepaliCode.git
```

### Large Files
```bash
# Install Git LFS for large files
git lfs install
git lfs track "*.exe"
git lfs track "*.vsix"
```

### Merge Conflicts
```bash
git pull origin main --rebase
# Resolve conflicts
git add .
git rebase --continue
```

## Support

For help with Git/GitHub:
- Git Documentation: https://git-scm.com/doc
- GitHub Documentation: https://docs.github.com/
- GitHub Community Forum: https://github.community/

---

**Ready to publish NepaliCode to the world! 🚀🇳🇵**
