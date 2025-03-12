import requests
import json
import time
import os
import sqlite3
import random
from datetime import datetime, timedelta
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import ssl

# Instagram credentials and settings
USERNAME = ""
PASSWORD = ""
BASE_URL = "https://www.instagram.com"
LOGIN_URL = f"{BASE_URL}/accounts/login/ajax/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": f"{BASE_URL}/",
    "Origin": BASE_URL,
    "Connection": "keep-alive",
    "DNT": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
}

# Global control variables
running = False
session = requests.Session()
session.headers.update(HEADERS)
session.max_redirects = 10

retry_strategy = Retry(
    total=2,
    backoff_factor=10,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.proxies = {}

def setup_database():
    conn = sqlite3.connect('instagram_bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS followed_users
                 (username TEXT PRIMARY KEY, follow_time TEXT, followed_by_bot INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS unfollow_queue
                 (username TEXT PRIMARY KEY, follow_time TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS action_log
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, action_type TEXT, timestamp TEXT)''')
    c.execute("DELETE FROM action_log")
    conn.commit()
    conn.close()

class InstagramBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Automation Bot")
        
        self.username_var = tk.StringVar(value="b2rayng")
        self.password_var = tk.StringVar(value="@Mm09020407808")
        self.sessionid_var = tk.StringVar(value="")
        self.follows_var = tk.IntVar(value=60)
        self.likes_var = tk.IntVar(value=200)
        self.comments_var = tk.IntVar(value=50)
        self.unfollows_var = tk.IntVar(value=20)
        self.tags_var = tk.StringVar(value="vpn,دختر,شیک,خرید,فیلتر,فیلترشکن")
        self.custom_comments_var = tk.StringVar(value="😍,❤️❤️,🔥🔥🔥,👌به به,چه جالب,عجیبه,🤩🤩")
        
        ttk.Label(root, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(root, textvariable=self.username_var).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(root, text="Password (optional if Session ID provided):").grid(row=1, column=0, padx=5, pady=5)
        ttk.Entry(root, textvariable=self.password_var, show="*").grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(root, text="Session ID (preferred):").grid(row=2, column=0, padx=5, pady=5)
        ttk.Entry(root, textvariable=self.sessionid_var).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(root, text="Follows/hour:").grid(row=3, column=0, padx=5, pady=5)
        ttk.Entry(root, textvariable=self.follows_var).grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(root, text="Likes/hour:").grid(row=4, column=0, padx=5, pady=5)
        ttk.Entry(root, textvariable=self.likes_var).grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(root, text="Comments/hour:").grid(row=5, column=0, padx=5, pady=5)
        ttk.Entry(root, textvariable=self.comments_var).grid(row=5, column=1, padx=5, pady=5)
        
        ttk.Label(root, text="Unfollows/hour:").grid(row=6, column=0, padx=5, pady=5)
        ttk.Entry(root, textvariable=self.unfollows_var).grid(row=6, column=1, padx=5, pady=5)
        
        ttk.Label(root, text="Tags (comma-separated):").grid(row=7, column=0, padx=5, pady=5)
        ttk.Entry(root, textvariable=self.tags_var).grid(row=7, column=1, padx=5, pady=5)
        
        ttk.Label(root, text="Comments (comma-separated):").grid(row=8, column=0, padx=5, pady=5)
        ttk.Entry(root, textvariable=self.custom_comments_var).grid(row=8, column=1, padx=5, pady=5)
        
        self.start_button = ttk.Button(root, text="Start", command=self.start_bot)
        self.start_button.grid(row=9, column=0, padx=5, pady=5)
        
        self.stop_button = ttk.Button(root, text="Stop", command=self.stop_bot, state="disabled")
        self.stop_button.grid(row=9, column=1, padx=5, pady=5)
        
        self.log_text = tk.Text(root, height=10, width=50)
        self.log_text.grid(row=10, column=0, columnspan=2, padx=5, pady=5)

    def log(self, message):
        self.log_text.insert(tk.END, f"{datetime.now()}: {message}\n")
        self.log_text.see(tk.END)

    def start_bot(self):
        global running, USERNAME, PASSWORD
        USERNAME = self.username_var.get()
        PASSWORD = self.password_var.get()
        session_id = self.sessionid_var.get()
        if not USERNAME or (not PASSWORD and not session_id):
            messagebox.showerror("Error", "Please enter username and either password or session ID")
            return
        running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        threading.Thread(target=run_bot, args=(
            self.follows_var.get(),
            self.likes_var.get(),
            self.comments_var.get(),
            self.unfollows_var.get(),
            self.tags_var.get().split(','),
            self.custom_comments_var.get().split(','),
            self.log,
            session_id
        ), daemon=True).start()

    def stop_bot(self):
        global running
        running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.log("Bot stopped")

def get_csrf_token():
    try:
        response = session.get(BASE_URL, timeout=20)
        if response.status_code == 429:
            raise Exception(f"Rate limited (HTTP 429): {response.text}")
        return session.cookies.get("csrftoken")
    except Exception as e:
        print(f"Error getting CSRF token: {str(e)}")
        return None

def login(max_retries=2):
    global session
    for attempt in range(max_retries):
        try:
            csrf_token = get_csrf_token()
            if not csrf_token:
                print(f"Login attempt {attempt + 1}/{max_retries}: Failed to get CSRF token")
                time.sleep(15)
                continue
            session.headers.update({"X-CSRFToken": csrf_token})
            payload = {
                "username": USERNAME,
                "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{PASSWORD}",
                "queryParams": "{}",
                "optIntoOneTap": "false"
            }
            response = session.post(LOGIN_URL, data=payload, timeout=20)
            print(f"Login attempt {attempt + 1}/{max_retries}: Response - {response.text}")
            if response.status_code == 429:
                raise Exception(f"Rate limited (HTTP 429): {response.text}")
            data = response.json()
            if data.get("authenticated"):
                with open("sessionid.txt", "w") as f:
                    f.write(session.cookies.get("sessionid"))
                return session
            else:
                print(f"Login attempt {attempt + 1}/{max_retries}: Authentication failed - {data}")
        except json.JSONDecodeError as e:
            print(f"Login attempt {attempt + 1}/{max_retries}: JSON decode error - {response.text}")
        except ssl.SSLEOFError as e:
            print(f"Login attempt {attempt + 1}/{max_retries}: SSL EOF error - {str(e)}. Retrying after delay.")
            time.sleep(30)
        except Exception as e:
            print(f"Login attempt {attempt + 1}/{max_retries}: {str(e)}")
            time.sleep(15)
    print(f"Login failed after {max_retries} retries. Use a manual session ID or check network.")
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
        profile_url = f"{BASE_URL}/api/v1/users/web_profile_info/?username={USERNAME}"
        response = session.get(profile_url, headers={"X-IG-App-ID": "936619743392459"}, timeout=20)
        if response.status_code == 429:
            raise Exception(f"Rate limited (HTTP 429): {response.text}")
        if response.status_code == 200:
            return True
        print(f"Session verification failed: HTTP {response.status_code} - {response.text}")
        return False
    except ssl.SSLEOFError as e:
        print(f"Session verification error: SSL EOF error - {str(e)}. Retrying after delay.")
        time.sleep(30)
        return False
    except Exception as e:
        print(f"Session verification error: {str(e)}")
        return False
def follow_user(session, username, log):
    try:
        user_id = get_user_profile_data(session, username)
        if not user_id:
            log(f"Failed to get user ID for {username}")
            return False
        
        follow_url = f"{BASE_URL}/api/v1/friendships/create/{user_id}/"
        headers = {"X-IG-App-ID": "936619743392459", "X-CSRFToken": get_csrf_token()}
        response = session.post(follow_url, headers=headers, timeout=20)
        
        if response.status_code == 429:
            log(f"Rate limited (HTTP 429) while following {username}: {response.text}")
            return False
        if response.status_code == 401:
            log(f"Unauthorized (HTTP 401) while following {username}: {response.text}")
            return False
        if response.status_code == 200:
            data = response.json()
            if data.get("friendship_status", {}).get("following"):
                conn = sqlite3.connect('instagram_bot.db')
                c = conn.cursor()
                timestamp = datetime.now().isoformat()
                c.execute("INSERT OR IGNORE INTO followed_users VALUES (?, ?, 1)",
                         (username, timestamp))
                c.execute("INSERT INTO action_log (action_type, timestamp) VALUES (?, ?)",
                         ("follow", timestamp))
                conn.commit()
                conn.close()
                log(f"Successfully followed {username}, stored in DB with timestamp {timestamp}")
                return True
            else:
                log(f"Failed to follow {username}: Response indicates not following - {response.text}")
        else:
            log(f"Failed to follow {username}: HTTP {response.status_code} - {response.text}")
        return False
    except sqlite3.Error as e:
        log(f"Database error while following {username}: {str(e)}")
        if 'conn' in locals():
            conn.close()
        return False
    except ssl.SSLEOFError as e:
        log(f"SSL EOF error while following {username}: {str(e)}. Retrying after delay.")
        time.sleep(30)
        return False
    except Exception as e:
        log(f"Error following {username}: {str(e)}")
        return False
    
    
def like_post(session, post_id, username, log):
    try:
        like_url = f"{BASE_URL}/api/v1/web/likes/{post_id}/like/"
        headers = {"X-IG-App-ID": "936619743392459", "X-CSRFToken": get_csrf_token()}
        response = session.post(like_url, headers=headers, timeout=20)
        
        if response.status_code == 429:
            log(f"Rate limited (HTTP 429) while liking post {post_id} by {username}: {response.text}")
            return False
        if response.status_code == 401:
            log(f"Unauthorized (HTTP 401) while liking post {post_id} by {username}: {response.text}")
            return False
        if response.status_code == 200:
            conn = sqlite3.connect('instagram_bot.db')
            c = conn.cursor()
            timestamp = datetime.now().isoformat()
            c.execute("INSERT INTO action_log (action_type, timestamp) VALUES (?, ?)",
                     ("like", timestamp))
            conn.commit()
            conn.close()
            log(f"Successfully liked post {post_id} by {username}, stored in DB with timestamp {timestamp}")
            return True
        else:
            log(f"Failed to like post {post_id} by {username}: HTTP {response.status_code} - {response.text}")
        return False
    except sqlite3.Error as e:
        log(f"Database error while liking post {post_id} by {username}: {str(e)}")
        if 'conn' in locals():
            conn.close()
        return False
    except ssl.SSLEOFError as e:
        log(f"SSL EOF error while liking post {post_id} by {username}: {str(e)}. Retrying after delay.")
        time.sleep(30)
        return False
    except Exception as e:
        log(f"Error liking post {post_id} by {username}: {str(e)}")
        return False


def comment_on_post(session, post_id, username, custom_comments, log):
    try:
        comment_url = f"{BASE_URL}/api/v1/web/comments/{post_id}/add/"
        headers = {"X-IG-App-ID": "936619743392459", "X-CSRFToken": get_csrf_token()}
        comment_text = random.choice(custom_comments)
        payload = {"comment_text": comment_text}
        response = session.post(comment_url, headers=headers, data=payload, timeout=20)
        
        if response.status_code == 429:
            log(f"Rate limited (HTTP 429) while commenting on post {post_id} by {username}: {response.text}")
            return False
        if response.status_code == 401:
            log(f"Unauthorized (HTTP 401) while commenting on post {post_id} by {username}: {response.text}")
            return False
        if response.status_code == 200:
            conn = sqlite3.connect('instagram_bot.db')
            c = conn.cursor()
            timestamp = datetime.now().isoformat()
            c.execute("INSERT INTO action_log (action_type, timestamp) VALUES (?, ?)",
                     ("comment", timestamp))
            conn.commit()
            conn.close()
            log(f"Successfully commented '{comment_text}' on post {post_id} by {username}, stored in DB with timestamp {timestamp}")
            return True
        else:
            log(f"Failed to comment on post {post_id} by {username}: HTTP {response.status_code} - {response.text}")
        return False
    except sqlite3.Error as e:
        log(f"Database error while commenting on post {post_id} by {username}: {str(e)}")
        if 'conn' in locals():
            conn.close()
        return False
    except ssl.SSLEOFError as e:
        log(f"SSL EOF error while commenting on post {post_id} by {username}: {str(e)}. Retrying after delay.")
        time.sleep(30)
        return False
    except Exception as e:
        log(f"Error commenting on post {post_id} by {username}: {str(e)}")
        return False

        
def unfollow_user(session, username, log):
    try:
        user_id = get_user_profile_data(session, username)
        if not user_id:
            log(f"Failed to get user ID for unfollowing {username}")
            return False
        
        unfollow_url = f"{BASE_URL}/api/v1/friendships/destroy/{user_id}/"
        headers = {"X-IG-App-ID": "936619743392459", "X-CSRFToken": get_csrf_token()}
        response = session.post(unfollow_url, headers=headers, timeout=20)
        
        if response.status_code == 429:
            log(f"Rate limited (HTTP 429) while unfollowing {username}: {response.text}")
            return False
        if response.status_code == 401:
            log(f"Unauthorized (HTTP 401) while unfollowing {username}: {response.text}")
            return False
        if response.status_code == 200:
            conn = sqlite3.connect('instagram_bot.db')
            c = conn.cursor()
            timestamp = datetime.now().isoformat()
            c.execute("DELETE FROM followed_users WHERE username = ?", (username,))
            c.execute("INSERT INTO action_log (action_type, timestamp) VALUES (?, ?)",
                     ("unfollow", timestamp))
            conn.commit()
            conn.close()
            log(f"Successfully unfollowed {username}, stored in DB with timestamp {timestamp}")
            return True
        else:
            log(f"Failed to unfollow {username}: HTTP {response.status_code} - {response.text}")
        return False
    except sqlite3.Error as e:
        log(f"Database error while unfollowing {username}: {str(e)}")
        if 'conn' in locals():
            conn.close()
        return False
    except ssl.SSLEOFError as e:
        log(f"SSL EOF error while unfollowing {username}: {str(e)}. Retrying after delay.")
        time.sleep(30)
        return False
    except Exception as e:
        log(f"Error unfollowing {username}: {str(e)}")
        return False
def get_user_profile_data(session, username):
    try:
        profile_url = f"{BASE_URL}/api/v1/users/web_profile_info/?username={username}"
        response = session.get(profile_url, headers={"X-IG-App-ID": "936619743392459"}, timeout=20)
        if response.status_code == 429:
            raise Exception(f"Rate limited (HTTP 429): {response.text}")
        if response.status_code == 200:
            return response.json()["data"]["user"]["id"]
    except ssl.SSLEOFError as e:
        print(f"Error getting profile data for {username}: SSL EOF error - {str(e)}. Retrying after delay.")
        time.sleep(30)
        return None
    except Exception as e:
        print(f"Error getting profile data for {username}: {str(e)}")
        return None

def get_explore_data(session):
    try:
        explore_url = f"{BASE_URL}/api/v1/discover/web_explore_grid/"
        response = session.get(explore_url, headers={"X-IG-App-ID": "936619743392459"}, timeout=20)
        if response.status_code == 429:
            raise Exception(f"Rate limited (HTTP 429): {response.text}")
        if response.status_code == 200:
            return response.json().get("sectional_items", [])
        return []
    except ssl.SSLEOFError as e:
        print(f"Error fetching explore data: SSL EOF error - {str(e)}. Retrying after delay.")
        time.sleep(30)
        return []
    except Exception as e:
        print(f"Error fetching explore data: {str(e)}")
        return []
    
def get_posts_by_tag(session, tag, log):
    try:
        url = f"{BASE_URL}/api/v1/tags/web_info/?tag_name={tag.strip()}"
        response = session.get(url, headers={"X-IG-App-ID": "936619743392459"}, timeout=20)
        if response.status_code == 429:
            log(f"Error fetching tag {tag}: HTTP 429 - Rate limited: {response.text}")
            return []
        if response.status_code == 200:
            data = response.json().get("data", {})
            sections = data.get("top", {}).get("sections", [])
            # Extract media items from sections
            media_items = []
            for section in sections:
                if "layout_content" in section:
                    for item in section["layout_content"].get("medias", []):
                        if "media" in item:
                            media_items.append(item["media"])
            log(f"Fetched {len(sections)} sections, {len(media_items)} media items for tag {tag}")
            return media_items
        else:
            log(f"Error fetching tag {tag}: HTTP {response.status_code} - {response.text}")
            return []
    except ssl.SSLEOFError as e:
        log(f"Error fetching tag {tag}: SSL EOF error - {str(e)}. Retrying after delay.")
        time.sleep(30)
        return []
    except json.JSONDecodeError as e:
        log(f"Error fetching tag {tag}: JSON decode error - {str(e)}")
        return []
    except Exception as e:
        log(f"Error fetching tag {tag}: {str(e)}")
        return []
def get_followers_of_following(session, username):
    try:
        user_id = get_user_profile_data(session, username)
        if not user_id:
            return []
        url = f"{BASE_URL}/api/v1/friendships/{user_id}/following/"
        response = session.get(url, headers={"X-IG-App-ID": "936619743392459"}, timeout=20)
        if response.status_code == 429:
            raise Exception(f"Rate limited (HTTP 429): {response.text}")
        if response.status_code == 200:
            return [user["username"] for user in response.json().get("users", [])]
        return []
    except ssl.SSLEOFError as e:
        print(f"Error fetching followers of {username}: SSL EOF error - {str(e)}. Retrying after delay.")
        time.sleep(30)
        return []
    except Exception as e:
        print(f"Error fetching followers of {username}: {str(e)}")
        return []

def sync_following_to_db(session, log):
    try:
        user_id = get_user_profile_data(session, USERNAME)
        if not user_id:
            log("Failed to get user ID for syncing followings")
            return
        
        url = f"{BASE_URL}/api/v1/friendships/{user_id}/following/"
        headers = {"X-IG-App-ID": "936619743392459"}
        params = {}
        all_followings = []
        
        while True:
            response = session.get(url, headers=headers, params=params, timeout=20)
            if response.status_code == 429:
                log(f"Error fetching followings: HTTP 429 - Rate limited: {response.text}")
                break
            if response.status_code != 200:
                log(f"Error fetching followings: HTTP {response.status_code}")
                break
            
            data = response.json()
            all_followings.extend(user["username"] for user in data.get("users", []))
            
            next_max_id = data.get("next_max_id")
            if not next_max_id:
                break
            
            params["max_id"] = next_max_id
            time.sleep(2)
        
        if all_followings:
            conn = sqlite3.connect('instagram_bot.db')
            c = conn.cursor()
            current_time = datetime.now().isoformat()
            for username in all_followings:
                c.execute("INSERT OR IGNORE INTO followed_users (username, follow_time, followed_by_bot) VALUES (?, ?, 0)",
                         (username, current_time))
            conn.commit()
            conn.close()
            log(f"Synced {len(all_followings)} existing followings to database")
        else:
            log("No followings found to sync")
            
    except ssl.SSLEOFError as e:
        log(f"Error syncing followings: SSL EOF error - {str(e)}. Retrying after delay.")
        time.sleep(30)
    except Exception as e:
        log(f"Error syncing followings: {str(e)}")

def get_action_counts_last_hour(log):
    conn = sqlite3.connect('instagram_bot.db')
    c = conn.cursor()
    
    # Last hour (previous 60 minutes)
    one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
    c.execute("SELECT action_type, COUNT(*) FROM action_log WHERE timestamp > ? GROUP BY action_type", (one_hour_ago,))
    last_hour_counts = dict(c.fetchall())
    c.execute("SELECT COUNT(*) FROM action_log WHERE timestamp > ?", (one_hour_ago,))
    last_hour_total = c.fetchone()[0]
    
    # Current hour (since start of this hour)
    now = datetime.now()
    start_of_hour = datetime(now.year, now.month, now.day, now.hour).isoformat()
    c.execute("SELECT action_type, COUNT(*) FROM action_log WHERE timestamp > ? GROUP BY action_type", (start_of_hour,))
    current_hour_counts = dict(c.fetchall())
    c.execute("SELECT COUNT(*) FROM action_log WHERE timestamp > ?", (start_of_hour,))
    current_hour_total = c.fetchone()[0]
    
    # Log the queried data for debugging
    log(f"Queried actions: Last hour since {one_hour_ago}: Total={last_hour_total}, Counts={last_hour_counts}")
    log(f"Queried actions: Current hour since {start_of_hour}: Total={current_hour_total}, Counts={current_hour_counts}")
    
    conn.close()
    
    # Return both sets of counts
    return {
        "last_hour": {
            "follow": last_hour_counts.get("follow", 0),
            "like": last_hour_counts.get("like", 0),
            "comment": last_hour_counts.get("comment", 0),
            "unfollow": last_hour_counts.get("unfollow", 0)
        },
        "current_hour": {
            "follow": current_hour_counts.get("follow", 0),
            "like": current_hour_counts.get("like", 0),
            "comment": current_hour_counts.get("comment", 0),
            "unfollow": current_hour_counts.get("unfollow", 0)
        }
    }

def run_bot(follows_per_hour, likes_per_hour, comments_per_hour, unfollows_per_hour, tags, custom_comments, log, session_id=None):
    global session, running
    
    try:
        setup_database()
        logged_in_session = load_session(session_id)
        if logged_in_session and verify_login(logged_in_session):
            log("Session loaded successfully")
        else:
            if session_id:
                log("Provided session ID invalid. Trying to login with credentials.")
            logged_in_session = login(max_retries=2)
            if not logged_in_session:
                log("Login failed after retries. Check network or use a valid session ID (see console). Pausing for 15 minutes.")
                time.sleep(900)
            else:
                log("Login successful")
        
        session = logged_in_session or requests.Session()
        session.headers.update(HEADERS)
        sync_following_to_db(session, log)
        log("Bot started")

        selected_tag = random.choice(tags)
        all_posts = get_posts_by_tag(session, selected_tag, log) or []
        if not all_posts:
            log(f"No posts fetched from tag {selected_tag}, falling back to explore data")
            all_posts = get_explore_data(session) or []
        
        conn = sqlite3.connect('instagram_bot.db')
        c = conn.cursor()
        c.execute("SELECT username FROM followed_users LIMIT 5")
        my_followings = [row[0] for row in c.fetchall()]
        c.execute("SELECT username FROM followed_users WHERE follow_time < ? AND followed_by_bot = 1",
                 ((datetime.now() - timedelta(hours=48)).isoformat(),))
        to_unfollow = [row[0] for row in c.fetchall()]
        conn.close()
        
        potential_follows = []
        for following in my_followings:
            follows = get_followers_of_following(session, following)
            potential_follows.extend(follows or [])
        
        log(f"Initial data: Posts={len(all_posts)}, Potential follows={len(potential_follows)}, To unfollow={len(to_unfollow)}")
        
        post_index = 0
        follow_index = 0
        unfollow_index = 0
        failed_attempts = 0
        max_failed_attempts = 5

        while running:
            counts = get_action_counts_last_hour(log)
            log(f"Action counts last hour: Follow={counts['last_hour']['follow']}/{follows_per_hour}, "
                f"Like={counts['last_hour']['like']}/{likes_per_hour}, "
                f"Comment={counts['last_hour']['comment']}/{comments_per_hour}, "
                f"Unfollow={counts['last_hour']['unfollow']}/{unfollows_per_hour}")
            log(f"Action counts this hour (since {datetime.now().strftime('%H:00')}): "
                f"Follow={counts['current_hour']['follow']}/{follows_per_hour}, "
                f"Like={counts['current_hour']['like']}/{likes_per_hour}, "
                f"Comment={counts['current_hour']['comment']}/{comments_per_hour}, "
                f"Unfollow={counts['current_hour']['unfollow']}/{unfollows_per_hour}")

            action_choice = random.randint(0, 99)
            action = None
            delay = 0

            try:
                if action_choice < 15 and counts["last_hour"]["follow"] < follows_per_hour and follow_index < len(potential_follows):
                    action = "follow"
                    delay = 10  # ~6 follows/min, 60/hour
                    username = potential_follows[follow_index]
                    if follow_user(session, username, log):
                        follow_index += 1
                elif 15 <= action_choice < 30 and counts["last_hour"]["unfollow"] < unfollows_per_hour and unfollow_index < len(to_unfollow):
                    action = "unfollow"
                    delay = 15  # ~4 unfollows/min, 20/hour with buffer
                    username = to_unfollow[unfollow_index]
                    if unfollow_user(session, username, log):
                        unfollow_index += 1
                elif 30 <= action_choice < 60 and counts["last_hour"]["comment"] < comments_per_hour and post_index < len(all_posts):
                    action = "comment"
                    delay = 12  # ~5 comments/min, 50/hour
                    post = all_posts[post_index]
                    username = post["user"]["username"]
                    post_id = post["pk"]
                    if comment_on_post(session, post_id, username, custom_comments, log):
                        post_index += 1
                elif action_choice >= 60 and counts["last_hour"]["like"] < likes_per_hour and post_index < len(all_posts):
                    action = "like"
                    delay = 3  # ~20 likes/min, 200/hour
                    post = all_posts[post_index]
                    username = post["user"]["username"]
                    post_id = post["pk"]
                    if like_post(session, post_id, username, log):
                        post_index += 1
                
                if action:
                    log(f"Performed {action}, next action choice: {action_choice}")
                    time.sleep(random.uniform(delay * 0.8, delay * 1.2))  # 20% variance, e.g., 3s → 2.4-3.6s
                    failed_attempts = 0
                else:
                    log(f"Skipped action due to limits or exhaustion: choice={action_choice}")
                    time.sleep(2)  # Faster retry
                    failed_attempts += 1

                if (post_index >= len(all_posts) or follow_index >= len(potential_follows) or unfollow_index >= len(to_unfollow) or failed_attempts >= max_failed_attempts):
                    if failed_attempts >= max_failed_attempts:
                        log(f"Too many failed attempts ({failed_attempts}/{max_failed_attempts}). Pausing for 15 minutes.")
                        time.sleep(900)
                        failed_attempts = 0
                    
                    log("Refreshing data")
                    selected_tag = random.choice(tags)
                    all_posts = get_posts_by_tag(session, selected_tag, log) or []
                    if not all_posts:
                        all_posts = get_explore_data(session) or []
                    
                    conn = sqlite3.connect('instagram_bot.db')
                    c = conn.cursor()
                    c.execute("SELECT username FROM followed_users LIMIT 5")
                    my_followings = [row[0] for row in c.fetchall()]
                    c.execute("SELECT username FROM followed_users WHERE follow_time < ? AND followed_by_bot = 1",
                             ((datetime.now() - timedelta(hours=48)).isoformat(),))
                    to_unfollow = [row[0] for row in c.fetchall()]
                    conn.close()
                    
                    potential_follows = []
                    for following in my_followings:
                        follows = get_followers_of_following(session, following)
                        potential_follows.extend(follows or [])
                    
                    if post_index >= len(all_posts):
                        post_index = 0
                    if follow_index >= len(potential_follows):
                        follow_index = 0
                    if unfollow_index >= len(to_unfollow):
                        unfollow_index = 0

            except ssl.SSLEOFError as e:
                log(f"Main loop error: SSL EOF error - {str(e)}. Waiting 5 minutes before retrying.")
                time.sleep(300)
            except Exception as e:
                log(f"Main loop error: {str(e)}. Waiting 5 minutes before retrying")
                time.sleep(300)

    except Exception as e:
        log(f"Startup error: {str(e)}")
        return
    
if __name__ == "__main__":
    root = tk.Tk()
    app = InstagramBotGUI(root)
    root.mainloop()