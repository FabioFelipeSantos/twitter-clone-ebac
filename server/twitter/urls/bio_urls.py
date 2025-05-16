from django.urls import path, include
from rest_framework.routers import DefaultRouter
from twitter.viewsets import BioViewSet

bio_router = DefaultRouter()
bio_router.register(r"bio", BioViewSet, basename="bio")

urlpatterns = []
urlpatterns.extend(bio_router.urls)
