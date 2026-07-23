from pathlib import Path
import subprocess
import traceback

from video.ffmpeg_engine import (
    build_ffmpeg_command,
    export_with_fallback,
    validate_video_file
)


class ExportManager:

    def __init__(
        self,
        encoder="libx264",
        quality="High",
        log_callback=None
    ):

        self.encoder = encoder
        self.quality = quality
        self.log_callback = log_callback

    # ======================================================
    # LOGGING
    # ======================================================

    def log(self, message):

        if self.log_callback:

            self.log_callback(str(message))

    # ======================================================
    # EXPORT SINGLE CLIP
    # ======================================================

    def export_clip(

        self,

        input_file,

        output_file,

        start_time,

        end_time

    ):

        output_file = Path(output_file)

        output_file.parent.mkdir(

            parents=True,

            exist_ok=True

        )

        self.log("=" * 80)

        self.log(

            f"Exporting : {output_file.name}"

        )

        self.log(

            f"Start : {start_time:.3f}"

        )

        self.log(

            f"End   : {end_time:.3f}"

        )

        try:

            process = export_with_fallback(

                input_file,

                output_file,

                start_time,

                end_time,

                encoder=self.encoder,

                quality=self.quality

            )

        except Exception:

            self.log(

                traceback.format_exc()

            )

            return False

        self.log(

            f"Return Code : {process.returncode}"

        )

        if process.stdout:

            self.log(process.stdout)

        if process.stderr:

            self.log(process.stderr)
                    # ======================================================
        # VALIDATE OUTPUT
        # ======================================================

        if process.returncode != 0:

            self.log(

                f"❌ FFmpeg failed : {output_file.name}"

            )

            return False

        if not validate_video_file(output_file):

            self.log(

                f"❌ Invalid video generated : {output_file.name}"

            )

            try:

                output_file.unlink(missing_ok=True)

            except Exception:

                pass

            return False

        self.log(

            f"✅ Export completed : {output_file.name}"

        )

        return True

    # ======================================================
    # EXPORT MULTIPLE CLIPS
    # ======================================================

    def export(

        self,

        input_file,

        clips,

        output_folder

    ):

        output_folder = Path(output_folder)

        output_folder.mkdir(

            parents=True,

            exist_ok=True

        )

        exported_files = []

        total = len(clips)

        self.log(

            f"Starting export of {total} clip(s)..."

        )

        for index, clip in enumerate(clips, start=1):

            output_file = output_folder / (

                f"clip_{index:03d}.mp4"

            )

            self.log(

                f"[{index}/{total}] Processing..."

            )

            success = self.export_clip(

                input_file,

                output_file,

                clip["start"],

                clip["end"]

            )

            if success:

                exported_files.append(

                    str(output_file)

                )

            else:

                self.log(

                    f"Skipped : {output_file.name}"

                )

        self.log("=" * 80)

        self.log(

            f"Export Finished"

        )

        self.log(

            f"Successful : {len(exported_files)}"

        )

        self.log(

            f"Failed : {total - len(exported_files)}"

        )

        return exported_files
        # ======================================================
    # VERIFY EXPORT FOLDER
    # ======================================================

    def verify_export_folder(

        self,

        output_folder

    ):

        output_folder = Path(output_folder)

        valid_files = []

        if not output_folder.exists():

            return valid_files

        for video in sorted(

            output_folder.glob("*.mp4")

        ):

            if validate_video_file(video):

                valid_files.append(str(video))

            else:

                self.log(

                    f"Removing invalid file : {video.name}"

                )

                try:

                    video.unlink()

                except Exception:

                    pass

        self.log(

            f"Verified {len(valid_files)} valid clip(s)."

        )

        return valid_files


    # ======================================================
    # CLEANUP
    # ======================================================

    def cleanup_invalid_files(

        self,

        output_folder

    ):

        output_folder = Path(output_folder)

        removed = 0

        if not output_folder.exists():

            return removed

        for file in output_folder.glob("*.mp4"):

            if not validate_video_file(file):

                try:

                    file.unlink()

                    removed += 1

                except Exception:

                    pass

        self.log(

            f"Cleanup complete. Removed {removed} invalid file(s)."

        )

        return removed


    # ======================================================
    # INFORMATION
    # ======================================================

    def manager_info(self):

        return {

            "encoder": self.encoder,

            "quality": self.quality,

            "logging": self.log_callback is not None

        }


    # ======================================================
    # STRING
    # ======================================================

    def __repr__(self):

        return (

            f"ExportManager("

            f"encoder='{self.encoder}', "

            f"quality='{self.quality}')"

        )