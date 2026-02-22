import pyperclip
import tempfile
import os
import platform
import subprocess
from PIL import Image, ImageTk, ImageGrab
from typing import Optional, Tuple

class ImageUtils:
    @staticmethod
    def get_clipboard_image() -> Optional[str]:
        """
        Gets image from clipboard and saves it to a temp file.
        Returns the path to the temp file or None.
        """
        img = ImageGrab.grabclipboard()
        if not img or not isinstance(img, Image.Image):
            return None

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        img.save(tmp.name, 'PNG')
        return tmp.name

    @staticmethod
    def process_image_for_display(image_path: str, size: Tuple[int, int] = (100, 100)) -> ImageTk.PhotoImage:
        """
        Opens an image from path and resizes it for display.
        """
        img = Image.open(image_path)
        img.thumbnail(size)
        return ImageTk.PhotoImage(img)

def get_clipboard_text() -> str:
    try:
        return pyperclip.paste()
    except Exception:
        return ""

def save_temp_file(data: bytes, suffix: str) -> str:
    """Saves bytes to a temporary file and returns the path."""
    try:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(data)
        tmp.close()
        return tmp.name
    except Exception as e:
        print(f"Error saving temp file: {e}")
        return ""

def play_audio(file_path: str):
    """Plays the audio file using the system default player."""
    if not os.path.exists(file_path):
        return

    system = platform.system()
    try:
        if system == 'Windows':
            os.startfile(file_path)
        elif system == 'Darwin':  # macOS
            subprocess.call(('open', file_path))
        else:  # Linux
            subprocess.call(('xdg-open', file_path))
    except Exception as e:
        print(f"Error playing audio: {e}")
