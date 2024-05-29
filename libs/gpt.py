import base64
import requests
from groq import Groq

class Generation:
    """
    A class that provides methods for generating text responses and encoding images.
    """
    def __init__(self):
        self.messages = []
        self.max_messages = 10
        self.client = Groq(api_key='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')

    def encode_image(self, image_path: str):
        with open(image_path, "rb") as image:
            encoded_image = base64.b64encode(image.read()).decode("utf-8")
        return encoded_image
    
    def generate_text_response(self, text: str):
        completion = self.client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                    {
                        "role": "system",
                        "content": "You're Fam, ai voice assistant, made by Akshat Kushwaha. You are always supposed to answer in brief sentences and in human-like language. You have to answer all kinds of questions and queries."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
            temperature=1,
            max_tokens=8192,
            top_p=1,
            stream=False,
            stop=None,
            )
    
        response = completion.choices[0].message.content
        return response
    
    def generate_text_with_image(self, text: str, image: str):
        api_key = 'sk-proj-K8hfsSF9vbG1ccu7Mo50T3BlbkFJXB6nXSORFrhYVjkzTWaR'

        # Getting the base64 string
        base64_image = self.encode_image(image)

        headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
        }

        payload = {
        "model": "gpt-4o",
        "messages": [
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": text
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
                }
            ]
            }
        ],
        "max_tokens": 300
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        print(response.json()['choices'][0]['message']['content'])

    def live_chat_with_ai(self, text: str):
        if len(self.messages) >= self.max_messages:
            return "Fam-ai has went to sleep and you can access it tomorrow."
        completion = self.client.chat.completions.create(
            model="llama3-70b-8192",
            messages=self.messages + [
                {
                    "role": "system",
                    "content": "You're Fam, ai voice assistant, made by Akshat Kushwaha. You are always supposed to answer in brief sentences and in human-like language. You have to answer all kinds of questions and queries."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=1,
            max_tokens=8192,
            top_p=1,
            stream=False,
            stop=None,
        )

        response = completion.choices[0].message.content
        self.messages.append({
            "role": "assistant",
            "content": response
        })

        if len(self.messages) > self.max_messages:
            self.messages = self.messages[1:]

        return response




