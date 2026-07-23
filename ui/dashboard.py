import threading
from pathlib import Path
from tkinter import filedialog, messagebox, StringVar

import customtkinter as ctk

from video.clip_generator import generate_clips


FEATURES = [
    ("GPU Acceleration", "Use your GPU when available to speed up exports."),
    ("Scene Detection", "Detect interesting scenes automatically."),
    ("Smart Clip Selection", "Select the best moments for your clips."),
    ("Vertical Reels", "Create optimized vertical video clips."),
    ("AI Subtitles", "Generate subtitles from speech automatically."),
    ("Parallel Export", "Export clips in parallel for faster output.")
]


class Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("MovieKiDukaan Studio V2")
        self.root.geometry("1500x900")
        self.root.minsize(1200, 750)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.movie_path = StringVar()
        self.output_path = StringVar(value="output")
        self.processing = False

        self.build_sidebar()
        self.build_main()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # Sidebar: internal widgets may use pack()
    def build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self.root, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(25, 10))
        ctk.CTkLabel(header, text="MovieKiDukaan", font=("Segoe UI", 24, "bold")).pack(anchor="w")
        ctk.CTkLabel(header, text="Studio V2", font=("Segoe UI", 15)).pack(anchor="w", pady=(10, 0))

        ctk.CTkFrame(self.sidebar, height=2, fg_color="#3b3b3b").pack(fill="x", padx=20, pady=(20, 20))
        ctk.CTkLabel(self.sidebar, text="Features", font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=20)

        for feature, _ in FEATURES:
            ctk.CTkButton(
                self.sidebar,
                text=feature,
                fg_color="#1f6aa5",
                hover_color="#2f82d2",
                command=lambda f=feature: self.feature_clicked(f),
                anchor="w",
                corner_radius=12,
                height=42,
            ).pack(fill="x", padx=20, pady=6)

        ctk.CTkLabel(
            self.sidebar,
            text="MovieKiDukaan Studio\nVersion 2.0",
            font=("Segoe UI", 12),
            justify="left",
        ).pack(side="bottom", pady=25, padx=20)

    # Main area: use grid() for children of root.main and scrollable_frame
    def build_main(self):
        self.main = ctk.CTkFrame(self.root, corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew")
        # Allow the main area to expand vertically and horizontally
        self.main.grid_rowconfigure(0, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        self.scrollable_frame = ctk.CTkScrollableFrame(self.main, corner_radius=0)
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        # Ensure scrollable content expands and the progress section can grow
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        # give the progress section (row index 3) available extra vertical space
        self.scrollable_frame.grid_rowconfigure(3, weight=1)

        # Fixed bottom toolbar to host persistent action buttons
        self.bottom_toolbar = ctk.CTkFrame(self.main, fg_color="transparent")
        self.bottom_toolbar.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 0))
        self.main.grid_rowconfigure(1, weight=0)
        self.bottom_toolbar.grid_columnconfigure(0, weight=1)

        self.build_header()
        self.build_file_section()
        self.build_settings_section()
        self.build_progress_section()

    def build_header(self):
        self.header = ctk.CTkFrame(self.scrollable_frame, fg_color="#1f1f1f", corner_radius=20)
        self.header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            self.header,
            text="MovieKiDukaan Studio V2",
            font=("Segoe UI", 28, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(
            self.header,
            text="Professional AI Movie Clip Generator",
            font=("Segoe UI", 14),
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 20))

    def build_file_section(self):
        self.file_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=20)
        self.file_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.file_frame.grid_columnconfigure(0, weight=1)
        self.file_frame.grid_columnconfigure(1, weight=0)

        ctk.CTkLabel(
            self.file_frame,
            text="Project Files",
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 10))

        ctk.CTkLabel(self.file_frame, text="Movie File").grid(row=1, column=0, sticky="w", padx=20)
        self.movie_entry = ctk.CTkEntry(self.file_frame, textvariable=self.movie_path, height=40)
        self.movie_entry.grid(row=2, column=0, sticky="ew", padx=20, pady=(5, 10))
        ctk.CTkButton(self.file_frame, text="Browse Movie", command=self.browse_movie, width=150).grid(
            row=2, column=1, sticky="e", padx=20, pady=(5, 10)
        )

        ctk.CTkLabel(self.file_frame, text="Output Folder").grid(row=3, column=0, sticky="w", padx=20, pady=(10, 0))
        self.output_entry = ctk.CTkEntry(self.file_frame, textvariable=self.output_path, height=40)
        self.output_entry.grid(row=4, column=0, columnspan=2, sticky="ew", padx=20, pady=(5, 10))
        ctk.CTkButton(self.file_frame, text="Browse Folder", command=self.browse_output, width=150).grid(
            row=5, column=1, sticky="e", padx=20, pady=(0, 20)
        )

    def build_settings_section(self):
        self.settings_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=20)
        self.settings_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        self.settings_frame.grid_columnconfigure(0, weight=1)
        self.settings_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self.settings_frame,
            text="Clip Settings",
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 10))

        duration_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        duration_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 10))
        duration_frame.grid_columnconfigure(0, weight=1)
        duration_frame.grid_columnconfigure(1, weight=0)
        ctk.CTkLabel(duration_frame, text="Clip Duration").grid(row=0, column=0, sticky="w")
        self.duration_value = ctk.CTkLabel(duration_frame, text="30 sec", width=70)
        self.duration_value.grid(row=0, column=1, sticky="e")

        self.duration_slider = ctk.CTkSlider(self.settings_frame, from_=10, to=120, command=self.duration_changed)
        self.duration_slider.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20)
        self.duration_slider.set(30)

        option_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        option_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20, pady=15)
        option_frame.grid_columnconfigure(0, weight=1)
        option_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(option_frame, text="Number of Clips").grid(row=0, column=0, sticky="w")
        self.clip_count = ctk.CTkOptionMenu(option_frame, values=["5", "10", "15", "20", "25", "30"]) 
        self.clip_count.grid(row=0, column=1, padx=15, sticky="e")
        self.clip_count.set("10")

        ctk.CTkLabel(option_frame, text="Quality").grid(row=1, column=0, sticky="w", pady=15)
        self.quality_menu = ctk.CTkOptionMenu(option_frame, values=["Low", "Medium", "High", "Original"]) 
        self.quality_menu.grid(row=1, column=1, padx=15, pady=15, sticky="e")
        self.quality_menu.set("High")

        ctk.CTkLabel(option_frame, text="Processing").grid(row=2, column=0, sticky="w")
        self.processor_menu = ctk.CTkOptionMenu(option_frame, values=["Auto", "GPU", "CPU"]) 
        self.processor_menu.grid(row=2, column=1, padx=15, pady=(0, 15), sticky="e")
        self.processor_menu.set("Auto")

    def duration_changed(self, value):
        self.duration_value.configure(text=f"{int(value)} sec")

    def build_progress_section(self):
        self.progress_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=20)
        self.progress_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 15), padx=0)
        self.progress_frame.grid_columnconfigure(0, weight=1)
        self.progress_frame.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            self.progress_frame,
            text="Processing Status",
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        self.status_label = ctk.CTkLabel(self.progress_frame, text="Ready", font=("Segoe UI", 14))
        self.status_label.grid(row=1, column=0, sticky="w", padx=20)
        self.progress_percent = ctk.CTkLabel(self.progress_frame, text="0%", font=("Segoe UI", 14, "bold"))
        self.progress_percent.grid(row=1, column=0, sticky="e", padx=20)

        self.progressbar = ctk.CTkProgressBar(self.progress_frame, height=18)
        self.progressbar.grid(row=2, column=0, sticky="ew", padx=20, pady=(8, 20))
        self.progressbar.set(0)

        ctk.CTkLabel(self.progress_frame, text="Live Logs", font=("Segoe UI", 16, "bold")).grid(row=3, column=0, sticky="w", padx=20, pady=(0, 10))
        self.log_box = ctk.CTkTextbox(self.progress_frame, height=220, wrap="word")
        self.log_box.grid(row=4, column=0, sticky="nsew", padx=20, pady=(0, 10))
        self.log_box.insert("end", "MovieKiDukaan Studio V2 Ready...\n")
        self.log_box.insert("end", "Waiting for movie selection...\n")
        self.log_box.configure(state="disabled")

        self.build_action_buttons()

    def build_action_buttons(self):
        # Prefer placing buttons in the fixed bottom toolbar so they remain visible
        parent = getattr(self, "bottom_toolbar", self.progress_frame)
        # If parent is the toolbar, place with padding so it lines up with content
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        if parent is self.progress_frame:
            button_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=(5, 20))
        else:
            button_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(10, 10))
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        self.generate_btn = ctk.CTkButton(button_frame, text="▶ Generate Clips", width=200, height=45, command=self.generate_clicked)
        self.generate_btn.grid(row=0, column=0, sticky="w")
        self.cancel_btn = ctk.CTkButton(
            button_frame,
            text="■ Cancel",
            width=120,
            height=45,
            fg_color="#c62828",
            hover_color="#8e0000",
            command=self.cancel_clicked,
        )
        self.cancel_btn.grid(row=0, column=1, sticky="e")

    def feature_clicked(self, feature_name):
        self.add_log(f"Feature selected: {feature_name}")
        messagebox.showinfo("Feature", f"Feature selected: {feature_name}")

    def browse_movie(self):
        file = filedialog.askopenfilename(title="Select Movie", filetypes=[("Video Files", "*.mp4 *.mkv *.avi *.mov *.webm")])
        if file:
            self.movie_path.set(file)
            self.add_log(f"Movie Selected : {Path(file).name}")

    def browse_output(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_path.set(folder)
            self.add_log(f"Output Folder : {folder}")

    def generate_clicked(self):
        if self.processing:
            return
        movie = self.movie_path.get().strip()
        if movie == "":
            messagebox.showwarning("Movie Required", "Please select a movie first.")
            return
        if not Path(movie).exists():
            messagebox.showerror("Error", "Movie file not found.")
            return

        self.processing = True
        self.generate_btn.configure(state="disabled")
        self.set_progress(0)
        self.set_status("Initializing...")
        self.add_log("Starting AI Engine...")

        worker = threading.Thread(target=self.run_generation, daemon=True)
        worker.start()

    def cancel_clicked(self):
        self.processing = False
        self.generate_btn.configure(state="normal")
        self.set_status("Cancelled")
        self.add_log("Generation Cancelled.")

    def run_generation(self):
        try:
            self.root.after(0, lambda: self.set_status("Processing Movie..."))
            self.root.after(0, lambda: self.add_log("Loading Movie..."))
            generate_clips(
                input_video=self.movie_path.get(),
                output_folder=self.output_path.get(),
                clip_duration=int(self.duration_slider.get()),
                max_clips=int(self.clip_count.get()),
                quality=self.quality_menu.get(),
                processor=self.processor_menu.get(),
                log_callback=self.log,
                progress_callback=self.update_progress,
            )
            self.root.after(0, lambda: self.finish_generation(True))
        except Exception as e:
            self.root.after(0, lambda: self.finish_generation(False, str(e)))

    def finish_generation(self, success, error=None):
        self.processing = False
        self.generate_btn.configure(state="normal")
        if success:
            self.set_progress(100)
            self.set_status("Completed")
            self.add_log("Movie clip generation completed.")
            messagebox.showinfo("Completed", "Movie clips generated successfully.")
        else:
            self.set_status("Failed")
            self.add_log(f"Error : {error}")
            messagebox.showerror("Generation Failed", str(error))

    def set_progress(self, value):
        value = max(0, min(100, value))
        self.progressbar.set(value / 100)
        self.progress_percent.configure(text=f"{int(value)}%")

    def set_status(self, text):
        self.status_label.configure(text=text)

    def add_log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def update_progress(self, progress, status=None):
        self.root.after(0, lambda: self._update_progress(progress, status))

    def _update_progress(self, progress, status):
        progress = max(0, min(progress, 100))
        self.progressbar.set(progress / 100)
        self.progress_percent.configure(text=f"{progress}%")
        if status:
            self.status_label.configure(text=status)

    def log(self, message):
        self.root.after(0, lambda: self.add_log(message))

    def on_close(self):
        if self.processing:
            if not messagebox.askyesno("Exit", "Processing is still running.\nDo you really want to exit?"):
                return
        self.root.destroy()
