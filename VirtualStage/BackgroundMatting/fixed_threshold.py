import os

from helpers import spawn


def fixed_split(videos, thresholds, mask_suffix, overlap=0):
    print(f"Splitting {len(videos)} videos vertically by a fixed threshold")
    log_file = open("split_logs.txt", 'w')

    for i, video in enumerate(videos):
        if i >= (len(thresholds)) or not thresholds[i]:
            continue

        try:
            os.makedirs(video + "_up")
            os.makedirs(video + "_dw")
        except FileExistsError:
            continue

        threshold = int(thresholds[i])
        iup_region = f"iw:{threshold + overlap}:0:0"
        idw_region = f"iw:ih-{threshold}+{overlap}:0:{threshold - overlap}"

        # crop color images
        code = spawn(
            [
                "ffmpeg",
                "-i",
                f"{os.path.join(video, '%04d_img.png')}",
                "-filter:v",
                f"crop={iup_region}",
                f"{os.path.join(video+'_up', '%04d_img.png')}",
            ],
            stdout=log_file,
            stderr=log_file,
        )
        if code != 0:
            exit(code)
        code = spawn(
            [
                "ffmpeg",
                "-i",
                f"{os.path.join(video, '%04d_img.png')}",
                '-filter:v',
                f"crop={idw_region}",
                f"{os.path.join(video+'_dw', '%04d_img.png')}",
            ],
            stdout=log_file,
            stderr=log_file,
        )
        if code != 0:
            exit(code)

        # crop mask images
        code = spawn(
            [
                "ffmpeg",
                "-i",
                f"{os.path.join(video, '%04d')}{mask_suffix}.png",
                '-filter:v',
                f"crop={iup_region}",
                f"{os.path.join(video+'_up', '%04d')}{mask_suffix}.png",
            ],
            stdout=log_file,
            stderr=log_file,
        )
        if code != 0:
            exit(code)
        code = spawn(
            [
                "ffmpeg",
                "-i",
                f"{os.path.join(video, '%04d')}{mask_suffix}.png",
                '-filter:v',
                f"crop={idw_region}",
                f"{os.path.join(video+'_dw', '%04d')}{mask_suffix}.png",
            ],
            stdout=log_file,
            stderr=log_file,
        )
        if code != 0:
            exit(code)

        # crop background image
        code = spawn(
            [
                "ffmpeg",
                "-y",
                "-i",
                f"{video+'.png'}",
                f"-filter:v \"crop={iup_region}\" {video+'_up.png'}",
            ],
            stdout=log_file,
            stderr=log_file,
        )
        if code != 0:
            exit(code)
        code = spawn(
            [
                "ffmpeg",
                "-y",
                "-i",
                f"{video+'.png'}",
                '-filter:v',
                f"crop={idw_region}",
                f"{video+'_dw.png'}",
            ],
            stdout=log_file,
            stderr=log_file,
        )
        if code != 0:
            exit(code)

        print(f" Splitted {video} ({i+1}/{len(videos)})")


def fixed_merge(videos, factors, output_dir, suffix, outputs_list, overlap=0):
    print(f"Reconstructing {len(videos)} output images")
    log_file = open("merge_logs.txt", 'w')

    for i, video in enumerate(videos):
        if i < (len(factors)) and factors[i]:
            # video split, merging
            out_path = os.path.join(
                output_dir,
                os.path.basename(video),
            ).replace("\\", "/")

            try:
                os.makedirs(out_path + suffix)
            except FileExistsError:
                continue

            outpup = (out_path + "_up" + suffix).replace("\\", "/")
            outpdw = (out_path + "_dw" + suffix).replace("\\", "/")

            for o in outputs_list:
                code = spawn(
                    [
                        "ffmpeg",
                        "-i",
                        f"{outpup}/%04d_{o}.png",
                        "-i",
                        f"{outpdw}/%04d_{o}.png",
                        '-filter_complex',
                        f"[0:0]crop=iw:ih-{overlap}:0:0[v0];[1:0]crop=iw:ih-{overlap}:0:{overlap}[v1];[v0][v1]vstack",
                        f"{out_path + suffix}/%04d_{o}.png",
                        "-hide_banner",
                    ],
                    stdout=log_file,
                    stderr=log_file,
                )
                if code != 0:
                    exit(code)

            print(f" Merged {video} ({i+1}/{len(videos)})")
