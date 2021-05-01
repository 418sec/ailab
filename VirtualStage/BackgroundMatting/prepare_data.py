import os

from helpers import spawn


def prepare_videos(
    videos,
    extension,
    start,
    duration,
    kinect_mask=True,
    width=1920,
    height=1080,
):
    video_start_secs = start % 60
    video_start_mins = start // 60
    print(f"Dumping frames and segmenting {len(videos)} input videos")
    log_file = open("bg_matting_logs.txt", "w")
    for i, video in enumerate(videos):
        try:
            os.makedirs(video)
        except FileExistsError:
            continue

        print(f"Dumping frames from {video} ({i+1}/{len(videos)})...")
        segmentation_log = open(f"segmentation_logs_{i}.txt", "w")
        ffmpeg_duration = ""
        if duration != "-1":
            ffmpeg_duration = f"-t {duration}"
        code = spawn(
            [
                "ffmpeg",
                "-y",
                "-ss",
                f"00:{video_start_mins:02}:{video_start_secs:02}.000",
                "-vsync",
                "0",
                "-i",
                f"{video}{extension}",
                "-vf",
                f"scale={width}:{height}",
                "-map",
                "0:0",
                f"{ffmpeg_duration}",
                f"{video}/%04d_img.png",
                "-hide_banner",
            ],
            stdout=log_file,
            stderr=log_file,
        )
        if code != 0:
            exit(code)

        print(f"Segmenting frames...")
        if kinect_mask:
            code = spawn(
                [
                    "KinectMaskGenerator.exe",
                    f"{video}{extension}",
                    f"{video}",
                    f"{start}",
                    f"{duration}",
                ],
                stdout=segmentation_log,
                stderr=segmentation_log,
            )
            if code != 0:
                exit(code)
        else:
            code = spawn(
                [
                    "python",
                    "segmentation_deeplab.py",
                    "-i",
                    f"{video}",
                ],
                stdout=segmentation_log,
                stderr=segmentation_log,
            )
            if code != 0:
                exit(code)

        print(f"Extracting background...")
        code = spawn(
            [
                "ffmpeg",
                "-y",
                "-i",
                f"{video}{extension}",
                "-vf",
                f"scale={width}:{height}",
                "-map",
                "0:0",
                "-ss",
                "00:00:02.000",
                "-vframes",
                "1",
                f"{video}.png",
                "-hide_banner",
            ],
            stdout=log_file,
            stderr=log_file,
        )
        if code != 0:
            exit(code)
