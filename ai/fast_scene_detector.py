from pathlib import Path
import subprocess
import tempfile

import cv2
import numpy as np

from video.ffmpeg_engine import find_ffmpeg


class FastSceneDetector:

    def __init__(
        self,
        threshold=30.0,
        sample_interval=5,
        min_scene_duration=3.0,
        log_callback=None
    ):

        self.threshold = threshold

        self.sample_interval = max(
            1,
            int(sample_interval)
        )

        self.min_scene_duration = float(
            min_scene_duration
        )

        self.log_callback = log_callback

    # --------------------------------------------------
    # Logging
    # --------------------------------------------------

    def log(self, message):

        if self.log_callback:
            self.log_callback(message)

    # --------------------------------------------------
    # Frame Difference
    # --------------------------------------------------

    @staticmethod
    def frame_difference(
        frame1,
        frame2
    ):

        gray1 = cv2.cvtColor(
            frame1,
            cv2.COLOR_BGR2GRAY
        )

        gray2 = cv2.cvtColor(
            frame2,
            cv2.COLOR_BGR2GRAY
        )

        difference = cv2.absdiff(
            gray1,
            gray2
        )

        return np.mean(difference)

    # --------------------------------------------------
    # Detect Scene Changes
    # --------------------------------------------------

    def detect(
        self,
        video_file
    ):

        video_file = Path(video_file)

        if not video_file.exists():
            raise FileNotFoundError(video_file)

        capture = cv2.VideoCapture(
            str(video_file)
        )

        if not capture.isOpened():
            self.log(
                "OpenCV failed to open video, using FFmpeg fallback."
            )
            with tempfile.NamedTemporaryFile(
                suffix=".mp4",
                delete=False
            ) as temp_file:
                ffmpeg = find_ffmpeg()
                command = [
                    ffmpeg,
                    "-y",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-i",
                    str(video_file),
                    "-c:v",
                    "libx264",
                    "-preset",
                    "ultrafast",
                    "-crf",
                    "23",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "128k",
                    str(temp_file.name)
                ]
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    raise RuntimeError(
                        "FFmpeg fallback failed to decode video. "
                        f"{result.stderr.strip()}"
                    )
                capture = cv2.VideoCapture(
                    temp_file.name
                )
                if not capture.isOpened():
                    raise RuntimeError(
                        "Failed to open temp decoded video."
                    )
                resolved_temp = Path(temp_file.name)
        else:
            resolved_temp = None

        fps = capture.get(
            cv2.CAP_PROP_FPS
        )

        if fps <= 0:
            fps = 30.0

        previous_frame = None

        frame_number = 0

        scene_changes = [0.0]

        self.log(
            f"Fast scanning {video_file.name}"
        )

        while True:

            success, frame = capture.read()

            if not success:
                break

            if frame_number % self.sample_interval != 0:
                frame_number += 1
                continue

            if previous_frame is not None:

                difference = self.frame_difference(
                    previous_frame,
                    frame
                )

                if difference >= self.threshold:

                    timestamp = frame_number / fps

                    if (
                        timestamp
                        - scene_changes[-1]
                    ) >= self.min_scene_duration:

                        scene_changes.append(
                            timestamp
                        )

            previous_frame = frame.copy()

            frame_number += 1

        video_duration = frame_number / fps

        if scene_changes[-1] < video_duration:
            scene_changes.append(video_duration)

        capture.release()
        if resolved_temp is not None:
            try:
                resolved_temp.unlink()
            except Exception:
                pass

        scenes = []

        for index in range(
            len(scene_changes) - 1
        ):

            start = scene_changes[index]

            end = scene_changes[index + 1]

            duration = end - start

            if duration < self.min_scene_duration:
                continue

            scenes.append({

                "start": round(start, 3),

                "end": round(end, 3),

                "duration": round(duration, 3),

                "score": 0.0,

                "faces": 0,

                "motion": 0.0,

                "speech": False,

                "subtitle_density": 0.0

            })

        self.log(
            f"{len(scenes)} fast scene(s) detected."
        )

        return scenes
    # ==========================================================
# SCENE VALIDATION
# ==========================================================

def validate_scene(scene):

    required = [
        "start",
        "end",
        "duration"
    ]

    for key in required:

        if key not in scene:
            return False

    if scene["start"] < 0:
        return False

    if scene["end"] <= scene["start"]:
        return False

    if scene["duration"] <= 0:
        return False

    return True


def validate_scene_list(scenes):

    return all(
        validate_scene(scene)
        for scene in scenes
    )


# ==========================================================
# SCENE SUMMARY
# ==========================================================

def scene_summary(scenes):

    if not scenes:

        return {

            "count": 0,

            "total_duration": 0.0,

            "average_duration": 0.0,

            "longest_scene": None

        }

    total_duration = sum(
        scene["duration"]
        for scene in scenes
    )

    longest = max(
        scenes,
        key=lambda scene: scene["duration"]
    )

    return {

        "count": len(scenes),

        "total_duration": round(
            total_duration,
            2
        ),

        "average_duration": round(
            total_duration / len(scenes),
            2
        ),

        "longest_scene": longest

    }


# ==========================================================
# CONVENIENCE FUNCTION
# ==========================================================

def fast_detect_scenes(

    video_file,

    threshold=30.0,

    sample_interval=5,

    min_scene_duration=3.0,

    log_callback=None

):

    detector = FastSceneDetector(

        threshold=threshold,

        sample_interval=sample_interval,

        min_scene_duration=min_scene_duration,

        log_callback=log_callback

    )

    return detector.detect(
        video_file
    )


# ==========================================================
# INFORMATION
# ==========================================================

def detector_info():

    return {

        "name": "FastSceneDetector",

        "engine": "OpenCV",

        "sampling": True,

        "optimized": True

    }