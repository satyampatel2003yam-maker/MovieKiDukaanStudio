import os

from faster_whisper import WhisperModel


class SubtitleGenerator:

    def __init__(self):

        print("Loading Whisper Model...")

        self.model = WhisperModel(
            "small",
            device="cuda",
            compute_type="float16"
        )

        print("Whisper Ready")

    def generate(
        self,
        input_video,
        output_folder
    ):

        os.makedirs(
            output_folder,
            exist_ok=True
        )

        base_name = os.path.splitext(
            os.path.basename(input_video)
        )[0]

        subtitle_file = os.path.join(
            output_folder,
            base_name + ".srt"
        )

        print("Generating AI Subtitles...")

        segments, info = self.model.transcribe(
            input_video,
            beam_size=5
        )

        with open(
            subtitle_file,
            "w",
            encoding="utf-8"
        ) as f:

            for i, segment in enumerate(segments, start=1):

                f.write(f"{i}\n")

                f.write(
                    f"{self.format_time(segment.start)} --> {self.format_time(segment.end)}\n"
                )

                f.write(segment.text.strip() + "\n\n")

        print("Subtitle Completed")

        return subtitle_file

    def format_time(self, seconds):

        ms = int((seconds % 1) * 1000)

        total = int(seconds)

        s = total % 60

        m = (total // 60) % 60

        h = total // 3600

        return f"{h:02}:{m:02}:{s:02},{ms:03}"