from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from twitter.models import User
from twitter.serializers import UserSerializer
from twitter.services import UserService
from twitter.response import ApiResponse, standard_response
from twitter.permissions import IsAdmin, IsOwnerOrAdmin


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD de usuários
    Suporta filtros, ordenação e paginação customizada
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """Define permissões específicas para cada método"""
        if self.action in ["create"]:
            permission_classes = [permissions.AllowAny]
        elif self.action == "list":
            permission_classes = [permissions.IsAuthenticated, IsAdmin]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Retorna queryset filtrado com base nos query params
        Suporta filtragem e ordenação
        """
        return UserService.filter_users(self.request.query_params)

    @standard_response
    def list(self, request, *args, **kwargs):
        """
        Lista usuários com mensagem personalizada
        """
        queryset = self.filter_queryset(self.get_queryset())

        num_users = queryset.count()
        if num_users == 0:
            message = "Nenhum usuário encontrado"
        elif num_users == 1:
            message = "Um usuário encontrado"
        else:
            message = f"{num_users} usuários encontrados"

        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse(data=serializer.data, message=message)

    @action(detail=False, methods=["get"])
    @standard_response
    def me(self, request):
        """Endpoint para obter o próprio usuário"""
        serializer = self.get_serializer(request.user)
        return ApiResponse(data=serializer.data, message="Usuário logado encontrado")

    @standard_response
    def retrieve(self, request, *args, **kwargs):
        """
        Busca um usuário pelo ID
        """
        user = UserService.get_user_by_id(kwargs.get("pk"))
        if not user:
            return ApiResponse(
                message="Usuário não encontrado.",
                status_code=404,
            )

        serializer = self.get_serializer(user)
        return ApiResponse(data=serializer.data, message="Usuário encontrado")

    @action(detail=False, methods=["get"])
    @standard_response
    def followers(self, request):
        """Endpoint para listar seguidores do usuário logado"""
        user = request.user
        followers = user.followers.all()

        serializer = self.get_serializer(followers, many=True)
        return ApiResponse(
            data=serializer.data,
            message="Usuários seguindo encontrados com sucesso",
        )

    @action(detail=False, methods=["get"])
    @standard_response
    def following(self, request):
        """Endpoint para listar usuários que o usuário logado segue"""
        user = request.user
        following = user.following.all()

        serializer = self.get_serializer(following, many=True)
        return ApiResponse(
            data=serializer.data,
            message="Usuários seguidos encontrados com sucesso",
            status_code=200,
        )

    @standard_response
    def create(self, request, *args, **kwargs):
        """
        Cria um novo usuário com validações adicionais
        """
        try:
            email = request.data.get("email", "")
            nickname = request.data.get("nickname", "")

            if not UserService.is_valid_email(email):
                error_data = {
                    "status": 400,
                    "message": "Este email já está em uso.",
                }
                return Response(error_data, status=400)

            if not UserService.is_valid_nickname(nickname):
                error_data = {
                    "status": 400,
                    "message": "Este nickname já está em uso.",
                }
                return Response(error_data, status=400)

            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                error_data = {
                    "status": 400,
                    "message": "Dados inválidos",
                    "data": serializer.errors,
                }
                return Response(error_data, status=400)

            serializer.save()

            return ApiResponse(
                data=serializer.data,
                status_code=201,
                message="Usuário criado com sucesso",
            )

        except Exception as e:
            error_data = {
                "status": 500,
                "message": "Erro ao criar usuário",
                "data": {"error": str(e)},
            }
            return Response(error_data, status=500)

    @standard_response
    def update(self, request, *args, **kwargs):
        """Permite ao usuário atualizar seus próprios dados"""
        instance = self.get_object()

        if str(instance.id) != str(request.user.id) and request.user.role != "admin":
            return ApiResponse(
                status_code=403,
                message="Permissão negada",
            )

        serializer = self.get_serializer(
            instance, data=request.data, partial=kwargs.get("partial", False)
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return ApiResponse(
            data=serializer.data,
            message="Usuário atualizado com sucesso",
        )

    @action(detail=True, methods=["post"])
    @standard_response
    def deactivate(self, request, pk=None):
        try:
            user = UserService.get_user_by_id(pk)
            if not user:
                return ApiResponse(
                    message=f"Usuário com ID '{pk}' não encontrado.",
                    status_code=404,
                )

            if str(user.id) != str(request.user.id) and request.user.role != "admin":
                return ApiResponse(
                    status_code=403,
                    message="Permissão negada para desativar este usuário.",
                )

            UserService.deactivate_user(user)
            return ApiResponse(
                message="Usuário desativado com sucesso.", status_code=200
            )
        except Exception as e:
            return ApiResponse(
                message=f"Erro ao desativar usuário",
                status_code=500,
                data={"error": str(e)},
            )

    @standard_response
    def destroy(self, request, *args, **kwargs):
        """Permite ao usuário excluir sua própria conta ou admins excluem qualquer conta"""
        instance = self.get_object()

        if str(instance.id) != str(request.user.id) and request.user.role != "admin":
            return ApiResponse(
                status_code=403,
                message="Permissão negada",
            )

        self.perform_destroy(instance)

        return ApiResponse(
            message="Usuário deletado com sucesso",
            status_code=200,
        )

    @action(detail=False, methods=["post"], url_path="follow/(?P<user_id>[^/.]+)")
    @standard_response
    def follow(self, request, user_id=None):
        """
        Endpoint para o usuário logado seguir outro usuário

        Args:
            request: Requisição com o usuário logado
            user_id: ID do usuário a ser seguido

        Returns:
            ApiResponse: Resposta formatada com os dados dos usuários
        """
        try:
            follower = request.user

            follow_data = UserService.follow_user(follower, user_id)

            return ApiResponse(
                data=follow_data, message="Usuário seguido com sucesso", status_code=201
            )

        except ValueError as e:
            return ApiResponse(data={"error": str(e)}, message=str(e), status_code=400)

        except Exception as e:
            return ApiResponse(
                data={"error": str(e)},
                message="Erro ao processar a solicitação",
                status_code=500,
            )

    @action(detail=False, methods=["post"], url_path="unfollow/(?P<user_id>[^/.]+)")
    @standard_response
    def unfollow(self, request, user_id=None):
        """
        Endpoint para o usuário logado deixar de seguir outro usuário
        """
        try:
            follower = request.user
            user_to_unfollow = UserService.get_user_by_id(user_id)

            if not user_to_unfollow:
                return ApiResponse(
                    data={"error": "Usuário não encontrado"},
                    message="Usuário não encontrado",
                    status_code=404,
                )

            if user_to_unfollow not in follower.following.all():
                return ApiResponse(
                    data={"error": "Você não segue este usuário"},
                    message="Você não segue este usuário",
                    status_code=400,
                )

            follower.following.remove(user_to_unfollow)

            result = {
                "unfollower": {
                    "id": str(follower.id),
                    "nickname": follower.nickname,
                    "followers_count": follower.followers.count(),
                    "following_count": follower.following.count(),
                },
                "unfollowed": {
                    "id": str(user_to_unfollow.id),
                    "nickname": user_to_unfollow.nickname,
                    "followers_count": user_to_unfollow.followers.count(),
                    "following_count": user_to_unfollow.following.count(),
                },
            }

            return ApiResponse(
                data=result,
                message="Deixou de seguir o usuário com sucesso",
                status_code=200,
            )

        except Exception as e:
            return ApiResponse(
                data={"error": str(e)},
                message="Erro ao processar a solicitação",
                status_code=500,
            )
