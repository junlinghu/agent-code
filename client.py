import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI()
model="gpt-4o-mini"