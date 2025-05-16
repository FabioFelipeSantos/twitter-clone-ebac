from typing import Literal

from django.db import models

from .base import BaseModel
from .user import User


class Tweet(BaseModel):
    text = models.TextField(null=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tweets")

    def __str__(self):
        return f"{self.user.nickname}: {self.text[:30]}"

    def get_statistics(
        self, statistic: Literal["likes", "re_tweets", "dislikes", "shares"]
    ) -> int:
        """
        Retorna a contagem de uma estatística específica para este tweet.

        Args:
            statistic: O tipo de estatística a ser contado ('likes', 're_tweets', 'dislikes' ou 'shares')

        Returns:
            Contagem de interações do tipo especificado
        """
        if statistic not in ["likes", "re_tweets", "dislikes", "shares"]:
            raise ValueError(f"Estatística inválida: {statistic}")

        return getattr(self, statistic).count()

    def get_all_statistics(self):
        """
        Retorna todas as estatísticas para este tweet em um dicionário.

        Returns:
            Dict contendo contagens de likes, re_tweets, dislikes e shares
        """
        return {
            "likes": self.get_statistics("likes"),
            "re_tweets": self.get_statistics("re_tweets"),
            "dislikes": self.get_statistics("dislikes"),
            "shares": self.get_statistics("shares"),
        }
