import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()


class GPT:
    def __init__(self):
        self.model = os.environ.get('MODEL_ID')
        self.client = InferenceClient(
            self.model,
            token=os.environ.get('HUGGINFACE_INFERENCE_TOKEN'),
        )

    def query(self, input: str):
        messages = []
        res = ""
        for i in input:
            if i[:5] == "user:":
                messages.append({"role": "user", "content": i[5:]})
            elif i[:7] == "system:":
                messages.append({"role": "system", "content": i[7:]})
        for message in self.client.chat_completion(
            messages=messages,
            max_tokens=500,
            stream=True,
        ):
            print(message.choices[0].delta.content, end="")
            res += message.choices[0].delta.content
        return res

# if __name__ == "__main__":
#     GPT().query("Will artificial intelligence help humanity conquer the universe?")
