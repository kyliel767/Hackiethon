import os
import sys
from groq import Groq

#--------------------------
# ai configuration
#--------------------------
GROQ_MODEL = "llama-3.3-70b-versatile"

class AIClient:
    def __init__(self):
        # load environment variables for API key
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("Missing GROQ_API_KEY in .env")
            sys.exit(1)
        self.client = Groq(api_key=api_key)

    def send_messages(self, messages):
        try:
            response = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                max_tokens=200,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as error:
            # return a fallback response if the API fails
            return f"[AI Error: {error}] [STATUS:ongoing]"