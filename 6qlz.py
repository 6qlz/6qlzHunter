#!/usr/bin/python3
VERSION = 'v1.4'

class Color:
    BLUE = '\033[94m'
    GREEN = '\033[1;92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    ORANGE = '\033[38;5;208m'
    BOLD = '\033[1m'
    UNBOLD = '\033[22m'
    ITALIC = '\033[3m'
    UNITALIC = '\033[23m'
    WHITE = '\033[1;37m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_RED = '\033[91m'

try:
    import os
    import requests
    import shutil
    import sys
    import random
    import re
    from colorama import Fore, Style, init
    import time
    from urllib.parse import quote
    import urllib3
    import argparse
    import concurrent.futures
    from rich.console import Console
    from rich.progress import Progress
    import signal  # For handling Ctrl+C

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.1.2 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.70",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
    ]

    init(autoreset=True)

    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')

    def center_text(text):
        terminal_width = shutil.get_terminal_size().columns
        return "\n".join(line.center(terminal_width) for line in text.split("\n"))

    ASCII_ART = f""" {Fore.RED}
⠀⠀⠀⢀⡤⢤⢄⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣼⡅⠠⢀⡈⢀⣙⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠤⠤⢤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢸⠀⠀⠀⠈⠙⠿⣝⢇⠀⠀⣀⣠⠤⠤⠤⠤⣤⡤⠚⠁⠀⠀⠀⠀⠀⠉⠢⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢧⡀⠀⠀⠠⣄⠈⢺⣺⡍⠀⠀⠀⠀⣠⠖⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠸⡆⢀⠘⣔⠄⠑⠂⠈⠀⡔⠤⠴⠚⡁⠀⠀⢀⠀⠀⠀⣠⠔⢶⡢⡀⠀⠠⡇⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢠⣇⠀⢃⡀⠁⠀⠀⠀⡸⠃⢀⡴⠊⢀⠀⠀⠈⢂⡤⠚⠁⠀⠀⠙⢿⠀⠉⡇⠀⠀⠀⠀⠀
⠀⠀⠀⣠⠾⣹⢤⢼⡆⠀⠀⠀⠀⠀⠀⠈⢀⠞⠁⠀⢠⣴⠏⠀⠀⠀⠀⠀⠀⠸⡇⠀⢇⠀⠀⠀⠀⠀
⠀⠀⣾⢡⣤⡈⠣⡀⠙⠒⠀⠀⠀⠀⣀⠤⠤⣤⠤⣌⠁⢛⡄⠀⠀⠀⠀⠀⠠⡀⢇⠀⠘⣆⠀⢀⡴⡆
⠀⠀⣿⢻⣿⣿⣄⡸⠀⡆⠀⠒⣈⣩⣉⣉⡈⠉⠉⠢⣉⠉⠀⠀⠀⠀⠀⠀⠀⢣⠈⠢⣀⠈⠉⢁⡴⠃
⠀⢀⢿⣿⣿⡿⠛⠁⠀⢻⣿⣿⣿⣿⣿⣿⣿⣷⣦⣄⣸⢿⠀⠀⠀⠀⠀⠀⠀⠸⡄⠀⡇⠉⠉⠁⠀⠀
⣠⣞⠘⢛⡛⢻⣷⣤⡀⠈⡎⣿⣿⣿⣿⣿⣿⣿⣿⣿⠹⠏⠀⠀⠀⠀⠀⠀⠀⠀⠇⢰⡇⠀⠀⠀⠀⠀
⠻⣌⠯⡁⢠⣸⣿⣿⣷⡄⠁⠈⢻⢿⣿⣿⣿⣿⠿⠋⠃⠰⣀⠀⠀⠀⠀⠀⠀⠀⠀⣾⠇⠀⠀⠀⠀⠀
⠀⠀⠉⢻⠨⠟⠹⢿⣿⢣⠀⠀⢨⡧⣌⠉⠁⣀⠴⠊⠑⠀⡸⠛⠀⠀⠀⠀⠀⣸⢲⡟⠀⠀⠀⠀⠀⠀
⠀⠀⣠⠏⠀⠀⠀⠉⠉⠁⠀⠐⠁⠀⠀⢉⣉⠁⠀⠀⢀⠔⢷⣄⠀⠀⠀⠀⢠⣻⡞⠀⠀⠀⠀⠀⠀⠀
⠀⢠⠟⡦⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⢾⠉⠀⣹⣦⠤⣿⣿⡟⠁⠀⠀⠀⢀⣶⠟⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠈⠙⣦⣁⡎⢈⠏⢱⠚⢲⠔⢲⠲⡖⠖⣦⣿⡟⠀⣿⡿⠁⣠⢔⡤⠷⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢿⣟⠿⡿⠿⠶⢾⠶⠾⠶⠾⠞⢻⠋⠏⣸⠁⠀⡽⠓⠚⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢸⡏⠳⠷⠴⠣⠜⠢⠜⠓⠛⠊⠀⢀⡴⠣⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⣏⠒⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠊⠁⢀⣀⣀⠴⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠘⢦⡀⠀⠀⠀⠀⠀⠀⢀⣀⠴⠖⠒⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠉⠑⠒⠒⠐⠒⠛⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
  ____      __    __ __          __  ____    
 / __/___ _/ /__ / // /_ _____  / /_|_  /____
/ _ \/ _ `/ /_ // _  / // / _ \/ __//_ </ __/
\___/\_, /_//__/_//_/\_,_/_//_/\__/____/_/   
      /_/                                    

----------- Made by @6qlz ------------

[1] Directory Scanner
[2] SQL Injection Scan
[3] Check Local File Inclusion
[4] XSS Vulnerability Scan
[5] Exit.{Style.RESET_ALL}

"""
    ASCII_ART = center_text(ASCII_ART)

    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_menu():
        clear_screen()
        print(Fore.RED + Style.BRIGHT + ASCII_ART)

    def load_payloads_from_file(filepath):
        try:
            with open(filepath, 'r') as f:
                return [line.strip() for line in f]
        except FileNotFoundError:
            print(Fore.RED + f"[-] Payload file not found: {filepath}")
            return []
        except Exception as e:
            print(Fore.RED + f"[-] Error reading payload file: {e}")
            return []

    def test_url(url, payload, scan_type):
        test_url = url.replace("FUZZ", quote(payload))
        try:
            response = requests.get(test_url, timeout=5,
                                    headers={'User-Agent': random.choice(USER_AGENTS)})
            status_code = response.status_code
            is_vulnerable = False

            if scan_type == "dir":
                if response.status_code != 404:  # Simple check for directory existence
                    is_vulnerable = True
            elif scan_type == "sqli":
                if re.search(r"SQL syntax.*MySQL", response.text) or re.search(r"Warning.*mysqli_query", response.text) or re.search(r"supplied argument is not a valid MySQL result", response.text):
                    is_vulnerable = True
            elif scan_type == "lfi":
                if "root:" in response.text or "PATH=" in response.text or "uid=" in response.text or "gid=" in response.text:
                    is_vulnerable = True
            elif scan_type == "xss":
                if payload in response.text:
                    is_vulnerable = True

            if is_vulnerable:
                log_entry = f"{Color.GREEN}[+]{Color.RESET}{Color.ORANGE}[{status_code}]{Color.RESET} {Color.BRIGHT_GREEN}{test_url}{Color.RESET} --> {Color.PURPLE}{payload}{Color.RESET}\n"
            else:
                log_entry = f"{Color.RED}[-]{Color.RESET}{Color.ORANGE}[{status_code}]{Color.RESET}  {Color.BRIGHT_RED}{test_url}{Color.RESET} --> {Color.PURPLE}{payload}{Color.RESET}\n"

            print(log_entry)

        except requests.exceptions.RequestException as e:
            error_message = str(e)
            shortened_message = error_message.split(" (Caused by ")[0]
            print(Fore.RED + Style.BRIGHT + f"[-] Request error: {shortened_message} for {test_url}")

    def scan_urls(urls, payloads, scan_type, num_threads):
        total_urls = len(urls)
        total_payloads = len(payloads)
        total_tests = total_urls * total_payloads
        start_time = time.time()

        try: # Handling Keyboard Interrupt during scanning
            with Progress() as progress:
                task = progress.add_task(Fore.RED + Style.BRIGHT + f"Scanning {scan_type.upper()}...", total=total_tests)

                with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                    futures = []
                    for url in urls:
                        for payload in payloads:
                            future = executor.submit(test_url, url, payload, scan_type)
                            futures.append(future)

                    for future in concurrent.futures.as_completed(futures):
                        try:
                            future.result()
                        except KeyboardInterrupt:
                            print(Fore.RED + "\n[!] Scan interrupted by user.")
                            executor.shutdown(wait=False)  # Attempt to stop threads quickly
                            return # Exit scan
                        except Exception as e:
                            print(Fore.RED + f"[-] Error processing URL: {e}")
                        progress.update(task, advance=1)

            end_time = time.time()
            time_taken = end_time - start_time
            print(Fore.RED + Style.BRIGHT + f"\n[+] Scan completed in {time_taken:.2f} seconds")

        except KeyboardInterrupt: #Handle Keyboard Interrupt during setup of Scan
            print(Fore.RED + "\n[!] Scan interrupted by user.")
            return

    def main():
        try:
            display_menu()
            choice = input(Fore.RED + Style.BRIGHT + "Enter your choice: " + Color.WHITE)

            if choice in ('1', '2', '3', '4'):
                if choice == '1':
                    scan_type = "dir"
                    payload_file = "payloads/dir.txt"
                elif choice == '2':
                    scan_type = "sqli"
                    payload_file = "payloads/sqli.txt"
                elif choice == '3':
                    scan_type = "lfi"
                    payload_file = "payloads/lfi.txt"
                elif choice == '4':
                    scan_type = "xss"
                    payload_file = "payloads/xss.txt"
                else:
                    print(Fore.RED + Style.BRIGHT + "[-] Invalid choice.")
                    return

                payloads = load_payloads_from_file(payload_file)
                if not payloads:
                    print(Fore.RED + f"[-] Failed to load {scan_type.upper()} payloads. Exiting.")
                    return

                url_input = input(Fore.RED + Style.BRIGHT + "Enter URL or file path (one URL per line): " + Color.WHITE).strip()

                if os.path.isfile(url_input):
                    try:
                        with open(url_input, 'r') as f:
                            urls = [line.strip() for line in f if line.strip()]
                    except Exception as e:
                        print(Fore.RED + f"Error reading URL file: {e}")
                        return
                else:
                    urls = [url_input]

                num_threads = int(input(Fore.RED + Style.BRIGHT + "Enter number of threads (default: 10): " + Color.WHITE) or 10)

                scan_urls(urls, payloads, scan_type, num_threads)

            elif choice == '5':
                print(Fore.RED + Style.BRIGHT + "\nExiting...\n")
                sys.exit(0)
            else:
                print(Fore.RED + "[-] Invalid choice. Please select a valid option.")

        except KeyboardInterrupt:
            print(Fore.RED + "\n[!] Exiting...\n") # Handles Ctrl+C during menu input
            sys.exit(0) # Exit cleanly

    if __name__ == "__main__":
        #Register signal handler
        signal.signal(signal.SIGINT, signal.default_int_handler)
        main()

except ImportError as e:
    print(f"Import error: {e}. Please install the missing module.")
    print("You can try: pip install -r requirements.txt")
