from typing import TypeVar

from datetime import datetime
from django.db.models import Q
from twitter.models import User
from rest_framework.response import Response


class UserService:
    @staticmethod
    def get_user_by_id(user_id):
        """Busca um usuário pelo ID"""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    def filter_users(query_params):
        """
        Filtra usuários com base nos parâmetros da query
        Suporta filtros por qualquer campo do modelo User
        """
        queryset = User.objects.all()

        model_fields = [field.name for field in User._meta.fields]
        text_fields = ["first_name", "last_name", "nickname", "email"]

        for param, value in query_params.items():
            if param in ["ordering", "limit", "offset"]:
                continue

            if param in model_fields:
                if param in text_fields:
                    queryset = queryset.filter(Q(**{f"{param}__icontains": value}))
                elif param == "is_active":
                    is_active = value.lower() in ("true", "t", "1", "yes")
                    queryset = queryset.filter(is_active=is_active)
                else:
                    queryset = queryset.filter(**{param: value})

        ordering = query_params.get("ordering")
        if ordering:
            ordering_fields = ordering.split(",")
            queryset = queryset.order_by(*ordering_fields)

        try:
            offset = int(query_params.get("offset", 0))
            limit = int(query_params.get("limit", 100))

            if limit > 100:
                limit = 100

            queryset = queryset[offset : offset + limit]
        except (ValueError, TypeError):
            queryset = queryset[:100]

        return queryset

    @staticmethod
    def is_valid_email(email):
        return not User.objects.filter(email=email).exists()

    @staticmethod
    def is_valid_nickname(nickname):
        return not User.objects.filter(nickname=nickname).exists()

    @staticmethod
    def deactivate_user(user: User):
        if not user.is_active:
            raise ValueError("Usuário já desativado")

        user.is_active = False
        user.disabled_at = datetime.now()
        user.save()

    @staticmethod
    def activate_user(user: User):
        user.is_active = True
        user.disabled_at = None
        user.save()

    @staticmethod
    def follow_user(follower, user_to_follow_id):
        """
        Faz um usuário seguir outro

        Args:
            follower (User): O usuário que irá seguir (usuário logado)
            user_to_follow_id (str): ID do usuário a ser seguido

        Returns:
            dict: Informações dos dois usuários e contagem de seguidores
        """
        try:
            user_to_follow = UserService.get_user_by_id(user_to_follow_id)

            if not user_to_follow:
                raise ValueError("Usuário a ser seguido não encontrado")

            if str(follower.id) == str(user_to_follow_id):
                raise ValueError("Você não pode seguir a si mesmo")

            if user_to_follow in follower.following.all():
                raise ValueError("Você já segue este usuário")

            if follower.role == "admin" and user_to_follow.role != "admin":
                raise ValueError("Você só pode seguir outro administrador")

            if follower.role != "admin" and user_to_follow.role == "admin":
                raise ValueError("Você só pode seguir um usuário não administrador")

            follower.following.add(user_to_follow)
            follower.save()

            result = {
                "follower": {
                    "id": str(follower.id),
                    "nickname": follower.nickname,
                    "email": follower.email,
                    "followers_count": follower.followers.count(),
                    "following_count": follower.following.count(),
                },
                "followed": {
                    "id": str(user_to_follow.id),
                    "nickname": user_to_follow.nickname,
                    "email": user_to_follow.email,
                    "followers_count": user_to_follow.followers.count(),
                    "following_count": user_to_follow.following.count(),
                },
            }

            return result

        except Exception as e:
            raise ValueError(f"Erro ao seguir usuário: {str(e)}")
