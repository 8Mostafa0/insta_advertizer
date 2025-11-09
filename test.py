import requests
import json
import time
import os
import sqlite3
import random
from datetime import datetime, timedelta
import threading
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Instagram settings
USERNAME = ""
PASSWORD = ""
BASE_URL = "https://www.instagram.com"
LOGIN_URL = f"{BASE_URL}/accounts/login/ajax/"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
]

HEADERS = {
    "User-Agent": random.choice(USER_AGENTS),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "X-Requested-With": "XMLHttpRequest",
    "X-Instagram-AJAX": "1",
    "Referer": f"{BASE_URL}/",
    "Origin": BASE_URL,
    "Content-Type": "application/x-www-form-urlencoded",
    "Connection": "keep-alive",
    "DNT": "1",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}

running_event = threading.Event()  # Thread-safe flag
session = requests.Session()
session.headers.update(HEADERS)

retry_strategy = Retry(
    total=3,
    backoff_factor=15,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)

# Customtkinter setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Settings dictionary with defaults
settings = {
    'username': 'b2rayng',
    'password': '@Mm09020407808',
    'session_id': '',
    'max_follows': 5,
    'max_likes': 20,
    'max_comments': 10,
    'max_unfollows': 5
}

def save_settings():
    settings.update({
        'username': username_var.get(),
        'password': password_var.get(),
        'session_id': sessionid_var.get(),
        'max_follows': follows_var.get(),
        'max_likes': likes_var.get(),
        'max_comments': comments_var.get(),
        'max_unfollows': unfollows_var.get()
    })
    with open('settings.json', 'w') as f:
        json.dump(settings, f)

def load_settings():
    global settings
    if os.path.exists('settings.json'):
        with open('settings.json', 'r') as f:
            settings.update(json.load(f))

def increase_number(var, key):
    var.set(var.get() + 1)
    save_settings()

def decrease_number(var, key):
    if var.get() > 1:
        var.set(var.get() - 1)
        save_settings()

def create_input_part(parent, label_text, var, key):
    def set_var(*args):
        save_settings()
    frame = ctk.CTkFrame(parent)
    frame.pack(pady=10, fill="both", expand=True)
    label = ctk.CTkLabel(frame, text=label_text, font=("Arial", 16))
    label.pack(side="top", pady=5)
    entry_part = ctk.CTkEntry(frame, textvariable=var, width=200, justify="right")
    entry_part.pack(side="left", expand=True)
    var.trace_add("write", set_var)
    return frame

def create_control_frame(parent, label_text, var, key):
    frame = ctk.CTkFrame(parent)
    frame.pack(pady=10, fill="both", expand=True)
    
    label = ctk.CTkLabel(frame, text=label_text, font=("Arial", 16))
    label.pack(side="top", pady=5)
    
    button_frame = ctk.CTkFrame(frame)
    button_frame.pack(pady=5)
    
    decrease_button = ctk.CTkButton(button_frame, text="-", width=30, command=lambda: decrease_number(var, key))
    decrease_button.pack(side="left", padx=20, ipadx=10)
    
    number_label = ctk.CTkLabel(button_frame, textvariable=var, font=("Arial", 16))
    number_label.pack(side="left", padx=20, ipadx=10)
    
    increase_button = ctk.CTkButton(button_frame, text="+", width=30, command=lambda: increase_number(var, key))
    increase_button.pack(side="left", padx=20, ipadx=10)
    
    return frame

