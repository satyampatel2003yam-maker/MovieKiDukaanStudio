from tkinter import filedialog
import customtkinter as ctk
import subprocess
import os


class Dashboard(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.pack(fill="both", expand=True)

        self.movie_path = ""
        self.movie_folder = ""
        self.output_folder = ""

        # ===========================
        # Title
        # ===========================
        title = ctk.CTkLabel(
            self,
            text="🎬 Movie Ki Dukaan Studio",
            font=("Segoe UI", 30, "bold")
        )
        title.pack(pady=20)

        # ===========================
        # Add Movie
        # ===========================
        ctk.CTkButton(
            self,
            text="📂 Add Movies",
            width=250,
            command=self.add_movie
        ).pack(pady=10)

        # ===========================
        # Add Folder
        # ===========================
        ctk.CTkButton(
            self,
            text="📁 Add Folder",
            width=250,
            command=self.add_folder
        ).pack(pady=10)

        # ===========================
        # Output Folder
        # ===========================
        ctk.CTkButton(
            self,
            text="📤 Output Folder",
            width=250,
            command=self.select_output_folder
        ).pack(pady=10)

        # ===========================
        # Generate Clips
        # ===========================
        ctk.CTkButton(
            self,
            text="🚀 Generate Clips",
            width=250,
            fg_color="green",
            hover_color="darkgreen",
            command=self.generate_clips
        ).pack(pady=10)

        # ===========================
        # Progress
        # ===========================
        self.progress = ctk.CTkProgressBar(
            self,
            width=700
        )

        self.progress.pack(pady=25)
        self.progress.set(0)

        # ===========================
        # Status
        # ===========================
        self.status = ctk.CTkLabel(
            self,
            text="Status : Ready"
        )

        self.status.pack()

    # ==========================================================
    # Add Single Movie
    # ==========================================================

    def add_movie(self):

        movie = filedialog.askopenfilename(

            title="Select Movie",

            filetypes=[
                ("Video Files", "*.mp4 *.mkv *.avi *.mov")
            ]
        )

        if movie:

            self.movie_path = movie

            self.status.configure(
                text="✅ Movie Ready For Processing"
            )

            print(movie)

    # ==========================================================
    # Add Folder
    # ==========================================================

    def add_folder(self):

        folder = filedialog.askdirectory(
            title="Select Movie Folder"
        )

        if folder:

            self.movie_folder = folder

            self.status.configure(
                text="📁 Movie Folder Selected"
            )

            print(folder)

    # ==========================================================
    # Output Folder
    # ==========================================================

    def select_output_folder(self):

        folder = filedialog.askdirectory(
            title="Select Output Folder"
        )

        if folder:

            self.output_folder = folder

            self.status.configure(
                text="📤 Output Folder Selected"
            )

            print(folder)

    # ==========================================================
    # Generate Clips
    # ==========================================================

    def generate_clips(self):

        if self.movie_path == "":
            self.status.configure(
                text="❌ Please select a movie first."
            )
            return

        if self.output_folder == "":
            self.status.configure(
                text="❌ Please select output folder."
            )
            return

        self.progress.set(0.10)
        self.status.configure(
            text="🔄 Loading FFmpeg..."
        )

        ffmpeg = os.path.join(
            os.getcwd(),
            "ffmpeg",
            "bin",
            "ffmpeg.exe"
        )

        if not os.path.exists(ffmpeg):

            self.status.configure(
                text="❌ FFmpeg not found."
            )

            return

        output_pattern = os.path.join(
            self.output_folder,
            "clip_%03d.mp4"
        )

        command = [

            ffmpeg,

            "-i",
            self.movie_path,

            "-c",
            "copy",

            "-map",
            "0",

            "-f",
            "segment",

            "-segment_time",
            "30",

            output_pattern

        ]

        try:

            self.progress.set(0.40)

            self.status.configure(
                text="🎬 Generating Clips..."
            )

            subprocess.run(
                command,
                check=True
            )

            self.progress.set(1)

            self.status.configure(
                text="✅ Clips Generated Successfully!"
            )

        except Exception as e:

            self.status.configure(
                text=f"❌ {e}"
            )