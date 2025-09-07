from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from .models import *


class AnimeSerializer(serializers.ModelSerializer):
    class Meta:
        model=Anime
        fields="__all__"

class SeasonSerializer(serializers.ModelSerializer):
    anime_name = serializers.CharField(source='anime.title', read_only=True)
    episodes_count = serializers.IntegerField(read_only=True)
    class Meta:
        model=Season
        fields=["anime_name","id","number","title","poster","type","episodes_count"]


class EpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model=Episode
        fields="__all__"

class VoiceOverSerializer(serializers.ModelSerializer):
    class Meta:
        model=VoiceOver
        fields="__all__"


class VideoQualitySerializer(serializers.ModelSerializer):
    class Meta:
        model=VideoQuality
        fields="__all__"