import os
import uuid
from datetime import datetime

from django.conf import settings

from twitter.models import Avatar


class AvatarService:
    @staticmethod
    def get_upload_path(user):
        """Retorna o caminho da pasta onde o avatar será salvo"""
        nickname_part = user.nickname[:10] if len(user.nickname) > 10 else user.nickname
        folder_name = f"{user.id}_{nickname_part}"

        base_path = os.path.join(settings.BASE_DIR, "uploads")

        upload_path = os.path.join(base_path, folder_name)

        os.makedirs(upload_path, exist_ok=True)

        return upload_path

    @staticmethod
    def generate_file_name(original_filename):
        """Gera o nome do arquivo a ser salvo"""
        hash_hex = uuid.uuid4().hex[:12]

        timestamp = datetime.now().strftime("%d%m%Y-%H%M%S")

        return f"{hash_hex}_{timestamp}_{original_filename}"

    @staticmethod
    def validate_avatar_file(file):
        """Valida o arquivo de avatar (tamanho e tipo)"""
        max_size = 5 * 1024 * 1024  # 5MB
        if file.size > max_size:
            raise ValueError(
                f"O tamanho da imagem não pode exceder 5MB. Tamanho atual: {file.size / (1024 * 1024):.2f}MB"
            )

        content_type = file.content_type.lower()
        if not content_type in ["image/jpeg", "image/png", "image/jpg"]:
            raise ValueError(
                "Apenas arquivos de imagem (JPEG, JPG ou PNG) são permitidos."
            )

        file_name = file.name.lower()
        valid_extensions = [".jpg", ".jpeg", ".png"]
        if not any(file_name.endswith(ext) for ext in valid_extensions):
            raise ValueError("O arquivo deve ter uma extensão .jpg, .jpeg ou .png")

        return True

    @staticmethod
    def create_avatar(bio, file):
        """Cria um novo avatar para uma bio"""
        AvatarService.validate_avatar_file(file)

        if hasattr(bio, "avatar"):
            AvatarService.delete_avatar(bio.avatar)

        user = bio.user
        upload_path = AvatarService.get_upload_path(user)

        file_name = file.name
        file_saved_name = AvatarService.generate_file_name(file_name)

        file_path = os.path.join(upload_path, file_saved_name)
        with open(file_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        relative_path = f"uploads/{user.id}_{user.nickname[:10]}/{file_saved_name}"

        avatar = Avatar.objects.create(
            bio=bio,
            file_name=file_name,
            file_saved_name=file_saved_name,
            file_path=relative_path,
        )

        return avatar

    @staticmethod
    def delete_avatar(avatar):
        """Remove um avatar do sistema"""
        try:
            file_path = os.path.join(settings.BASE_DIR, avatar.file_path)
            if os.path.exists(file_path):
                os.remove(file_path)

            avatar.delete()
            return True

        except Exception as e:
            raise ValueError(f"Erro ao excluir avatar: {str(e)}")
