from celery import shared_task
from .utils import convert_to_hls, get_video_quality

def get_nearest_quality(height):
    """
    Определяем максимальное качество, которое может быть установлено
    """
    for q in [1080, 720, 480, 360]:
        if height >= q:
            return f"{q}p"
    return "360p"

@shared_task
def convert_video_task(video_path, output_dir):
    # Получаем реальную высоту видео
    real_height = get_video_quality(video_path)
    max_quality = get_nearest_quality(real_height)

    # Обновляем запись

    # Конвертируем видео в HLS
    convert_to_hls(video_path, output_dir, max_quality)