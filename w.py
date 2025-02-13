import os
import sys
import time
import requests
import subprocess
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# GitHub Repository Information
GITHUB_REPO = "https://raw.githubusercontent.com/1inam1llion/pywin/main"
LOCAL_VERSION_FILE = "version.txt"
SCRIPT_NAME = "w.py"
CURRENT_VERSION = "0.1"  # Change this when updating manually

def fetch_latest_version():
    """Fetches the latest version number from GitHub."""
    try:
        response = requests.get(f"{GITHUB_REPO}/version.txt", timeout=10)
        if response.status_code == 200:
            return response.text.strip()
    except requests.RequestException:
        print("[ERROR] Could not fetch latest version info.")
    return None

def update_script():
    """Downloads the latest script version from GitHub and restarts if needed."""
    print("[UPDATE] Checking for updates...")
    latest_version = fetch_latest_version()

    if latest_version and latest_version != CURRENT_VERSION:
        print(f"[UPDATE] New version {latest_version} found! Updating...")

        # Download the latest script
        response = requests.get(f"{GITHUB_REPO}/{SCRIPT_NAME}", timeout=10)
        if response.status_code == 200:
            with open(SCRIPT_NAME, "wb") as f:
                f.write(response.content)

            # Update the local version.txt file properly
            with open(LOCAL_VERSION_FILE, "w") as f:
                f.write(latest_version)

            print("[INFO] Update complete. Restarting script...")
            time.sleep(2)
            os.execv(sys.executable, ["python3"] + sys.argv)
        else:
            print("[ERROR] Failed to download the updated script.")
    else:
        print("[INFO] You are running the latest version.")

def setup_venv():
    """Sets up a virtual environment and installs dependencies."""
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print("[SETUP] Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    
    pip_executable = str(venv_path / "bin" / "pip") if os.name != "nt" else str(venv_path / "Scripts" / "pip.exe")
    
    print("[SETUP] Installing dependencies...")
    subprocess.run([pip_executable, "install", "--upgrade", "pip", "selenium", "webdriver-manager", "requests"], check=True)

def launch_browser():
    """Launches a browser to fetch Windows 10 ISO links."""
    print("[INFO] Launching browser to fetch Windows 10 ISO links...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://www.microsoft.com/en-us/software-download/windows10ISO")
    time.sleep(5)  # Wait for the page to load
    driver.quit()
    print("[INFO] Finished fetching Windows 10 ISO links.")

if __name__ == "__main__":
    print(f"[INFO] Running script version {CURRENT_VERSION}")
    
    # Step 1: Check for updates
    update_script()
    
    # Step 2: Setup Virtual Environment
    setup_venv()
    
    # Step 3: Run the main function
    launch_browser()
