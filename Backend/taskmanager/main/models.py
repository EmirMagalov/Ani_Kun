from django.db import models
from PIL import Image

from .tasks import convert_video_task
import os
from django.conf import settings
class Anime(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название аниме")
    description = models.TextField(blank=True, verbose_name="Описание")
    poster = models.ImageField(upload_to="posters/", blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # сначала сохраняем файл

        if self.poster:
            img = Image.open(self.poster.path)
            img = img.resize((300, 450), Image.LANCZOS)
            img.save(self.poster.path)
    def __str__(self):
        return f"{self.title}"


class Season(models.Model):
    TYPE_CHOICES = [
        ("season", "Сезон"),
        ("movie", "Фильм"),
    ]

    anime = models.ForeignKey(
        Anime, on_delete=models.CASCADE, related_name="seasons"
    )
    number = models.PositiveIntegerField(verbose_name="Номер", default=1)
    title = models.CharField(max_length=255, blank=True, verbose_name="Название")
    poster = models.ImageField(upload_to="season_posters/", blank=True, null=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="season")

    class Meta:
        unique_together = ("anime", "number", "type")

    def __str__(self):
        return f"{self.anime.title} — {self.get_type_display()} {self.number}"


class Episode(models.Model):
    season = models.ForeignKey(
        Season, on_delete=models.CASCADE, related_name="episodes"
    )
    number = models.PositiveIntegerField(verbose_name="Номер серии")
    title = models.CharField(max_length=255, blank=True, verbose_name="Название серии")

    class Meta:
        unique_together = ("season", "number")  # уникальная серия в сезоне

    def __str__(self):
        return f"{self.season} — {f'{self.number} серия' if self.season.type == 'season' else f'{self.number} Фильм'}"


class VoiceOver(models.Model):
    episode = models.ForeignKey(
        Episode, on_delete=models.CASCADE, related_name="voiceovers"
    )
    name = models.CharField(max_length=255, verbose_name="Название озвучки")  # Anilibria, AniDub и т.д.

    def __str__(self):
        return f"{self.episode} [{self.name}]"


class VideoQuality(models.Model):
    voiceover = models.ForeignKey(
        "VoiceOver", on_delete=models.CASCADE, related_name="qualities"
    )
    # quality = models.CharField(
    #     max_length=50,
    #     verbose_name="Качество",
    #     blank=True,
    #     null=True
    # )
    video_file = models.FileField(
        upload_to="videos/",
        verbose_name="Видео файл"
    )

    class Meta:
        unique_together = ("voiceover",)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.video_file:
            output_dir = os.path.join(settings.MEDIA_ROOT, f"videos/episode_{self.pk}")
            convert_video_task.delay(self.video_file.path, output_dir)
    def __str__(self):
        return f"{self.voiceover} — {self.video_file.name}"