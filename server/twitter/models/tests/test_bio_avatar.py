import pytest
from twitter.models import User, Bio, Avatar


@pytest.mark.django_db
class TestBioAvatarModel:
    @pytest.fixture
    def user(self, user_data):
        return User.objects.create_user(
            email=user_data["email"],
            nickname=user_data["nickname"],
            first_name=user_data["first_name"],
            password=user_data["password"],
        )

    def test_create_bio(self, user):
        bio = Bio.objects.create(
            user=user,
            text="Essa é a minha bio",
            city="São Paulo",
            state="SP",
            country="Brasil",
        )

        assert bio.pk is not None
        assert bio.text == "Essa é a minha bio"
        assert bio.user == user
        assert bio.country == "Brasil"

    def test_create_avatar(self, user):
        bio = Bio.objects.create(user=user, text="Essa é a minha bio")

        avatar = Avatar.objects.create(bio=bio, file_name="profile.jpg")
        assert avatar.pk is not None
        assert avatar.bio == bio
        assert avatar.file_name == "profile.jpg"
