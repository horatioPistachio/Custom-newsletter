from google import genai
import os
from dotenv import load_dotenv

load_dotenv()  # This looks for the .env file automatically
api_key= os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="how many fingers do i have?",
)

print(response.text)