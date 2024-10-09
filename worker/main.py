import asyncio
from src.redis.config import Redis
from src.model.gpt import GPT
from src.redis.cache import Cache
from src.schema.chat import Message

redis = Redis()

async def main():
    json_client = redis.create_rejson_connection()

    await Cache(json_client).add_message_to_cache(
        token="a92ceed7-7c17-46a5-98d6-102be3828ef9",
        source="user",
        message_data={
            "id": "1",
            "msg": "Hello",
            "timestamp": "2022-07-16 13:20:01.092109"
        }
    )

    data = await Cache(json_client).get_chat_history(token="a92ceed7-7c17-46a5-98d6-102be3828ef9")
    print(data)
    message_data = data['messages'][-10:]
    short_mem_data = [i['msg'] for i in message_data]
    res = GPT().query(input=short_mem_data)
    msg = Message(msg=res)
    print(msg)
    await Cache(json_client).add_message_to_cache(
        token="a92ceed7-7c17-46a5-98d6-102be3828ef9",
        source="system",
        message_data=msg.model_dump()
    )

if __name__ == "__main__":
    asyncio.run(main())
