from googlesearch import search
from ddgs import DDGS
from datetime import datetime
from colorama import init, Fore
import time
import os

# Initialize colorama for colored terminal output
init(autoreset=True)

# Output and error log file paths
OUTPUT_FILE = "results.txt"
ERROR_FILE = "error.log"

# Ensure required files exist
open(OUTPUT_FILE, "a").close()
open(ERROR_FILE, "a").close()

def run_dork_query(dork, num_results=3, delay=10):
    """Perform a dork query using Google and DuckDuckGo and log the results."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    engines = ["google", "duckduckgo"]

    for engine in engines:
        print(Fore.CYAN + f"\n[+] Searching with {engine.title()}: {dork} | Time: {timestamp}")
        try:
            with open(OUTPUT_FILE, "a") as f:
                f.write(f"\n[+] Dork: {dork} | Engine: {engine} | Time: {timestamp}\n")

                if engine == "google":
                    results = search(dork, num_results=num_results)
                elif engine == "duckduckgo":
                    with DDGS() as ddgs:
                        results = [r['href'] for r in ddgs.text(dork, max_results=num_results)]
                else:
                    results = []

                for url in results:
                    print(Fore.GREEN + url)
                    f.write(url + "\n")
                    time.sleep(delay)

        except Exception as e:
            print(Fore.RED + f"[!] Error during {engine} search: {e}")
            with open(ERROR_FILE, "a") as err:
                err.write(f"[{timestamp}] Error with dork '{dork}' using {engine}: {e}\n")

def main():
    print(Fore.YELLOW + "\n==== Automated Dork Executor (Google + DuckDuckGo) ====")
    print("1. Run Government Dorks")
    print("2. Run University Dorks")
    
    choice = input("Choose option (1 or 2): ").strip()
    if choice not in ["1", "2"]:
        print(Fore.RED + "[!] Invalid selection. Please enter 1 or 2.")
        return

    domain_input = input("Enter full domain : ").strip()
    if not domain_input:
        print(Fore.RED + "[!] Domain input required.")
        return

    dork_file = "gov_dorks.txt" if choice == "1" else "uni_dorks.txt"
    if not os.path.exists(dork_file):
        print(Fore.RED + f"[!] Dork file '{dork_file}' not found.")
        return

    print(Fore.YELLOW + f"\n[+] Running dorks from: {dork_file} | Target Domain: {domain_input}")
    with open(dork_file, "r") as file:
        for line in file:
            dork_suffix = line.strip()
            if dork_suffix:
                full_dork = f"site:{domain_input} {dork_suffix}"
                run_dork_query(full_dork)

    print(Fore.BLUE + "✔️ Output successfully saved to results.txt")

# Run the main function
if __name__ == "__main__":
    main()

# After all dorking is done, send results via email
import mail_sender
mail_sender.send_email()
