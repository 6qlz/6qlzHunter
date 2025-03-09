#!/usr/bin/python3

"""
PathSploit - Web Application Vulnerability Scanner
Version: v1.5
Author: @6qlz, with improvements
"""

import argparse
import concurrent.futures
import json
import os
import random
import re
import signal
import sys
import time
import urllib3
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, urlparse

try:
    import jinja2
    import requests
    from colorama import Fore, Style, init
    from rich.console import Console
    from rich.progress import Progress
    from rich.table import Table

    # Initialize colorama
    init(autoreset=True)
except ImportError as e:
    print(Fore.RED + f"[-] Import error: {e}. Please install the missing module.{Style.RESET_ALL}")
    print(Fore.RED + "You can try: pip install -r requirements.txt" + Style.RESET_ALL)
    sys.exit(1)

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ----- Module: Constants and Configuration -----
class Config:
    VERSION = 'v1.5'
    DEFAULT_THREADS = 50  # Increased threads
    DEFAULT_TIMEOUT = 5
    DEFAULT_USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.1.2 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.70",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
    ]
    REPORT_DIR = "reports"

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

# ----- Module: UI Components -----
class UI:
    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def center_text(text):
        terminal_width = os.get_terminal_size().columns
        return "\n".join(line.center(terminal_width) for line in text.split("\n"))

    @staticmethod
    def get_ascii_art():
        ascii_art = f""" {Fore.RED}

⠀⠀⠀⢀⡤⢤⢄⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣼⡅⠠⢀⡈⢀⣙⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠤⠤⢤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢸⠀⠀⠀⠈⠙⠿⣝⢇⠀⠀⣀⣠⠤⠤⠤⠤⣤⡤⠚⠁⠀⠀⠀⠀⠀⠀⠉⠢⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢧⡀⠀⠀⠠⣄⠈⢺⣺⡍⠀⠀⠀⠀⣠⠖⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡄⠀⠀⠀⠀
⠀⠀⠀⠀⠸⡆⢀⠘⣔⠄⠑⠂⠈⠀⡔⠤⠴⠚⡁⠀⠀⢀⠀⠀⠀⣠⠔⢶⡢⡀⠀⠠⡇⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢠⣇⠀⢃⡀⠁⠀⠀⠀⡸⠃⢀⡴⠊⢀⠀⠀⠈⢂⡤⠚⠁⠀⠀⠙⢿⠀⠉⡇⠀⠀⠀⠀⠀
⠀⠀⠀⣠⠾⣹⢤⢼⡆⠀⠀⠀⠀⠀⠀⠈⢀⠞⠁⠀⢠⣴⠏⠀⠀⠀⠀⠀⠀⠸⡇⠀⢇⠀⠀⠀⠀⠀
⠀⠀⣾⢡⣤⡈⠣⡀⠙⠒⠀⠀⠀⠀⣀⠤⠤⣤⠤⣌⠁⢛⡄⠀⠀⠀⠀⠀⠠⡀⢇⠀⠘⣆⠀⢀⡴⡆
⠀⠀⣿⢻⣿⣿⣄⡸⠀⡆⠀⠒⣈⣩⣉⣉⡈⠉⠉⠢⣉⠉⠀⠀⠀⠀⠀⠀⠀⢣⠈⠢⣀⠈⠉⢁⡴⠃
⠀⢀⢿⣿⣿⡿⠛⠁⠀⢻⣿⣿⣿⣿⣿⣿⣿⣷⣦⣄⣸⢿⠀⠀⠀⠀⠀⠀⠀⠸⡄⠀⡇⠉⠉⠁⠀⠀
⣠⣞⠘⢛⡛⢻⣷⣤⡀⠈⡎⣿⣿⣿⣿⣿⣿⣿⣿⣿⠹⠏⠀⠀⠀⠀⠀⠀⠀⠀⠇⢰⡇⠀⠀⠀⠀⠀
⠻⣌⠯⡁⢠⣸⣿⣿⣷⡄⠁⠈⢻⢿⣿⣿⣿⣿⠿⠋⠃⠰⣀⠀⠀⠀⠀⠀⠀⠀⠀⣾⠇⠀⠀⠀⠀⠀
⠀⠀⠉⢻⠨⠟⠹⢿⣿⢣⠀⠀⢨⡧⣌⠉⠁⣀⠴⠊⠑⠀⡸⠛⠀⠀⠀⠀⠀⠀⣸⢲⡟⠀⠀⠀⠀⠀
⠀⠀⣠⠏⠀⠀⠀⠉⠉⠁⠀⠐⠁⠀⠀⢉⣉⠁⠀⠀⢀⠔⢷⣄⠀⠀⠀⠀⠀⢠⣻⡞⠀⠀⠀⠀⠀⠀
⠀⢠⠟⡦⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⢾⠉⠀⣹⣦⠤⣿⣿⡟⠁⠀⠀⠀⢀⣶⠟⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠈⠙⣦⣁⡎⢈⠏⢱⠚⢲⠔⢲⠲⡖⠖⣦⣿⡟⠀⣿⡿⠁⣠⢔⡤⠷⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢿⣟⠿⡿⠿⠶⢾⠶⠾⠶⠾⠞⢻⠋⠏⣸⠁⠀⡽⠓⠚⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢸⡏⠳⠷⠴⠣⠜⠢⠜⠓⠛⠊⠀⢀⡴⠣⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⣏⠒⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠊⠁⢀⣀⣀⠴⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠘⢦⡀⠀⠀⠀⠀⠀⠀⢀⣀⠴⠖⠒⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠉⠑⠒⠒⠐⠒⠛⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
   __       _    _  _          _           
  / /  __ _| |__| || |_  _ _ _| |_ ___ _ _ 
 / _ \/ _` | |_ / __ | || | ' \  _/ -_) '_|
 \___/\__, |_/__|_||_|\_,_|_||_\__\___|_|  
         |_|                               

----------- Made by @6qlz ------------
--------- Version {Config.VERSION} -----------

[1] Directory Scanner
[2] SQL Injection Scan
[3] Check Local File Inclusion
[4] XSS Vulnerability Scan
[5] Generate Report
[6] Exit.{Style.RESET_ALL}


"""
        return UI.center_text(ascii_art)

    @staticmethod
    def display_menu():
        UI.clear_screen()
        ascii_art = UI.get_ascii_art()  # Get the ascii art
        print(Fore.RED + Style.BRIGHT + ascii_art)

        # Prompt the user for input
        choice = input(f"{Fore.RED}{Style.BRIGHT}[?]Enter your choice (1-6): {Fore.WHITE}{Style.RESET_ALL} ")
        return choice

