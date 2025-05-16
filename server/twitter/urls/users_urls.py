from django.urls import path
from rest_framework.routers import DefaultRouter
from twitter.viewsets import UserViewSet, AdminUserViewSet, PublicActivateView

user_router = DefaultRouter()
user_router.register(r"users", UserViewSet, basename="users")
user_router.register(r"admin", AdminUserViewSet, basename="admin")

urlpatterns = [
    path(
        "users/<uuid:user_id>/public-activate/",
        PublicActivateView.as_view(),
        name="public-activate",
    )
]
urlpatterns.extend(user_router.urls)
