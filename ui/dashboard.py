import customtkinter as ctk


class Dashboard(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.pack(fill="both", expand=True)

        title = ctk.CTkLabel(
            self,
            text="🎬 Movie Ki Dukaan Studio",
            font=("Segoe UI", 30, "bold")
        )
        title.pack(pady=20)

        ctk.CTkButton(
            self,
            text="📂 Add Movies",
            width=250
        ).pack(pady=10)

        ctk.CTkButton(
            self,
            text="📁 Add Folder",
            width=250
        ).pack(pady=10)

        ctk.CTkButton(
            self,
            text="📤 Output Folder",
            width=250
        ).pack(pady=10)

        self.progress = ctk.CTkProgressBar(self, width=500)
        self.progress.pack(pady=30)
        self.progress.set(0)

        self.status = ctk.CTkLabel(
            self,
            text="Status : Ready"
        )
        self.status.pack()
        