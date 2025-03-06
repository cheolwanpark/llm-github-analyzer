from openai import OpenAI

API_BASE_URL = "https://api.lambdalabs.com/v1"
MODEL = "llama3.3-70b-instruct-fp8"

class LLM:
    def __init__(
            self, 
            api_key: str, 
            base_url: str = API_BASE_URL,
            model: str = MODEL
    ):
        self.client = OpenAI(
            api_key=api_key, 
            base_url=base_url
        )
        self.model = model
    
    def prompt(self, system: str, user: str) -> str:
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            model=self.model
        )
        return response.choices[0].message.content