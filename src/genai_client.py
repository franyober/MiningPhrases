from google import genai
from .config import GEMINI_API_KEY, GEMINI_MODEL

class GenAIClient:
    def __init__(self, api_key: str = GEMINI_API_KEY):
        if not api_key:
            raise ValueError("GEMINI_KEY_API environment variable not set")
        self.client = genai.Client(api_key=api_key)
        self.model = GEMINI_MODEL

    def generate_meaning(self, word: str, context: str, source: str = "") -> str:
        prompt = (f"Explain the meaning of '{word}' in this context:\n- Sentence: '{context}'" +
                  (f"\n- Source: {source}" if source else "") +
                  "\nAnswer concisely in English: 1) Meaning (max 15 words). 2) Part of speech. 3) Example sentence.")

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0.2,
                    top_p=0.3
                )
            )
            return response.text
        except Exception as e:
            return f"Error API: {str(e)}"
