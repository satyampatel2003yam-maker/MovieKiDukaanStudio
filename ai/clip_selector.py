from copy import deepcopy


class ClipSelector:
    def __init__(
        self,
        clip_duration=30,
        max_clips=10,
        log_callback=None,
    ):
        self.clip_duration = clip_duration
        self.max_clips = max_clips
        self.log_callback = log_callback

    def log(self, message):
        if self.log_callback:
            self.log_callback(message)

    def initialize_scores(self, scenes):
        scored = []

        for scene in scenes:
            item = deepcopy(scene)

            item.setdefault("score", 0.0)
            item.setdefault("faces", 0)
            item.setdefault("motion", 0.0)
            item.setdefault("speech", False)
            item.setdefault("subtitle_density", 0.0)

            scored.append(item)

        return scored

    def apply_duration_score(self, scenes):
        for scene in scenes:
            duration = scene.get("duration", 0)
            scene["score"] += (
                min(duration / self.clip_duration, 1.0) * 30
            )

        self.log("Duration score applied.")
        return scenes

    def apply_face_score(self, scenes):
        for scene in scenes:
            scene["score"] += min(scene.get("faces", 0) * 5, 25)

        self.log("Face score applied.")
        return scenes

    def apply_motion_score(self, scenes):
        for scene in scenes:
            motion = max(
                0.0,
                min(scene.get("motion", 0.0), 1.0),
            )

            scene["score"] += motion * 20

        self.log("Motion score applied.")
        return scenes

    def apply_speech_score(self, scenes):
        for scene in scenes:
            if scene.get("speech", False):
                scene["score"] += 15

        self.log("Speech score applied.")
        return scenes

    def apply_subtitle_score(self, scenes):
        for scene in scenes:
            density = max(
                0.0,
                min(scene.get("subtitle_density", 0.0), 1.0),
            )

            scene["score"] += density * 10

        self.log("Subtitle score applied.")
        return scenes

    def calculate_scores(self, scenes):
        scenes = self.initialize_scores(scenes)
        scenes = self.apply_duration_score(scenes)
        scenes = self.apply_face_score(scenes)
        scenes = self.apply_motion_score(scenes)
        scenes = self.apply_speech_score(scenes)
        scenes = self.apply_subtitle_score(scenes)
        return scenes

    def rank_scenes(self, scenes):
        ranked = sorted(
            scenes,
            key=lambda scene: scene.get("score", 0),
            reverse=True,
        )

        self.log("Scenes ranked successfully.")
        return ranked

    def trim_clips(self, scenes):
        trimmed = []

        for scene in scenes:
            item = deepcopy(scene)

            if item["duration"] > self.clip_duration:
                item["end"] = (
                    item["start"] + self.clip_duration
                )
                item["duration"] = self.clip_duration

            trimmed.append(item)

        return trimmed

    def remove_overlaps(
        self,
        scenes,
        overlap=2.0,
    ):
        selected = []

        for scene in scenes:
            keep = True

            for chosen in selected:
                latest_start = max(
                    scene["start"],
                    chosen["start"],
                )

                earliest_end = min(
                    scene["end"],
                    chosen["end"],
                )

                if (
                    earliest_end - latest_start
                ) > overlap:
                    keep = False
                    break

            if keep:
                selected.append(scene)

        self.log(
            f"{len(selected)} clip(s) after overlap removal."
        )

        return selected

    def select(self, scenes):
        scenes = self.calculate_scores(scenes)
        scenes = self.rank_scenes(scenes)
        scenes = self.trim_clips(scenes)
        scenes = self.remove_overlaps(scenes)

        selected = scenes[: self.max_clips]

        self.log(
            f"{len(selected)} clip(s) selected."
        )

        return selected

    def __repr__(self):
        return (
            f"ClipSelector("
            f"clip_duration={self.clip_duration}, "
            f"max_clips={self.max_clips})"
        )


def select_best_clips(
    scenes,
    clip_duration=30,
    max_clips=10,
    log_callback=None,
):
    """
    Compatibility wrapper for older code.
    """

    selector = ClipSelector(
        clip_duration=clip_duration,
        max_clips=max_clips,
        log_callback=log_callback,
    )

    return selector.select(scenes)