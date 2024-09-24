import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import yt_dlp
import threading
from PIL import Image

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class VideoDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.current_theme = "dark"
        ctk.set_appearance_mode(self.current_theme)
        ctk.set_default_color_theme("blue")

        self.title("NM Video Downloader")
        self.geometry("700x750")

        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
        else:
            print("Warning: icon.ico not found. The application will use the default icon.")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(12, weight=1)

        self.create_widgets()

    def create_widgets(self):
        # Title and Theme Toggle
        title_theme_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        title_theme_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=(20, 30), sticky="ew")
        title_theme_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(title_theme_frame, text="NM Video Downloader", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=10, sticky="w")

        # Theme toggle button
        self.theme_button = ctk.CTkButton(title_theme_frame, text="", width=30, height=30, command=self.toggle_theme)
        self.theme_button.grid(row=0, column=1, padx=(0, 10), sticky="e")
        self.update_theme_icon()

        # Input type selection
        self.input_type_label = ctk.CTkLabel(self.main_frame, text="Input Type:", font=ctk.CTkFont(size=14))
        self.input_type_label.grid(row=1, column=0, padx=10, pady=(10, 5), sticky="w")

        self.input_type_var = tk.StringVar(value="videos")
        self.videos_radio = ctk.CTkRadioButton(self.main_frame, text="Video URLs", variable=self.input_type_var, value="videos", command=self.toggle_input_type)
        self.videos_radio.grid(row=1, column=1, padx=10, pady=(10, 5), sticky="w")
        self.account_radio = ctk.CTkRadioButton(self.main_frame, text="Account URL", variable=self.input_type_var, value="account", command=self.toggle_input_type)
        self.account_radio.grid(row=2, column=1, padx=10, pady=(0, 5), sticky="w")

        # Video URL input
        self.url_label = ctk.CTkLabel(self.main_frame, text="Video/Account URLs:", font=ctk.CTkFont(size=14))
        self.url_label.grid(row=3, column=0, padx=10, pady=(10, 5), sticky="w")

        self.url_entry = ctk.CTkTextbox(self.main_frame, width=400, height=100)
        self.url_entry.grid(row=4, column=0, columnspan=2, padx=10, pady=(0, 15), sticky="ew")

        # Output directory selection
        self.output_label = ctk.CTkLabel(self.main_frame, text="Output Directory:", font=ctk.CTkFont(size=14))
        self.output_label.grid(row=5, column=0, padx=10, pady=(10, 5), sticky="w")

        self.output_frame = ctk.CTkFrame(self.main_frame)
        self.output_frame.grid(row=6, column=0, columnspan=2, padx=10, pady=(0, 15), sticky="ew")
        self.output_frame.grid_columnconfigure(0, weight=1)

        self.output_entry = ctk.CTkEntry(self.output_frame, width=300, height=35, placeholder_text="Select output directory")
        self.output_entry.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")

        self.output_button = ctk.CTkButton(self.output_frame, text="Browse", width=100, command=self.select_output_dir)
        self.output_button.grid(row=0, column=1, padx=(0, 0), pady=5)

        # Download type selection
        self.download_type_label = ctk.CTkLabel(self.main_frame, text="Download Type:", font=ctk.CTkFont(size=14))
        self.download_type_label.grid(row=7, column=0, padx=10, pady=(10, 5), sticky="w")

        self.download_type_var = tk.StringVar(value="video")
        self.video_radio = ctk.CTkRadioButton(self.main_frame, text="Video", variable=self.download_type_var, value="video", command=self.toggle_quality_menu)
        self.video_radio.grid(row=7, column=1, padx=10, pady=(10, 5), sticky="w")
        self.audio_radio = ctk.CTkRadioButton(self.main_frame, text="Audio Only", variable=self.download_type_var, value="audio", command=self.toggle_quality_menu)
        self.audio_radio.grid(row=8, column=1, padx=10, pady=(0, 5), sticky="w")

        # Quality selection
        self.quality_label = ctk.CTkLabel(self.main_frame, text="Video Quality:", font=ctk.CTkFont(size=14))
        self.quality_label.grid(row=9, column=0, padx=10, pady=(10, 5), sticky="w")

        self.quality_var = tk.StringVar(value="BEST")
        self.quality_menu = ctk.CTkOptionMenu(self.main_frame, variable=self.quality_var, values=["BEST", "720p", "480p", "360p"], width=150)
        self.quality_menu.grid(row=9, column=1, padx=10, pady=(10, 15), sticky="e")

        # Download button
        self.download_button = ctk.CTkButton(self.main_frame, text="Download", font=ctk.CTkFont(size=16, weight="bold"), height=40, command=self.start_download)
        self.download_button.grid(row=10, column=0, columnspan=2, padx=10, pady=(20, 10), sticky="ew")

        # Status label
        self.status_label = ctk.CTkLabel(self.main_frame, text="", font=ctk.CTkFont(size=14))
        self.status_label.grid(row=11, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="ew")

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        ctk.set_appearance_mode(self.current_theme)
        self.update_theme_icon()

    def update_theme_icon(self):
        if self.current_theme == "dark":
            icon = self.load_icon("sun.png")
        else:
            icon = self.load_icon("moon.png")
        
        if icon:
            self.theme_button.configure(image=icon)

    def load_icon(self, filename):
        icon_path = resource_path(os.path.join("icons", filename))
        if os.path.exists(icon_path):
            return ctk.CTkImage(light_image=Image.open(icon_path),
                                dark_image=Image.open(icon_path),
                                size=(20, 20))
        else:
            print(f"Warning: {filename} not found in the icons folder.")
            return None

    def select_output_dir(self):
        output_dir = filedialog.askdirectory()
        if output_dir:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, output_dir)

    def toggle_quality_menu(self):
        if self.download_type_var.get() == "audio":
            self.quality_menu.configure(state="disabled")
        else:
            self.quality_menu.configure(state="normal")

    def toggle_input_type(self):
        if self.input_type_var.get() == "account":
            self.url_label.configure(text="Account URL:")
        else:
            self.url_label.configure(text="Video URLs (one per line):")

    def start_download(self):
        if not self.validate_inputs():
            return

        self.download_button.configure(state="disabled")
        self.status_label.configure(text="Preparing to download...")

        threading.Thread(target=self.process_download, daemon=True).start()

    def validate_inputs(self):
        if not self.url_entry.get("1.0", tk.END).strip() or not self.output_entry.get():
            messagebox.showerror("Error", "Please enter URL(s) and select output directory.")
            return False
        return True

    def process_download(self):
        try:
            input_type = self.input_type_var.get()
            if input_type == "account":
                account_url = self.url_entry.get("1.0", tk.END).strip()
                video_urls = self.extract_video_urls(account_url)
            else:
                video_urls = self.url_entry.get("1.0", tk.END).strip().split("\n")

            self.download_videos(video_urls)
        except Exception as e:
            self.update_ui(f"Error: {str(e)}", False)

    def extract_video_urls(self, account_url):
        self.update_status("Extracting video URLs from account...")
        ydl_opts = {
            'extract_flat': True,
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(account_url, download=False)
            if 'entries' in result:
                return [entry['url'] for entry in result['entries']]
            else:
                raise Exception("No videos found in the account.")

    def download_videos(self, video_urls):
        output_path = self.output_entry.get()
        download_type = self.download_type_var.get()
        quality = self.quality_var.get()

        outtmpl = os.path.join(output_path, '%(title)s.%(ext)s')

        ydl_opts = {
            'outtmpl': outtmpl,
            'quiet': True,
            'no_warnings': True,
        }

        if download_type == "audio":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            ydl_opts['format'] = f'{quality}/best' if quality != 'BEST' else 'bestvideo+bestaudio/best'

        total_videos = len(video_urls)
        for index, video_url in enumerate(video_urls, start=1):
            self.update_status(f"Downloading video {index}/{total_videos}...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

        self.update_ui("All downloads completed successfully!", True)

    def update_status(self, message):
        self.after(0, self.status_label.configure, {"text": message})

    def update_ui(self, message, success):
        self.status_label.configure(text=message)
        self.download_button.configure(state="normal")

if __name__ == "__main__":
    app = VideoDownloaderApp()
    app.mainloop()