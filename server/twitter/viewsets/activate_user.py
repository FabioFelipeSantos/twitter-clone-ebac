from rest_framework.views import APIView
from rest_framework import permissions
from twitter.response import ApiResponse
from twitter.services import UserService


class PublicActivateView(APIView):
    """
    View pública para ativação de usuário sem autenticação
    """

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, user_id):
        try:
            user = UserService.get_user_by_id(user_id)
            if not user:
                return ApiResponse(
                    message=f"Usuário com ID '{user_id}' não encontrado.",
                    status_code=404,
                )

            if user.is_active:
                return ApiResponse(
                    message="Este usuário já está ativo.", status_code=400
                )

            UserService.activate_user(user)

            return ApiResponse(
                message="Conta ativada com sucesso.",
                status_code=200,
                data={
                    "user": {
                        "id": str(user.id),
                        "nickname": user.nickname,
                        "is_active": user.is_active,
                    }
                },
            )
        except Exception as e:
            return ApiResponse(
                message=f"Erro ao ativar usuário: {str(e)}", status_code=500
            )
