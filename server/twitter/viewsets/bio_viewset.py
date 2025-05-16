from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from twitter.models import Bio
from twitter.serializers import BioSerializer, UserBasicSerializer
from twitter.services import BioService, AvatarService
from twitter.response import ApiResponse, standard_response


class BioViewSet(viewsets.ModelViewSet):
    serializer_class = BioSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put", "delete"]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        """Retorna a bio do usuário autenticado"""
        return Bio.objects.filter(user=self.request.user)

    @standard_response
    def create(self, request):
        """Cria uma nova bio para o usuário autenticado"""
        try:
            user = request.user
            if BioService.get_bio_by_user(user):
                return ApiResponse(
                    data=None,
                    message="Este usuário já possui uma bio.",
                    status_code=400,
                )

            serializer = self.get_serializer(
                data=request.data, context={"allow_empty_text": False}
            )
            if not serializer.is_valid():
                return ApiResponse(
                    data=serializer.errors,
                    message="Dados inválidos para a bio.",
                    status_code=400,
                )

            bio = BioService.create_bio(user, serializer.validated_data)

            avatar_file = None
            avatar_error = None

            if "avatar" in request.FILES:
                avatar_file = request.FILES["avatar"]
                print(f"FOUND AVATAR: {avatar_file.name}, size: {avatar_file.size}")

                try:
                    avatar = AvatarService.create_avatar(bio, avatar_file)
                except Exception as e:
                    avatar_error = str(e)

            bio = Bio.objects.get(id=bio.id)

            response_data = {
                "bio": BioSerializer(bio).data,
            }

            if avatar_error:
                response_data["avatar_error"] = avatar_error
                return ApiResponse(
                    data=response_data,
                    message="Bio criada, mas houve um erro ao processar o avatar.",
                    status_code=201,
                )

            return ApiResponse(
                data=response_data,
                message="Bio criada com sucesso.",
                status_code=201,
            )

        except Exception as e:
            import traceback

            print(traceback.format_exc())
            return ApiResponse(
                data={"detail": str(e)}, message="Erro ao criar bio.", status_code=500
            )

    @standard_response
    def update(self, request, pk=None):
        """Atualiza a bio do usuário autenticado"""
        try:
            user = request.user
            bio = get_object_or_404(Bio, id=pk, user=user)

            serializer = self.get_serializer(bio, data=request.data, partial=True)
            if not serializer.is_valid():
                return ApiResponse(
                    data=serializer.errors,
                    message="Dados inválidos para atualização da bio.",
                    status_code=400,
                )

            bio = BioService.update_bio(bio, serializer.validated_data)

            avatar_error = None
            if "avatar" in request.FILES:
                avatar_file = request.FILES["avatar"]
                try:
                    avatar = AvatarService.create_avatar(bio, avatar_file)
                except ValueError as e:
                    avatar_error = str(e)

            bio = Bio.objects.get(id=bio.id)

            response_data = {
                "bio": BioSerializer(bio).data,
            }

            if avatar_error:
                response_data["avatar_error"] = avatar_error
                return ApiResponse(
                    data=response_data,
                    message="Bio atualizada, mas houve um erro ao processar o avatar.",
                    status_code=200,
                )

            return ApiResponse(
                data=response_data,
                message="Bio atualizada com sucesso.",
                status_code=200,
            )

        except Exception as e:
            return ApiResponse(
                data={"detail": str(e)},
                message="Erro ao atualizar bio.",
                status_code=500,
            )

    @standard_response
    def destroy(self, request, pk=None):
        """Remove a bio do usuário autenticado"""
        try:
            user = request.user
            bio = get_object_or_404(Bio, id=pk, user=user)

            BioService.delete_bio(bio)

            return ApiResponse(
                data=None,
                message="Bio removida com sucesso.",
                status_code=200,
            )

        except Exception as e:
            return ApiResponse(
                data={"detail": str(e)}, message="Erro ao remover bio.", status_code=500
            )

    @standard_response
    def retrieve(self, request, pk=None):
        """Retorna uma bio específica"""
        bio = get_object_or_404(Bio, id=pk)

        return ApiResponse(
            data={
                "bio": BioSerializer(bio).data,
            },
            message="Bio encontrada.",
            status_code=200,
        )
