from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.db import close_old_connections
from rest_framework_jwt.authentication import BaseJSONWebTokenAuthentication
from authentication.models import User
from decouple import config
import jwt


@database_sync_to_async
def get_user(token_key):
    try:
        user = User.objects.get(id=token_key)
        return user
    except User.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        token_key = scope['query_string'].decode().split('=')[-1]
        print(token_key)

        scope['user'] = await get_user(jwt.decode(token_key, config('SECRET_KEY'), algorithms=["HS256"])["user_id"])

        return await super().__call__(scope, receive, send)

class JsonTokenAuthMiddleware(BaseJSONWebTokenAuthentication):
    """
    Token authorization middleware for Django Channels 2
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):

        try:
        # Close old database connections to prevent usage of timed out connections
            close_old_connections()
            user_id = scope["query_string"].decode("utf-8")
            user = User.objects.get(id=user_id)
            print(user)
            if user.is_authenticated:
                scope["user"] = user
        except:
            scope["user"] = AnonymousUser()

        return self.inner(scope)