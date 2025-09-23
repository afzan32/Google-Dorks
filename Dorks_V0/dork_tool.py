from googlesearch import search
from ddgs import DDGS
from datetime import datetime
from colorama import init, Fore
import time
import os

# Initialize colorama for colored console output
init(autoreset=True)

# Output file paths
OUTPUT_FILE = "dork_results.txt"
ERROR_FILE = "errors.log"

# Dork categories mapped to their respective filenames
CATEGORY_FILES = {
    "1": ("Exposed_files", "Exposed_files.txt"),
    "2": ("Goverment_sites", "Goverment_sites.txt"),
    "3": ("Login_portal", "Login_portal.txt"),
    "4": ("Sample_dorks", "Sample_dorks.txt"),
    "5": ("Sensitive_information", "Sensitive_information.txt"),
    "6": ("Dictionary_listing", "Dictionary_listing.txt")
}

# Ensure output files exist
open(OUTPUT_FILE, "a").close()
open(ERROR_FILE, "a").close()

def run_dork_query(dork, num_results=1, delay=2):
    """Runs the given dork against Google and DuckDuckGo, saving results."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    search_engines = ["google", "duckduckgo"]

    for engine in search_engines:
        print(Fore.CYAN + f"\n[+] Searching ({engine}): {dork} | Time: {timestamp}")

        try:
            with open(OUTPUT_FILE, "a") as output_file:
                output_file.write(f"\n[+] Dork: {dork} | Engine: {engine} | Time: {timestamp}\n")

                if engine == "google":
                    results = search(dork, num_results=num_results)
                elif engine == "duckduckgo":
                    with DDGS() as ddgs:
                        results = [r['href'] for r in ddgs.text(dork, max_results=num_results)]
                else:
                    results = []

                for url in results:
                    print(Fore.GREEN + url)
                    output_file.write(url + "\n")
                    time.sleep(delay)

        except Exception as e:
            print(Fore.RED + f"[!] Error using {engine}: {e}")
            with open(ERROR_FILE, "a") as error_file:
                error_file.write(f"[{timestamp}] Error with dork '{dork}' using {engine}: {e}\n")


print(Fore.BLUE + " Output successfully saved to dork_results.txt")
    

def main():
    """Main menu and controller for the dork scanner."""
    print(Fore.YELLOW + "==== Multi-Engine Dork Automation Tool (Google + DuckDuckGo) ====")
    print("\n1. Single Dork")
    print("2. Load Dorks from File (Choose Category)")

    choice = input("Choose option (1 or 2): ").strip()

    if choice == "1":
        dork_query = input("Enter Google Dork: ").strip()
        run_dork_query(dork_query)

    elif choice == "2":
        print("\nSelect a category to scan:")
        for key, (name, _) in CATEGORY_FILES.items():
            print(f"{key}. {name}")

        category_choice = input("Choose category (1 to 6): ").strip()

        if category_choice not in CATEGORY_FILES:
            print(Fore.RED + "[!] Invalid category selection.")
            return

        category_name, dork_file = CATEGORY_FILES[category_choice]

        if not os.path.exists(dork_file):
            print(Fore.RED + f"[!] File '{dork_file}' not found.")
            return

        print(Fore.YELLOW + f"\n[+] Running dorks from file: {dork_file} (Category: {category_name})")
        with open(dork_file, "r") as file:
            for line in file:
                dork = line.strip()
                if dork:
                    run_dork_query(dork)

    else:
        print(Fore.RED + "[!] Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()
# import send_email
# send_email.send_email()
