from pathlib import Path
import subprocess

from video.ffmpeg_engine import (
    build_vertical_command,
    validate_video_file
)


class VerticalConverter:

    def __init__(
        self,
        encoder="libx264",
        quality="High",
        progress_callback=None,
        log_callback=None
    ):
        self.encoder = encoder
        self.quality = quality
        self.progress_callback = progress_callback
        self.log_callback = log_callback

    # --------------------------------------------------
    # Logging
    # --------------------------------------------------

    def log(self, message):

        if self.log_callback:
            self.log_callback(message)

    # --------------------------------------------------
    # Progress
    # --------------------------------------------------

    def progress(self, current, total):

        if self.progress_callback:
            self.progress_callback(current, total)

    # --------------------------------------------------
    # Convert One File
    # --------------------------------------------------

    def convert(
        self,
        input_file,
        output_file,
        encoder=None,
        quality=None
    ):

        input_file = Path(input_file)
        output_file = Path(output_file)

        if encoder is None:
            encoder = self.encoder

        if quality is None:
            quality = self.quality

        if not input_file.exists():
            raise FileNotFoundError(input_file)

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        command = build_vertical_command(
            input_file=input_file,
            output_file=output_file,
            encoder=encoder,
            quality=quality
        )

        self.log(
            f"Converting {input_file.name}"
        )

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:

            raise RuntimeError(
                result.stderr.strip()
            )

        if not validate_video_file(output_file):

            raise RuntimeError(
                "Invalid output video."
            )

        self.log(
            f"Finished {output_file.name}"
        )

        return str(output_file)
        # --------------------------------------------------
    # Convert Multiple Files
    # --------------------------------------------------

    def convert_all(
        self,
        input_files,
        output_folder,
        encoder="libx264",
        quality="High"
    ):

        output_folder = Path(output_folder)
        output_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        converted_files = []
        failed_files = []

        total = len(input_files)

        for index, input_file in enumerate(input_files, start=1):

            output_file = (
                output_folder /
                f"vertical_{index:03d}.mp4"
            )

            try:

                converted = self.convert(
                    input_file=input_file,
                    output_file=output_file,
                    encoder=encoder,
                    quality=quality
                )

                converted_files.append(converted)

                self.log(
                    f"SUCCESS {output_file.name}"
                )

            except Exception as e:

                failed_files.append(str(input_file))

                self.log(
                    f"FAILED {Path(input_file).name} : {e}"
                )

            self.progress(index, total)

        return {

            "converted": converted_files,

            "failed": failed_files,

            "total": total,

            "success": len(converted_files),

            "failed_count": len(failed_files)

        }

    # --------------------------------------------------
    # String Representation
    # --------------------------------------------------

    def __repr__(self):

        return (
            f"VerticalConverter("
            f"progress_callback={self.progress_callback is not None}, "
            f"log_callback={self.log_callback is not None}"
            f")"
        )


# ======================================================
# Convenience Function
# ======================================================

def convert_to_vertical(
    input_file,
    output_file,
    encoder="libx264",
    quality="High",
    progress_callback=None,
    log_callback=None
):

    converter = VerticalConverter(
        progress_callback=progress_callback,
        log_callback=log_callback
    )

    return converter.convert(
        input_file=input_file,
        output_file=output_file,
        encoder=encoder,
        quality=quality
    )