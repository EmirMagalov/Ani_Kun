from django.urls import path,include
from .views import *
from rest_framework import routers
router=routers.DefaultRouter()
router.register(r'animes',AnimeViewSet)
router.register(r'seasons',SeasonViewSet)
router.register(r'episodes',EpisodeViewSet)
router.register(r'voiceovers',VoiceOverViewSet)
router.register(r'videoqualitys',VideoQualityViewSet)
router.register(r'video_url',VideoViewSet, basename='video')
urlpatterns = [

    # path("",test),
    path("api/",include(router.urls)),
]
