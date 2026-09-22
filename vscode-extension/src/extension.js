const vscode = require('vscode');
const path = require('path');
const { exec } = require('child_process');
const os = require('os');
const fs = require('fs');

function activate(context) {
    console.log('NepaliLang extension is now active!');

    // Register run file command
    let runFileCommand = vscode.commands.registerCommand('nepalilang.runFile', () => {
        runNepaliFile();
    });

    // Register debug file command
    let debugFileCommand = vscode.commands.registerCommand('nepalilang.debugFile', () => {
        debugNepaliFile();
    });

    // Register run selection command
    let runSelectionCommand = vscode.commands.registerCommand('nepalilang.runSelection', () => {
        runNepaliSelection();
    });

    // Register check syntax command
    let checkSyntaxCommand = vscode.commands.registerCommand('nepalilang.checkSyntax', () => {
        checkNepaliSyntax();
    });

    context.subscriptions.push(runFileCommand, debugFileCommand, runSelectionCommand, checkSyntaxCommand);

    // Register task provider for F5 debugging
    const taskProvider = vscode.tasks.registerTaskProvider('nepalilang', {
        provideTasks: () => {
            return [
                new vscode.Task(
                    { type: 'nepalilang', run: 'run' },
                    vscode.TaskScope.Workspace,
                    'Run NepaliLang File',
                    'nepalilang',
                    new vscode.ShellExecution('nepali', ['${file}'])
                )
            ];
        },
        resolveTask: () => undefined
    });
    context.subscriptions.push(taskProvider);
}

function runNepaliFile() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No active editor');
        return;
    }

    const document = editor.document;
    if (document.languageId !== 'nepalilang') {
        vscode.window.showErrorMessage('Not a NepaliLang file');
        return;
    }

    if (!document.isUntitled) {
        const filePath = document.fileName;
        const fileDir = path.dirname(filePath);
        const parentDir = path.dirname(fileDir);
        const projectDir = vscode.workspace.rootPath;
        
        // Prioritize main.py (most reliable) then batch files
        const searchDirs = [fileDir, parentDir];
        if (projectDir && projectDir !== fileDir && projectDir !== parentDir) {
            searchDirs.push(projectDir);
        }
        
        const executables = [];
        for (const dir of searchDirs) {
            executables.push(
                path.join(dir, 'main.py'),
                path.join(dir, 'nepali.bat'),
                path.join(dir, 'run_np.bat'),
                path.join(dir, 'nepali.exe.bat'),
                path.join(dir, 'nepali.cmd'),
                path.join(dir, 'dist', 'nepali.exe')
            );
        }
        
        // Find the first existing executable
        for (const exe of executables) {
            if (fs.existsSync(exe)) {
                const terminal = vscode.window.createTerminal('NepaliLang');
                
                // Use appropriate command based on file type
                if (exe.endsWith('.py')) {
                    terminal.sendText(`python "${exe}" "${filePath}"`);
                } else if (exe.endsWith('.exe')) {
                    terminal.sendText(`& "${exe}" "${filePath}"`);
                } else {
                    terminal.sendText(`& "${exe}" "${filePath}"`);
                }
                
                terminal.show();
                return;
            }
        }
        
        // Show detailed error with debugging info
        vscode.window.showErrorMessage(
            `NepaliLang files not found. Searched in:\n${searchDirs.join('\n')}\n\nPlease ensure main.py, run_np.bat, or nepali.exe.bat exists.`
        );
    } else {
        vscode.window.showWarningMessage('Please save the file first');
    }
}

function debugNepaliFile() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No active editor');
        return;
    }

    const document = editor.document;
    if (document.languageId !== 'nepalilang') {
        vscode.window.showErrorMessage('Not a NepaliLang file');
        return;
    }

    if (!document.isUntitled) {
        const filePath = document.fileName;
        const fileDir = path.dirname(filePath);
        const parentDir = path.dirname(fileDir);
        const projectDir = vscode.workspace.rootPath;
        
        // Use the same logic as runNepaliFile
        const searchDirs = [fileDir, parentDir];
        if (projectDir && projectDir !== fileDir && projectDir !== parentDir) {
            searchDirs.push(projectDir);
        }
        
        const executables = [];
        for (const dir of searchDirs) {
            executables.push(
                path.join(dir, 'main.py'),
                path.join(dir, 'nepali.bat'),
                path.join(dir, 'run_np.bat'),
                path.join(dir, 'nepali.exe.bat'),
                path.join(dir, 'nepali.cmd'),
                path.join(dir, 'dist', 'nepali.exe')
            );
        }
        
        for (const exe of executables) {
            if (fs.existsSync(exe)) {
                const terminal = vscode.window.createTerminal('NepaliLang Debug');
                
                if (exe.endsWith('.py')) {
                    terminal.sendText(`python "${exe}" "${filePath}"`);
                } else if (exe.endsWith('.exe')) {
                    terminal.sendText(`"${exe}" "${filePath}"`);
                } else {
                    terminal.sendText(`"${exe}" "${filePath}"`);
                }
                
                terminal.show();
                return;
            }
        }
        
        vscode.window.showErrorMessage('NepaliLang files not found');
    } else {
        vscode.window.showWarningMessage('Please save the file first');
    }
}

function runNepaliSelection() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No active editor');
        return;
    }

    const selection = editor.selection;
    if (selection.isEmpty) {
        vscode.window.showWarningMessage('No text selected');
        return;
    }

    const text = editor.document.getText(selection);
    const terminal = vscode.window.createTerminal('NepaliLang');
    terminal.sendText(`echo '${text}' | & nepali`);
    terminal.show();
}

function checkNepaliSyntax() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No active editor');
        return;
    }

    const document = editor.document;
    if (document.languageId !== 'nepalilang') {
        vscode.window.showErrorMessage('Not a NepaliLang file');
        return;
    }

    const sourceCode = document.getText();
    
    // Basic syntax validation
    const errors = validateSyntax(sourceCode);
    
    if (errors.length === 0) {
        vscode.window.showInformationMessage('✓ Syntax is valid!');
    } else {
        vscode.window.showErrorMessage(`✗ Syntax errors found:\n${errors.join('\n')}`);
    }
}

function validateSyntax(code) {
    const errors = [];
    
    // Check for basic syntax issues
    const lines = code.split('\n');
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const lineNum = i + 1;
        
        // Check for unmatched quotes
        const quotes = line.match(/"/g);
        if (quotes && quotes.length % 2 !== 0) {
            errors.push(`Line ${lineNum}: Unmatched quotes`);
        }
        
        // Check for unmatched parentheses
        const openParens = (line.match(/\(/g) || []).length;
        const closeParens = (line.match(/\)/g) || []).length;
        if (openParens !== closeParens) {
            errors.push(`Line ${lineNum}: Unmatched parentheses`);
        }
        
        // Check for unmatched brackets
        const openBrackets = (line.match(/\[/g) || []).length;
        const closeBrackets = (line.match(/\]/g) || []).length;
        if (openBrackets !== closeBrackets) {
            errors.push(`Line ${lineNum}: Unmatched brackets`);
        }
        
        // Check for unmatched braces
        const openBraces = (line.match(/\{/g) || []).length;
        const closeBraces = (line.match(/\}/g) || []).length;
        if (openBraces !== closeBraces) {
            errors.push(`Line ${lineNum}: Unmatched braces`);
        }
    }
    
    return errors;
}

function deactivate() {
    console.log('NepaliLang extension is now deactivated!');
}

module.exports = {
    activate,
    deactivate
};