"""
Middleware de rate limiting par utilisateur/IP.
Limite les requêtes POST vers /*/process à 10 par minute.
Utilise Redis pour le comptage distribué (compatible Celery existant).
"""

import logging
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# Limite configurable
RATE_LIMIT = 10   # requêtes max
WINDOW_SEC  = 60  # fenêtre glissante en secondes


async def _get_client_key(request: Request) -> str:
    """Identifie le client via son user_id JWT ou son adresse IP."""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        try:
            from jose import jwt, JWTError
            from core.config import settings
            payload = jwt.decode(
                auth[7:], settings.SECRET_KEY, algorithms=["HS256"]
            )
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except Exception:
            pass

    # Fallback : adresse IP (supporte les proxies)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return f"ip:{forwarded.split(',')[0].strip()}"
    client = request.client
    return f"ip:{client.host if client else 'unknown'}"


class RateLimitMiddleware:
    """
    Middleware ASGI limitant les appels POST /api/*/process.
    Renvoie HTTP 429 si le client dépasse RATE_LIMIT requêtes / WINDOW_SEC s.
    """

    def __init__(self, app, redis_url: str):
        self.app = app
        self.redis_url = redis_url
        self._redis = None

    async def _get_redis(self):
        if self._redis is None:
            try:
                import redis.asyncio as aioredis
                self._redis = aioredis.from_url(self.redis_url, decode_responses=True)
            except Exception as exc:
                logger.warning("Rate limit Redis indisponible : %s", exc)
        return self._redis

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)

        # Appliquer uniquement aux POST /api/*/process
        if request.method == "POST" and "/process" in request.url.path:
            redis = await self._get_redis()
            if redis is not None:
                try:
                    key = await _get_client_key(request)
                    cache_key = f"rl:{key}"
                    count = await redis.incr(cache_key)
                    if count == 1:
                        await redis.expire(cache_key, WINDOW_SEC)

                    if count > RATE_LIMIT:
                        response = JSONResponse(
                            status_code=429,
                            content={
                                "detail": (
                                    f"Trop de requêtes. Limite : {RATE_LIMIT} "
                                    f"traitements par {WINDOW_SEC} secondes."
                                )
                            },
                            headers={"Retry-After": str(WINDOW_SEC)},
                        )
                        await response(scope, receive, send)
                        return
                except Exception as exc:
                    # En cas d'erreur Redis, on laisse passer (fail open)
                    logger.warning("Rate limit check échoué : %s", exc)

        await self.app(scope, receive, send)
