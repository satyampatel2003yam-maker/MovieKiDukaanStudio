from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector


def detect_scenes(video_path):
    """
    Detect scenes in a movie.
    Returns:
        [(start_sec, end_sec), ...]
    """

    video = open_video(video_path)

    scene_manager = SceneManager()

    # Threshold badhaoge to kam scenes milenge.
    scene_manager.add_detector(ContentDetector(threshold=27))

    scene_manager.detect_scenes(video)

    scene_list = scene_manager.get_scene_list()

    scenes = []

    for start, end in scene_list:
        scenes.append(
            (
                start.get_seconds(),
                end.get_seconds()
            )
        )

    return scenes