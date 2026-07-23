"""
MovieKiDukaan Studio V2
FFmpeg Engine

Part 1
- Imports
- FFmpeg Path Detection
- Quality Presets
- Encoder Validation
"""

from pathlib import Path
import subprocess
import shutil
import os

# ==========================================================
# PROJECT ROOT
# ==========================================================

CURRENT_FILE = Path(__file__).resolve()

PROJECT_ROOT = CURRENT_FILE.parent.parent


# ==========================================================
# FFMPEG AUTO DETECTION
# ==========================================================

def find_ffmpeg():

    candidates = [

        PROJECT_ROOT / "ffmpeg" / "bin" / "ffmpeg.exe",

        PROJECT_ROOT / "ffmpeg.exe",

        Path("ffmpeg.exe")

    ]

    for exe in candidates:

        if exe.exists():

            return str(exe)

    system = shutil.which("ffmpeg")

    if system:

        return system

    raise FileNotFoundError(

        "FFmpeg executable not found.\n"
        "Expected:\n"
        f"{PROJECT_ROOT / 'ffmpeg' / 'bin' / 'ffmpeg.exe'}"

    )


def find_ffprobe():

    candidates = [

        PROJECT_ROOT / "ffmpeg" / "bin" / "ffprobe.exe",

        PROJECT_ROOT / "ffprobe.exe",

        Path("ffprobe.exe")

    ]

    for exe in candidates:

        if exe.exists():

            return str(exe)

    system = shutil.which("ffprobe")

    if system:

        return system

    raise FileNotFoundError(

        "FFprobe executable not found."

    )


FFMPEG = find_ffmpeg()

FFPROBE = find_ffprobe()


# ==========================================================
# QUALITY PRESETS
# ==========================================================

QUALITY_PRESETS = {

    "Low": {

        "cpu_crf": 28,

        "nvenc_cq": 30,

        "preset": "fast"

    },

    "Medium": {

        "cpu_crf": 24,

        "nvenc_cq": 26,

        "preset": "medium"

    },

    "High": {

        "cpu_crf": 20,

        "nvenc_cq": 22,

        "preset": "slow"

    },

    "Original": {

        "cpu_crf": 18,

        "nvenc_cq": 18,

        "preset": "p7"

    }

}


# ==========================================================
# SUPPORTED ENCODERS
# ==========================================================

SUPPORTED_ENCODERS = {

    "libx264",

    "h264_nvenc",

    "h264_qsv",

    "h264_amf"

}


# ==========================================================
# VALIDATION
# ==========================================================

def validate_encoder(encoder):

    if encoder not in SUPPORTED_ENCODERS:

        raise ValueError(

            f"Unsupported encoder: {encoder}"

        )

    return encoder


def validate_quality(quality):

    if quality not in QUALITY_PRESETS:

        quality = "High"

    return QUALITY_PRESETS[quality]


# ==========================================================
# SYSTEM INFO
# ==========================================================

def ffmpeg_info():

    return {

        "ffmpeg": FFMPEG,

        "ffprobe": FFPROBE,

        "project_root": str(PROJECT_ROOT),

        "available": os.path.exists(FFMPEG)

    }
# ==========================================================
# VIDEO ENCODER ARGUMENTS
# ==========================================================

def get_video_encoder_args(
    encoder="libx264",
    quality="High"
):

    validate_encoder(encoder)

    preset = validate_quality(quality)

    if encoder == "libx264":

        return [

            "-c:v", "libx264",

            "-preset", preset["preset"],

            "-crf", str(preset["cpu_crf"])

        ]

    elif encoder == "h264_nvenc":

        return [

            "-c:v", "h264_nvenc",

            "-preset", preset["preset"],

            "-cq", str(preset["nvenc_cq"])

        ]

    elif encoder == "h264_qsv":

        return [

            "-c:v", "h264_qsv",

            "-global_quality",

            str(preset["nvenc_cq"])

        ]

    elif encoder == "h264_amf":

        return [

            "-c:v", "h264_amf",

            "-quality",

            "quality"

        ]

    return [

        "-c:v",

        "libx264"

    ]


# ==========================================================
# BUILD CLIP EXPORT COMMAND
# ==========================================================

def build_ffmpeg_command(

    input_file,

    output_file,

    start_time,

    end_time,

    encoder="libx264",

    quality="High",

    copy_audio=False

):

    validate_encoder(encoder)

    input_file = str(Path(input_file).resolve())

    output_file = str(Path(output_file).resolve())

    duration = max(

        0.10,

        float(end_time) - float(start_time)

    )

    command = [

        FFMPEG,

        "-y",

        "-hide_banner",

        "-loglevel",

        "error",

        "-ss",

        str(round(start_time, 3)),

        "-i",

        input_file,

        "-t",

        str(round(duration, 3))

    ]

    command.extend(

        get_video_encoder_args(

            encoder,

            quality

        )

    )

    if copy_audio:

        command.extend([

            "-c:a",

            "copy"

        ])

    else:

        command.extend([

            "-c:a",

            "aac",

            "-b:a",

            "192k"

        ])

    command.extend([

        "-movflags",

        "+faststart",

        "-pix_fmt",

        "yuv420p",

        output_file

    ])

    return command


# ==========================================================
# RUN FFMPEG
# ==========================================================

def run_ffmpeg(command):

    process = subprocess.run(

        command,

        capture_output=True,

        text=True,

        encoding="utf-8",

        errors="ignore"

    )

    return process


# ==========================================================
# GPU FALLBACK
# ==========================================================

