import requests
import json
import time
import sqlite3
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Settings
CHAT_BASE_URL = "https://grok.com/chat"
CHAT_ID = "4c705a8c-f864-439a-9981-e3f0eb612427"  # Hardcoded chat ID
USERNAME = "mosielite5@gmail.com"
PASSWORD = "@Mm09020407808"  # Kept for reference, not used
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

# Global control variables
running = False
session = requests.Session()
session.headers.update(HEADERS)
chat_id = CHAT_ID

# Manually set cookies (replace with your actual cookies)
session.cookies.set("sessionid", "your_sessionid_here")  # Example: "abc123"
# Add more cookies if needed, e.g.:
# session.cookies.set("auth_token", "xyz789")
# session.cookies.set("__cfduid", "def456")

# Database setup
def setup_database():
    conn = sqlite3.connect('grok_chat.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history
                 (username TEXT, message TEXT, response TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

# GUI Class
class GrokChatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Grok Chat with Manual Chat ID")
        
        self.username_var = tk.StringVar(value=USERNAME)
        self.password_var = tk.StringVar(value=PASSWORD)
        self.message_var = tk.StringVar(value="hi")
        
        ttk.Label(root, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(root, textvariable=self.username_var, state="disabled").grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(root, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Entry(root, textvariable=self.password_var, show="*", state="disabled").grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(root, text="Message:").grid(row=2, column=0, padx=5, pady=5)
        ttk.Entry(root, textvariable=self.message_var).grid(row=2, column=1, padx=5, pady=5)
        
        self.start_button = ttk.Button(root, text="Start Chat", command=self.start_bot)
        self.start_button.grid(row=3, column=0, padx=5, pady=5)
        
        self.stop_button = ttk.Button(root, text="Stop", command=self.stop_bot, state="disabled")
        self.stop_button.grid(row=3, column=1, padx=5, pady=5)
        
        self.chat_text = tk.Text(root, height=10, width=50)
        self.chat_text.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    def log(self, message):
        self.chat_text.insert(tk.END, f"{datetime.now()}: {message}\n")
        self.chat_text.see(tk.END)

    def start_bot(self):
        global running
        running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        threading.Thread(target=run_bot, args=(self.message_var.get(), self.log), daemon=True).start()

    def stop_bot(self):
        global running
        running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.log("Chat stopped")

# Core Functions
def send_message(message, log):
    global chat_id
    if not chat_id:
        log("No chat ID available.")
        return False
    
    message_url = f"{CHAT_BASE_URL}/{chat_id}/send"  # Hypothetical endpoint
    try:
        response = session.post(message_url, json={"message": message}, timeout=10)
        if response.status_code == 200:
            reply = response.json().get("response", "No reply from Grok")
            log(f"You: {message}")
            log(f"Grok: {reply}")
            
            conn = sqlite3.connect('grok_chat.db')
            c = conn.cursor()
            c.execute("INSERT INTO chat_history VALUES (?, ?, ?, ?)",
                     (USERNAME, message, reply, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            return True
        else:
            log(f"Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        log(f"Error sending message: {str(e)}")
        return False

def run_bot(initial_message, log):
    global running
    
    setup_database()
    log(f"Using Chat ID: {chat_id}")
    
    if initial_message:
        send_message(initial_message, log)
    
    while running:
        time.sleep(1)
        new_message = app.message_var.get()
        if new_message and new_message != initial_message:
            send_message(new_message, log)
            initial_message = new_message

if __name__ == "__main__":
    root = tk.Tk()
    app = GrokChatGUI(root)
    root.mainloop()