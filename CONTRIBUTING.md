# Contributing to NepaliCode

Thank you for your interest in contributing to NepaliCode! This document provides guidelines and instructions for contributing to the project.

## 🤝 How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report:

1. **Use a clear and descriptive title**
2. **Provide detailed information**:
   - NepaliCode version
   - Operating system
   - Python version (if applicable)
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Error messages or stack traces
3. **Include minimal code example** that reproduces the issue
4. **Use appropriate labels** (bug, enhancement, etc.)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:

1. **Use a clear title**
2. **Provide a detailed description** of the enhancement
3. **Explain why this enhancement would be useful**
4. **Provide examples** of how the enhancement would work
5. **List any alternatives** you've considered

### Pull Requests

We welcome pull requests! Here's how to contribute:

#### Development Workflow

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/NepaliCode.git
   cd NepaliCode
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make your changes**
   - Write code following the style guide
   - Add tests for new features
   - Update documentation
   - Ensure all tests pass

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat(module): add your feature description"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request**
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Provide a clear description of your changes
   - Link to related issues

#### Commit Message Guidelines

Follow the Conventional Commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks
- `perf`: Performance improvements

**Examples:**
```
feat(ganit): add trigonometric functions

Add sin, cos, tan functions to the ganit module
with proper degree/radian conversion support.

Closes #123
```

```
fix(parser): handle nested expressions correctly

Fixed parsing of nested mathematical expressions
that were causing syntax errors in complex formulas.

Fixes #456
```

## 📝 Code Style Guidelines

### Python Code

- Follow PEP 8 style guide
- Use 4 spaces for indentation
- Maximum line length: 88 characters
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Type hints where appropriate

### NepaliCode Code

- Use clear, descriptive names
- Prefer English variable names, Nepali keywords for language constructs
- Add comments for complex logic
- Follow existing patterns in the codebase
- Keep functions focused and small

### Examples

**Good:**
```python
def calculate_compound_interest(principal, rate, time):
    """Calculate compound interest over time period."""
    return principal * (1 + rate) ** time
```

**Bad:**
```python
def calc(p, r, t):
    return p * (1 + r) ** t
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python tests/run_all_tests.py

# Run specific test file
python tests/test_bytecode.py

# Run with coverage
pytest --cov=src tests/
```

### Writing Tests

- Write tests for all new features
- Test both success and failure cases
- Use descriptive test names
- Keep tests independent
- Mock external dependencies

**Example:**
```python
def test_add_function():
    """Test the add function in ganit module."""
    result = ganit.jod(5, 3)
    assert result == 8

def test_add_with_negative():
    """Test add function with negative numbers."""
    result = ganit.jod(-5, 3)
    assert result == -2
```

## 📚 Documentation

### Updating Documentation

- Keep documentation in sync with code changes
- Use clear, concise language
- Include code examples
- Update relevant sections in README
- Add comments to complex code

### Example Documentation

```python
def parse_expression(expression):
    """
    Parse a mathematical expression into an AST.
    
    Args:
        expression (str): The mathematical expression to parse
        
    Returns:
        AST: The abstract syntax tree representation
        
    Raises:
        SyntaxError: If the expression has invalid syntax
        
    Example:
        >>> parse_expression("2 + 3")
        AST(BinaryOperation('+', Number(2), Number(3)))
    """
    # Implementation
```

## 🏗️ Project Structure

### Core Components

- `src/lexer.py` - Lexical analysis
- `src/parser.py` - Parsing and AST generation
- `src/interpreter.py` - AST interpretation
- `src/bytecode.py` - Bytecode compilation and VM
- `src/cli.py` - Command-line interface

### Standard Library

- `stdlib/ganit.py` - Mathematics
- `stdlib/samaya.py` - Date/time
- `stdlib/randomlib.py` - Random numbers
- `stdlib/jsonlib.py` - JSON operations
- `stdlib/file.py` - File operations
- Add new modules following existing patterns

### Examples

- Add examples in `examples/` directory
- Use numbered naming: `XX_description.np`
- Test all examples before submitting
- Update `examples/EXAMPLES_INDEX.md`

## 🎯 Areas for Contribution

### High Priority

- **Bug fixes** - Help squash bugs
- **Tests** - Improve test coverage
- **Documentation** - Improve docs and examples
- **Standard library** - Add new library functions

### Medium Priority

- **Performance** - Optimize code
- **Refactoring** - Improve code quality
- **Features** - Implement planned features
- **VS Code extension** - Improve extension

### Low Priority

- **Tooling** - Development tools
- **Infrastructure** - CI/CD improvements
- **Community** - Help newcomers

## 🚀 Getting Started

### First-Time Setup

```bash
# Clone repository
git clone https://github.com/NepaliSource/NepaliCode.git
cd NepaliCode

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (if any)
pip install -r requirements.txt

# Run tests to verify setup
python tests/run_all_tests.py
```

### Making Your First Contribution

1. Start with documentation improvements
2. Fix a simple bug
3. Add a test case
4. Improve an example
5. Add a small feature

## 📋 Review Process

### What We Look For

- **Code quality** - Clean, readable, maintainable
- **Tests** - Comprehensive test coverage
- **Documentation** - Well-documented changes
- **Style** - Follows project guidelines
- **Purpose** - Aligns with project goals

### Review Timeline

- Pull requests are typically reviewed within 1-3 days
- Complex changes may take longer
- Feel free to ping if no response after 3 days

### Merging

- Maintainers will review and merge
- Squash commits for clean history
- Update CHANGELOG for significant changes
- Tag releases for version bumps

## 🌟 Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation
- GitHub contributors list

## 💬 Communication

### Channels

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - General discussions
- **Pull Requests** - Code reviews and collaboration

### Getting Help

- Check existing issues and discussions
- Read documentation thoroughly
- Ask questions in Discussions
- Be patient and respectful

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Thank You

Thank you for contributing to NepaliCode! Your contributions help make programming more accessible to everyone in Nepal and around the world.

---

**Made with ❤️ by the NepaliCode community** 🇳🇵
