import base64
import requests
from groq import Groq
import wikipediaapi
import datetime
import yaml
import subprocess
from functools import lru_cache
from difflib import SequenceMatcher

with open('conf/config.yaml', 'r') as file:
    config = yaml.safe_load(file)
groqKey = config['main']['groq_api_key']
openaiKey = config['main']['openai_api_key']

class Generation:
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
            messages=[{"role": "system", "content": system_message}, {"role": "user", "content": text}],
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
            "You are Fam, an AI voice assistant created by Akshat Singh Kushwaha. "
            "Provide correct and factual answers, and use the available tools when necessary. "
            "Use 'SEARCH_WIKIPEDIA <query>' to search Wikipedia, "
            "'SEARCH_DUCKDUCKGO <query>' for a web search, "
            "'RUN_PYTHON_CODE' followed by code to execute Python code, "
            "Respond thoroughly and do not hesitate to use tokens."
        )

        self.messages.append({"role": "system", "content": system_message})
        self.messages.append({"role": "user", "content": text})

        completion = self.client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=self.messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=False,
            stop=None,
        )

        response = completion.choices[0].message.content

        # Process special commands in the assistant's response
        if "SEARCH_WIKIPEDIA" in response:
            search_term = self.extract_command_argument(response, "SEARCH_WIKIPEDIA")
            wiki_summary = self.search_wikipedia(search_term)
            response = response.replace(f"SEARCH_WIKIPEDIA {search_term}", wiki_summary)
            return self.live_chat_with_ai(f"{text}\n\n{wiki_summary}")

        if "SEARCH_DUCKDUCKGO" in response:
            search_term = self.extract_command_argument(response, "SEARCH_DUCKDUCKGO")
            duckduckgo_summary = self.search_duckduckgo(search_term)
            response = response.replace(f"SEARCH_DUCKDUCKGO {search_term}", duckduckgo_summary)
            return self.live_chat_with_ai(f"{text}\n\n{duckduckgo_summary}")

        if "RUN_PYTHON_CODE" in response:
            code_to_run = self.extract_code(response)
            code_output = self.run_python_code(code_to_run)
            response = response.replace(f"RUN_PYTHON_CODE\n{code_to_run}", code_output)
            return self.live_chat_with_ai(f"{text}\n\n{code_output}")

        self.messages.append({"role": "assistant", "content": response})
        return response

    def extract_command_argument(self, response: str, command: str) -> str:
        # Extract the argument following the command
        start = response.find(command) + len(command)
        end = response.find("\n", start)
        if end == -1:
            end = len(response)
        return response[start:end].strip()

    def is_similar_response(self, new_response: str, last_response: str, threshold: float = 0.9) -> bool:
        similarity = SequenceMatcher(None, new_response, last_response).ratio()
        return similarity > threshold

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