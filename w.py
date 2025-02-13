import os
import sys
import subprocess
import time
import requests

# --- CONFIGURATIONS ---
GITHUB_REPO = "https://raw.githubusercontent.com/1inam1llion/pywin/main/"
VERSION_FILE = "version.txt"
SCRIPT_FILE = "w.py"
CURRENT_VERSION = "0.0.0"

# --- CHECK FOR UPDATES ---
def check_for_update():
    """Fetches version.txt from GitHub and compares with the local version."""
    try:
        response = requests.get(GITHUB_REPO + VERSION_FILE, timeout=10)
        if response.status_code == 200:
            latest_version = response.text.strip()
            if latest_version != CURRENT_VERSION:
                print(f"[UPDATE] New version {latest_version} found! Updating...")
                update_script()
            else:
                print(f"[INFO] Running latest version: {CURRENT_VERSION}")
        else:
            print("[WARNING] Unable to check for updates.")
    except requests.RequestException:
        print("[ERROR] Failed to fetch update information.")

def update_script():
    """Downloads the latest script from GitHub and restarts it."""
    try:
        response = requests.get(GITHUB_REPO + SCRIPT_FILE, timeout=10)
        if response.status_code == 200:
            with open(SCRIPT_FILE, "wb") as f:
                f.write(response.content)
            print("[INFO] Update complete. Restarting script...")
            os.execv(sys.executable, ['python3'] + sys.argv)
        else:
            print("[ERROR] Failed to download the latest script.")
    except requests.RequestException:
        print("[ERROR] Update process failed.")

# --- SETUP VIRTUAL ENVIRONMENT ---
VENV_DIR = "venv"

def setup_venv():
    """Creates and activates a virtual environment if not already set up."""
    if not os.path.exists(VENV_DIR):
        print("[INFO] Setting up virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)
    
    # Activate venv
    if sys.platform == "win32":
        activate_script = os.path.join(VENV_DIR, "Scripts", "activate")
    else:
        activate_script = os.path.join(VENV_DIR, "bin", "activate")
    
    os.environ["VIRTUAL_ENV"] = os.path.abspath(VENV_DIR)
    os.environ["PATH"] = os.path.abspath(os.path.join(VENV_DIR, "bin")) + os.pathsep + os.environ["PATH"]
    
    print("[INFO] Virtual environment is ready.")

# --- INSTALL DEPENDENCIES ---
REQUIREMENTS = ["selenium", "requests", "rich"]

def install_dependencies():
    """Ensures all required dependencies are installed inside the virtual environment."""
    print("[INFO] Checking dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run([sys.executable, "-m", "pip", "install"] + REQUIREMENTS, check=True)
        print("[INFO] Dependencies installed successfully.")
    except subprocess.CalledProcessError:
        print("[ERROR] Failed to install dependencies.")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    check_for_update()
    setup_venv()
    install_dependencies()

    # Import dependencies after ensuring installation
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    from rich.console import Console

    console = Console()

    # --- SETUP SELENIUM BROWSER ---
    console.print("[INFO] Launching browser to fetch Windows 10 ISO links...", style="bold cyan")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get("https://www.microsoft.com/en-us/software-download/windows10ISO")
        time.sleep(5)  # Wait for the page to load

        # Extract and display available editions
        console.print("[INFO] Available Windows 10 Editions:", style="bold green")
        editions = driver.find_elements("tag name", "option")
        edition_dict = {}
        for i, edition in enumerate(editions, 1):
            edition_dict[str(i)] = edition.get_attribute("value")
            console.print(f"{i}. {edition.text}")

        selection = input("\nSelect the edition number: ")
        if selection not in edition_dict:
            console.print("[ERROR] Invalid selection. Exiting.", style="bold red")
            sys.exit(1)

        # Proceed with selection (simplified for this example)
        console.print(f"[INFO] Selected: {editions[int(selection)-1].text}", style="bold yellow")

        # Clean up Selenium session
        driver.quit()
    except Exception as e:
        console.print(f"[ERROR] {str(e)}", style="bold red")
        sys.exit(1)
