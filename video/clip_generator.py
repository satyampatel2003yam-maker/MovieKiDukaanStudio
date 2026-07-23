"""
MovieKiDukaan Studio V2
Clip Generator
Production Version
"""

from pathlib import Path
import sys
import time
import traceback

from ai.fast_scene_detector import FastSceneDetector
from ai.clip_selector import ClipSelector

from video.export_manager import ExportManager
from video.vertical_convertor import VerticalConverter
from video.ffmpeg_engine import validate_video_file


class ClipGenerator:

    # ==========================================================
    # INIT
    # ==========================================================

    def __init__(

        self,

        encoder="libx264",

        quality="High",

        clip_duration=30,

        max_clips=10,

        vertical=True,

        log_callback=None,

        progress_callback=None

    ):

        self.encoder = encoder

        self.quality = quality

        self.clip_duration = clip_duration

        self.max_clips = max_clips

        self.vertical = vertical

        self.log_callback = log_callback

        self.progress_callback = progress_callback

        self.detector = FastSceneDetector(

            log_callback=self.log

        )

        self.selector = ClipSelector(

            clip_duration=clip_duration,

            max_clips=max_clips,

            log_callback=self.log

        )

        self.exporter = ExportManager(

            encoder=encoder,

            quality=quality,

            log_callback=self.log

        )

        self.converter = VerticalConverter(

            encoder=encoder,

            quality=quality,

            log_callback=self.log

        )

    # ==========================================================
    # LOGGING
    # ==========================================================

    def log(self, message):

        text = str(message)
        safe_text = text.encode("ascii", errors="replace").decode("ascii")

        try:
            print(safe_text)
        except Exception:
            pass

        if self.log_callback:
            try:
                self.log_callback(safe_text)
            except Exception:
                pass

    # ==========================================================
    # PROGRESS
    # ==========================================================

    def progress(

        self,

        percent,

        status

    ):

        if self.progress_callback:

            self.progress_callback(

                percent,

                status

            )

    # ==========================================================
    # OUTPUT FOLDERS
    # ==========================================================

    def prepare_output(

        self,

        output_folder

    ):

        output = Path(output_folder)

        clips = output / "clips"

        vertical = output / "vertical"

        logs = output / "logs"

        clips.mkdir(

            parents=True,

            exist_ok=True

        )

        vertical.mkdir(

            parents=True,

            exist_ok=True

        )

        logs.mkdir(

            parents=True,

            exist_ok=True

        )

        return {

            "root": output,

            "clips": clips,

            "vertical": vertical,

            "logs": logs

        }
        # ==========================================================
    # GENERATE CLIPS
    # ==========================================================

    def generate(

        self,

        input_video,

        output_folder

    ):

        start_time = time.time()

        try:

            self.log("=" * 80)
            self.log("MovieKiDukaan Studio V2 Started")
            self.log("=" * 80)

            self.progress(

                5,

                "Preparing..."

            )

            input_video = Path(input_video)

            if not input_video.exists():

                raise FileNotFoundError(

                    input_video

                )

            folders = self.prepare_output(

                output_folder

            )

            self.log(

                f"Input Video : {input_video.name}"

            )

            self.progress(

                10,

                "Detecting scenes..."

            )

            # ==========================================
            # SCENE DETECTION
            # ==========================================

            scenes = self.detector.detect(

                input_video

            )

            if not scenes:

                raise RuntimeError(

                    "No scenes detected."

                )

            self.log(

                f"Detected {len(scenes)} scene(s)."

            )

            self.progress(

                25,

                "Selecting clips..."

            )

            # ==========================================
            # CLIP SELECTION
            # ==========================================

            selected_clips = self.selector.select(

                scenes

            )

            if not selected_clips:

                raise RuntimeError(

                    "No clips selected."

                )

            self.log(

                f"Selected {len(selected_clips)} clip(s)."

            )

            self.progress(

                40,

                "Exporting clips..."

            )

            exported_files = self.exporter.export(

                input_file=str(input_video),

                clips=selected_clips,

                output_folder=str(folders["clips"])

            )

            if not exported_files:

                raise RuntimeError(

                    "Clip export failed."

                )

            self.log(

                f"Exported {len(exported_files)} clip(s)."

            )
                        # ==========================================
            # VERIFY EXPORTED CLIPS
            # ==========================================

            self.progress(

                55,

                "Verifying exported clips..."

            )

            verified_files = []

            for clip in exported_files:

                if validate_video_file(clip):

                    verified_files.append(

                        str(clip)

                    )

                else:

                    self.log(

                        f"Invalid clip removed : {Path(clip).name}"

                    )

                    try:

                        Path(clip).unlink(

                            missing_ok=True

                        )

                    except Exception:

                        pass

            if not verified_files:

                raise RuntimeError(

                    "No valid exported clips found."

                )

            self.log(

                f"Verified {len(verified_files)} clip(s)."

            )

            # ==========================================
            # VERTICAL CONVERSION
            # ==========================================

            vertical_files = []

            if self.vertical:

                self.progress(

                    70,

                    "Generating vertical clips..."

                )

                total = len(verified_files)

                for index, clip in enumerate(

                    verified_files,

                    start=1

                ):

                    output_file = (

                        folders["vertical"]

                        /

                        Path(clip).name

                    )

                    try:

                        success = self.converter.convert(

                            input_file=clip,

                            output_file=output_file

                        )

                        if success and validate_video_file(output_file):

                            vertical_files.append(

                                str(output_file)

                            )

                            self.log(

                                f"Vertical Clip {index}/{total} Completed"

                            )

                        else:

                            self.log(

                                f"Vertical Clip Failed : {Path(clip).name}"

                            )

                    except Exception as e:

                        self.log(

                            str(e)

                        )

                    self.progress(

                        70 + int(

                            index * 20 / total

                        ),

                        f"Vertical {index}/{total}"

                    )

            else:

                vertical_files = verified_files
                            # ==========================================
            # FINAL SUMMARY
            # ==========================================

            self.progress(

                95,

                "Finalizing..."

            )

            elapsed = round(

                time.time() - start_time,

                2

            )

            summary = {

                "success": True,

                "input_video": str(input_video),

                "output_folder": str(folders["root"]),

                "clips_generated": len(verified_files),

                "vertical_generated": len(vertical_files),

                "clips": verified_files,

                "vertical_clips": vertical_files,

                "processing_time": elapsed,

                "encoder": self.encoder,

                "quality": self.quality

            }

            self.progress(

                100,

                "Completed"

            )

            self.log("=" * 80)

            self.log("MovieKiDukaan Studio V2 Finished")

            self.log("=" * 80)

            self.log(

                f"Clips Generated     : {len(verified_files)}"

            )

            self.log(

                f"Vertical Generated  : {len(vertical_files)}"

            )

            self.log(

                f"Processing Time     : {elapsed} sec"

            )

            self.log("=" * 80)

            return summary

        except Exception as e:

            self.log("=" * 80)

            self.log("PIPELINE FAILED")

            self.log("=" * 80)

            self.log(str(e))

            self.log(traceback.format_exc())

            self.progress(

                0,

                "Failed"

            )

            return {

                "success": False,

                "error": str(e)

            }

    # ==========================================================
    # INFORMATION
    # ==========================================================

    def info(self):

        return {

            "encoder": self.encoder,

            "quality": self.quality,

            "clip_duration": self.clip_duration,

            "max_clips": self.max_clips,

            "vertical": self.vertical

        }

    # ==========================================================
    # STRING
    # ==========================================================

    def __repr__(self):

        return (

            "ClipGenerator("

            f"encoder='{self.encoder}', "

            f"quality='{self.quality}', "

            f"clip_duration={self.clip_duration}, "

            f"max_clips={self.max_clips}, "

            f"vertical={self.vertical}"

            ")"

        )
    # ======================================================
# Compatibility Wrapper (Dashboard V2)
# ======================================================

def generate_clips(
    input_video,
    output_folder,
    clip_duration=30,
    max_clips=10,
    quality="High",
    processor="Auto",
    log_callback=None,
    progress_callback=None,
):

    # Auto -> GPU if available
    encoder = "libx264"

    if processor == "GPU":
        encoder = "h264_nvenc"

    generator = ClipGenerator(
        encoder=encoder,
        quality=quality,
        clip_duration=clip_duration,
        max_clips=max_clips,
        log_callback=log_callback,
        progress_callback=progress_callback,
    )

    return generator.generate(
        input_video=input_video,
        output_folder=output_folder,
    )