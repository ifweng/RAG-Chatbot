from typing import Optional
from fastapi import WebSocket, status, Query
from ..redis.config import Redis

redis = Redis()


async def get_token(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
):
    """Receives a WebSocket and token, then checks if the token is None or null
    """
    if token is None or token == "":
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

    redis_client = await redis.create_connection()
    isexists = await redis_client.exists(token)

    if isexists == 1:
        return token
    else:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Session not authenticated or expired token"
        )
