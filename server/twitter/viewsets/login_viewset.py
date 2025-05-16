from rest_framework import views, permissions

from twitter.serializers import LoginSerializer
from twitter.services import AuthService
from twitter.response import ApiResponse


class LoginViewSet(views.APIView):
    """Endpoint para login de usuários"""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username_or_email = serializer.validated_data["username_or_email"]
            password = serializer.validated_data["password"]

            tokens = AuthService.login(username_or_email, password)

            if tokens:
                return ApiResponse(
                    data=tokens, message="Usuário logado com sucesso", status_code=200
                )

            return ApiResponse(
                data=None,
                message="Credenciais inválidas ou usuário inativo",
                status_code=401,
            )

        return ApiResponse(
            data=serializer.errors,
            message="Não foi possível fazer login",
            status_code=400,
        )
