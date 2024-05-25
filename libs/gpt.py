import openai
import base64
import requests
import time

class Generation:
    """
    A class that provides methods for generating text responses and encoding images.
    """

    def encode_image(self, image_path: str):
        with open(image_path, "rb") as image:
            encoded_image = base64.b64encode(image.read()).decode("utf-8")
        return encoded_image

    def generate_text_response(self, text: str):
        # client = openai.OpenAI(api_key='sk-proj-K8hfsSF9vbG1ccu7Mo50T3BlbkFJXB6nXSORFrhYVjkzTWaR')
        # model="gpt-4o",
        # response = client.chat.completions.create(
        #     model="gpt-4o",
        #     messages=[
        #         {
        #             "role": "system",
        #             "content": "You're Fam, ai voice assistant, made by Akshat Kushwaha"
        #         },
        #         {
        #             "role": "user",
        #             "content": text
        #         }
        #     ],
        #     temperature=0.5,
        #     max_tokens=100,
        #     top_p=1,
        #     frequency_penalty=0,
        #     presence_penalty=0
        # )
        # response = response.choices[0].message.content
        # return response
    
        time.sleep(1)
        return str 
    
    def generate_text_with_image(self, text: str, image: str):
        # api_key = 'sk-proj-K8hfsSF9vbG1ccu7Mo50T3BlbkFJXB6nXSORFrhYVjkzTWaR'

        # # Getting the base64 string
        # base64_image = self.encode_image(image)

        # headers = {
        # "Content-Type": "application/json",
        # "Authorization": f"Bearer {api_key}"
        # }

        # payload = {
        # "model": "gpt-4o",
        # "messages": [
        #     {
        #     "role": "user",
        #     "content": [
        #         {
        #         "type": "text",
        #         "text": text
        #         },
        #         {
        #         "type": "image_url",
        #         "image_url": {
        #             "url": f"data:image/jpeg;base64,{base64_image}"
        #         }
        #         }
        #     ]
        #     }
        # ],
        # "max_tokens": 300
        # }

        # response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        # print(response.json()['choices'][0]['message']['content'])

        time.sleep(1)
        return "you're looking cute"



gpt = Generation()
print(gpt.generate_text_response("tell me abt meosis"))

# You look great today!
# Your off-shoulder top is very stylish,
# and your smile adds a lovely and cheerful vibe to your selfie.
# The light purple phone case is a nice touch as well. Keep shining!'