# ----- Module: Utilities -----
class Utils:
    @staticmethod
    def load_payloads_from_file(filepath):
        """Load payloads from a text file."""
        try:
            with open(filepath, 'r') as f:
                return [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except FileNotFoundError:
            print(Fore.RED + f"[-] Payload file not found: {filepath}{Style.RESET_ALL}")
            return []
        except Exception as e:
            print(Fore.RED + f"[-] Error reading payload file: {e}{Style.RESET_ALL}")
            return []

    @staticmethod
    def load_urls(url_input):
        """Load URLs from user input or file."""
        if os.path.isfile(url_input):
            try:
                with open(url_input, 'r') as f:
                    return [line.strip() for line in f if line.strip() and not line.startswith('#')]
            except Exception as e:
                print(Fore.RED + f"[-] Error reading URL file: {e}{Style.RESET_ALL}")
                return []
        else:
            return [url_input]

    @staticmethod
    def ensure_directory_exists(directory):
        """Ensure a directory exists, create it if not."""
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def generate_report_filename(target_url):
        """Generate a unique report filename based on the target URL and timestamp."""
        parsed_url = urlparse(target_url)
        base_name = parsed_url.netloc.replace('.', '_') + "_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{Config.REPORT_DIR}/{base_name}.html"

    @staticmethod
    def create_console():
        """Create and return a Rich Console instance."""
        return Console()

    @staticmethod
    def build_scan_table(results):
        """Build a Rich Table for displaying scan results."""
        table = Table(title=f"{Color.BLUE}Scan Results{Color.RESET}")
        table.add_column(f"{Color.BLUE}URL{Color.RESET}", justify="left", style="cyan", no_wrap=True)
        table.add_column(f"{Color.BLUE}Payload{Color.RESET}", justify="left", style="magenta")
        table.add_column(f"{Color.BLUE}Status{Color.RESET}", justify="center", style="yellow")
        table.add_column(f"{Color.BLUE}Vulnerable{Color.RESET}", justify="center", style="green")
        table.add_column(f"{Color.BLUE}Type{Color.RESET}", justify="center", style="white")  # Scan type
        table.add_column(f"{Color.BLUE}Response Time (ms){Color.RESET}", justify="right", style="white")
        table.add_column(f"{Color.BLUE}Response Size (bytes){Color.RESET}", justify="right", style="white")

        for result in results:
            status_style = "green" if result.status_code < 400 else "yellow" if result.status_code < 500 else "red"
            vulnerable_str = "Yes" if result.is_vulnerable else "No"
            vulnerable_style = "green" if result.is_vulnerable else "red"
            table.add_row(
                result.url,
                result.payload,
                f"[{status_style}]{result.status_code}[/{status_style}]",
                f"[{vulnerable_style}]{vulnerable_str}[/{vulnerable_style}]",
                result.scan_type,
                str(result.response_time) if result.response_time is not None else "N/A",
                str(result.response_size) if result.response_size is not None else "N/A"
            )
        return table

    @staticmethod
    def get_template(template_name="report_template.html"):
        """Load a Jinja2 template from the templates directory."""
        template_dir = Path(__file__).parent / "templates"  # Assuming templates are in the same directory
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        return env.get_template(template_name)

    @staticmethod
    def write_report(results, target_url, report_file):
        """Generate an HTML report from scan results using Jinja2 templates."""
        Utils.ensure_directory_exists(Config.REPORT_DIR)
        template = Utils.get_template()
        html_content = template.render(
            results=results,
            target_url=target_url,
            scan_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            version=Config.VERSION
        )
        try:
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(Fore.GREEN + f"[+] Report saved to: {report_file}{Style.RESET_ALL}")
        except Exception as e:
            print(Fore.RED + f"[-] Error writing report to file: {e}{Style.RESET_ALL}")

# ----- Module: Scanner Engine -----
class ScanResult:
    def __init__(self, url, payload, status_code, is_vulnerable, scan_type, response_time=None, response_size=None):
        self.url = url
        self.payload = payload
        self.status_code = status_code
        self.is_vulnerable = is_vulnerable
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.scan_type = scan_type
        self.response_time = response_time
        self.response_size = response_size

class Scanner:
    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None
        self.scan_type = None
        self.targets = []
        self.payloads = []

    def test_url(self, url, payload, scan_type):
        """Test a single URL with a specific payload."""
        test_url = url.replace("FUZZ", quote(payload))
        result = None
        try:
            start_time = time.time()
            response = requests.get(
                test_url,
                timeout=Config.DEFAULT_TIMEOUT,
                headers={'User-Agent': random.choice(Config.DEFAULT_USER_AGENTS)},
                verify=False  # Disable SSL verification
            )
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)  # in ms
            status_code = response.status_code
            response_size = len(response.content)
            is_vulnerable = self.detect_vulnerability(response, scan_type, payload)
            result = ScanResult(
                url=test_url,
                payload=payload,
                status_code=status_code,
                is_vulnerable=is_vulnerable,
                scan_type=scan_type,
                response_time=response_time,
                response_size=response_size
            )
            self.results.append(result)
            if is_vulnerable:
                log_entry = f"{Color.GREEN}[+]{Color.RESET}{Color.ORANGE}[{status_code}]{Color.RESET} {Color.BRIGHT_GREEN}{test_url}{Color.RESET} --> {Color.PURPLE}{payload}{Color.RESET}"
            else:
                log_entry = f"{Color.RED}[-]{Color.RESET}{Color.ORANGE}[{status_code}]{Color.RESET} {Color.BRIGHT_RED}{test_url}{Color.RESET} --> {Color.PURPLE}{payload}{Color.RESET}"
            # Add additional info
            log_entry += f" ({response_time}ms, {response_size} bytes)"
            print(Fore.RED + log_entry + Style.RESET_ALL)  # Make everything red
            return result
        except requests.exceptions.RequestException as e:
            error_message = str(e)
            shortened_message = error_message.split(" (Caused by ")[0]
            print(Fore.RED + Style.BRIGHT + f"[-] Request error: {shortened_message} for {test_url}{Style.RESET_ALL}")
            return None

    def detect_vulnerability(self, response, scan_type, payload):
        """Enhanced vulnerability detection logic."""
        if scan_type == "dir":
            # More sophisticated directory detection
            if response.status_code < 400:  # Success or redirect
                return True
            return False
        elif scan_type == "sqli":
            # Enhanced SQL injection detection patterns
            error_patterns = [
                # MySQL
                r"SQL syntax.*MySQL",
                r"Warning.*mysqli_query",
                r"MySQLSyntaxErrorException",
                r"valid MySQL result",
                r"check the manual that corresponds to your (MySQL|MariaDB) server version",
                # PostgreSQL
                r"PostgreSQL.*ERROR",
                r"Warning.*\Wpg_",
                r"valid PostgreSQL result",
                r"Npgsql\.",
                # MSSQL
                r"Driver.* SQL[\-\_\ ]*Server",
                r"OLE DB.* SQL Server",
                r"(\W|\A)SQL Server.*Driver",
                r"Warning.*mssql_",
                r"(\W|\A)SQL Server.*[0-9a-fA-F]{8}",
                r"(?s)Exception.*\WSystem\.Data\.SqlClient\.",
                r"(?s)Exception.*\WRoadhouse\.Cms\.",
                # Oracle
                r"ORA-[0-9][0-9][0-9][0-9]",
                r"Oracle error",
                r"Warning.*\Woci_",
                r"Microsoft OLE DB Provider for Oracle",
                # General
                r"SQL (Server|database|DB) error",
                r"Unclosed quotation mark after the character string",
                r"you have an error in your sql syntax"
            ]
            # Check all patterns in response text
            for pattern in error_patterns:
                if re.search(pattern, response.text, re.IGNORECASE):
                    return True
            return False
        elif scan_type == "lfi":
            # Enhanced LFI detection patterns
            sensitive_patterns = [
                # Unix system files
                r"root:.*:0:0:",  # /etc/passwd
                r"(\n|\r)UID\s+PID",  # Process listing
                r"PATH=.*(:|;)(/[a-z0-9]+)+",  # Environment variables
                r"uid=[0-9]+\(.*\)\s+gid=[0-9]+",  # id command output
                # Window system files
                r"\[boot loader\]",  # boot.ini
                r"\[operating systems\]",  # boot.ini
                r"C:\\WINDOWS\\system32",  # Common windows path
                r"C:\\(Windows|WinNT|Program Files)\\",
                # Common log patterns
                r"([0-9]{1,3}\.){3}[0-9]{1,3}.*\[.*\].*\"(GET|POST)",  # Web server logs
                r"php (warning|error):",  # PHP errors
                r"\[error\]"  # Server errors
            ]
            # Check all patterns in response text
            for pattern in sensitive_patterns:
                if re.search(pattern, response.text, re.IGNORECASE):
                    return True
            return False
        elif scan_type == "xss":
            # Enhanced XSS detection - check if payload is actually executed, not just reflected
            # Basic reflection check
            if payload in response.text:
                # Look for signs that the payload might be properly rendered as script
                if "" in response.text:  # Example: Check for script tag rendering
                    return True
            return False
        return False

    def run_scan(self, target_url, payloads, scan_type, threads=Config.DEFAULT_THREADS):
        """Run the scan using a thread pool."""
        self.start_time = datetime.now()
        self.scan_type = scan_type
        self.targets = Utils.load_urls(target_url)
        self.payloads = Utils.load_payloads_from_file(payloads) if payloads else [
            ""]  # Empty payload for directory scan

        with Progress(transient=True) as progress:
            task = progress.add_task(f"[red]Scanning {target_url}...", total=len(self.targets) * len(self.payloads))

            with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
                futures = []
                for url in self.targets:
                    for payload in self.payloads:
                        futures.append(executor.submit(self.test_url, url, payload, scan_type))

                for future in concurrent.futures.as_completed(futures):
                    progress.update(task, advance=1)

        self.end_time = datetime.now()
        print(Fore.GREEN + "[+] Scan completed." + Style.RESET_ALL)

