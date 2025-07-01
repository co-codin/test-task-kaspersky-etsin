from proxyscrape import create_collector, get_collector

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
    def __init__(self, verbose=False):
        self.verbose = verbose
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