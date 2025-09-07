import os
import subprocess
import json

def get_video_quality(video_path: str) -> int:
    """
    Возвращает высоту (в пикселях) видео через ffprobe
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=height",
        "-of", "json",
        video_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Ошибка ffprobe: {result.stderr}")

    info = json.loads(result.stdout)
    if "streams" not in info or len(info["streams"]) == 0:
        return 0

    return info["streams"][0].get("height", 0)


def convert_to_hls(input_file: str, output_dir: str, max_quality: str):
    """
    Конвертирует видео в HLS с качествами от max_quality до 360p
    и создаёт master.m3u8 для плеера
    """

    ALL_QUALITIES = [
        ("1080p", "1920x1080"),
        ("720p", "1280x720"),
        ("480p", "854x480"),
        ("360p", "640x360"),
    ]

    os.makedirs(output_dir, exist_ok=True)

    # Берём все качества меньше или равные max_quality
    max_value = int(max_quality[:-1])
    qualities_to_process = [q for q in ALL_QUALITIES if int(q[0][:-1]) <= max_value]

    streams = []
    for qname, resolution in qualities_to_process:
        q_dir = os.path.join(output_dir, qname)
        os.makedirs(q_dir, exist_ok=True)
        playlist_path = os.path.join(q_dir, "playlist.m3u8")

        cmd = [
            "ffmpeg",
            "-i", input_file,
            "-vf", f"scale={resolution}",
            "-c:a", "aac",
            "-ar", "48000",
            "-c:v", "h264",
            "-profile:v", "main",
            "-crf", "20",
            "-sc_threshold", "0",
            "-g", "48",
            "-keyint_min", "48",
            "-hls_time", "4",
            "-hls_playlist_type", "vod",
            "-b:v", "0",
            "-hls_segment_filename", os.path.join(q_dir, "segment%d.ts"),
            playlist_path
        ]
        subprocess.run(cmd, check=True)
        streams.append((qname, playlist_path))

    # Создание master.m3u8
    master_file = os.path.join(output_dir, "master.m3u8")
    with open(master_file, "w") as f:
        f.write("#EXTM3U\n")
        for qname, playlist in streams:
            bandwidth_map = {
                "1080p": 5000000,
                "720p": 2500000,
                "480p": 1000000,
                "360p": 600000,
            }
            f.write(f'#EXT-X-STREAM-INF:BANDWIDTH={bandwidth_map[qname]},RESOLUTION={dict(ALL_QUALITIES)[qname]}\n')
            f.write(f'{qname}/playlist.m3u8\n')

    # Удаляем исходный файл
    if os.path.exists(input_file):
        os.remove(input_file)
