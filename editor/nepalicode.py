"""
NepaliCode - Built-in Editor for NepaliLang
A simple IDE with syntax highlighting and code execution.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import threading

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer import tokenize
from src.parser import parse
from src.interpreter import Interpreter, NpError


class NepaliCode:
    def __init__(self, root):
        self.root = root
        self.root.title("NepaliCode - NepaliLang Editor")
        self.root.geometry("1200x800")
        
        self.current_file = None
        self.setup_ui()
        
    def setup_ui(self):
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Run menu
        run_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run File (F5)", command=self.run_file)
        run_menu.add_command(label="Check Syntax", command=self.check_syntax)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Editor tab
        editor_frame = ttk.Frame(self.notebook)
        self.notebook.add(editor_frame, text="Editor")
        
        # Create text editor with line numbers
        self.create_editor(editor_frame)
        
        # Output tab
        output_frame = ttk.Frame(self.notebook)
        self.notebook.add(output_frame, text="Output")
        
        # Create output area
        self.create_output(output_frame)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Bind keyboard shortcuts
        self.root.bind('<F5>', lambda e: self.run_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-n>', lambda e: self.new_file())
        
    def create_editor(self, parent):
        # Create paned window for editor and line numbers
        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Line numbers
        self.line_numbers = tk.Text(paned, width=4, padx=3, takefocus=0,
                                    bg='#f0f0f0', fg='#666666', font=('Consolas', 12))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.line_numbers.config(state=tk.DISABLED)
        
        # Code editor
        self.editor = tk.Text(paned, font=('Consolas', 12), wrap=tk.NONE,
                             bg='#ffffff', fg='#000000', insertbackground='#000000')
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(paned, orient=tk.VERTICAL, command=self.editor.yview)
        h_scroll = ttk.Scrollbar(paned, orient=tk.HORIZONTAL, command=self.editor.xview)
        self.editor.config(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        paned.add(self.line_numbers)
        paned.add(self.editor)
        
        # Add scrollbars to paned window
        paned.add(v_scroll)
        paned.add(h_scroll)
        
        # Configure tags for syntax highlighting
        self.configure_syntax_highlighting()
        
        # Bind events
        self.editor.bind('<KeyRelease>', self.on_key_release)
        self.editor.bind('<Button-1>', self.on_click)
        
    def configure_syntax_highlighting(self):
        # Configure syntax highlighting colors
        self.editor.tag_configure('keyword', foreground='#0000FF', font=('Consolas', 12, 'bold'))
        self.editor.tag_configure('nepali_keyword', foreground='#800080', font=('Consolas', 12, 'bold'))
        self.editor.tag_configure('string', foreground='#008000')
        self.editor.tag_configure('comment', foreground='#808080', font=('Consolas', 12, 'italic'))
        self.editor.tag_configure('number', foreground='#FF6600')
        
    def create_output(self, parent):
        # Create output text area
        self.output = tk.Text(parent, font=('Consolas', 10), bg='#1e1e1e', fg='#d4d4d4')
        self.output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Output scrollbar
        output_scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.output.yview)
        self.output.config(yscrollcommand=output_scroll.set)
        output_scroll.pack(fill=tk.Y, side=tk.RIGHT)
        
    def update_line_numbers(self):
        # Update line numbers
        lines = self.editor.get('1.0', tk.END).count('\n')
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete('1.0', tk.END)
        for i in range(1, lines + 1):
            self.line_numbers.insert(tk.END, f"{i}\n")
        self.line_numbers.config(state=tk.DISABLED)
        
    def on_key_release(self, event):
        self.update_line_numbers()
        self.highlight_syntax()
        
    def on_click(self, event):
        self.update_line_numbers()
        
    def highlight_syntax(self):
        # Simple syntax highlighting
        content = self.editor.get('1.0', tk.END)
        
        # Remove existing tags
        self.editor.tag_remove('keyword', '1.0', tk.END)
        self.editor.tag_remove('nepali_keyword', '1.0', tk.END)
        self.editor.tag_remove('string', '1.0', tk.END)
        self.editor.tag_remove('comment', '1.0', tk.END)
        self.editor.tag_remove('number', '1.0', tk.END)
        
        # Keywords to highlight
        keywords = ['if', 'else', 'elif', 'for', 'while', 'def', 'return', 'class', 
                   'import', 'from', 'try', 'except', 'True', 'False', 'None']
        nepali_keywords = ['yedi', 'natra', 'natabhaye', 'ko_lagi', 'jabasamma', 
                        'kaam', 'firta', 'kakshya', 'lyau', 'bata', 'sacho', 'jhut', 'khali']
        
        # Apply keyword highlighting
        for keyword in keywords:
            self.highlight_word(keyword, 'keyword')
        
        for keyword in nepali_keywords:
            self.highlight_word(keyword, 'nepali_keyword')
        
        # Highlight comments
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '#' in line:
                comment_start = line.index('#')
                start_pos = f"{i+1}.{comment_start}"
                end_pos = f"{i+1}.{len(line)}"
                self.editor.tag_add('comment', start_pos, end_pos)
        
    def highlight_word(self, word, tag):
        # Highlight all occurrences of a word
        content = self.editor.get('1.0', tk.END)
        pos = '1.0'
        
        while True:
            pos = self.editor.search(word, pos, stopindex=tk.END, regexp=True)
            if not pos:
                break
            end_pos = f"{pos}+{len(word)}c"
            self.editor.tag_add(tag, pos, end_pos)
            pos = end_pos
        
    def new_file(self):
        self.current_file = None
        self.editor.delete('1.0', tk.END)
        self.update_line_numbers()
        self.status_bar.config(text="New file")
        
    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("NepaliLang Files", "*.np"), ("All Files", "*.*")]
        )
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.editor.delete('1.0', tk.END)
            self.editor.insert('1.0', content)
            self.current_file = file_path
            self.update_line_numbers()
            self.status_bar.config(text=f"Opened: {file_path}")
            
    def save_file(self):
        if self.current_file:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.editor.get('1.0', tk.END))
            self.status_bar.config(text=f"Saved: {self.current_file}")
        else:
            self.save_file_as()
            
    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".np",
            filetypes=[("NepaliLang Files", "*.np"), ("All Files", "*.*")]
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.editor.get('1.0', tk.END))
            self.current_file = file_path
            self.status_bar.config(text=f"Saved: {file_path}")
            
    def run_file(self):
        # Save current file first
        if not self.current_file:
            self.save_file_as()
            if not self.current_file:
                return
        
        # Switch to output tab
        self.notebook.select(1)
        self.output.delete('1.0', tk.END)
        self.output.insert('1.0', f"Running: {self.current_file}\n")
        self.output.insert('1.0', f"{'='*50}\n")
        
        # Run in separate thread to avoid freezing
        def run_in_thread():
            try:
                interp = Interpreter()
                interp.run_source(self.editor.get('1.0', tk.END))
                self.output.insert('1.0', "\nProgram completed successfully!\n")
            except NpError as e:
                self.output.insert('1.0', f"\n{e}\n")
            except Exception as e:
                self.output.insert('1.0', f"\nError: {e}\n")

            self.status_bar.config(text="Execution completed")
        
        thread = threading.Thread(target=run_in_thread)
        thread.start()
        
    def check_syntax(self):
        content = self.editor.get('1.0', tk.END)
        self.notebook.select(1)
        self.output.delete('1.0', tk.END)
        self.output.insert('1.0', "Checking syntax...\n")
        
        try:
            tokens = tokenize(content)
            statements = parse(tokens)
            self.output.insert('1.0', f"✓ Syntax is valid!\n")
            self.output.insert('1.0', f"  Tokens: {len(tokens)}\n")
            self.output.insert('1.0', f"  AST nodes: {len(statements)}\n")
            self.status_bar.config(text="Syntax check passed")
        except NpError as e:
            self.output.insert('1.0', f"✗ {e}\n")
            self.status_bar.config(text="Syntax check failed")
        except Exception as e:
            self.output.insert('1.0', f"✗ Error: {e}\n")
            self.status_bar.config(text="Syntax check failed")
            
    def show_about(self):
        about_text = """NepaliCode - NepaliLang Editor
        
Version 0.1.0

Made by Diwas Khatri
NepaliSource

A simple IDE for NepaliLang programming language.
        
Features:
- Syntax highlighting
- Code execution
- File operations
- Output display"""
        
        messagebox.showinfo("About NepaliCode", about_text)


def main():
    root = tk.Tk()
    app = NepaliCode(root)
    root.mainloop()


if __name__ == "__main__":
    main()