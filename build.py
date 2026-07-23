import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.resolve()

DIST_DIR = PROJECT_ROOT / "dist"

BUILD_DIR = PROJECT_ROOT / "build"

RELEASE_DIR = PROJECT_ROOT / "release"

TEMP_DIR = PROJECT_ROOT / "temp"

OUTPUT_DIR = PROJECT_ROOT / "output"

ASSETS_DIR = PROJECT_ROOT / "assets"

FFMPEG_DIR = PROJECT_ROOT / "ffmpeg"

MAIN_FILE = PROJECT_ROOT / "main.py"


# ==========================================================
# PRINT
# ==========================================================

def title(message):

    print("\n" + "=" * 60)

    print(message)

    print("=" * 60)


# ==========================================================
# CHECK FILE
# ==========================================================

def require(path):

    if not path.exists():

        raise FileNotFoundError(path)


# ==========================================================
# CLEAN OLD BUILD
# ==========================================================

def clean():

    title("Cleaning old build...")

    for folder in [

        DIST_DIR,

        BUILD_DIR,

        RELEASE_DIR

    ]:

        if folder.exists():

            shutil.rmtree(folder)

            print(
                f"Removed {folder.name}"
            )

    BUILD_DIR.mkdir(
        exist_ok=True
    )

    RELEASE_DIR.mkdir(
        exist_ok=True
    )


# ==========================================================
# VERIFY PROJECT
# ==========================================================

def verify():

    title("Checking project...")

    require(MAIN_FILE)

    require(FFMPEG_DIR)

    require(ASSETS_DIR)

    print("Project verified.")
    # ==========================================================
# PYINSTALLER COMMAND
# ==========================================================

def build_exe():

    title("Building EXE...")

    command = [

        sys.executable,

        "-m",

        "PyInstaller",

        "--noconfirm",

        "--clean",

        "--windowed",

        "--name",

        "MovieKiDukaan Studio V2",

        "--icon",

        str(
            ASSETS_DIR / "icon.ico"
        ),

        "--add-data",

        f"{ASSETS_DIR};assets",

        "--add-data",

        f"{FFMPEG_DIR};ffmpeg",

        "--collect-all",

        "customtkinter",

        "--hidden-import",

        "whisper",

        "--hidden-import",

        "torch",

        "--hidden-import",

        "cv2",

        "--hidden-import",

        "numpy",

        str(MAIN_FILE)

    ]

    subprocess.run(
        command,
        check=True
    )

    print("EXE Build Finished")


# ==========================================================
# COPY RELEASE FILES
# ==========================================================

def prepare_release():

    title("Preparing Release...")

    exe_dir = DIST_DIR / "MovieKiDukaan Studio V2"

    if not exe_dir.exists():

        raise FileNotFoundError(
            exe_dir
        )

    shutil.copytree(

        exe_dir,

        RELEASE_DIR / "MovieKiDukaan Studio V2",

        dirs_exist_ok=True

    )

    print("Release folder created.")
    import time


# ==========================================================
# BUILD PIPELINE
# ==========================================================

def main():

    start_time = time.time()

    try:

        title("MovieKiDukaan Studio V2 Build")

        verify()

        clean()

        build_exe()

        prepare_release()

        elapsed = round(
            time.time() - start_time,
            2
        )

        title("BUILD SUCCESSFUL")

        print(
            f"Build completed in {elapsed} seconds."
        )

        print(
            f"Release Folder : {RELEASE_DIR}"
        )

    except subprocess.CalledProcessError as e:

        title("BUILD FAILED")

        print("PyInstaller returned an error.")

        print(e)

        sys.exit(1)

    except Exception as e:

        title("BUILD FAILED")

        print(e)

        sys.exit(1)


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    main()