import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason, Tool
import vertexai.preview.generative_models as generative_models

class Generation:
    """
    A class that provides methods for generating text responses and encoding images.
    """

    def encode_image(self, image_path):
        """Encode an image to base64 format."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def generate_text_response(self, prompt: str):
        """
        Generate a text response based on the given prompt.

        Args:
            prompt (str): The prompt for generating the text response.

        Returns:
            str: The generated text response.
        """
        vertexai.init(project="caramel-biplane-423714-f8", location="asia-south1")
        tools = [
            Tool.from_google_search_retrieval(
                google_search_retrieval=generative_models.grounding.GoogleSearchRetrieval(disable_attribution=False) #type: ignore
            ),
        ]

        generation_config = {
            "max_output_tokens":8192,
            "temperature": 1,
            "top_p": 0.95,
        }

        safety_settings = {
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }

        model = GenerativeModel(
            "gemini-1.5-flash-preview-0514",
            tools=tools,
        )
        responses = model.generate_content(
            contents=[prompt],
            generation_config=generation_config,
            safety_settings=safety_settings,
        )
        response: str = responses.text #type: ignore
        return response

def generate_text_with_image(self, image_path, prompt):
    """
    Generates text content using an image and a prompt.

    Args:
        image_path (str): The path to the image file.
        prompt (str): The prompt for generating the text content.

    Returns:
        str: The generated text content.
    """
    # Initialize Vertex AI
    vertexai.init(project="caramel-biplane-423714-f8", location="asia-south1")
    
    # Load the generative model
    model = GenerativeModel("gemini-1.5-pro-preview-0514")
    
    encoded_image = self.encode_image(image_path)
    
    # Prepare the image part
    image_part = Part.from_data(
        mime_type="image/jpeg",
        data=encoded_image  # type: ignore
    )
    
    # Configuration settings
    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 1,
        "top_p": 0.95,
    }

    safety_settings = {
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }
    
    # Generate content with the image and prompt
    responses = model.generate_content(
        contents=[image_part, prompt],
        generation_config=generation_config,
        safety_settings=safety_settings
    )
    
    response = responses.text #type: ignore
    return str(response)