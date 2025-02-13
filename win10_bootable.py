import os
import sys
import subprocess
import requests
import shutil

# GitHub Repo (Change this to your repository URL)
GITHUB_REPO = "https://raw.githubusercontent.com/1inam1llion/pywin/main/"

# Version File Path
LOCAL_VERSION_FILE = "version.txt"

# Fetch current version from GitHub
def get_latest_version():
    try:
        response = requests.get(GITHUB_REPO + "version.txt", timeout=10)
        if response.status_code == 200:
            return response.text.strip()
    except requests.RequestException:
        return None
    return None

# Read local version
def get_local_version():
    if os.path.exists(LOCAL_VERSION_FILE):
        with open(LOCAL_VERSION_FILE, "r") as file:
            return file.read().strip()
    return "0.0.0"

# Download and replace script if an update is found
def update_script():
    latest_version = get_latest_version()
    local_version = get_local_version()

    print(f"[INFO] Current Version: {local_version}")
    if latest_version and latest_version != local_version:
        print(f"[UPDATE] New Version Found: {latest_version}. Updating...")
        try:
            script_response = requests.get(GITHUB_REPO + "win10_bootable.py", timeout=10)
            if script_response.status_code == 200:
                with open(sys.argv[0], "wb") as script_file:
                    script_file.write(script_response.content)
                with open(LOCAL_VERSION_FILE, "w") as version_file:
                    version_file.write(latest_version)
                print("[SUCCESS] Update complete! Restarting script...")
                os.execv(sys.executable, [sys.executable] + sys.argv)  # Relaunch script
        except requests.RequestException:
            print("[ERROR] Failed to download update.")
    else:
        print("[INFO] No updates found. Running latest version.")

# Ensure virtual environment is set up
def setup_venv():
    venv_dir = os.path.join(os.getcwd(), "venv")
    if not os.path.exists(venv_dir):
        print("[INFO] Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
    
    pip_path = os.path.join(venv_dir, "bin", "pip") if os.name != "nt" else os.path.join(venv_dir, "Scripts", "pip.exe")
    requirements_file = "requirements.txt"
    
    if not os.path.exists(requirements_file):
        with open(requirements_file, "w") as f:
            f.write("selenium\nrich\nrequests\n")

    print("[INFO] Installing dependencies...")
    subprocess.run([pip_path, "install", "-r", requirements_file], check=True)

# Run the script inside the virtual environment
def run_script():
    venv_python = os.path.join(os.getcwd(), "venv", "bin", "python") if os.name != "nt" else os.path.join(os.getcwd(), "venv", "Scripts", "python.exe")
    if sys.executable != venv_python:
        print("[INFO] Relaunching script inside virtual environment...")
        os.execv(venv_python, [venv_python] + sys.argv)

# Main execution
if __name__ == "__main__":
    update_script()  # Check for updates
    setup_venv()  # Ensure virtual environment is ready
    run_script()  # Relaunch script inside venv before continuing
    
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from rich.console import Console
    from rich.table import Table
    import time

    console = Console()
    
    # Set up Selenium
    console.print("[INFO] Launching browser to fetch Windows 10 ISO links...", style="bold cyan")
    
    options = Options()
    options.headless = True  # Run in headless mode
    service = Service("/usr/bin/chromedriver")  # Update this if ChromeDriver is in a different location
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://www.microsoft.com/en-us/software-download/windows10ISO")
        time.sleep(5)  # Allow JavaScript to load

        page_source = driver.page_source
        iso_links = []
        
        for line in page_source.splitlines():
            if "software-download.microsoft.com" in line and ".iso" in line:
                iso_link = line.split('"')[1]
                if iso_link not in iso_links:
                    iso_links.append(iso_link)

        if iso_links:
            table = Table(title="Available Windows 10 ISO Links")
            table.add_column("#", justify="center", style="bold magenta")
            table.add_column("Download Link", justify="left", style="bold green")
            for index, link in enumerate(iso_links, start=1):
                table.add_row(str(index), link)
            
            console.print(table)
            
            choice = console.input("[bold yellow]Enter the number of the ISO to download:[/bold yellow] ")
            if choice.isdigit() and 1 <= int(choice) <= len(iso_links):
                selected_iso = iso_links[int(choice) - 1]
                iso_filename = "Windows10.iso"
                
                console.print(f"[INFO] Downloading {iso_filename}...", style="bold cyan")
                with requests.get(selected_iso, stream=True) as r:
                    with open(iso_filename, "wb") as f:
                        shutil.copyfileobj(r.raw, f)
                console.print("[SUCCESS] Windows 10 ISO downloaded!", style="bold green")

                # Automate mkusb
                usb_device = console.input("[bold yellow]Enter USB device path (e.g., /dev/sdb):[/bold yellow] ")
                if os.path.exists(usb_device):
                    console.print("[INFO] Creating bootable USB...", style="bold cyan")
                    subprocess.run(["sudo", "mkusb", iso_filename, usb_device], check=True)
                    console.print("[SUCCESS] Bootable USB created!", style="bold green")
                else:
                    console.print("[ERROR] Invalid USB device path!", style="bold red")
            else:
                console.print("[ERROR] Invalid selection!", style="bold red")
        else:
            console.print("[ERROR] No ISO links found.", style="bold red")
    
    finally:
        driver.quit()
