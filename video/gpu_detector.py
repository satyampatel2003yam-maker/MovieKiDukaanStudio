import subprocess
import os


def get_best_encoder():

    ffmpeg = os.path.join("ffmpeg", "bin", "ffmpeg.exe")

    try:
        result = subprocess.run(
            [ffmpeg, "-hide_banner", "-encoders"],
            capture_output=True,
            text=True
        )

        encoders = result.stdout

        if "h264_nvenc" in encoders:
            return "h264_nvenc"

        elif "h264_qsv" in encoders:
            return "h264_qsv"

        elif "h264_amf" in encoders:
            return "h264_amf"

        else:
            return "libx264"

    except Exception:
        return "libx264"