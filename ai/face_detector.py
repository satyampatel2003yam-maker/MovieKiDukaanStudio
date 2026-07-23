from pathlib import Path

import cv2


class FaceDetector:

    def __init__(
        self,
        cascade_path=None,
        sample_interval=15,
        log_callback=None
    ):

        if cascade_path is None:
            cascade_path = (
                cv2.data.haarcascades
                + "haarcascade_frontalface_default.xml"
            )

        self.detector = cv2.CascadeClassifier(cascade_path)

        if self.detector.empty():
            raise RuntimeError(
                "Unable to load Haar Cascade."
            )

        self.sample_interval = max(
            1,
            int(sample_interval)
        )

        self.log_callback = log_callback

    # --------------------------------------------------
    # Logging
    # --------------------------------------------------

    def log(self, message):

        if self.log_callback:
            self.log_callback(message)

    # --------------------------------------------------
    # Detect Faces In One Frame
    # --------------------------------------------------

    def detect_frame(
        self,
        frame
    ):

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        faces = self.detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(40, 40)
        )

        return len(faces)

    # --------------------------------------------------
    # Analyze One Video
    # --------------------------------------------------

    def analyze_video(
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
            raise RuntimeError(
                f"Cannot open {video_file.name}"
            )

        frame_index = 0
        sampled_frames = 0
        total_faces = 0
        max_faces = 0

        self.log(
            f"Scanning {video_file.name}"
        )

        while True:

            success, frame = capture.read()

            if not success:
                break

            if frame_index % self.sample_interval == 0:

                try:

                    face_count = self.detect_frame(
                        frame
                    )

                    total_faces += face_count

                    max_faces = max(
                        max_faces,
                        face_count
                    )

                    sampled_frames += 1

                except Exception:
                    pass

            frame_index += 1

        capture.release()

        if sampled_frames == 0:

            average_faces = 0.0
            face_density = 0.0

        else:

            average_faces = (
                total_faces /
                sampled_frames
            )

            face_density = min(
                average_faces / 5.0,
                1.0
            )

        analysis = {

            "frames_analyzed": sampled_frames,

            "total_faces": total_faces,

            "average_faces": round(
                average_faces,
                2
            ),

            "max_faces": max_faces,

            "face_density": round(
                face_density,
                3
            )

        }

        self.log(

            f"{video_file.name} : "
            f"Avg Faces = {analysis['average_faces']} | "
            f"Max Faces = {analysis['max_faces']}"

        )

        return analysis
        # --------------------------------------------------
    # Analyze Multiple Videos
    # --------------------------------------------------

    def analyze_all(
        self,
        video_files
    ):

        results = {}

        total = len(video_files)

        for index, video_file in enumerate(
            video_files,
            start=1
        ):

            try:

                analysis = self.analyze_video(
                    video_file
                )

                results[str(video_file)] = analysis

                self.log(
                    f"[{index}/{total}] "
                    f"{Path(video_file).name} completed."
                )

            except Exception as e:

                self.log(
                    f"{Path(video_file).name} : {e}"
                )

        return results

    # --------------------------------------------------
    # Update Scene Face Scores
    # --------------------------------------------------

    def analyze_scenes(
        self,
        scenes,
        analysis
    ):

        average_faces = analysis.get(
            "average_faces",
            0
        )

        density = analysis.get(
            "face_density",
            0
        )

        for scene in scenes:

            scene["faces"] = round(
                average_faces
            )

            scene["face_density"] = density

        self.log(
            "Scene face statistics updated."
        )

        return scenes

    # --------------------------------------------------
    # Information
    # --------------------------------------------------

    def __repr__(self):

        return (
            f"FaceDetector("
            f"sample_interval={self.sample_interval}"
            f")"
        )