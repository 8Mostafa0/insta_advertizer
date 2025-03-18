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

running = False
session = requests.Session()
session.headers.update(HEADERS)

retry_strategy = Retry(
    total=3,
    backoff_factor=15,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)

def setup_database():
    conn = sqlite3.connect('instagram_bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS followed_users
                 (username TEXT PRIMARY KEY, follow_time TEXT, followed_by_bot INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS action_log
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, action_type TEXT, timestamp TEXT)''')
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

class InstagramBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Human-like Bot")
        
        self.username_var = tk.StringVar(value="b2rayng")
        self.password_var = tk.StringVar(value="@Mm09020407808")
        self.sessionid_var = tk.StringVar(value="")
        self.follows_var = tk.IntVar(value=5)
        self.likes_var = tk.IntVar(value=20)
        self.comments_var = tk.IntVar(value=10)
        self.unfollows_var = tk.IntVar(value=5)
        
        ttk.Label(root, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(root, textvariable=self.username_var).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(root, text="Password (optional if Session ID):").grid(row=1, column=0, padx=5, pady=5)
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
        
        self.start_button = ttk.Button(root, text="Start", command=self.start_bot)
        self.start_button.grid(row=7, column=0, padx=5, pady=5)
        
        self.stop_button = ttk.Button(root, text="Stop", command=self.stop_bot, state="disabled")
        self.stop_button.grid(row=7, column=1, padx=5, pady=5)
        
        self.post_button = ttk.Button(root, text="Post", command=self.repost_last_post)
        self.post_button.grid(row=7, column=2, padx=5, pady=5)
        
        self.log_text = tk.Text(root, height=10, width=50)
        self.log_text.grid(row=8, column=0, columnspan=3, padx=5, pady=5)

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
            self.log,
            session_id
        ), daemon=True).start()

    def stop_bot(self):
        global running
        running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.log("Bot stopped")

    def repost_last_post(self):
        threading.Thread(target=self._repost_last_post_thread, daemon=True).start()

    def _repost_last_post_thread(self):
        global session
        self.log("Fetching last post...")
        last_post = get_last_post(session, USERNAME, self.log)
        if not last_post:
            self.log("Failed to fetch last post")
            return
        
        media_url = last_post.get("media_url")
        caption = last_post.get("caption", "")
        thumbnail_url = last_post.get("thumbnail_url", media_url)
        
        self.log("Downloading media and thumbnail...")
        media_path = download_file(media_url, "last_post_media")
        thumbnail_path = download_file(thumbnail_url, "last_post_thumbnail")
        
        if not media_path or not thumbnail_path:
            self.log("Failed to download media or thumbnail")
            return
        
        self.log("Creating new post...")
        success = create_post(session, media_path, caption, thumbnail_path, self.log)
        if success:
            self.log("Successfully reposted last post")
        else:
            self.log("Failed to create new post")

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
                "username": USERNAME,
                "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{PASSWORD}",
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
        profile_url = f"{BASE_URL}/api/v1/users/web_profile_info/?username={USERNAME}"
        response = session.get(profile_url, headers={"X-IG-App-ID": "936619743392459"}, timeout=20)
        return response.status_code == 200
    except Exception:
        return False

def get_user_profile_data(session, username, log=None):
    try:
        csrf_token = get_csrf_token()
        if not csrf_token:
            if log:
                log("Failed to get CSRF token for profile fetch")
            return None
        
        session.headers.update({"User-Agent": random.choice(USER_AGENTS), "X-CSRFToken": csrf_token})
        profile_url = f"{BASE_URL}/api/v1/users/web_profile_info/?username={username}"
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
    user_data = get_user_profile_data(session, username, log)
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

def get_last_post(session, username, log):
    try:
        if not verify_login(session):
            log("Session invalid, please re-login")
            return None
        
        user_data = get_user_profile_data(session, username, log)
        if not user_data:
            return None
        
        user_id = user_data["id"]
        url = f"{BASE_URL}/api/v1/feed/user/{user_id}/"
        session.headers.update({"User-Agent": random.choice(USER_AGENTS)})
        response = session.get(url, headers={"X-IG-App-ID": "936619743392459"}, timeout=20)
        
        if response.status_code != 200:
            log(f"Failed to fetch posts, HTTP status: {response.status_code}")
            return None
        
        if "<!DOCTYPE html>" in response.text:
            log("Received HTML instead of JSON for user posts")
            return None
        
        data = response.json()
        items = data.get("items", [])
        if not items:
            log("No posts found for this user")
            return None
        
        last_post = items[0]
        media_url = last_post["image_versions2"]["candidates"][0]["url"] if "image_versions2" in last_post else last_post.get("video_versions", [{}])[0].get("url")
        if not media_url:
            log("No media URL found in last post")
            return None
        
        caption = last_post.get("caption", {}).get("text", "") if last_post.get("caption") else ""
        thumbnail_url = last_post.get("image_versions2", {}).get("candidates", [{}])[0].get("url", media_url)
        
        log(f"Fetched last post: {media_url[:50]}...")
        return {"media_url": media_url, "caption": caption, "thumbnail_url": thumbnail_url}
    except Exception as e:
        log(f"Error fetching last post: {str(e)}")
        return None

def download_file(url, filename_prefix):
    try:
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            ext = ".jpg" if "image" in response.headers.get("Content-Type", "") else ".mp4"
            filename = f"{filename_prefix}{ext}"
            with open(filename, "wb") as f:
                f.write(response.content)
            return filename
        return None
    except Exception:
        return None

def create_post(session, media_path, caption, thumbnail_path, log):
    try:
        # Refresh CSRF token
        csrf_token = get_csrf_token()
        if not csrf_token:
            log("Failed to get CSRF token for post upload")
            return False
        
        session.headers.update({"User-Agent": random.choice(USER_AGENTS), "X-CSRFToken": csrf_token})
        upload_url = f"{BASE_URL}/api/v1/media/upload/"
        with open(media_path, "rb") as f:
            files = {"photo": (os.path.basename(media_path), f, "image/jpeg" if media_path.endswith(".jpg") else "video/mp4")}
            response = session.post(upload_url, files=files, headers={"X-IG-App-ID": "936619743392459"}, timeout=20)
            if response.status_code != 200:
                log(f"Media upload failed, HTTP status: {response.status_code}, response: {response.text[:100]}")
                return False
            upload_id = response.json().get("upload_id")
            if not upload_id:
                log("No upload ID returned from media upload")
                return False
            log(f"Media uploaded, upload ID: {upload_id}")
        
        configure_url = f"{BASE_URL}/api/v1/media/configure/"
        payload = {
            "upload_id": upload_id,
            "caption": caption,
            "usertags": "[]",
            "source_type": "4",
        }
        response = session.post(configure_url, data=payload, headers={"X-IG-App-ID": "936619743392459", "X-CSRFToken": csrf_token}, timeout=20)
        if response.status_code != 200:
            log(f"Post configuration failed, HTTP status: {response.status_code}, response: {response.text[:100]}")
            return False
        
        log("Post configured successfully")
        return True
    except Exception as e:
        log(f"Error creating post: {str(e)}")
        return False

def run_bot(follows_per_hour, likes_per_hour, comments_per_hour, unfollows_per_hour, log, session_id=None):
    global session, running
    
    setup_database()
    logged_in_session = load_session(session_id)
    if logged_in_session and verify_login(logged_in_session):
        log("Session loaded successfully")
    else:
        log("Trying to login with credentials...")
        logged_in_session = login()
        if not logged_in_session:
            log("Login failed after retries. Check credentials or use a valid session ID.")
            return
        log("Login successful")
    
    session = logged_in_session
    log("Bot started")

    while running:
        try:
            if random.random() < 0.1:
                check_messages(session, log)
                time.sleep(random.uniform(5, 15))

            counts = get_action_counts_last_hour()
            posts = get_feed_data(session)
            if not posts:
                log("No posts found in feed, waiting...")
                time.sleep(60)
                continue

            action_weights = [
                ("like", 0.4, counts["like"] < likes_per_hour),
                ("comment", 0.25, counts["comment"] < comments_per_hour),
                ("follow", 0.2, counts["follow"] < follows_per_hour),
                ("unfollow", 0.15, counts["unfollow"] < unfollows_per_hour)
            ]
            
            available_actions = [a for a, _, cond in action_weights if cond]
            if not available_actions:
                log("All action limits reached, waiting...")
                time.sleep(300)
                continue

            action = random.choices(
                [a for a, _, _ in action_weights],
                weights=[w for _, w, c in action_weights if c],
                k=1
            )[0]

            post = random.choice(posts)
            if "media" not in post:
                continue
            media = post["media"]
            username = media["user"]["username"]
            post_id = media["pk"] if "pk" in media else media["id"]

            if action == "like":
                like_post(session, post_id, username, log)
                time.sleep(random.uniform(2, 8))

            elif action == "comment":
                comment_on_post(session, post_id, username, log)
                time.sleep(random.uniform(5, 15))

            elif action == "follow":
                followers = get_followers(session, username)
                if followers:
                    target = random.choice(followers)
                    follow_user(session, target, log)
                    time.sleep(random.uniform(10, 20))

            elif action == "unfollow":
                conn = sqlite3.connect('instagram_bot.db')
                c = conn.cursor()
                c.execute("SELECT username FROM followed_users WHERE follow_time < ? AND followed_by_bot = 1 LIMIT 1",
                         ((datetime.now() - timedelta(hours=48)).isoformat(),))
                to_unfollow = c.fetchone()
                conn.close()
                if to_unfollow:
                    unfollow_user(session, to_unfollow[0], log)
                    time.sleep(random.uniform(15, 25))

            if random.random() < 0.2:
                log("Taking a short human-like break")
                time.sleep(random.uniform(30, 120))
            elif random.random() < 0.05:
                log("Taking a longer human-like break")
                time.sleep(random.uniform(300, 600))

        except Exception as e:
            log(f"Error: {str(e)}")
            time.sleep(300)

if __name__ == "__main__":
    root = tk.Tk()
    app = InstagramBotGUI(root)
    root.mainloop()