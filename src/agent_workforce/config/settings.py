# Configuration settings and constants

from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel

# GEMINI API KEY
GEMINI_MODEL = "gemini/gemini-2.0-flash-exp"
GEMINI_API_KEY = "AIzaSyBvfElPEA0pW0cYnjaTzZO4hRMjI7tq6no"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

def create_client() -> AsyncOpenAI:
    """Create and return the OpenAI client"""
    return AsyncOpenAI(
        api_key=GEMINI_API_KEY,
        base_url=GEMINI_BASE_URL
    )

def create_model(client: AsyncOpenAI) -> OpenAIChatCompletionsModel:
    """Create and return the model instance"""
    return OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=client
    )
