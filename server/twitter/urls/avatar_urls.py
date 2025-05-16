from django.urls import path, include
from rest_framework.routers import DefaultRouter
from twitter.viewsets import AvatarViewSet

avatar_router = DefaultRouter()
avatar_router.register(r"avatar", AvatarViewSet, basename="avatar")


urlpatterns = []
urlpatterns.extend(avatar_router.urls)
