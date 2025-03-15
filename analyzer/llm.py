import os
from openai import OpenAI

API_BASE_URL = "https://api.lambdalabs.com/v1"
MODEL = "llama3.3-70b-instruct-fp8"

class LLM:
    def __init__(
            self,
            model: str = MODEL,
            base_url: str = API_BASE_URL,
    ):
        api_key = os.environ.get("LLM_API_KEY", "API_KEY")
        self.client = OpenAI(
            api_key=api_key, 
            base_url=base_url
        )
        self.model = model
    
    def prompt(self, system: str, user: str, temperature: int = 0.1) -> str:
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            model=self.model,
            temperature=temperature
        )
        return response.choices[0].message.content