import tkinter as tk
from tkinter import messagebox, scrolledtext
from threading import Thread
from crawling import WebCrawler  
from urllib.parse import urlparse
from datetime import datetime
import sys
import io

class CrawlerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title(" Advanced Web Crawler GUI")
        self.master.geometry("900x720")
        self.master.configure(bg="#2c3e50")

        title = tk.Label(master, text="Advanced Web Crawler", font=("Helvetica", 20, "bold"), fg="white", bg="#2c3e50")
        title.pack(pady=15)

        tk.Label(master, text="Enter Target URL (http/https):", fg="white", bg="#2c3e50", font=("Helvetica", 12)).pack(pady=5)
        self.url_entry = tk.Entry(master, width=80, font=("Courier", 11))
        self.url_entry.pack(pady=2)

        tk.Label(master, text="Enter Crawl Depth:", fg="white", bg="#2c3e50", font=("Helvetica", 12)).pack(pady=5)
        self.depth_entry = tk.Entry(master, width=10, font=("Courier", 11))
        self.depth_entry.pack(pady=2)

        self.start_button = tk.Button(master, text="🚀 Start Crawling", command=self.start_crawling, bg="#27ae60", fg="white", font=("Helvetica", 12, "bold"), width=20)
        self.start_button.pack(pady=15)

        tk.Label(master, text="Crawl Output:", fg="white", bg="#2c3e50", font=("Helvetica", 12)).pack(pady=5)
        self.output_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=110, height=30, bg="#ecf0f1", font=("Courier", 10))
        self.output_area.pack(padx=10, pady=10)

    def start_crawling(self):
        url = self.url_entry.get().strip()
        depth_str = self.depth_entry.get().strip()

        if not url.startswith(('http://', 'https://')):
            messagebox.showerror("Invalid URL", "URL must start with http:// or https://")
            return
        try:
            depth = int(depth_str)
            if depth < 1:
                raise ValueError
        except:
            messagebox.showerror("Invalid Depth", "Depth must be a positive integer")
            return

        self.start_button.config(state="disabled")
        self.output_area.delete('1.0', tk.END)
        t = Thread(target=self.run_crawler, args=(url, depth))
        t.start()

    def run_crawler(self, url, depth):
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()

        try:
            crawler = WebCrawler(url, depth)
            crawler.run()
        except Exception as e:
            print(f"[ERROR] {e}")

        sys.stdout = old_stdout
        output_text = redirected_output.getvalue()
        self.output_area.insert(tk.END, output_text)
        self.start_button.config(state="normal")
        messagebox.showinfo("Done", "Crawling completed. Results saved to file.")

if __name__ == '__main__':
    root = tk.Tk()
    app = CrawlerGUI(root)
    root.mainloop()
