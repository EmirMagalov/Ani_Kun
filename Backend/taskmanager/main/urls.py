from django.urls import path, include, re_path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView,TokenVerifyView


from rest_framework import routers
router=routers.DefaultRouter()
router.register(r'animes',AnimeViewSet)
router.register(r'seasons',SeasonViewSet)
router.register(r'episodes',EpisodeViewSet)
router.register(r'voiceovers',VoiceOverViewSet)
router.register(r'videoqualitys',VideoQualityViewSet)
router.register(r'video_url',VideoViewSet, basename='video')
router.register("users", UserViewSet, basename="users")
urlpatterns = [


    # path("",test),
    path("api/",include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/', include('djoser.urls')),
    path(r'api/auth/', include('djoser.urls.authtoken')),
]
