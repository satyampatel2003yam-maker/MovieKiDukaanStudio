import customtkinter as ctk
from ui.dashboard import Dashboard

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()

app.title("Movie Ki Dukaan Studio")
app.geometry("1400x800")

Dashboard(app)

app.mainloop()