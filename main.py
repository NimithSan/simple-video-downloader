import os
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import yt_dlp
import threading

class VideoDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Set the theme and color
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Universal Video Downloader")
        self.geometry("700x550")  # Increased height to accommodate new elements

        # Set the icon
        if os.path.exists("icon.ico"):
            self.iconbitmap("icon.ico")
        else:
            print("Warning: icon.ico not found. The application will use the default icon.")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(9, weight=1)  # Increased to accommodate new elements

        self.create_widgets()

    def create_widgets(self):
        # Title
        self.title_label = ctk.CTkLabel(self.main_frame, text="Universal Video Downloader", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(20, 30), sticky="ew")

        # Video URL input
        self.url_label = ctk.CTkLabel(self.main_frame, text="Video URL:", font=ctk.CTkFont(size=14))
        self.url_label.grid(row=1, column=0, padx=10, pady=(10, 5), sticky="w")

        self.url_entry = ctk.CTkEntry(self.main_frame, width=400, height=35, placeholder_text="Enter video URL here")
        self.url_entry.grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 15), sticky="ew")

        # Output directory selection
        self.output_label = ctk.CTkLabel(self.main_frame, text="Output Directory:", font=ctk.CTkFont(size=14))
        self.output_label.grid(row=3, column=0, padx=10, pady=(10, 5), sticky="w")

        self.output_frame = ctk.CTkFrame(self.main_frame)
        self.output_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=(0, 15), sticky="ew")
        self.output_frame.grid_columnconfigure(0, weight=1)

        self.output_entry = ctk.CTkEntry(self.output_frame, width=300, height=35, placeholder_text="Select output directory")
        self.output_entry.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")

        self.output_button = ctk.CTkButton(self.output_frame, text="Browse", width=100, command=self.select_output_dir)
        self.output_button.grid(row=0, column=1, padx=(0, 0), pady=5)

        # Download type selection
        self.download_type_label = ctk.CTkLabel(self.main_frame, text="Download Type:", font=ctk.CTkFont(size=14))
        self.download_type_label.grid(row=5, column=0, padx=10, pady=(10, 5), sticky="w")

        self.download_type_var = tk.StringVar(value="video")
        self.video_radio = ctk.CTkRadioButton(self.main_frame, text="Video", variable=self.download_type_var, value="video", command=self.toggle_quality_menu)
        self.video_radio.grid(row=5, column=1, padx=10, pady=(10, 5), sticky="w")
        self.audio_radio = ctk.CTkRadioButton(self.main_frame, text="Audio Only", variable=self.download_type_var, value="audio", command=self.toggle_quality_menu)
        self.audio_radio.grid(row=6, column=1, padx=10, pady=(0, 5), sticky="w")

        # Quality selection
        self.quality_label = ctk.CTkLabel(self.main_frame, text="Video Quality:", font=ctk.CTkFont(size=14))
        self.quality_label.grid(row=7, column=0, padx=10, pady=(10, 5), sticky="w")

        self.quality_var = tk.StringVar(value="BEST")
        self.quality_menu = ctk.CTkOptionMenu(self.main_frame, variable=self.quality_var, values=["BEST", "720p", "480p", "360p"], width=150)
        self.quality_menu.grid(row=7, column=1, padx=10, pady=(10, 15), sticky="e")

        # Download button
        self.download_button = ctk.CTkButton(self.main_frame, text="Download", font=ctk.CTkFont(size=16, weight="bold"), height=40, command=self.start_download)
        self.download_button.grid(row=8, column=0, columnspan=2, padx=10, pady=(20, 10), sticky="ew")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, height=15)
        self.progress_bar.grid(row=9, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="ew")
        self.progress_bar.set(0)

        # Status label
        self.status_label = ctk.CTkLabel(self.main_frame, text="", font=ctk.CTkFont(size=14))
        self.status_label.grid(row=10, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="ew")

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

    def start_download(self):
        if not self.validate_inputs():
            return

        self.download_button.configure(state="disabled")
        self.progress_bar.set(0)
        self.status_label.configure(text="Preparing to download...")

        threading.Thread(target=self.download_video, daemon=True).start()

    def validate_inputs(self):
        if not self.url_entry.get() or not self.output_entry.get():
            messagebox.showerror("Error", "Please enter video URL and select output directory.")
            return False
        return True

    def download_video(self):
        try:
            video_url = self.url_entry.get()
            output_path = self.output_entry.get()
            download_type = self.download_type_var.get()
            quality = self.quality_var.get()

            ydl_opts = {
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
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

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            self.update_ui("Download completed successfully!", True)
        except Exception as e:
            self.update_ui(f"Error: {str(e)}", False)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes')
            downloaded_bytes = d.get('downloaded_bytes')
            if total_bytes and downloaded_bytes:
                progress = (downloaded_bytes / total_bytes) * 100
                self.update_progress(f"{progress:.1f}%")
            elif 'total_bytes_estimate' in d:
                total_bytes_estimate = d['total_bytes_estimate']
                progress = (downloaded_bytes / total_bytes_estimate) * 100
                self.update_progress(f"{progress:.1f}%")
        elif d['status'] == 'finished':
            self.update_status("Download finished. Processing...")

    def update_progress(self, progress):
        progress_float = float(progress.strip('%')) / 100
        self.after(0, self.progress_bar.set, progress_float)
        self.after(0, self.status_label.configure, {"text": f"Downloading... {progress}"})

    def update_status(self, message):
        self.after(0, self.status_label.configure, {"text": message})

    def update_ui(self, message, success):
        self.status_label.configure(text=message)
        self.download_button.configure(state="normal")
        self.progress_bar.set(1 if success else 0)

if __name__ == "__main__":
    app = VideoDownloaderApp()
    app.mainloop()