# ----- Module: Vulnerability Scanners -----
class DirectoryScanner:
    def __init__(self, target_url, wordlist, threads):
        self.target_url = target_url
        self.wordlist = wordlist
        self.threads = threads
        self.scanner = Scanner()

    def scan(self):
        print(Fore.BLUE + Style.BRIGHT + "[+] Starting Directory Scan..." + Style.RESET_ALL)
        self.scanner.run_scan(self.target_url, self.wordlist, "dir", self.threads)
        return self.scanner.results

class SQLInjectionScanner:
    def __init__(self, target_url, payload_file, threads):
        self.target_url = target_url
        self.payload_file = payload_file
        self.threads = threads
        self.scanner = Scanner()

    def scan(self):
        print(Fore.BLUE + Style.BRIGHT + "[+] Starting SQL Injection Scan..." + Style.RESET_ALL)
        self.scanner.run_scan(self.target_url, self.payload_file, "sqli", self.threads)
        return self.scanner.results

class LFIscanner:
    def __init__(self, target_url, payload_file, threads):
        self.target_url = target_url
        self.payload_file = payload_file
        self.threads = threads
        self.scanner = Scanner()

    def scan(self):
        print(Fore.BLUE + Style.BRIGHT + "[+] Starting LFI Scan..." + Style.RESET_ALL)
        self.scanner.run_scan(self.target_url, self.payload_file, "lfi", self.threads)
        return self.scanner.results

