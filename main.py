import os
import sys
import customtkinter as ctk

from ui.dashboard import Dashboard


def resource_path(relative_path: str):
    """
    Returns absolute path for development and PyInstaller EXE.
    """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def create_directories():

    folders = [
        "output",
        "output/clips",
        "output/vertical",
        "output/subtitles",
        "temp",
        "logs",
        "database"
    ]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)


def main():

    # Make project folder current working directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    create_directories()

    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()

    app.title("MovieKiDukaan Studio V2")
    app.geometry("1500x900")
    app.minsize(1200, 750)

    Dashboard(app)

    app.mainloop()


if __name__ == "__main__":
    main()