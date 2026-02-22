import pyperclip
import tempfile
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