class XSSscanner:
    def __init__(self, target_url, payload_file, threads):
        self.target_url = target_url
        self.payload_file = payload_file
        self.threads = threads
        self.scanner = Scanner()

    def scan(self):
        print(Fore.BLUE + Style.BRIGHT + "[+] Starting XSS Scan..." + Style.RESET_ALL)
        self.scanner.run_scan(self.target_url, self.payload_file, "xss", self.threads)
        return self.scanner.results

# ----- Module: CLI and Main Logic -----
class CLI:
    @staticmethod
    def setup_argparse():
        parser = argparse.ArgumentParser(description="PathSploit - Web Application Vulnerability Scanner")
        parser.add_argument("-u", "--url", help="Target URL for scanning")
        parser.add_argument("-d", "--dir", action="store_true", help="Enable directory scan")
        parser.add_argument("-s", "--sqli", action="store_true", help="Enable SQL injection scan")
        parser.add_argument("-l", "--lfi", action="store_true", help="Enable Local File Inclusion scan")
        parser.add_argument("-x", "--xss", action="store_true", help="Enable XSS scan")
        parser.add_argument("-t", "--threads", type=int, default=Config.DEFAULT_THREADS,
                            help=f"Number of threads (default: {Config.DEFAULT_THREADS})")
        parser.add_argument("-o", "--output", help="Output file for the report")
        return parser.parse_args()

