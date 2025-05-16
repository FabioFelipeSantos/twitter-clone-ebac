from .auth_urls import urlpatterns as auth_urlpatterns
from .users_urls import urlpatterns as user_urlpatterns
from .bio_urls import urlpatterns as bio_urlpatterns
from .avatar_urls import urlpatterns as avatar_urlpatterns

# from .tweets import urlpatterns as tweet_urlpatterns

urlpatterns = []
urlpatterns.extend(auth_urlpatterns)
urlpatterns.extend(user_urlpatterns)
urlpatterns.extend(bio_urlpatterns)
urlpatterns.extend(avatar_urlpatterns)
# urlpatterns.extend(tweet_urlpatterns)
