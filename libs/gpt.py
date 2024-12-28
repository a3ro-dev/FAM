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
import json 
import openai

with open('conf/secrets.yaml', 'r') as file:
    config = yaml.safe_load(file)
groqKey = config['main']['groq_api_key']
openaiKey = config['main']['openai_api_key']

class Generation:
    """
    A class for handling AI-powered text generation and chat functionality.

    This class provides methods for generating text responses using the Groq API,
    analyzing images using OpenAI's API, and conducting live chat sessions with web search integration.

    Attributes:
        messages (list): List of conversation messages.
        max_messages (int): Maximum number of messages to store.
        client (Groq): Groq API client instance.
    """

    def __init__(self):
        self.messages = []
        self.max_messages = 10
        self.client = Groq(api_key=groqKey)
        openai.api_key = openaiKey

    def encode_image(self, image_path: str) -> str:
        """
        Encode an image file to base64 format.

        Args:
            image_path (str): Path to the image file.

        Returns:
            str: Base64 encoded string of the image.
        """
        with open(image_path, "rb") as image:
            encoded_image = base64.b64encode(image.read()).decode("utf-8")
        return encoded_image
    
    def generate_text_response(self, text: str) -> str:
        """
        Generate a text response using the Groq API.

        Args:
            text (str): Input text prompt.

        Returns:
            str: Generated text response.
        """
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
        """
        Generate a text response based on both text and image input using OpenAI's API.

        Args:
            text (str): Text prompt to analyze the image.
            image (str): Path to the image file.

        Returns:
            str: Generated response describing the image and addressing the text prompt.
        """
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
        """
        Conduct a live chat session with AI using OpenAI's gpt-4o-mini model and web search tool calling.
        """
        import json
        current_time_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        system_message = (
            f"Current time and date: {current_time_date}. "
            "You are Fam, an AI voice assistant created by Akshat Singh Kushwaha. "
            "You can search the web for current information using the function search_web. "
            "Only call search_web when a user needs up-to-date info."
        )
        self.messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": text},
        ]

        functions = [{
            "name": "search_web",
            "description": "Search the web for current information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            },
        }]

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.messages,
            functions=functions,
            function_call="auto",
            temperature=0.7,
            max_tokens=2048,
        )

        response_msg = response.choices[0].message
        if response_msg.get("function_call"):
            try:
                call_name = response_msg["function_call"]["name"]
                args = json.loads(response_msg["function_call"]["arguments"])
                if call_name == "search_web":
                    result = self.search_web(args.get("query", ""))
                    self.messages.append(response_msg)
                    self.messages.append({
                        "role": "function",
                        "name": "search_web",
                        "content": result,
                    })
                    second_response = openai.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=self.messages,
                        temperature=0.7,
                        max_tokens=2048,
                    )
                    return second_response.choices[0].message.content
            except Exception as e:
                return f"Error calling function: {e}"

        return response_msg["content"]
    
    def extract_command_argument(self, response: str, command: str) -> Optional[str]:
        """
        Extract the argument for a given command from the response text.

        Args:
            response (str): The response text containing the command.
            command (str): The command to search for.

        Returns:
            Optional[str]: The extracted argument, or None if the command is not found.
        """
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
        """
        Check if the new response is similar to the last response based on a similarity threshold.

        Args:
            new_response (str): The new response text.
            last_response (str): The last response text.
            threshold (float): Similarity threshold (default is 0.98).

        Returns:
            bool: True if the responses are similar, False otherwise.
        """
        similarity = SequenceMatcher(None, new_response, last_response).ratio()
        return similarity > threshold

    @lru_cache(maxsize=32)
    def search_wikipedia(self, query: str) -> str:
        """
        Search Wikipedia for a given query and return a summary.

        Args:
            query (str): The search query.

        Returns:
            str: Summary of the Wikipedia page, or an error message if the page does not exist.
        """
        wiki_wiki = wikipediaapi.Wikipedia('en')
        page = wiki_wiki.page(query)
        if page.exists():
            return page.summary[:200]  # Limit the summary to 200 characters
        else:
            return "Sorry, I couldn't find any information on Wikipedia for that topic."
            
    def extract_code(self, response: str) -> Optional[str]:
        """
        Extract code block from the response text.

        Args:
            response (str): The response text containing the code block.

        Returns:
            Optional[str]: The extracted code block, or None if no code block is found.
        """
        if not response:
            return None
        start = response.find("```") + 3
        end = response.rfind("```")
        return response[start:end].strip() if start > 3 and end > start else None
 
    def search_web(self, query: str) -> str:
        """
        Perform a web search using the SerpAPI and return the search results.

        Args:
            query (str): The search query.

        Returns:
            str: Search results or an error message if the search fails.
        """
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
        """
        Execute a Python code snippet and return the output.

        Args:
            code (str): The Python code to execute.

        Returns:
            str: The output of the executed code, or an error message if execution fails.
        """
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
