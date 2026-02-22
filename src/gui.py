import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from .anki_client import AnkiClient
from .genai_client import GenAIClient
from .utils import ImageUtils, get_clipboard_text
from .config import ANKI_DECK_NAME

class MiningApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Minado de Oraciones con Imágenes")
        self.root.geometry("600x750")

        self.anki_client = AnkiClient()
        self.genai_client = GenAIClient()
        self.image_path = None
        self.img_tk = None

        self._setup_ui()
        self._bind_shortcuts()

    def _setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Input Section
        input_frame = ttk.LabelFrame(main_frame, text="Entrada", padding="10")
        input_frame.pack(fill=tk.X, pady=5)

        ttk.Label(input_frame, text="Frase:").grid(row=0, column=0, sticky=tk.W)
        self.phrase_text = tk.Text(input_frame, height=4, width=50)
        self.phrase_text.grid(row=1, column=0, columnspan=2, pady=5)

        ttk.Button(input_frame, text="Pegar (Ctrl+T)", command=self.paste_text).grid(row=2, column=0, sticky=tk.W)

        ttk.Label(input_frame, text="Palabra desconocida:").grid(row=3, column=0, sticky=tk.W, pady=(10, 0))
        self.word_text = tk.Text(input_frame, height=1, width=50)
        self.word_text.grid(row=4, column=0, columnspan=2, pady=5)

        ttk.Label(input_frame, text="Fuente (tags):").grid(row=5, column=0, sticky=tk.W, pady=(10, 0))
        self.source_text = tk.Text(input_frame, height=1, width=50)
        self.source_text.grid(row=6, column=0, columnspan=2, pady=5)

        ttk.Button(input_frame, text="Obtener Significado", command=self.fetch_meaning).grid(row=7, column=0, columnspan=2, pady=10)

        # Meaning Section
        meaning_frame = ttk.LabelFrame(main_frame, text="Significado", padding="10")
        meaning_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.meaning_text = tk.Text(meaning_frame, height=6, width=50)
        self.meaning_text.pack(fill=tk.BOTH, expand=True)

        # Image Section
        image_frame = ttk.LabelFrame(main_frame, text="Imagen", padding="10")
        image_frame.pack(fill=tk.X, pady=5)

        btn_frame = ttk.Frame(image_frame)
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="Seleccionar Imagen", command=self.select_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Quitar Imagen", command=self.remove_image).pack(side=tk.LEFT, padx=5)
        ttk.Label(btn_frame, text="(Ctrl+V para pegar)").pack(side=tk.LEFT, padx=5)

        self.img_label = ttk.Label(image_frame)
        self.img_label.pack(pady=5)

        # Action Section
        action_frame = ttk.Frame(main_frame, padding="10")
        action_frame.pack(fill=tk.X)

        ttk.Button(action_frame, text="Agregar a Anki", command=self.add_to_anki).pack(fill=tk.X, pady=5)

    def _bind_shortcuts(self):
        self.root.bind('<Control-v>', lambda e: self.paste_image())
        self.root.bind('<Control-V>', lambda e: self.paste_image())
        self.root.bind('<Control-t>', lambda e: self.paste_text())

    def paste_text(self):
        text = get_clipboard_text()
        if text:
            self.phrase_text.delete("1.0", tk.END)
            self.phrase_text.insert("1.0", text)

    def paste_image(self, event=None):
        path = ImageUtils.get_clipboard_image()
        if path:
            self.image_path = path
            self._update_image_preview()
        else:
            messagebox.showwarning("Advertencia", "No hay imagen válida en el portapapeles.")

    def select_image(self):
        path = filedialog.askopenfilename(
            title="Selecciona una imagen",
            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if path:
            self.image_path = path
            self._update_image_preview()

    def remove_image(self):
        self.image_path = None
        self.img_label.config(image='')
        self.img_tk = None

    def _update_image_preview(self):
        if self.image_path:
            self.img_tk = ImageUtils.process_image_for_display(self.image_path)
            self.img_label.config(image=self.img_tk)

    def fetch_meaning(self):
        phrase = self.phrase_text.get("1.0", tk.END).strip()
        word = self.word_text.get("1.0", tk.END).strip()
        source = self.source_text.get("1.0", tk.END).strip()

        if not phrase:
            messagebox.showwarning("Advertencia", "Por favor, ingresa una frase.")
            return

        # Show loading indicator (simple cursor change)
        self.root.config(cursor="wait")
        self.root.update()

        try:
            meaning = self.genai_client.generate_meaning(word, phrase, source)
            self.meaning_text.delete("1.0", tk.END)
            self.meaning_text.insert("1.0", meaning)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.root.config(cursor="")

    def add_to_anki(self):
        phrase = self.phrase_text.get("1.0", tk.END).strip()
        meaning = self.meaning_text.get("1.0", tk.END).strip()
        word = self.word_text.get("1.0", tk.END).strip()
        tags_str = self.source_text.get("1.0", tk.END).strip()
        tags = [t.strip() for t in tags_str.split(",")] if tags_str else []

        if not phrase or not meaning:
            messagebox.showwarning("Advertencia", "Llena frase y significado antes de añadir.")
            return

        result = self.anki_client.add_note(
            deck_name=ANKI_DECK_NAME,
            sentence=phrase,
            word=word,
            definition=meaning,
            tags=tags,
            image_path=self.image_path
        )

        if result.get('error'):
            messagebox.showerror("Error Anki", result['error'])
        else:
            messagebox.showinfo("Éxito", "Tarjeta añadida a Anki")
            self._clear_fields()

    def _clear_fields(self):
        self.phrase_text.delete("1.0", tk.END)
        self.word_text.delete("1.0", tk.END)
        self.source_text.delete("1.0", tk.END)
        self.meaning_text.delete("1.0", tk.END)
        self.remove_image()

def run():
    root = tk.Tk()
    app = MiningApp(root)
    root.mainloop()
