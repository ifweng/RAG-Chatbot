from .config import Redis
from rejson import Path

class Cache:
    def __init__(self, json_client):
        self.json_client = json_client

    async def get_chat_history(self, token: str):
        data = self.json_client.jsonget(
            str(token), Path.rootPath()
        )
        return data

    async def add_message_to_cache(self, token: str, source: str, message_data: dict):
        """Appends the new message to the message array

        Args:
            token (str): the token that is assign to the user, every user has a unique token
            source (str): either 'system' or 'user'
            message_data (dict): a dictionary including id, msg content and time stamp
        """
        if source == "system":
            message_data['msg'] = "system:" + message_data['msg']
        elif source == "user":
            message_data['msg'] = "user:" + message_data['msg']

        self.json_client.jsonarrappend(
            str(token), Path('.messages'), message_data
        )
