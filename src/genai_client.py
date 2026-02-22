from google import genai
from google.genai import types
import base64
import wave
import io
import os
from .config import GEMINI_API_KEY, GEMINI_MODEL, IMAGEN_MODEL, TTS_MODEL

class GenAIClient:
    def __init__(self, api_key: str = GEMINI_API_KEY):
        if not api_key:
            raise ValueError("GEMINI_KEY_API environment variable not set")
        self.client = genai.Client(api_key=api_key)
        self.model = GEMINI_MODEL
        # Use appropriate models from config
        self.imagen_model = IMAGEN_MODEL
        self.tts_model = TTS_MODEL

    def generate_meaning(self, word: str, context: str, source: str = "") -> str:
        prompt = (f"Explain the meaning of '{word}' in this context:\n- Sentence: '{context}'" +
                  (f"\n- Source: {source}" if source else "") +
                  "\nAnswer concisely in English: 1) Meaning (max 15 words). 2) Part of speech. 3) Example sentence.")

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    top_p=0.3
                )
            )
            return response.text
        except Exception as e:
            return f"Error API: {str(e)}"

    def generate_image_bytes(self, word: str, context: str) -> bytes:
        """Generates an image for the word in context."""
        prompt = f"A realistic illustration of '{word}' in the context of: '{context}'. No text in image."
        try:
            response = self.client.models.generate_images(
                model=self.imagen_model,
                prompt=prompt,
                config=types.GenerateImageConfig(
                    number_of_images=1,
                )
            )
            # Access generated_images[0].image.image_bytes
            # The structure is response.generated_images[0].image.image_bytes
            # Note: Verify if image_bytes is bytes or base64 string.
            # Usually in Python SDK it is bytes.
            return response.generated_images[0].image.image_bytes
        except Exception as e:
            print(f"Image generation error: {e}")
            return None

    def generate_audio_bytes(self, text: str) -> bytes:
        """Generates audio (WAV) for the given text using Gemini TTS."""
        try:
            # Use specific config for TTS
            speech_config = types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Puck"
                    )
                )
            )

            response = self.client.models.generate_content(
                model=self.tts_model,
                contents=f"Say: {text}",
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=speech_config
                )
            )

            # The response contains inline data.
            # SDK usually decodes it to bytes automatically if it's Blob.
            # But let's be careful.
            part = response.candidates[0].content.parts[0]
            if part.inline_data:
                data = part.inline_data.data
                # If it's bytes, good. If it's string, decode.
                if isinstance(data, str):
                    data = base64.b64decode(data)
            else:
                return None

            # Convert PCM to WAV
            # Default is usually 24kHz mono 16-bit
            wav_io = io.BytesIO()
            with wave.open(wav_io, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)
                wf.writeframes(data)

            return wav_io.getvalue()

        except Exception as e:
            print(f"Audio generation error: {e}")
            return None
