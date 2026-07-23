import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from video.clip_generator import generate_clips

if __name__ == '__main__':
    result = generate_clips(
        input_video=r'P:/Download/SATYAM PATEL GIMT.mp4',
        output_folder=r'P:/Download/test',
        clip_duration=5,
        max_clips=1,
        quality='High',
        processor='CPU'
    )
    print(result)
