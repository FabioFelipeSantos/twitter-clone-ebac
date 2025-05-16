from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from twitter.models import Avatar
from twitter.serializers import (
    AvatarSerializer,
    UserBasicSerializer,
    BioSerializer,
    AvatarUploadSerializer,
)
from twitter.services import BioService, AvatarService
from twitter.response import ApiResponse, standard_response


class AvatarViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @standard_response
    def create(self, request):
        """Cria ou atualiza o avatar para o usuário autenticado"""
        try:
            user = request.user

            bio = BioService.get_bio_by_user(user)
            bio_created = False

            if not bio:
                bio = BioService.create_bio(
                    user,
                    {"text": "", "city": "", "state": "", "country": "Brasil"},
                    allow_empty=True,
                )
                bio_created = True

            serializer = AvatarUploadSerializer(data=request.data)
            if not serializer.is_valid():
                if bio_created:
                    bio.delete()

                return ApiResponse(
                    data=serializer.errors,
                    message="Arquivo de avatar inválido.",
                    status_code=400,
                )

            avatar_file = serializer.validated_data["file"]
            avatar = AvatarService.create_avatar(bio, avatar_file)

            bio = BioService.get_bio_by_user(user)

            message = "Avatar criado com sucesso."
            if bio_created:
                message = (
                    "Avatar criado com sucesso e bio vazia criada automaticamente."
                )

            return ApiResponse(
                data={
                    "avatar": AvatarSerializer(avatar).data,
                    "bio_id": BioSerializer(bio).data["id"],
                },
                message=message,
                status_code=201,
            )

        except ValueError as e:
            return ApiResponse(data=None, message=str(e), status_code=400)
        except Exception as e:
            return ApiResponse(
                data={"detail": str(e)},
                message="Erro ao processar avatar.",
                status_code=500,
            )

    @standard_response
    def destroy(self, request, pk=None):
        """Remove o avatar do usuário"""
        try:
            user = request.user
            bio = BioService.get_bio_by_user(user)

            if not bio or not hasattr(bio, "avatar"):
                return ApiResponse(
                    data=None,
                    message="Você não possui um avatar para remover.",
                    status_code=404,
                )

            avatar = get_object_or_404(Avatar, id=pk)
            if avatar.bio.user != user:
                return ApiResponse(
                    data=None,
                    message="Você não tem permissão para remover este avatar.",
                    status_code=403,
                )

            AvatarService.delete_avatar(avatar)

            return ApiResponse(
                data=None,
                message="Avatar removido com sucesso.",
                status_code=200,
            )

        except Exception as e:
            return ApiResponse(
                data={"detail": str(e)},
                message="Erro ao remover avatar.",
                status_code=500,
            )
