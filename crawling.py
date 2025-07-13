import warnings
from termcolor import colored
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup, Comment
import sys
from datetime import datetime
import ssl
import certifi
import re

from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)

def print_banner():
    print("-" * 80)
    print(colored(f" Advanced Web Crawler | Started at {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 'cyan', attrs=['bold']))
    print("-" * 80)

def get_user_input():
    try:
        url = input("[+] Enter target URL (with http/https): ").strip()
        if not url.startswith(('http://', 'https://')):
            print(colored("[-] Invalid URL format. Must start with http:// or https://", 'red'))
            sys.exit(1)
        depth = int(input("[+] Enter crawl depth (e.g., 2): ").strip())
        if depth < 1:
            raise ValueError
        return url, depth
    except KeyboardInterrupt:
        print(colored("[-] Operation cancelled by user.", 'yellow'))
        sys.exit(0)
    except Exception:
        print(colored("[-] Depth must be a positive integer.", 'red'))
        sys.exit(1)

class WebCrawler:
    def __init__(self, base_url, max_depth, target_depth=None):
        self.base_url = base_url.strip()
        self.max_depth = max_depth
        self.target_depth = target_depth or max_depth
        self.visited = set()
        parsed = urlparse(self.base_url)
        self.domain = parsed.netloc
        self.links = set()
        self.subdomains = set()
        self.js_files = set()
        self.emails = set()
        self.forms = set()
        self.comments = set()
        self.images = set()
        self.css_files = set()

    def normalize_url(self, url):
        if not url:
            return None
        return url.strip()

    def is_same_domain(self, url):
        return urlparse(url.strip()).netloc == self.domain

    def is_subdomain(self, url):
        netloc = urlparse(url.strip()).netloc
        return netloc != self.domain and netloc.endswith("." + self.domain)

    def extract_links_and_assets(self, soup, base):
        for script in soup.find_all('script', src=True):
            js_url = urljoin(base, script['src']).strip()
            if self.is_same_domain(js_url) or self.is_subdomain(js_url):
                self.js_files.add(js_url)

        for link_tag in soup.find_all('link', href=True):
            if 'stylesheet' in link_tag.get('rel', []):
                css_url = urljoin(base, link_tag['href']).strip()
                if self.is_same_domain(css_url) or self.is_subdomain(css_url):
                    self.css_files.add(css_url)

        for img in soup.find_all('img', src=True):
            img_url = urljoin(base, img['src']).strip()
            if self.is_same_domain(img_url) or self.is_subdomain(img_url):
                self.images.add(img_url)

        for tag in soup.find_all('a', href=True):
            link = urljoin(base, tag['href']).strip()
            if not link.startswith(('http://', 'https://')):
                continue
            if self.is_same_domain(link):
                yield link
            elif self.is_subdomain(link):
                self.subdomains.add(link)

        for form in soup.find_all('form', action=True):
            action_url = urljoin(base, form['action']).strip()
            self.forms.add(action_url)

        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            clean_comment = comment.strip()
            if clean_comment:
                self.comments.add(clean_comment)

        emails_found = re.findall(r'[\w\.-]+@[\w\.-]+', soup.get_text())
        self.emails.update(emails_found)

    def crawl(self, url=None, depth=1):
        url = url.strip()
        if depth > self.max_depth or url in self.visited:
            return
        try:
            response = requests.get(url, timeout=5, allow_redirects=True, verify=certifi.where())
            response.raise_for_status()
        except Exception:
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        self.visited.add(url)

        if depth == self.target_depth:
            print(colored(f"[DEPTH {depth}] Crawling: {url}", 'yellow'))
            self.links.add(url)

        for link in self.extract_links_and_assets(soup, url):
            self.crawl(link, depth + 1)

    def run(self):
        print_banner()
        print(f"[*] Target URL\t\t: {self.base_url}")
        print(f"[*] Max Depth\t\t: {self.max_depth}")
        print(f"[*] Base Domain\t\t: {self.domain}")
        print("-" * 80)
        print(colored("[+] Starting crawl process...", 'green'))

        self.crawl(self.base_url, 1)

        print("-" * 80)
        domain_name = urlparse(self.base_url).netloc.replace("www.", "")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{domain_name}_crawl_{timestamp}.txt"

        output_lines = []

        for label, items in [
            ("Subdomains", self.subdomains),
            ("Links", self.links),
            ("JS Files", self.js_files),
            ("CSS Files", self.css_files),
            ("Images", self.images),
            ("Forms", self.forms),
            ("Emails", self.emails),
            ("Comments", self.comments)
        ]:
            if items:
                line = f"[+] {label}"
                print(colored(line, 'blue'))
                output_lines.append(line)
                for item in sorted(items):
                    line = f"    - {item}"
                    print(line)
                    output_lines.append(line)
                print("")
                output_lines.append("")

        with open(filename, 'w') as f:
            f.write("\n".join(output_lines))

        print("-" * 80)
        print(colored(f"[+] Results saved to {filename}", 'green'))

if __name__ == "__main__":
    url, depth = get_user_input()
    crawler = WebCrawler(url, depth, target_depth=depth)
    crawler.run()
