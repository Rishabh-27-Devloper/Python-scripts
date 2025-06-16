"""
Secure Folder Manager Gen 2 - Enhanced Security with Migration
@author: Prakhar Shukla
@email: Rishabh27@outlook.in

This is Gen 2 of the Secure Folder Manager with improved security and data migration capabilities.
The folder is now stored in a safer location (AppData on Windows, ~/.local/share on Linux/Mac)
instead of the temporary directory to prevent accidental deletion by system cleaners.

Key Improvements in Gen 2:
- Files stored in AppData/Local Application Data instead of temp folder
- Automatic detection and migration of Gen 1 data
- Removed drag-and-drop functionality for enhanced security
- Removed folder adding capability (existing folders preserved)
- Better cross-platform support for secure storage locations

Requirements:
- Python 3.6+
- tkinter (usually included with Python)
- pywin32 (Windows only): pip install pywin32

Usage:
    python secure_folder_manager_gen2.py
"""

import os,sys

def install_and_restart(modulename, pipname=None):
    import subprocess
    import sys
    pipname = pipname or modulename
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pipname])
    except Exception as e:
        print(f"Failed to install {pipname}: {e}")
        sys.exit(1)
    print(f"Installed {pipname}, restarting...")
    os.execl(sys.executable, sys.executable, *sys.argv)

# Standard library imports
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
import shutil
import hashlib
import json
import platform
import subprocess
import time
from pathlib import Path

# Windows-specific imports (optional)
if platform.system() == "Windows":
    try:
        import win32com.client
    except ImportError:
        install_and_restart("pywin32", "pywin32")

class SecureFolderManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Secure Folder Manager Gen 2")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Version info
        self.version = "2.0"
        
        # Configuration paths (safer locations)
        self.config_dir = self.get_safe_config_directory()
        self.config_file = os.path.join(self.config_dir, ".config_gen2.json")
        
        # Legacy Gen 1 config for migration
        self.legacy_config_dir = os.path.join(os.path.expanduser("~"), ".secure_folder_config")
        self.legacy_config_file = os.path.join(self.legacy_config_dir, ".config.json")
        
        # Secure folder path (will be set dynamically in safer location)
        self.secure_folder = None
        self.is_unlocked = False
        self.password_hash = None
        
        # Create config directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)
        self.hide_path(self.config_dir)
        
        # Initialize UI
        self.setup_ui()
        
        # Check for Gen 1 migration first
        self.check_and_migrate_gen1()
        
        # Load configuration
        self.load_config()
        
        # Check if first run
        if not self.password_hash:
            self.first_run_setup()
    
    def get_safe_config_directory(self):
        """Get a safe directory for storing configuration and data"""
        system = platform.system()
        
        if system == "Windows":
            # Use AppData/Local for Windows
            appdata_local = os.environ.get('LOCALAPPDATA')
            if appdata_local:
                return os.path.join(appdata_local, "SecureFolderManager")
            else:
                # Fallback to user profile
                return os.path.join(os.path.expanduser("~"), "AppData", "Local", "SecureFolderManager")
        
        elif system == "Darwin":  # macOS
            # Use ~/Library/Application Support for macOS
            return os.path.join(os.path.expanduser("~"), "Library", "Application Support", "SecureFolderManager")
        
        else:  # Linux and other Unix-like systems
            # Use ~/.local/share for Linux
            return os.path.join(os.path.expanduser("~"), ".local", "share", "SecureFolderManager")
    
    def get_safe_secure_directory(self):
        """Generate a secure folder path in a safe location"""
        # Create a unique folder name in the safe config directory
        folder_name = f".secure_vault_{hashlib.md5(os.urandom(32)).hexdigest()[:16]}"
        secure_path = os.path.join(self.config_dir, folder_name)
        return secure_path
    
    def check_and_migrate_gen1(self):
        """Check for Gen 1 installation and migrate data if found"""
        if os.path.exists(self.legacy_config_file):
            try:
                # Load Gen 1 configuration
                with open(self.legacy_config_file, 'r') as f:
                    legacy_config = json.load(f)
                
                legacy_secure_folder = legacy_config.get('secure_folder')
                legacy_password_hash = legacy_config.get('password_hash')
                
                if legacy_secure_folder and os.path.exists(legacy_secure_folder):
                    # Ask user if they want to migrate
                    migrate = messagebox.askyesno(
                        "Gen 1 Data Found", 
                        "Gen 1 Secure Folder Manager data detected!\n\n"
                        "Your files are currently stored in a temporary location which "
                        "may be cleaned by system maintenance tools.\n\n"
                        "Would you like to migrate your data to a safer location?\n"
                        "(This will move your files to a more secure directory)"
                    )
                    
                    if migrate:
                        self.migrate_from_gen1(legacy_config, legacy_secure_folder, legacy_password_hash)
                        return True
                    else:
                        messagebox.showinfo(
                            "Migration Skipped",
                            "Migration skipped. Your Gen 1 data will remain in its current location.\n"
                            "Note: Files in temporary directories may be deleted by system cleaners."
                        )
            
            except Exception as e:
                messagebox.showerror("Migration Error", f"Error checking Gen 1 data: {e}")
        
        return False
    
    def migrate_from_gen1(self, legacy_config, legacy_secure_folder, legacy_password_hash):
        """Migrate data from Gen 1 to Gen 2"""
        try:
            # Create new secure folder in safe location
            new_secure_folder = self.get_safe_secure_directory()
            os.makedirs(new_secure_folder, exist_ok=True)
            self.hide_path(new_secure_folder)
            
            # Count files to migrate
            file_count = 0
            for root, dirs, files in os.walk(legacy_secure_folder):
                file_count += len(files)
            
            if file_count > 0:
                # Show progress dialog
                progress_window = tk.Toplevel(self.root)
                progress_window.title("Migrating Data...")
                progress_window.geometry("400x150")
                progress_window.transient(self.root)
                progress_window.grab_set()
                
                # Center the progress window
                progress_window.geometry("+%d+%d" % (
                    self.root.winfo_rootx() + 200,
                    self.root.winfo_rooty() + 200
                ))
                
                ttk.Label(progress_window, text="Migrating your secure files to safer location...").pack(pady=10)
                
                progress_var = tk.DoubleVar()
                progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=100)
                progress_bar.pack(pady=10, padx=20, fill='x')
                
                status_label = ttk.Label(progress_window, text="Preparing migration...")
                status_label.pack(pady=5)
                
                # Update the progress window
                progress_window.update()
                
                # Copy all files and folders
                migrated_count = 0
                for root, dirs, files in os.walk(legacy_secure_folder):
                    for file in files:
                        source_file = os.path.join(root, file)
                        # Maintain directory structure
                        rel_path = os.path.relpath(source_file, legacy_secure_folder)
                        dest_file = os.path.join(new_secure_folder, rel_path)
                        
                        # Create destination directory if needed
                        dest_dir = os.path.dirname(dest_file)
                        os.makedirs(dest_dir, exist_ok=True)
                        
                        # Copy file
                        shutil.copy2(source_file, dest_file)
                        migrated_count += 1
                        
                        # Update progress
                        progress = (migrated_count / file_count) * 100
                        progress_var.set(progress)
                        status_label.config(text=f"Migrated {migrated_count}/{file_count} files...")
                        progress_window.update()
                
                progress_window.destroy()
            
            # Update configuration
            self.password_hash = legacy_password_hash
            self.secure_folder = new_secure_folder
            self.save_config()
            
            # Backup and remove legacy config
            legacy_backup = self.legacy_config_file + ".backup"
            shutil.copy2(self.legacy_config_file, legacy_backup)
            
            # Ask if user wants to delete old data
            delete_old = messagebox.askyesno(
                "Migration Complete",
                f"Migration completed successfully!\n\n"
                f"Migrated {file_count} files to safer location.\n\n"
                f"Would you like to delete the old data from the temporary location?\n"
                f"(A backup of your old configuration has been saved)"
            )
            
            if delete_old:
                try:
                    shutil.rmtree(legacy_secure_folder)
                    os.remove(self.legacy_config_file)
                    messagebox.showinfo("Cleanup Complete", "Old data has been safely removed.")
                except Exception as e:
                    messagebox.showwarning("Cleanup Warning", f"Could not remove old data: {e}")
            else:
                messagebox.showinfo("Migration Complete", 
                                  "Migration completed! Your old data remains in the temporary location.")
        
        except Exception as e:
            messagebox.showerror("Migration Error", f"Error during migration: {e}")
            raise
    
    def hide_path(self, path):
        """Hide a file or folder based on the operating system"""
        try:
            if platform.system() == "Windows":
                # Windows: Set hidden attribute
                subprocess.run(['attrib', '+H', path], check=True, 
                             creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                # Linux/Mac: Paths starting with . are hidden by default
                pass
        except Exception as e:
            print(f"Warning: Could not hide path {path}: {e}")
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title with version
        title_label = ttk.Label(main_frame, text=f"Secure Folder Manager Gen 2 (v{self.version})", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Password section
        self.password_frame = ttk.LabelFrame(main_frame, text="Access Control", padding="10")
        self.password_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(self.password_frame, text="Password:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(self.password_frame, textvariable=self.password_var, 
                                       show="*", width=30)
        self.password_entry.grid(row=0, column=1, padx=(0, 10))
        self.password_entry.bind('<Return>', lambda e: self.unlock_folder())
        
        self.unlock_btn = ttk.Button(self.password_frame, text="Unlock", 
                                    command=self.unlock_folder)
        self.unlock_btn.grid(row=0, column=2, padx=(0, 10))
        
        self.lock_btn = ttk.Button(self.password_frame, text="Lock", 
                                  command=self.lock_folder, state="disabled")
        self.lock_btn.grid(row=0, column=3)
        
        # File explorer section
        self.explorer_frame = ttk.LabelFrame(main_frame, text="Secure Files", padding="10")
        self.explorer_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.explorer_frame.columnconfigure(0, weight=1)
        self.explorer_frame.rowconfigure(0, weight=1)
        
        # Treeview for file listing
        self.tree = ttk.Treeview(self.explorer_frame, columns=("Size", "Modified"), show="tree headings")
        self.tree.heading("#0", text="Name")
        self.tree.heading("Size", text="Size")
        self.tree.heading("Modified", text="Modified")
        self.tree.column("#0", width=400)
        self.tree.column("Size", width=100)
        self.tree.column("Modified", width=200)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(self.explorer_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(self.explorer_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout for tree and scrollbars
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Context menu (removed folder-related options)
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Open", command=self.open_file)
        self.context_menu.add_command(label="Delete", command=self.delete_file)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Add Files", command=self.add_files)
        self.context_menu.add_command(label="Refresh", command=self.refresh_files)
        
        # Bind right-click
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.open_file)
        
        # Button frame (removed folder-related buttons and drag-drop info)
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(btn_frame, text="Add Files", command=self.add_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Change Password", command=self.change_password).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Show Storage Info", command=self.show_storage_info).pack(side=tk.LEFT, padx=(0, 5))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Folder is locked. Please enter password to unlock.")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def show_storage_info(self):
        """Show information about the storage location"""
        if not self.secure_folder:
            messagebox.showinfo("Storage Info", "No secure folder has been created yet.")
            return
        
        try:
            # Get folder size
            total_size = 0
            file_count = 0
            folder_count = 0
            
            if os.path.exists(self.secure_folder):
                for root, dirs, files in os.walk(self.secure_folder):
                    folder_count += len(dirs)
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            total_size += os.path.getsize(file_path)
                            file_count += 1
                        except (OSError, IOError):
                            pass
            
            # Format size
            size_str = self.format_size(total_size)
            
            # Storage location info
            storage_info = (
                f"Secure Folder Manager Gen 2 - Storage Information\n\n"
                f"Storage Location: {self.config_dir}\n"
                f"Files: {file_count}\n"
                f"Folders: {folder_count}\n"
                f"Total Size: {size_str}\n\n"
                f"Gen 2 stores your files in a safer location that won't be\n"
                f"accidentally deleted by system cleanup tools.\n\n"
                f"Location Details:\n"
                f"• Windows: AppData/Local/SecureFolderManager\n"
                f"• macOS: ~/Library/Application Support/SecureFolderManager\n"
                f"• Linux: ~/.local/share/SecureFolderManager"
            )
            
            messagebox.showinfo("Storage Information", storage_info)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not retrieve storage information: {e}")
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.password_hash = config.get('password_hash')
                    self.secure_folder = config.get('secure_folder')
                    # Validate secure folder path
                    if self.secure_folder and not os.path.exists(self.secure_folder):
                        os.makedirs(self.secure_folder, exist_ok=True)
                        self.hide_path(self.secure_folder)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            config = {
                'password_hash': self.password_hash,
                'secure_folder': self.secure_folder,
                'version': self.version,
                'created_time': time.time()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.hide_path(self.config_file)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def first_run_setup(self):
        """Setup for first run - create password and secure folder"""
        messagebox.showinfo("Welcome", 
                           f"Welcome to Secure Folder Manager Gen 2!\n\n"
                           f"This version stores your files in a safer location that won't\n"
                           f"be accidentally deleted by system cleanup tools.\n\n"
                           f"Please set up a password to protect your secure folder.")
        
        password = simpledialog.askstring("Set Password", "Enter a password for your secure folder:", show="*")
        if not password:
            messagebox.showerror("Error", "Password is required!")
            self.root.quit()
            return
        
        confirm_password = simpledialog.askstring("Confirm Password", "Confirm your password:", show="*")
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            self.root.quit()
            return
        
        # Set password hash
        self.password_hash = self.hash_password(password)
        
        # Create secure folder in safe location
        self.secure_folder = self.get_safe_secure_directory()
        os.makedirs(self.secure_folder, exist_ok=True)
        self.hide_path(self.secure_folder)
        
        # Save configuration
        self.save_config()
        
        messagebox.showinfo("Success", 
                           f"Secure folder created successfully!\n\n"
                           f"Your files are now stored in a safe location:\n"
                           f"{self.config_dir}\n\n"
                           f"You can now use the application to store your files securely.")
    
    def unlock_folder(self):
        """Unlock the secure folder"""
        password = self.password_var.get()
        if not password:
            messagebox.showerror("Error", "Please enter a password.")
            return
        
        if self.hash_password(password) == self.password_hash:
            self.is_unlocked = True
            self.unlock_btn.config(state="disabled")
            self.lock_btn.config(state="normal")
            self.password_entry.config(state="disabled")
            self.status_var.set("Folder unlocked. You can now view and manage your files.")
            self.refresh_files()
            messagebox.showinfo("Success", "Folder unlocked successfully!")
        else:
            messagebox.showerror("Error", "Incorrect password!")
            self.password_var.set("")
    
    def lock_folder(self):
        """Lock the secure folder"""
        self.is_unlocked = False
        self.unlock_btn.config(state="normal")
        self.lock_btn.config(state="disabled")
        self.password_entry.config(state="normal")
        self.password_var.set("")
        self.status_var.set("Folder is locked. Please enter password to unlock.")
        
        # Clear file tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        messagebox.showinfo("Success", "Folder locked successfully!")
    
    def refresh_files(self):
        """Refresh the file list"""
        if not self.is_unlocked:
            return
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not os.path.exists(self.secure_folder):
            return
        
        # Add files and folders (including migrated folders)
        try:
            for item in os.listdir(self.secure_folder):
                item_path = os.path.join(self.secure_folder, item)
                if os.path.isfile(item_path):
                    size = self.format_size(os.path.getsize(item_path))
                    modified = self.format_time(os.path.getmtime(item_path))
                    self.tree.insert("", "end", text=item, values=(size, modified), tags=("file",))
                elif os.path.isdir(item_path):
                    modified = self.format_time(os.path.getmtime(item_path))
                    self.tree.insert("", "end", text=f"📁 {item}", values=("Folder", modified), tags=("folder",))
        except Exception as e:
            messagebox.showerror("Error", f"Error refreshing files: {e}")
    
    def format_size(self, size):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def format_time(self, timestamp):
        """Format timestamp to readable format"""
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    
    def show_context_menu(self, event):
        """Show context menu on right click"""
        if not self.is_unlocked:
            return
        
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def open_file(self, event=None):
        """Open selected file"""
        if not self.is_unlocked:
            return
        
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        filename = self.tree.item(item)["text"]
        if filename.startswith("📁 "):
            filename = filename[2:]  # Remove folder emoji
        
        file_path = os.path.join(self.secure_folder, filename)
        
        if os.path.isfile(file_path):
            try:
                if platform.system() == "Windows":
                    os.startfile(file_path)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", file_path])
                else:  # Linux
                    subprocess.run(["xdg-open", file_path])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")
        elif os.path.isdir(file_path):
            # Show info about existing folders (migrated from Gen 1)
            messagebox.showinfo("Folder Info", 
                              f"This folder was migrated from Gen 1.\n"
                              f"Folder navigation is not implemented in Gen 2 for security reasons.\n"
                              f"You can access individual files using your system's file manager if needed.")
    
    def delete_file(self):
        """Delete selected file"""
        if not self.is_unlocked:
            return
        
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        filename = self.tree.item(item)["text"]
        if filename.startswith("📁 "):
            filename = filename[2:]  # Remove folder emoji
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{filename}'?"):
            file_path = os.path.join(self.secure_folder, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                self.refresh_files()
                messagebox.showinfo("Success", f"'{filename}' deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete file: {e}")
    
    def add_files(self):
        """Add files to secure folder"""
        if not self.is_unlocked:
            messagebox.showwarning("Access Denied", "Please unlock the folder first.")
            return
        
        files = filedialog.askopenfilenames(title="Select files to add")
        for file_path in files:
            self.copy_to_secure_folder(file_path)
        
        if files:
            self.refresh_files()
            messagebox.showinfo("Success", f"{len(files)} file(s) added successfully!")
    
    def copy_to_secure_folder(self, source_path):
        """Copy file to secure folder"""
        try:
            filename = os.path.basename(source_path)
            dest_path = os.path.join(self.secure_folder, filename)
            
            # Handle name conflicts
            counter = 1
            base_name, ext = os.path.splitext(filename)
            while os.path.exists(dest_path):
                if ext:
                    new_name = f"{base_name}_{counter}{ext}"
                else:
                    new_name = f"{base_name}_{counter}"
                dest_path = os.path.join(self.secure_folder, new_name)
                counter += 1
            
            if os.path.isfile(source_path):
                shutil.copy2(source_path, dest_path)
            else:
                raise ValueError("Only files can be added in Gen 2")
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not copy '{source_path}': {e}")
    
    def change_password(self):
        """Change the folder password"""
        if not self.is_unlocked:
            messagebox.showwarning("Access Denied", "Please unlock the folder first.")
            return
        
        current_password = simpledialog.askstring("Current Password", "Enter current password:", show="*")
        if not current_password or self.hash_password(current_password) != self.password_hash:
            messagebox.showerror("Error", "Incorrect current password!")
            return
        
        new_password = simpledialog.askstring("New Password", "Enter new password:", show="*")
        if not new_password:
            return
        
        confirm_password = simpledialog.askstring("Confirm Password", "Confirm new password:", show="*")
        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return
        
        self.password_hash = self.hash_password(new_password)
        self.save_config()
        messagebox.showinfo("Success", "Password changed successfully!")
    
    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle application closing"""
        if self.is_unlocked:
            if messagebox.askyesno("Exit", "The folder is currently unlocked. Do you want to lock it before exiting?"):
                self.lock_folder()
        self.root.quit()

if __name__ == "__main__":
    app = SecureFolderManager()
    app.run()