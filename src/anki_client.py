import json
import requests
from typing import Dict, Any, List, Optional
import base64
import os
from .config import ANKI_CONNECT_URL, ANKI_MODEL_NAME

class AnkiClient:
    def __init__(self, url: str = ANKI_CONNECT_URL):
        self.url = url

    def _request(self, action: str, **params) -> Dict[str, Any]:
        payload = {'action': action, 'version': 6, 'params': params}
        try:
            response = requests.post(self.url, data=json.dumps(payload))
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def create_deck(self, deck_name: str) -> None:
        self._request('createDeck', deck=deck_name)

    def add_note(self, deck_name: str, sentence: str, word: str, definition: str,
                 tags: List[str], image_path: Optional[str] = None,
                 audio_path: Optional[str] = None) -> Dict[str, Any]:

        self.create_deck(deck_name)

        note = {
            "deckName": deck_name,
            "modelName": ANKI_MODEL_NAME,
            "fields": {
                "Sentence": sentence,
                "Word": word,
                "Definition": definition,
                "Image": "",
                "Audio": ""
            },
            "tags": tags,
            "options": {"allowDuplicate": False}
        }

        # Handle Image
        if image_path:
            try:
                with open(image_path, "rb") as img_file:
                    img_data = img_file.read()
                    b64_img = base64.b64encode(img_data).decode('utf-8')
                filename_img = os.path.basename(image_path)
                note["picture"] = [{
                    "data": b64_img,
                    "filename": filename_img,
                    "fields": ["Image"]
                }]
            except IOError as e:
                return {'error': f"Failed to read image: {str(e)}"}

        # Handle Audio
        if audio_path:
            try:
                with open(audio_path, "rb") as aud_file:
                    aud_data = aud_file.read()
                    b64_aud = base64.b64encode(aud_data).decode('utf-8')
                filename_aud = os.path.basename(audio_path)
                note["audio"] = [{
                    "data": b64_aud,
                    "filename": filename_aud,
                    "fields": ["Audio"]
                }]
            except IOError as e:
                return {'error': f"Failed to read audio: {str(e)}"}

        return self._request('addNote', note=note)
