from rest_framework import serializers
from twitter.models import Avatar


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avatar
        fields = [
            "id",
            "file_name",
            "file_saved_name",
            "file_path",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "file_saved_name",
            "file_path",
            "created_at",
            "updated_at",
        ]


class AvatarUploadSerializer(serializers.Serializer):
    file = serializers.ImageField(
        required=True,
        error_messages={
            "required": "Nenhum arquivo enviado.",
            "invalid": "Arquivo inválido. Envie uma imagem no formato PNG ou JPG/JPEG.",
            "empty": "O arquivo enviado está vazio.",
        },
    )

    def validate_file(self, file):
        """Validação básica do arquivo de imagem"""
        max_size = 5 * 1024 * 1024  # 5MB
        if file.size > max_size:
            raise serializers.ValidationError(
                f"O tamanho da imagem não pode exceder 5MB. Atual: {file.size / (1024 * 1024):.2f}MB"
            )

        content_type = file.content_type.lower()
        if content_type not in ["image/jpeg", "image/png", "image/jpg"]:
            raise serializers.ValidationError(
                "Apenas arquivos JPEG, JPG ou PNG são permitidos."
            )

        return file