def export_with_fallback(

    input_file,

    output_file,

    start_time,

    end_time,

    encoder="h264_nvenc",

    quality="High"

):

    command = build_ffmpeg_command(

        input_file,

        output_file,

        start_time,

        end_time,

        encoder,

        quality,

        copy_audio=False

    )

    result = run_ffmpeg(command)

    if result.returncode == 0:

        return result

    cpu_command = build_ffmpeg_command(

        input_file,

        output_file,

        start_time,

        end_time,

        "libx264",

        quality,

        copy_audio=False

    )

    return run_ffmpeg(cpu_command)
# ==========================================================
# BUILD PREVIEW COMMAND
# ==========================================================

def build_preview_command(

    input_file,

    output_file

):

    input_file = str(Path(input_file).resolve())

    output_file = str(Path(output_file).resolve())

    return [

        FFMPEG,

        "-y",

        "-hide_banner",

        "-loglevel",

        "error",

        "-i",

        input_file,

        "-vf",

        "scale=640:-2",

        "-an",

        "-c:v",

        "libx264",

        "-preset",

        "ultrafast",

        "-crf",

        "35",

        "-pix_fmt",

        "yuv420p",

        "-movflags",

        "+faststart",

        output_file

    ]


# ==========================================================
# BUILD VERTICAL COMMAND
# ==========================================================

def build_vertical_command(

    input_file,

    output_file,

    encoder="libx264",

    quality="High"

):

    input_file = str(Path(input_file).resolve())

    output_file = str(Path(output_file).resolve())

    command = [

        FFMPEG,

        "-y",

        "-hide_banner",

        "-loglevel",

        "error",

        "-i",

        input_file,

        "-vf",

        (

            "scale=1080:1920:"

            "force_original_aspect_ratio=increase,"

            "crop=1080:1920"

        )

    ]

    command.extend(

        get_video_encoder_args(

            encoder,

            quality

        )

    )

    command.extend([

        "-c:a",

        "aac",

        "-b:a",

        "192k",

        "-pix_fmt",

        "yuv420p",

        "-movflags",

        "+faststart",

        output_file

    ])

    return command


# ==========================================================
# BUILD SUBTITLE COMMAND
# ==========================================================

def build_subtitle_command(

    input_file,

    subtitle_file,

    output_file,

    encoder="libx264",

    quality="High"

):

    input_file = str(Path(input_file).resolve())

    subtitle_file = str(Path(subtitle_file).resolve())

    output_file = str(Path(output_file).resolve())

    command = [

        FFMPEG,

        "-y",

        "-hide_banner",

        "-loglevel",

        "error",

        "-i",

        input_file,

        "-vf",

        f"subtitles={subtitle_file}"

    ]

    command.extend(

        get_video_encoder_args(

            encoder,

            quality

        )

    )

    command.extend([

        "-c:a",

        "aac",

        "-b:a",

        "192k",

        "-pix_fmt",

        "yuv420p",

        "-movflags",

        "+faststart",

        output_file

    ])

    return command
# ==========================================================
# VIDEO INFORMATION
# ==========================================================

def get_video_duration(video_file):

    command = [

        FFPROBE,

        "-v",

        "error",

        "-show_entries",

        "format=duration",

        "-of",

        "default=noprint_wrappers=1:nokey=1",

        str(Path(video_file).resolve())

    ]

    result = subprocess.run(

        command,

        capture_output=True,

        text=True,

        encoding="utf-8",

        errors="ignore"

    )

    if result.returncode != 0:

        return 0.0

    try:

        return float(result.stdout.strip())

    except Exception:

        return 0.0


# ==========================================================
# VIDEO RESOLUTION
# ==========================================================

def get_video_resolution(video_file):

    command = [

        FFPROBE,

        "-v",

        "error",

        "-select_streams",

        "v:0",

        "-show_entries",

        "stream=width,height",

        "-of",

        "csv=p=0:s=x",

        str(Path(video_file).resolve())

    ]

    result = subprocess.run(

        command,

        capture_output=True,

        text=True,

        encoding="utf-8",

        errors="ignore"

    )

    if result.returncode != 0:

        return None

    text = result.stdout.strip()

    if "x" not in text:

        return None

    try:

        w, h = text.split("x")

        return (

            int(w),

            int(h)

        )

    except Exception:

        return None


# ==========================================================
# VIDEO VALIDATION
# ==========================================================

def validate_video_file(video_file):

    """
    Production validation.

    Checks:

    ✔ File exists
    ✔ Size > 1 KB
    ✔ FFprobe can read it
    ✔ Duration > 0
    ✔ Resolution detected
    """

    path = Path(video_file)

    if not path.exists():

        return False

    if path.stat().st_size < 1024:

        return False

    duration = get_video_duration(path)

    if duration <= 0:

        return False

    resolution = get_video_resolution(path)

    if resolution is None:

        return False

    return True


# ==========================================================
# FFMPEG CHECK
# ==========================================================

def is_ffmpeg_available():

    try:

        result = subprocess.run(

            [

                FFMPEG,

                "-version"

            ],

            capture_output=True,

            text=True

        )

        return result.returncode == 0

    except Exception:

        return False


# ==========================================================
# ENGINE INFO
# ==========================================================

def engine_info():

    return {

        "ffmpeg": FFMPEG,

        "ffprobe": FFPROBE,

        "ffmpeg_available": is_ffmpeg_available(),

        "supported_encoders": list(

            SUPPORTED_ENCODERS

        ),

        "quality_presets": list(

            QUALITY_PRESETS.keys()

        )

    }


# ==========================================================
# SELF TEST
# ==========================================================

if __name__ == "__main__":

    print(

        "========== FFMPEG ENGINE =========="

    )

    print(

        engine_info()

    )