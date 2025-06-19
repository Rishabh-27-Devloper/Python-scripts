import sys

# List of required modules
required_modules = [
    "os",
    "shutil",
    "win32com.client",
    "tkinter",
    "threading",
    "time",
    "psutil",
    "requests",
    "subprocess",
    "platform",
    "PIL"
]

missing = []
for mod in required_modules:
    try:
        if mod == "PIL":
            import PIL
        elif mod == "win32com.client":
            import win32com.client
        elif mod == "tkinter":
            import tkinter
        else:
            __import__(mod)
    except ImportError:
        missing.append(mod)

if missing:
    import subprocess
    import sys

    # Map module names to pip install names
    pip_names = {
        "win32com.client": "pywin32",
        "psutil": "psutil",
        "PIL": "pillow"
    }
    to_install = []
    for mod in missing:
        if mod in pip_names:
            to_install.append(pip_names[mod])
        else:
            to_install.append(mod)

    print("Installing missing dependencies:", to_install)
    subprocess.check_call([sys.executable, "-m", "pip", "install", *to_install])
    # Restart the script
    os.execl(sys.executable, sys.executable, *sys.argv)

import os
import shutil
import win32com.client
import tkinter as tk
from tkinter import ttk
import threading
import time
import psutil
import subprocess
import platform
from PIL import Image, ImageTk, ImageDraw
import io

class FocusModeApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Focus Mode Controller")
        self.root.geometry("300x200")
        self.root.resizable(False, False)
        
        # Focus mode state
        self.focus_mode_active = False
        self.monitoring_thread = None
        self.stop_monitoring = False
        
        # Game overlay window
        self.overlay_window = None
        self.character_canvas = None
        self.dismiss_timer = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Instagram Focus Mode", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Status: OFF", 
                                     font=("Arial", 10))
        self.status_label.pack(pady=(0, 10))
        
        # Toggle button
        self.toggle_btn = ttk.Button(main_frame, text="Turn ON Focus Mode", 
                                    command=self.toggle_focus_mode)
        self.toggle_btn.pack(pady=10)
        
        # Info label
        info_label = ttk.Label(main_frame, 
                              text="Focus Mode blocks Instagram distractions",
                              font=("Arial", 8), foreground="gray")
        info_label.pack()
        
    def toggle_focus_mode(self):
        if self.focus_mode_active:
            self.stop_focus_mode()
        else:
            self.start_focus_mode()
            
    def start_focus_mode(self):
        self.focus_mode_active = True
        self.stop_monitoring = False
        self.status_label.config(text="Status: ON - Monitoring...")
        self.toggle_btn.config(text="Turn OFF Focus Mode")
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self.monitor_instagram, daemon=True)
        self.monitoring_thread.start()
        
    def stop_focus_mode(self):
        self.focus_mode_active = False
        self.stop_monitoring = True
        self.status_label.config(text="Status: OFF")
        self.toggle_btn.config(text="Turn ON Focus Mode")
        
        # Close overlay if open
        if self.overlay_window:
            self.close_overlay()
            
    def monitor_instagram(self):
        """Monitor for Instagram windows and trigger intervention"""
        while not self.stop_monitoring:
            try:
                if self.is_instagram_active():
                    self.trigger_focus_intervention()
                time.sleep(2)  # Check every 2 seconds
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(5)
                
    def is_instagram_active(self):
        """Check if Instagram is running in any active window"""
        try:
            if platform.system() == "Windows":
                return self.check_windows_instagram()
            elif platform.system() == "Darwin":  # macOS
                return self.check_macos_instagram()
            else:  # Linux
                return self.check_linux_instagram()
        except Exception as e:
            print(f"Error checking Instagram: {e}")
            return False
            
    def check_windows_instagram(self):
        """Check for Instagram on Windows"""
        try:
            # Check running processes
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    name = proc.info['name'].lower()
                    if 'instagram' in name:
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            # Check active window titles using PowerShell
            try:
                cmd = '''
                Add-Type -AssemblyName System.Windows.Forms
                $window = [System.Windows.Forms.Application]::OpenForms | Select-Object -First 1
                if ($window) { $window.Text } else {
                    Add-Type @"
                        using System;
                        using System.Runtime.InteropServices;
                        using System.Text;
                        public class Win32 {
                            [DllImport("user32.dll")]
                            public static extern IntPtr GetForegroundWindow();
                            [DllImport("user32.dll")]
                            public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
                        }
"@
                    $hwnd = [Win32]::GetForegroundWindow()
                    $text = New-Object System.Text.StringBuilder(256)
                    [Win32]::GetWindowText($hwnd, $text, $text.Capacity)
                    $text.ToString()
                }
                '''
                result = subprocess.run(['powershell', '-Command', cmd], 
                                      capture_output=True, text=True)
                if result.stdout and 'instagram' in result.stdout.lower():
                    return True
            except:
                pass
                
        except Exception as e:
            print(f"Windows check error: {e}")
            
        return False
        
    def check_macos_instagram(self):
        """Check for Instagram on macOS"""
        try:
            # Check running applications
            result = subprocess.run(['osascript', '-e', 
                                   'tell application "System Events" to get name of every process'],
                                  capture_output=True, text=True)
            if result.stdout and 'instagram' in result.stdout.lower():
                return True
                
            # Check active window title
            result = subprocess.run(['osascript', '-e',
                                   'tell application "System Events" to get title of front window of (first application process whose frontmost is true)'],
                                  capture_output=True, text=True)
            if result.stdout and 'instagram' in result.stdout.lower():
                return True
                
        except Exception as e:
            print(f"macOS check error: {e}")
            
        return False
        
    def check_linux_instagram(self):
        """Check for Instagram on Linux"""
        try:
            # Check running processes
            for proc in psutil.process_iter(['pid', 'name']):
                if 'instagram' in proc.info['name'].lower():
                    return True
                    
            # Try to get active window title using xdotool
            try:
                result = subprocess.run(['xdotool', 'getactivewindow', 'getwindowname'],
                                      capture_output=True, text=True)
                if result.stdout and 'instagram' in result.stdout.lower():
                    return True
            except:
                pass
                
        except Exception as e:
            print(f"Linux check error: {e}")
            
        return False
        
    def trigger_focus_intervention(self):
        """Show the game-like intervention overlay"""
        if self.overlay_window:  # Already showing
            return
            
        self.create_overlay_window()
        
    def create_overlay_window(self):
        """Create the game-like overlay window"""
        self.overlay_window = tk.Toplevel()
        self.overlay_window.title("Focus Guardian")
        
        # Make it fullscreen and topmost
        self.overlay_window.attributes('-fullscreen', True)
        self.overlay_window.attributes('-topmost', True)
        self.overlay_window.configure(bg='black')
        
        # Semi-transparent effect
        self.overlay_window.attributes('-alpha', 0.9)
        
        # Bind click to dismiss
        self.overlay_window.bind('<Button-1>', self.dismiss_overlay)
        
        # Create canvas for character animation
        self.character_canvas = tk.Canvas(self.overlay_window, bg='black', highlightthickness=0)
        self.character_canvas.pack(fill=tk.BOTH, expand=True)
        self.character_canvas.bind('<Button-1>', self.dismiss_overlay)
        
        # Draw character and message
        self.draw_focus_character()
        
        # Set auto-dismiss timer (1 minute)
        self.dismiss_timer = self.overlay_window.after(60000, self.force_dismiss)
        
    def draw_focus_character(self):
        """Draw a game-like character with message"""
        canvas = self.character_canvas
        
        # Get screen dimensions
        screen_width = canvas.winfo_screenwidth()
        screen_height = canvas.winfo_screenheight()
        
        # Character position (coming from left)
        char_x = screen_width // 4
        char_y = screen_height // 2
        
        # Draw character (simple robot-like figure)
        # Body
        canvas.create_rectangle(char_x-40, char_y-60, char_x+40, char_y+20, 
                               fill='#4CAF50', outline='#2E7D32', width=3)
        
        # Head
        canvas.create_oval(char_x-30, char_y-100, char_x+30, char_y-40, 
                          fill='#66BB6A', outline='#2E7D32', width=3)
        
        # Eyes
        canvas.create_oval(char_x-20, char_y-85, char_x-10, char_y-75, 
                          fill='white', outline='black')
        canvas.create_oval(char_x+10, char_y-85, char_x+20, char_y-75, 
                          fill='white', outline='black')
        canvas.create_oval(char_x-18, char_y-83, char_x-12, char_y-77, 
                          fill='black')
        canvas.create_oval(char_x+12, char_y-83, char_x+18, char_y-77, 
                          fill='black')
        
        # Arms
        canvas.create_rectangle(char_x-60, char_y-40, char_x-40, char_y-10, 
                               fill='#4CAF50', outline='#2E7D32', width=2)
        canvas.create_rectangle(char_x+40, char_y-40, char_x+60, char_y-10, 
                               fill='#4CAF50', outline='#2E7D32', width=2)
        
        # Legs
        canvas.create_rectangle(char_x-25, char_y+20, char_x-10, char_y+50, 
                               fill='#4CAF50', outline='#2E7D32', width=2)
        canvas.create_rectangle(char_x+10, char_y+20, char_x+25, char_y+50, 
                               fill='#4CAF50', outline='#2E7D32', width=2)
        
        # Speech bubble
        bubble_x = char_x + 100
        bubble_y = char_y - 80
        
        # Bubble background
        canvas.create_oval(bubble_x-10, bubble_y-60, bubble_x+250, bubble_y+50, 
                          fill='white', outline='#2E7D32', width=3)
        
        # Bubble pointer
        points = [char_x+60, char_y-60, bubble_x-10, bubble_y-10, bubble_x-10, bubble_y+10]
        canvas.create_polygon(points, fill='white', outline='#2E7D32', width=2)
        
        # Message text
        canvas.create_text(bubble_x+120, bubble_y-10, 
                          text="🚫 FOCUS TIME! 🚫\nClose Instagram and\nget back to Study!", 
                          font=('Arial', 16, 'bold'), 
                          fill='#D32F2F', justify=tk.CENTER)
        
        # Animated elements
        self.animate_character()
        
        # Instructions
        canvas.create_text(screen_width//2, screen_height-100, 
                          text="Click anywhere to dismiss (or wait 1 minute)", 
                          font=('Arial', 14), fill='#FFB74D', justify=tk.CENTER)
        
    def animate_character(self):
        """Add simple animation to the character"""
        if not self.overlay_window:
            return
            
        # Simple bouncing animation
        def bounce():
            if self.overlay_window:
                items = self.character_canvas.find_all()
                for item in items:
                    self.character_canvas.move(item, 0, -2)
                self.overlay_window.after(500, lambda: restore())
                
        def restore():
            if self.overlay_window:
                items = self.character_canvas.find_all()
                for item in items:
                    self.character_canvas.move(item, 0, 2)
                self.overlay_window.after(1000, bounce)
                
        bounce()
        
    def dismiss_overlay(self, event=None):
        """Dismiss the overlay when clicked"""
        self.close_overlay()
        
    def force_dismiss(self):
        """Force dismiss after 1 minute"""
        self.close_overlay()
        
    def close_overlay(self):
        """Close the overlay window"""
        if self.dismiss_timer:
            self.overlay_window.after_cancel(self.dismiss_timer)
            self.dismiss_timer = None
            
        if self.overlay_window:
            self.overlay_window.destroy()
            self.overlay_window = None
            self.character_canvas = None
            
    def run(self):
        """Start the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        """Clean up when closing the app"""
        self.stop_focus_mode()
        self.root.destroy()

if __name__ == "__main__":
    try:
        app = FocusModeApp()
        app.run()
    except Exception as e:
        print(f"Error starting app: {e}")
        input("Press Enter to exit...")


