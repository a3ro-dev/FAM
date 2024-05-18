import base64
import requests
from openai import OpenAI

class Generation:
    def __init__(self, api_key='', model="gpt-4o"):
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=api_key)
    
    def encode_image(self, image_path):
        """Encode an image to base64 format."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def generate_text_response(self, prompt, max_tokens, temperature=0.5):
        """Generate a text response using GPT-4o."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        if response.choices:
            return response.choices[0].message.content.strip() if response.choices[0].message.content else ""
        else:
            return ""

    def generate_text_with_image_response(self, prompt, image_path, max_tokens=300, detail="auto"):
        """Generate a text response based on an image and additional prompt using GPT-4o."""
        base64_image = self.encode_image(image_path)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": detail
                            }
                        }
                    ]
                }
            ],
            "max_tokens": max_tokens
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        return response.json()['choices'][0]['message']['content'].strip()
