import os
import sys
import time
import subprocess
import requests
import zipfile
import shutil
from pathlib import Path

# ==== CONFIGURATION ====
GITHUB_REPO = "https://raw.githubusercontent.com/1inam1llion/pywin/main/"
VERSION_FILE = "version.txt"
SCRIPT_FILE = "win10_bootable.py"
CURRENT_VERSION = "0.1"  # This should match the latest version

# Paths
BASE_DIR = Path(__file__).resolve().parent
VERSION_PATH = BASE_DIR / VERSION_FILE
SCRIPT_PATH = BASE_DIR / SCRIPT_FILE
VENV_PATH = BASE_DIR / "venv"

# ==== UPDATE CHECK FUNCTION ====
def check_for_updates():
    try:
        response = requests.get(GITHUB_REPO + VERSION_FILE, timeout=10)
        if response.status_code == 200:
            latest_version = response.text.strip()
            if not VERSION_PATH.exists() or VERSION_PATH.read_text().strip() != latest_version:
                print(f"[UPDATE] New version {latest_version} found! Updating...")
                update_script()
            else:
                print(f"[INFO] Running latest version: {CURRENT_VERSION}")
        else:
            print("[ERROR] Could not fetch version info.")
    except requests.RequestException as e:
        print(f"[ERROR] Failed to check for updates: {e}")

# ==== UPDATE FUNCTION ====
def update_script():
    try:
        script_url = GITHUB_REPO + SCRIPT_FILE
        response = requests.get(script_url, timeout=10)
        if response.status_code == 200:
            with open(SCRIPT_PATH, "wb") as f:
                f.write(response.content)
            with open(VERSION_PATH, "w") as f:
                f.write(response.text.strip())
            print("[INFO] Update complete. Restarting script...")
            time.sleep(2)
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            print("[ERROR] Failed to download updated script.")
    except requests.RequestException as e:
        print(f"[ERROR] Update failed: {e}")

# ==== VIRTUAL ENV SETUP ====
def setup_venv():
    if not VENV_PATH.exists():
        print("[INFO] Setting up virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(VENV_PATH)], check=True)
    pip_path = VENV_PATH / "bin" / "pip" if os.name != "nt" else VENV_PATH / "Scripts" / "pip.exe"
    subprocess.run([str(pip_path), "install", "--upgrade", "pip", "selenium", "requests"], check=True)

# ==== MAIN FUNCTION ====
def main():
    check_for_updates()
    setup_venv()

    print("[INFO] All dependencies installed. Proceeding with Windows ISO download...")

    # Now, launch Selenium and continue your main logic here...
    # Example: Launch a browser instance
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://www.microsoft.com/en-us/software-download/windows10ISO")

    print("[INFO] Browser launched successfully!")
    input("Press Enter to exit...")  # Keep window open

if __name__ == "__main__":
    main()
