from django.shortcuts import render,HttpResponse
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Case, When, Value, IntegerField, Count
from rest_framework import filters,viewsets
from .serializers import *
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
# Create your views here.

def test(request):
    return HttpResponse("<h1>Test</h1>")


class AnimeViewSet(viewsets.ModelViewSet):
    queryset = Anime.objects.all().order_by("id")
    serializer_class = AnimeSerializer


class SmallResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 5

class SeasonViewSet(viewsets.ModelViewSet):
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title"]
    pagination_class = SmallResultsSetPagination

    def get_queryset(self):
        search = self.request.query_params.get('search', '').strip()
        if not search:
            return Season.objects.none()
        return Season.objects.filter(title__icontains=search)

    @method_decorator(cache_page(60 * 5))
    @action(detail=False, methods=["get"])
    def seasons(self, request, pk=None):
        anime_id = request.query_params.get("anime_id")
        season_id = request.query_params.get("season_id")

        qs = Season.objects.all()

        if anime_id:
            qs = qs.filter(anime_id=anime_id)
        if season_id:
            qs = qs.filter(id=season_id)

        qs = qs.annotate(
            type_order=Case(
                When(type="season", then=Value(0)),
                When(type="movie", then=Value(1)),
                output_field=IntegerField(),
            ),
            episodes_count=Count("episodes"),
        ).order_by("type_order", "number")

        serializer = SeasonSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

class EpisodeViewSet(viewsets.ModelViewSet):
    queryset = Episode.objects.all()
    serializer_class = EpisodeSerializer

    @action(detail=False, methods=["get"])
    def eps(self, request):
        season_id = request.query_params.get("season")
        if not season_id:
            return Response({"error": "Не указан season id"}, status=400)

        videos = Episode.objects.filter(season_id=season_id)
        serializer = EpisodeSerializer(videos, many=True, context={"request": request})
        return Response(serializer.data)


class VoiceOverViewSet(viewsets.ModelViewSet):
    queryset = VoiceOver.objects.all()
    serializer_class =VoiceOverSerializer

class VideoQualityViewSet(viewsets.ModelViewSet):
    queryset =  VideoQuality.objects.all()
    serializer_class = VideoQualitySerializer



class VideoViewSet(viewsets.ModelViewSet):
    queryset = Episode.objects.all()
    serializer_class = EpisodeSerializer

    @action(detail=False, methods=["get"])
    def get_video(self, request, pk=None):

        episode_number = request.query_params.get("episode_number")
        season_id = request.query_params.get("season_id")
        season=Season.objects.get(pk=season_id)
        episode = Episode.objects.get(number=episode_number, season_id=season_id)
        try:
            video = VideoQuality.objects.get(
                voiceover__episode=episode,

            )
        except VideoQuality.DoesNotExist:
            return Response({"error": "Видео не найдено"}, status=404)
        print(episode.number)
        return Response({
            "video_id":video.pk,
            "video_file": request.build_absolute_uri(video.video_file.url),
            "episode_number": episode.number,
            "episode_title": episode.title,
            "season_number":season.number,
            "type":season.type,
            "anime_name":season.anime.title,
            "season_id":season.pk,
            "anime_id":season.anime.pk
        })


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == "create":  # регистрация
            return RegisterSerializer
        return RegisterSerializer  # или свой сериализатор для чтения

    def get_permissions(self):
        if self.action == "create":  # регистрация доступна всем
            return [AllowAny()]
        return [IsAuthenticated()]  # остальные действия только для авторизованных

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Возвращает текущего авторизованного пользователя"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)