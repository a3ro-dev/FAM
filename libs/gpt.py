import base64
import requests
from groq import Groq
import wikipediaapi
import datetime
import yaml
import subprocess
from functools import lru_cache

with open('conf/config.yaml', 'r') as file:
    config = yaml.safe_load(file)
groqKey = config['main']['groq_api_key']
openaiKey = config['main']['openai_api_key']

class Generation:
    """
    A class that handles various generative AI tasks in the backend.

    Methods
    -------
    __init__():
        Initializes the Generation class with default settings.
    encode_image(image_path: str) -> str:
        Encodes an image from the given file path to a base64 string.
    generate_text_response(text: str) -> str:
        Generates a text response based on the provided input text using the Groq API.
    generate_text_with_image(text: str, image: str) -> str:
        Generates a text response based on the provided input text and image using the OpenAI API.
    live_chat_with_ai(text: str) -> str:
        Engages in a live chat with the AI, providing conversational responses based on the input text.
    search_wikipedia(query: str) -> str:
        Searches Wikipedia for the given query and returns a summary.
    search_duckduckgo(query: str) -> str:
        Searches DuckDuckGo for the given query and returns a summary.
    extract_code(response: str) -> str:
        Extracts code from a response string enclosed in triple backticks.
    run_python_code(code: str) -> str:
        Runs the provided Python code and returns the output or an error message.
    """
    def __init__(self):
        self.messages = []
        self.max_messages = 10
        self.client = Groq(api_key=groqKey)

    def encode_image(self, image_path: str):
        with open(image_path, "rb") as image:
            encoded_image = base64.b64encode(image.read()).decode("utf-8")
        return encoded_image
    
    def generate_text_response(self, text: str) -> str:
        current_time_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        system_message = f"Current time and date: {current_time_date}. Do as directed."

        completion = self.client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": text}
            ],
            temperature=1,
            max_tokens=8192,
            top_p=1,
            stream=False,
            stop=None,
        )

        response = completion.choices[0].message.content
        return str(response)
    
    def generate_text_with_image(self, text: str, image: str):
        api_key = openaiKey
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
                        {"type": "text", "text": text},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            "max_tokens": 300
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        return response.json()['choices'][0]['message']['content']
    
    def live_chat_with_ai(self, text: str):
        current_time_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        system_message = (
            f"Current time and date: {current_time_date}. "
            "You are Fam, an AI voice assistant created by Akshat Kushwaha. "
            "You must answer in brief sentences and in human-like language. "
            "Do not use any styling such as **bold** or _italic_. "
            "Do not return any code. Only provide conversational responses, questions, and answers. "
            "If you feel you lack the information to answer a question, only return 'SEARCH_WIKIPEDIA' or 'SEARCH_DUCKDUCKGO'. "
            "If you need to calculate something or run code, only return 'RUN_PYTHON_CODE'."
        )

        completion = self.client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=self.messages + [
                {"role": "system", "content": system_message},
                {"role": "user", "content": text}
            ],
            temperature=1,
            max_tokens=409,
            top_p=1,
            stream=False,
            stop=None,
        )

        response = completion.choices[0].message.content

        if response and "SEARCH_WIKIPEDIA" in response:
            search_term = text
            wiki_summary = self.search_wikipedia(search_term)
            response = response.replace("SEARCH_WIKIPEDIA", f"```\n{wiki_summary}\n```")
            return self.live_chat_with_ai(f"{text}\n\n{wiki_summary}")

        if response and "SEARCH_DUCKDUCKGO" in response:
            search_term = text
            duckduckgo_summary = self.search_duckduckgo(search_term)
            response = response.replace("SEARCH_DUCKDUCKGO", f"```\n{duckduckgo_summary}\n```")
            return self.live_chat_with_ai(f"{text}\n\n{duckduckgo_summary}")

        if response and "RUN_PYTHON_CODE" in response:
            code_to_run = self.extract_code(response)
            code_output = self.run_python_code(code_to_run)
            if code_output is None:
                code_output = "Failed to respond."
            response = response.replace("RUN_PYTHON_CODE", f"```\n{code_output}\n```")
            return self.live_chat_with_ai(f"{text}\n\n{code_output}")

        self.messages.append({"role": "assistant", "content": response})
        return response

    @lru_cache(maxsize=32)
    def search_wikipedia(self, query: str) -> str:
        wiki_wiki = wikipediaapi.Wikipedia('en')
        page = wiki_wiki.page(query)
        if page.exists():
            return page.summary[:200]  # Limit the summary to 200 characters
        else:
            return "Sorry, I couldn't find any information on Wikipedia for that topic."
    
    @lru_cache(maxsize=32)
    def search_duckduckgo(self, query: str) -> str:
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }
        response = requests.get(url, params=params)
        data = response.json()

        if "AbstractText" in data and data["AbstractText"]:
            return data["AbstractText"]
        elif "RelatedTopics" in data and data["RelatedTopics"]:
            return data["RelatedTopics"][0]["Text"]
        else:
            return "Sorry, I couldn't find any information on that topic."
    
    def extract_code(self, response: str) -> str:
        start = response.find("```") + 3
        end = response.rfind("```")
        return response[start:end].strip()
    
    def run_python_code(self, code: str) -> str:
        try:
            result = subprocess.run(
                ["python", "-c", code],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"Error: {e}"