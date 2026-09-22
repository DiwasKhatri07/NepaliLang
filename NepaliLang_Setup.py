"""
NepaliLang All-in-One Setup and Installer
Creates a complete Windows installer package
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import subprocess
import threading
import webbrowser
from tkinter import simpledialog

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer import tokenize
from src.parser import parse
from src.interpreter import interpret, NepaliRuntimeError


class NepaliLangSetup:
    def __init__(self, root):
        self.root = root
        self.root.title("NepaliLang Setup")
        self.root.geometry("600x500")
        self.root.configure(bg="#2c3e50")
        
        # Custom styling
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#34495e", height=100)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = tk.Label(header_frame, text="🇳🇵 NepaliLang Setup", 
                              font=("Arial", 24, "bold"), 
                              bg="#34495e", fg="white")
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(header_frame, text="Programming Language from Nepal",
                                 font=("Arial", 12), 
                                 bg="#34495e", fg="#ecf0f1")
        subtitle_label.pack()
        
        # Main content
        content_frame = tk.Frame(self.root, bg="#2c3e50")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Options
        options = [
            ("Add to System PATH", "path_var"),
            ("Install VS Code Extension", "vscode_var"),
            ("Create Desktop Shortcut", "desktop_var"),
            ("Add to Start Menu", "startmenu_var")
        ]
        
        self.vars = {}
        for i, (text, var_name) in enumerate(options):
            var = tk.BooleanVar(value=True)
            self.vars[var_name] = var
            
            checkbox = tk.Checkbutton(content_frame, text=text, variable=var,
                                   font=("Arial", 11), bg="#2c3e50", fg="white",
                                   selectcolor="#34495e", activebackground="#2c3e50")
            checkbox.pack(anchor=tk.W, pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(content_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=20)
        
        # Status label
        self.status_label = tk.Label(content_frame, text="Ready to install",
                                    font=("Arial", 10), bg="#2c3e50", fg="#bdc3c7")
        self.status_label.pack()
        
        # Buttons
        button_frame = tk.Frame(self.root, bg="#2c3e50")
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        install_btn = tk.Button(button_frame, text="Install NepaliLang", 
                              command=self.install,
                              font=("Arial", 12, "bold"),
                              bg="#e74c3c", fg="white",
                              relief=tk.FLAT, padx=20, pady=10)
        install_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        test_btn = tk.Button(button_frame, text="Test Installation",
                           command=self.test_installation,
                           font=("Arial", 12),
                           bg="#3498db", fg="white",
                           relief=tk.FLAT, padx=20, pady=10)
        test_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        editor_btn = tk.Button(button_frame, text="Open Editor",
                             command=self.open_editor,
                             font=("Arial", 12),
                             bg="#27ae60", fg="white",
                             relief=tk.FLAT, padx=20, pady=10)
        editor_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
    def install(self):
        self.status_label.config(text="Installing...")
        self.progress.start()
        
        def install_thread():
            try:
                # Get current directory
                current_dir = os.path.dirname(os.path.abspath(__file__))
                
                # Add to PATH if selected
                if self.vars['path_var'].get():
                    self.add_to_path(current_dir)
                
                # Install VS Code extension if selected
                if self.vars['vscode_var'].get():
                    self.install_vscode_extension(current_dir)
                
                # Create desktop shortcut if selected
                if self.vars['desktop_var'].get():
                    self.create_shortcut(current_dir, "desktop")
                
                # Add to Start Menu if selected
                if self.vars['startmenu_var'].get():
                    self.create_shortcut(current_dir, "startmenu")
                
                self.root.after(0, lambda: self.status_label.config(text="Installation complete!"))
                self.root.after(0, lambda: self.progress.stop())
                self.root.after(0, lambda: messagebox.showinfo("Success", "NepaliLang installed successfully!"))
                
            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(text=f"Error: {str(e)}"))
                self.root.after(0, lambda: self.progress.stop())
                self.root.after(0, lambda: messagebox.showerror("Error", f"Installation failed: {str(e)}"))
        
        threading.Thread(target=install_thread, daemon=True).start()
    
    def add_to_path(self, directory):
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS)
            current_path = winreg.QueryValueEx(key, "PATH")[0]
            
            if directory not in current_path:
                new_path = current_path + ";" + directory
                winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
                winreg.CloseKey(key)
                
                # Notify system of environment change
                import ctypes
                ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x001A, 0, "Environment", 0, 5000, 0x102)
                
                return True
            return False
        except Exception as e:
            print(f"Error adding to PATH: {e}")
            return False
    
    def install_vscode_extension(self, project_dir):
        try:
            vscode_extensions = os.path.expanduser("~/.vscode/extensions")
            extension_dir = os.path.join(vscode_extensions, "nepalilang-0.1.0")
            
            if os.path.exists(extension_dir):
                import shutil
                shutil.rmtree(extension_dir)
            
            import shutil
            vscode_src = os.path.join(project_dir, "vscode-extension")
            shutil.copytree(vscode_src, extension_dir)
            
            return True
        except Exception as e:
            print(f"Error installing VS Code extension: {e}")
            return False
    
    def create_shortcut(self, project_dir, location):
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            
            if location == "desktop":
                shortcut_path = os.path.join(os.path.expanduser("~/Desktop"), "NepaliCode.lnk")
            else:
                shortcut_path = os.path.join(os.path.expanduser("~/AppData/Roaming/Microsoft/Windows/Start Menu/Programs"), "NepaliCode.lnk")
            
            target = os.path.join(project_dir, "nepalicode.bat")
            working_dir = project_dir
            
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = target
            shortcut.WorkingDirectory = working_dir
            shortcut.Description = "NepaliLang Editor"
            shortcut.save()
            
            return True
        except Exception as e:
            print(f"Error creating shortcut: {e}")
            return False
    
    def test_installation(self):
        self.status_label.config(text="Testing installation...")
        
        try:
            # Test if nepali command works
            result = subprocess.run(["python", "main.py", "--version"], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                self.status_label.config(text="Installation test passed!")
                messagebox.showinfo("Test Result", "✓ NepaliLang is working correctly!")
            else:
                self.status_label.config(text="Installation test failed!")
                messagebox.showerror("Test Result", "✗ NepaliLang test failed!")
                
        except Exception as e:
            self.status_label.config(text=f"Test error: {str(e)}")
            messagebox.showerror("Test Error", f"Test failed: {str(e)}")
    
    def open_editor(self):
        try:
            subprocess.Popen(["python", "editor/nepalicode.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open editor: {str(e)}")


def main():
    root = tk.Tk()
    app = NepaliLangSetup(root)
    root.mainloop()


if __name__ == "__main__":
    main()