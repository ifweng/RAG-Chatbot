import os
import uuid
from rejson import Path
from fastapi import APIRouter, FastAPI, WebSocket,  Request, HTTPException, WebSocketDisconnect, Depends
from ..socket.connection import ConnectionManager
from ..socket.utils import get_token
from ..redis.producer import Producer
from ..redis.config import Redis
from ..schema.chat import Chat


chat = APIRouter()
manager = ConnectionManager()
redis = Redis()

@chat.post("/token")
async def token_generator(name: str, request: Request):
    """Issue the user a session token for access to the chat session
    """
    token = str(uuid.uuid4())

    if name == "":
        raise HTTPException(
            status_code=400,
            detail={
                "loc": "name",
                "msg": "Enter a valid name"
            }
        )

    # Create new chat session
    json_client = redis.create_rejson_connection()

    chat_session = Chat(
        token=token,
        messages=[],
        name=name
    )

    # Store chat session in redis JSON with the token as key
    json_client.jsonset(str(token), Path.rootPath(), chat_session.model_dump())

    # Set timeout for redis data
    redis_client = await redis.create_connection()
    await redis_client.expire(str(token), 600)

    return chat_session.model_dump()


@chat.post("/refresh_token")
async def refresh_token(request: Request):
    """get session history for the user if the connection is lost, 
    as long as the token is still active and not expired

    Args:
        request (Request): _description_

    Returns:
        _type_: _description_
    """
    return None


@chat.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket, token: str=Depends(get_token)):
    """opens a WebSocket to send messages between the client and server
    """
    await manager.connect(websocket)
    redis_client = await redis.create_connection()
    producer = Producer(redis_client)
    try:
        while True: #Ensure the socket stays open
            data = await websocket.receive_text() #receive any message sent by the client
            stream_data = {}
            stream_data[token] = data
            await producer.add_to_stream(stream_data, "message_channel")
            await manager.send_personal_message(
                "Response: Simulating response from the GPT service",
                websocket
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
