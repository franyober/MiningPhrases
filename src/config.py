import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_KEY_API")
ANKI_CONNECT_URL = os.getenv("ANKI_CONNECT_URL", "http://localhost:8765")
GEMINI_MODEL = "gemini-2.0-flash"

# Anki Settings
ANKI_DECK_NAME = "English"
ANKI_MODEL_NAME = "vocabsieve-notes"
