import base64
import requests
from groq import Groq
import wikipediaapi
import datetime
import yaml
import subprocess
from functools import lru_cache
from difflib import SequenceMatcher
from typing import Optional

with open('conf/config.yaml', 'r') as file:
    config = yaml.safe_load(file)
groqKey = config['main']['groq_api_key']
openaiKey = config['main']['openai_api_key']

class Generation:
    def __init__(self):
        self.messages = []
        self.max_messages = 10
        self.client = Groq(api_key=groqKey)

    def encode_image(self, image_path: str) -> str:
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
        return str(response) if response is not None else ""
    
    def generate_text_with_image(self, text: str, image: str) -> str:
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
    
    def live_chat_with_ai(self, text: str) -> str:
        current_time_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        system_message = (
            f"Current time and date: {current_time_date}. "
            "You are Fam, an AI voice assistant created by Akshat Singh Kushwaha. "
            "When you need up-to-date information, use 'SEARCH_WEB <query>' to search the web. "
            "Replace the 'SEARCH_WEB <query>' command in your response with the actual search results. "
            "Provide correct and factual answers, and utilize available tools when necessary. "
            "Respond thoroughly without stating any limitations or knowledge cutoffs."
        )

        self.messages = [{"role": "system", "content": system_message}]
        self.messages.append({"role": "user", "content": text})

        last_response = ""
        while True:
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
            if response is None:
                return ""

            # Process special commands in the assistant's response
            if "SEARCH_WEB" in response:
                search_term = self.extract_command_argument(response, "SEARCH_WEB")
                if search_term:
                    web_summary = self.search_web(search_term)
                    # Replace the command with the search results
                    modified_response = response.replace(f"SEARCH_WEB {search_term}", web_summary)
                    self.messages.append({"role": "assistant", "content": modified_response})
                    # Continue the loop to allow the assistant to refine its response if needed
                    last_response = modified_response
                    continue
            else:
                # Prevent infinite loops by checking for similar responses
                if self.is_similar_response(response, last_response):
                    self.messages.append({"role": "assistant", "content": response})
                    return response
                last_response = response
                self.messages.append({"role": "assistant", "content": response})
                return response

    def extract_command_argument(self, response: str, command: str) -> Optional[str]:
        if not response:
            return None
        # Make command detection case-insensitive and trim whitespace
        command_lower = command.lower()
        response_lower = response.lower()
        start = response_lower.find(command_lower)
        if start == -1:
            return None
        start += len(command)
        end = response.find("\n", start)
        if end == -1:
            end = len(response)
        return response[start:end].strip()

    def is_similar_response(self, new_response: str, last_response: str, threshold: float = 0.98) -> bool:
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
            
    def extract_code(self, response: str) -> Optional[str]:
        if not response:
            return None
        start = response.find("```") + 3
        end = response.rfind("```")
        return response[start:end].strip() if start > 3 and end > start else None
 
    def search_web(self, query: str) -> str:
        import requests

        api_key = config['main']['serpapi_api_key']
        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
        }

        try:
            response = requests.get("https://serpapi.com/search", params=params, timeout=10)
            data = response.json()

            if "error" in data:
                return f"Search error: {data['error']}"

            snippets = []
            if "answer_box" in data and "snippet" in data["answer_box"]:
                snippets.append(data["answer_box"]["snippet"])
            elif "organic_results" in data:
                for result in data["organic_results"][:3]:
                    snippet = result.get("snippet") or result.get("title")
                    if snippet:
                        snippets.append(snippet)

            if snippets:
                return "\n\n".join(snippets)
            else:
                return "No relevant results found."

        except Exception as e:
            return f"An error occurred during web search: {str(e)}"
    
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
        