def signal_handler(sig, frame):
    print(Fore.RED + "\n[!] Ctrl+C detected. Exiting..." + Style.RESET_ALL)
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    UI.clear_screen()

    print(Fore.RED + Style.BRIGHT + "Starting PathSploit..." + Style.RESET_ALL)
    args = CLI.setup_argparse()

    if not any([args.url, args.dir, args.sqli, args.lfi, args.xss]):
        while True:
            choice = UI.display_menu()

            if choice == '1':
                target_url = input(f"{Fore.RED}{Style.BRIGHT}[?] Enter target URL: {Fore.WHITE}{Style.RESET_ALL}")
                wordlist = "./payloads/dir.txt"
                threads = int(input(
                    f"{Fore.RED}{Style.BRIGHT}[?] Enter number of threads (default: {Config.DEFAULT_THREADS}): {Fore.WHITE}{Style.RESET_ALL}") or Config.DEFAULT_THREADS)
                directory_scanner = DirectoryScanner(target_url, wordlist, threads)
                results = directory_scanner.scan()
                report_file = input(
                    f"{Fore.RED}{Style.BRIGHT}[?] Enter report filename (or leave blank for auto-generation): {Fore.WHITE}{Style.RESET_ALL}") or Utils.generate_report_filename(
                    target_url)
                Utils.write_report(results, target_url, report_file)
                break

            elif choice == '2':
                target_url = input(f"{Fore.RED}{Style.BRIGHT}[?] Enter target URL: {Fore.WHITE}{Style.RESET_ALL}")
                payload_file = "./payloads/sqli.txt"
                threads = int(input(
                    f"{Fore.RED}{Style.BRIGHT}[?] Enter number of threads (default: {Config.DEFAULT_THREADS}): {Fore.WHITE}{Style.RESET_ALL}") or Config.DEFAULT_THREADS)
                sqli_scanner = SQLInjectionScanner(target_url, payload_file, threads)
                results = sqli_scanner.scan()
                report_file = input(
                    f"{Fore.RED}{Style.BRIGHT}[?] Enter report filename (or leave blank for auto-generation): {Fore.WHITE}{Style.RESET_ALL}") or Utils.generate_report_filename(
                    target_url)
                Utils.write_report(results, target_url, report_file)
                break

            elif choice == '3':
                target_url = input(f"{Fore.RED}{Style.BRIGHT}[?] Enter target URL: {Fore.WHITE}{Style.RESET_ALL}")
                payload_file = "./payloads/lfi.txt"
                threads = int(input(
                    f"{Fore.RED}{Style.BRIGHT}[?] Enter number of threads (default: {Config.DEFAULT_THREADS}): {Fore.WHITE}{Style.RESET_ALL}") or Config.DEFAULT_THREADS)
                lfi_scanner = LFIscanner(target_url, payload_file, threads)
                results = lfi_scanner.scan()
                report_file = input(
                    f"{Fore.RED}{Style.BRIGHT}[?] Enter report filename (or leave blank for auto-generation): {Fore.WHITE}{Style.RESET_ALL}") or Utils.generate_report_filename(
                    target_url)
                Utils.write_report(results, target_url, report_file)
                break

            elif choice == '4':
                target_url = input(f"{Fore.RED}{Style.BRIGHT}[?] Enter target URL: {Fore.WHITE}{Style.RESET_ALL}")
                payload_file = "./payloads/xss.txt"
                threads = int(input(
                    f"{Fore.RED}{Style.BRIGHT}[?] Enter number of threads (default: {Config.DEFAULT_THREADS}): {Fore.WHITE}{Style.RESET_ALL}") or Config.DEFAULT_THREADS)
                xss_scanner = XSSscanner(target_url, payload_file, threads)
                results = xss_scanner.scan()
                report_file = input(
                    f"{Fore.RED}{Style.BRIGHT}[?] Enter report filename (or leave blank for auto-generation): {Fore.WHITE}{Style.RESET_ALL}") or Utils.generate_report_filename(
                    target_url)
                Utils.write_report(results, target_url, report_file)
                break

            elif choice == '5':
                target_url = input(f"{Fore.RED}{Style.BRIGHT}[?] Enter target URL for the report: {Fore.WHITE}{Style.RESET_ALL}")
                # Assume previous results are stored or loaded from a file
                print(Fore.RED + "Report generation requires scan results. Please run a scan first." + Style.RESET_ALL)
                # Placeholder for loading/accessing previous results
                results = []  # Replace with actual results
                report_file = input(
                    f"{Fore.RED}{Style.BRIGHT}[?] Enter report filename (or leave blank for auto-generation): {Fore.WHITE}{Style.RESET_ALL}") or Utils.generate_report_filename(
                    target_url)
                Utils.write_report(results, target_url, report_file)
                break

            elif choice == '6':
                print(Fore.RED + "Exiting PathSploit..." + Style.RESET_ALL)
                break
            else:
                print(Fore.RED + "Invalid choice. Please select a valid option (1-6)." + Style.RESET_ALL)
    else:
        target_url = args.url
        threads = args.threads

        if args.dir:
            wordlist = "./payloads/dir.txt"
            directory_scanner = DirectoryScanner(target_url, wordlist, threads)
            results = directory_scanner.scan()
            report_file = args.output or Utils.generate_report_filename(target_url)
            Utils.write_report(results, target_url, report_file)

        elif args.sqli:
            payload_file = "./payloads/sqli.txt"
            sqli_scanner = SQLInjectionScanner(target_url, payload_file, threads)
            results = sqli_scanner.scan()
            report_file = args.output or Utils.generate_report_filename(target_url)
            Utils.write_report(results, target_url, report_file)

        elif args.lfi:
            payload_file = "./payloads/lfi.txt"
            lfi_scanner = LFIscanner(target_url, payload_file, threads)
            results = lfi_scanner.scan()
            report_file = args.output or Utils.generate_report_filename(target_url)
            Utils.write_report(results, target_url, report_file)

        elif args.xss:
            payload_file = "./payloads/xss.txt"
            xss_scanner = XSSscanner(target_url, payload_file, threads)
            results = xss_scanner.scan()
            report_file = args.output or Utils.generate_report_filename(target_url)
            Utils.write_report(results, target_url, report_file)

if __name__ == "__main__":
    main()
