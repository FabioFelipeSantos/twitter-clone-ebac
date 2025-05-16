from django.db import models
from .base import BaseModel
from .user import User


class Bio(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="bio")
    text = models.TextField(null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default="Brasil")

    def __str__(self):
        return f"Bio de {self.user.nickname}"
