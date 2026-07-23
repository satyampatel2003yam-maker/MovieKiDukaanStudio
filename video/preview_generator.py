import os
import subprocess


def create_preview(movie_path):

    ffmpeg = os.path.join(
        "ffmpeg",
        "bin",
        "ffmpeg.exe"
    )

    preview_folder = "temp"

    os.makedirs(preview_folder, exist_ok=True)

    preview_video = os.path.join(
        preview_folder,
        "preview.mp4"
    )

    command = [

        ffmpeg,

        "-y",

        "-i", movie_path,

        # 480p Preview
        "-vf", "scale=640:-2",

        # 15 FPS
        "-r", "15",

        # Fast Encoding
        "-preset", "ultrafast",

        # Small File Size
        "-crf", "35",

        # H264 Codec
        "-c:v", "libx264",

        # Remove Audio
        "-an",

        preview_video

    ]

    subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )

    return preview_video