from channels.db import database_sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from django.contrib.auth.models import AnonymousUser
from urllib.parse import parse_qs

@database_sync_to_async
def get_user_from_token(token):
    try:
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(token)
        return jwt_auth.get_user(validated_token)
    except (InvalidToken, AuthenticationFailed, Exception):
        return AnonymousUser()

class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # 1. Try to get token from query string (e.g. ws://...?token=xxxx)
        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]

        # 2. If not in query string, try to get from headers
        if not token:
            headers = dict(scope.get("headers", []))
            auth_header = headers.get(b"authorization", b"").decode()
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if token:
            scope["user"] = await get_user_from_token(token)
        else:
            scope["user"] = AnonymousUser()

        return await self.app(scope, receive, send)
