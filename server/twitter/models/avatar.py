import uuid
from django.db import models
from .base import BaseModel
from .bio import Bio


class Avatar(BaseModel):
    bio = models.OneToOneField(Bio, on_delete=models.CASCADE, related_name="avatar")
    file_name = models.CharField(max_length=255, null=False)
    file_saved_name = models.CharField(max_length=300, blank=True)
    file_path = models.CharField(max_length=500, blank=True)

    # def save(self, *args, **kwargs):
    #     if not self.file_saved_name and self.file_name:
    #         hash_hex = uuid.uuid4().hex[:16]
    #         self.file_saved_name = f"{hash_hex}_{self.file_name}"

    # super().save(*args, **kwargs)

    def __str__(self):
        return f"Avatar de {self.bio.user.nickname}"
