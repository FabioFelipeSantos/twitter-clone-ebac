from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from twitter.models import User


class AuthService:
    @staticmethod
    def login(username_or_email, password):
        """
        Autentica um usuário pelo nickname ou email
        Retorna tokens JWT se bem-sucedido, None se falhar
        """
        user = authenticate(username=username_or_email, password=password)

        if not user:
            try:
                email_user = User.objects.get(nickname=username_or_email)
                user = authenticate(username=email_user.email, password=password)
            except User.DoesNotExist:
                pass

        if user:
            return AuthService.get_tokens_for_user(user)
        return None

    @staticmethod
    def get_tokens_for_user(user):
        """Gera tokens JWT para um usuário"""
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": str(user.id),
                "email": user.email,
                "nickname": user.nickname,
                "is_active": user.is_active,
            },
        }

    @staticmethod
    def get_user_from_token(request):
        """Retorna o usuário autenticado a partir do token"""
        return request.user

    @staticmethod
    def get_user_details(user):
        """Retorna detalhes do usuário, incluindo seguidores e pessoas que segue"""
        followers = [
            {"id": str(f.id), "nickname": f.nickname} for f in user.followers.all()
        ]

        following = [
            {"id": str(f.id), "nickname": f.nickname} for f in user.following.all()
        ]

        return {
            "id": str(user.id),
            "email": user.email,
            "nickname": user.nickname,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "followers_count": len(followers),
            "followers": followers,
            "following_count": len(following),
            "following": following,
        }
