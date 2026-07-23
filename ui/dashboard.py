import customtkinter as ctk
from tkinter import filedialog
import threading
import os

from video.clip_generator import generate_clips


class Dashboard:

    def __init__(self, root):

        self.root = root

        self.movie_path = ""
        self.output_path = ""

        self.build_ui()

    def build_ui(self):

        title = ctk.CTkLabel(
            self.root,
            text="🎬 MovieKiDukaan Studio",
            font=("Arial", 28, "bold")
        )
        title.pack(pady=20)

        self.movie_label = ctk.CTkLabel(
            self.root,
            text="No Movie Selected",
            width=700
        )
        self.movie_label.pack(pady=5)

        ctk.CTkButton(
            self.root,
            text="📂 Add Movie",
            command=self.select_movie,
            width=250
        ).pack(pady=10)

        self.output_label = ctk.CTkLabel(
            self.root,
            text="No Output Folder Selected",
            width=700
        )
        self.output_label.pack(pady=5)

        ctk.CTkButton(
            self.root,
            text="📁 Output Folder",
            command=self.select_output,
            width=250
        ).pack(pady=10)

        ctk.CTkButton(
            self.root,
            text="🚀 Generate Clips",
            command=self.start_generation,
            width=300,
            height=45
        ).pack(pady=20)

        self.progress = ctk.CTkProgressBar(self.root, width=700)
        self.progress.pack(pady=10)
        self.progress.set(0)

        self.status = ctk.CTkLabel(
            self.root,
            text="Status : Waiting..."
        )
        self.status.pack()

        self.log_box = ctk.CTkTextbox(
            self.root,
            width=900,
            height=300
        )
        self.log_box.pack(pady=20)

    def log(self, text):

        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")

    def select_movie(self):

        path = filedialog.askopenfilename(
            filetypes=[
                ("Video Files", "*.mp4 *.mkv *.avi *.mov")
            ]
        )

        if path:
            self.movie_path = path
            self.movie_label.configure(
                text=os.path.basename(path)
            )

    def select_output(self):

        path = filedialog.askdirectory()

        if path:
            self.output_path = path
            self.output_label.configure(
                text=path
            )

    def start_generation(self):

        if self.movie_path == "":
            self.log("❌ Please Select Movie")
            return

        if self.output_path == "":
            self.log("❌ Please Select Output Folder")
            return

        threading.Thread(
            target=self.run_generator,
            daemon=True
        ).start()

    def run_generator(self):

        self.progress.set(0)

        self.status.configure(
            text="Creating Preview..."
        )

        self.log("🎥 Creating Preview Video...")

        try:

            generate_clips(
                self.movie_path,
                self.output_path
            )

            self.progress.set(1)

            self.status.configure(
                text="Completed"
            )

            self.log("✅ All Clips Generated Successfully")

        except Exception as e:

            self.log(str(e))

            self.status.configure(
                text="Failed")