def setup_database():
    conn = sqlite3.connect('instagram_bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS followed_users
                 (username TEXT PRIMARY KEY, follow_time TEXT, followed_by_bot INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS action_log
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, action_type TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

    # New database for run logs
    conn = sqlite3.connect('action_log.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS run_log
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, start_time TEXT)''')
    conn.commit()
    conn.close()

def generate_persian_comment():
    base_comments = [
        "عالی بود واقعا لذت بردم",
        "چه پست قشنگی آفرین",
        "خیلی خوبه ادامه بده",
        "فوق العاده است کارات",
    ]
    emojis = ["✨", "❤️", "🌟", "👏"]
    comment = random.choice(base_comments)
    if random.random() > 0.3:
        comment += " " + random.choice(emojis)
    return comment

# GUI Setup
app = ctk.CTk()
app.title("Insta Automation")
app.geometry("800x700")
app.iconbitmap('app.ico')  # Set the app icon (ensure app.ico exists in the directory)

# Load settings before initializing variables
load_settings()

# Define variables after loading settings
username_var = ctk.StringVar(value=settings['username'])
password_var = ctk.StringVar(value=settings['password'])
sessionid_var = ctk.StringVar(value=settings['session_id'])
follows_var = ctk.IntVar(value=settings['max_follows'])
likes_var = ctk.IntVar(value=settings['max_likes'])
comments_var = ctk.IntVar(value=settings['max_comments'])
unfollows_var = ctk.IntVar(value=settings['max_unfollows'])

# Left Frame
left_frame = ctk.CTkFrame(app)
left_frame.pack(side="left", padx=20, pady=20, fill="both", expand=True)

create_input_part(left_frame, "نام کاربری", username_var, "username")
create_input_part(left_frame, "رمز", password_var, "password")
create_input_part(left_frame, "شناسه جلسه", sessionid_var, "session_id")
create_control_frame(left_frame, "تعداد فالو :", follows_var, 'max_follows')
create_control_frame(left_frame, "تعداد لایک :", likes_var, 'max_likes')
create_control_frame(left_frame, "تعداد کامنت :", comments_var, 'max_comments')
create_control_frame(left_frame, "تعداد آنفالو :", unfollows_var, 'max_unfollows')

# Right Frame for Logs
logs_frame = ctk.CTkFrame(app)
logs_frame.pack(side="right", padx=20, pady=20, fill="both", expand=True)

def log_message(*args):
    message = " ".join(map(str, args))
    log_box.insert("end", f"{datetime.now()}: {message}\n")
    log_box.see("end")

start_stop_button = ctk.CTkButton(logs_frame, text="شروع", fg_color="green", width=30, command=lambda: start_stop_main_func())
start_stop_button.pack(side="top", padx=20, pady=10, ipadx=10)

log_box = ctk.CTkTextbox(logs_frame, width=300, height=200, wrap="word")
log_box.pack(pady=10, padx=10, fill="both", expand=True)

# Instagram Functions
def get_csrf_token():
    try:
        response = session.get(BASE_URL, timeout=20)
        if response.status_code != 200:
            return None
        return session.cookies.get("csrftoken")
    except Exception:
        return None

def login(max_retries=3):
    global session
    for attempt in range(max_retries):
        try:
            csrf_token = get_csrf_token()
            if not csrf_token:
                time.sleep(random.uniform(10, 20))
                continue

            session.headers.update({"X-CSRFToken": csrf_token})
            payload = {
                "username": username_var.get(),
                "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{password_var.get()}",
                "optIntoOneTap": "false",
                "queryParams": "{}",
            }
            
            time.sleep(random.uniform(1, 3))
            response = session.post(LOGIN_URL, data=payload, timeout=20)
            
            if response.status_code == 429:
                time.sleep(random.uniform(60, 120))
                continue
            
            if response.status_code != 200:
                time.sleep(random.uniform(10, 20))
                continue

            try:
                data = response.json()
                if data.get("authenticated"):
                    sessionid = session.cookies.get("sessionid")
                    if sessionid:
                        with open("sessionid.txt", "w") as f:
                            f.write(sessionid)
                        return session
            except requests.exceptions.JSONDecodeError:
                if "checkpoint_required" in response.text:
                    return None
                time.sleep(random.uniform(10, 20))
        
        except Exception:
            time.sleep(random.uniform(15, 30))
    
    return None

def load_session(session_id=None):
    if session_id:
        session.cookies.set("sessionid", session_id)
        return session
    if os.path.exists("sessionid.txt"):
        with open("sessionid.txt", "r") as f:
            session.cookies.set("sessionid", f.read().strip())
        return session
    return None

def verify_login(session):
    try:
        profile_url = f"{BASE_URL}/api/v1/users/web_profile_info/?username={username_var.get()}"
        response = session.get(profile_url, headers={"X-IG-App-ID": "936619743392459"}, timeout=20)
        return response.status_code == 200
    except Exception:
        return False
def get_user_id_graphql(session, username, log):
    try:
        url = "https://i.instagram.com/api/v1/users/lookup/"
        payload = {
            "q": username,
            "signed_body": "SIGNATURE." + json.dumps({"q": username}),
        }
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "X-CSRFToken": get_csrf_token(),
            "X-IG-App-ID": "567067343352427",  # این یکی جدیده و کار می‌کنه!
        }
        
        response = session.post(url, data=payload, headers=headers, timeout=20)
        if response.status_code == 200:
            data = response.json()
            if data.get("user", {}).get("pk"):
                user_id = data["user"]["pk"]
                log(f"User ID found via mobile API: {username} → {user_id}")
                return {"id": str(user_id), "is_private": data["user"].get("is_private", False)}
        
        log(f"Mobile lookup failed for {username}: {response.status_code}")
        return None
        
    except Exception as e:
        log(f"Error in mobile lookup: {e}")
        return None
    
def get_user_profile_data(session, username, log=None):
    try:
        csrf_token = get_csrf_token()
        if not csrf_token:
            if log:
                log("Failed to get CSRF token for profile fetch")
            return None
        
        session.headers.update({"User-Agent": random.choice(USER_AGENTS), "X-CSRFToken": csrf_token})
        profile_url = f"{BASE_URL}/api/v1/users/web_profile_info/?username={username}"
        print(profile_url)
        headers = {"X-IG-App-ID": "936619743392459"}
        response = session.get(profile_url, headers=headers, timeout=20)
        
        if response.status_code != 200:
            if log:
                log(f"Profile fetch failed, HTTP status: {response.status_code}")
            return None
        
        if "<!DOCTYPE html>" in response.text:
            if log:
                log("Received HTML instead of JSON for profile data")
            return None
        
        user_data = response.json()["data"]["user"]
        if log:
            log(f"Successfully fetched profile data for {username}")
        return {"id": user_data["id"], "is_private": user_data.get("is_private", False)}
    except Exception as e:
        if log:
            log(f"Error fetching profile data: {str(e)}")
        return None

def follow_user(session, username, log):
    user_data = get_user_profile_data(session, username, log)
    if not user_data or user_data["is_private"]:
        return False
    
    follow_url = f"{BASE_URL}/api/v1/friendships/create/{user_data['id']}/"
    response = session.post(follow_url, headers={"X-IG-App-ID": "936619743392459", "X-CSRFToken": get_csrf_token()}, timeout=20)
    
    if response.status_code == 200:
        conn = sqlite3.connect('instagram_bot.db')
        c = conn.cursor()
        timestamp = datetime.now().isoformat()
        c.execute("INSERT OR IGNORE INTO followed_users VALUES (?, ?, 1)", (username, timestamp))
        c.execute("INSERT INTO action_log (action_type, timestamp) VALUES (?, ?)", ("follow", timestamp))
        conn.commit()
        conn.close()
        log(f"🫂 Followed {username}")
        return True
    return False

def like_post(session, post_id, username, log):
    like_url = f"{BASE_URL}/api/v1/web/likes/{post_id}/like/"
    response = session.post(like_url, headers={"X-IG-App-ID": "936619743392459", "X-CSRFToken": get_csrf_token()}, timeout=20)
    
    if response.status_code == 200:
        conn = sqlite3.connect('instagram_bot.db')
        c = conn.cursor()
        timestamp = datetime.now().isoformat()
        c.execute("INSERT INTO action_log (action_type, timestamp) VALUES (?, ?)", ("like", timestamp))
        conn.commit()
        conn.close()
        log(f"❤️ Liked post {post_id} by {username}")
        return True
    return False

def comment_on_post(session, post_id, username, log):
    comment_url = f"{BASE_URL}/api/v1/web/comments/{post_id}/add/"
    comment_text = generate_persian_comment()
    payload = {"comment_text": comment_text}
    response = session.post(comment_url, headers={"X-IG-App-ID": "936619743392459", "X-CSRFToken": get_csrf_token()}, data=payload, timeout=20)
    
    if response.status_code == 200:
        conn = sqlite3.connect('instagram_bot.db')
        c = conn.cursor()
        timestamp = datetime.now().isoformat()
        c.execute("INSERT INTO action_log (action_type, timestamp) VALUES (?, ?)", ("comment", timestamp))
        conn.commit()
        conn.close()
        log(f"💬 Commented '{comment_text}' on {post_id} by {username}")
        return True
    return False

def unfollow_user(session, username, log):
    user_data = get_user_id_graphql(session, username, log)
    if not user_data:
        return False
    unfollow_url = f"{BASE_URL}/api/v1/friendships/destroy/{user_data['id']}/"
    response = session.post(unfollow_url, headers={"X-IG-App-ID": "936619743392459", "X-CSRFToken": get_csrf_token()}, timeout=20)
    
    if response.status_code == 200:
        conn = sqlite3.connect('instagram_bot.db')
        c = conn.cursor()
        timestamp = datetime.now().isoformat()
        c.execute("DELETE FROM followed_users WHERE username = ?", (username,))
        c.execute("INSERT INTO action_log (action_type, timestamp) VALUES (?, ?)", ("unfollow", timestamp))
        conn.commit()
        conn.close()
        log(f"Unfollowed {username}")
        return True
    return False

def get_feed_data(session):
    try:
        feed_url = f"{BASE_URL}/api/v1/feed/timeline/"
        session.headers.update({"User-Agent": random.choice(USER_AGENTS)})
        response = session.get(feed_url, headers={"X-IG-App-ID": "936619743392459"}, timeout=20)
        if response.status_code == 200:
            if "<!DOCTYPE html>" in response.text:
                return []
            data = response.json()
            posts = [{"media": item["media_or_ad"]} for item in data.get("feed_items", []) if "media_or_ad" in item]
            return posts
        return []
    except Exception:
        return []

def get_followers(session, username):
    try:
        user_data = get_user_profile_data(session, username)
        if not user_data:
            return []
        url = f"{BASE_URL}/api/v1/friendships/{user_data['id']}/followers/"
        response = session.get(url, headers={"X-IG-App-ID": "936619743392459"}, timeout=20)
        if response.status_code == 200:
            return [user["username"] for user in response.json().get("users", [])]
        return []
    except Exception:
        return []

def check_messages(session, log):
    try:
        inbox_url = f"{BASE_URL}/api/v1/direct_v2/inbox/?persistentBadging=true"
        response = session.get(inbox_url, headers={"X-IG-App-ID": "936619743392459"}, timeout=20)
        if response.status_code == 200:
            data = response.json()
            unread_count = data["inbox"]["unseen_count"]
            threads = data["inbox"]["threads"]
            log(f"📩 Checked messages: {unread_count} unread, {len(threads)} total conversations")
            return True
        return False
    except Exception as e:
        log(f"📩 Error checking messages: {str(e)}")
        return False

def get_action_counts_last_hour():
    conn = sqlite3.connect('instagram_bot.db')
    c = conn.cursor()
    one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
    c.execute("SELECT action_type, COUNT(*) FROM action_log WHERE timestamp > ? GROUP BY action_type", (one_hour_ago,))
    counts = dict(c.fetchall())
    conn.close()
    return {
        "follow": counts.get("follow", 0),
        "like": counts.get("like", 0),
        "comment": counts.get("comment", 0),
        "unfollow": counts.get("unfollow", 0)
    }

def check_last_run():
    conn = sqlite3.connect('action_log.db')
    c = conn.cursor()
    c.execute("SELECT start_time FROM run_log ORDER BY start_time DESC LIMIT 1")
    last_run = c.fetchone()
    conn.close()
    
    if last_run:
        if last_run[0] != '':
            last_run_time = datetime.fromisoformat(last_run[0])
            if datetime.now() - last_run_time < timedelta(hours=1):
                return False  # Don't run if less than an hour has passed
        return True  # Run if no recent run or more than an hour has passed

def log_run_start():
    conn = sqlite3.connect('action_log.db')
    c = conn.cursor()
    timestamp = datetime.now().isoformat()
    c.execute("INSERT INTO run_log (start_time) VALUES (?)", (timestamp,))
    conn.commit()
    conn.close()

def run_bot():
    global session
    setup_database()
    
    # if not check_last_run():
    #     log_message("Bot has already run within the last hour. Waiting to prevent Instagram banning.")
    #     running_event.clear()
    #     start_stop_button.configure(text="شروع", fg_color="green")
    #     return
    
    log_run_start()
    
    logged_in_session = load_session(sessionid_var.get())
    if logged_in_session and verify_login(logged_in_session):
        log_message("Session loaded successfully")
    else:
        log_message("Trying to login with credentials...")
        logged_in_session = login()
        if not logged_in_session:
            log_message("Login failed after retries. Check credentials or use a valid session ID.")
            return
        log_message("Login successful")
    
    session = logged_in_session
    log_message("Bot started")

    while running_event.is_set():
        try:
            if random.random() < 0.1:
                check_messages(session, log_message)
                time.sleep(random.uniform(5, 15))

            counts = get_action_counts_last_hour()
            posts = get_feed_data(session)
            if not posts:
                log_message("No posts found in feed, waiting...")
                time.sleep(1)
                continue

            action_weights = [
                ("like", 0.4, counts["like"] < likes_var.get()),
                ("comment", 0.25, counts["comment"] < comments_var.get()),
                ("follow", 0.2, counts["follow"] < follows_var.get()),
                ("unfollow", 0.15, counts["unfollow"] < unfollows_var.get())
            ]
            
            available_actions = [a for a, _, cond in action_weights if cond]
            if not available_actions:
                log_message("All action limits reached, waiting...")
                time.sleep(300)
                continue

            action = random.choice([a for a, _, c in action_weights if c])
            post = random.choice(posts)
            if "media" not in post:
                continue
            media = post["media"]
            username = media["user"]["username"]
            post_id = media["pk"] if "pk" in media else media["id"]

            if action == "like":
                like_post(session, post_id, username, log_message)
                time.sleep(random.uniform(2, 8))

            elif action == "comment":
                comment_on_post(session, post_id, username, log_message)
                time.sleep(random.uniform(5, 15))

            elif action == "follow":
                followers = get_followers(session, username)
                if followers:
                    target = random.choice(followers)
                    follow_user(session, target, log_message)
                    time.sleep(random.uniform(10, 20))

            elif action == "unfollow":
                conn = sqlite3.connect('instagram_bot.db')
                c = conn.cursor()
                check_time = datetime.now() - timedelta(hours=48)
                c.execute(f"SELECT username FROM followed_users WHERE follow_time < '{check_time}' AND followed_by_bot = 1 LIMIT 1")
                to_unfollow = c.fetchone()[0]
                conn.close()
                if to_unfollow:
                    unfollow_user(session, to_unfollow, log_message)
                    time.sleep(random.uniform(15, 25))

            if random.random() < 0.2:
                log_message("Taking a short human-like break")
                time.sleep(random.uniform(30, 120))
            elif random.random() < 0.05:
                log_message("Taking a longer human-like break")
                time.sleep(random.uniform(300, 600))

        except Exception as e:
            log_message(f"Error: {str(e)}")
            time.sleep(300)

def start_stop_main_func():
    if running_event.is_set():
        running_event.clear()
        start_stop_button.configure(text="شروع", fg_color="green")
        log_message("Bot stopped.")
    else:
        if not username_var.get() or (not password_var.get() and not sessionid_var.get()):
            log_message("Error: Please enter username and either password or session ID")
            return
        running_event.set()
        start_stop_button.configure(text="توقف", fg_color="red")
        log_message("Bot starting...")
        threading.Thread(target=run_bot, daemon=True).start()

# Run app
app.mainloop()

# when i run it twice in one hour its print:
# 2025-04-02 13:46:45.644256: Bot starting...
# 2025-04-02 13:46:45.648255: Bot has already run within the last hour. Waiting to prevent Instagram banning.

# i dont want this i want to for example if the follow value is 5 and bot followed 2 people its should follow 3 more people in this hour and dont more till the next hours come
# and do this for all part like,comment,..