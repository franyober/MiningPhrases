import tkinter as tk
from tkinter import messagebox, filedialog
import pyperclip
import requests
import json
from dotenv import load_dotenv
import os
import base64
import tempfile
from PIL import Image, ImageTk, ImageGrab
import google.generativeai as genai

# Cargar variables de entorno
env_path = os.getenv('DOTENV_PATH', '.env')
load_dotenv(env_path)

gemini_key = os.getenv('GEMINI_KEY_API')
modelo = "gemini-2.0-flash"
# Configuración de Anki Connect
ANKI_CONNECT_URL = "http://localhost:8765"

# Variable global para ruta de imagen seleccionada
global image_path
image_path = None


def anki_connect(action, **params):
    request_payload = {'action': action, 'version': 6, 'params': params}
    response = requests.post(ANKI_CONNECT_URL, data=json.dumps(request_payload))
    return response.json()


def add_to_anki(deck_name, sentence, word, definition, tag):
    global image_path
    # Crear mazo si no existe
    anki_connect('createDeck', deck=deck_name)
    tags = [t.strip() for t in tag.split(",")] if tag else []

    # Construir la nota
    note = {
        "deckName": deck_name,
        "modelName": "vocabsieve-notes",
        "fields": {
            "Sentence": sentence,
            "Word": word,
            "Definition": definition,
            "Image": ""
        },
        "tags": tags,
        "options": {"allowDuplicate": False}
    }

    # Si hay imagen, prepararla para Anki
    if image_path:
        with open(image_path, "rb") as img_file:
            img_data = img_file.read()
            b64 = base64.b64encode(img_data).decode('utf-8')
        filename = os.path.basename(image_path)
        note["picture"] = [{
            "data": b64,
            "filename": filename,
            "fields": ["Image"]
        }]

    result = anki_connect('addNote', note=note)
    if result.get('error'):
        messagebox.showerror("Error", result['error'])
    else:
        messagebox.showinfo("Éxito", "Tarjeta añadida a Anki")
        clear_fields()


def fetch_meaning():
    phrase = phrase_entry.get("1.0", tk.END).strip()
    word = word_entry.get("1.0", tk.END).strip()
    source = source_entry.get("1.0", tk.END).strip()

    if not phrase:
        messagebox.showwarning("Advertencia", "Por favor, pega una frase primero.")
        return

    prompt = (f"Explain the meaning of '{word}' in this context:\n- Sentence: '{phrase}'" +
              (f"\n- Source: {source}" if source else "") +
              "\nAnswer concisely in English: 1) Meaning (max 15 words). 2) Part of speech. 3) Example sentence.")

    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel(modelo)

    try:
        response = model.generate_content(prompt,
                                         generation_config=genai.types.GenerationConfig(
                                             temperature=0.2,
                                             top_p=0.3))
        meaning_entry.delete("1.0", tk.END)
        meaning_entry.insert("1.0", response.text)
    except Exception as e:
        messagebox.showerror("Error API", f"No se pudo conectar: {e}")


def on_add_to_anki():
    phrase = phrase_entry.get("1.0", tk.END).strip()
    meaning = meaning_entry.get("1.0", tk.END).strip()
    word = word_entry.get("1.0", tk.END).strip()
    tag = source_entry.get("1.0", tk.END).strip()

    if not phrase or not meaning:
        messagebox.showwarning("Advertencia", "Llena frase y significado antes de añadir.")
        return

    add_to_anki("English", phrase, word, meaning, tag)


def clear_fields():
    global image_path
    phrase_entry.delete("1.0", tk.END)
    word_entry.delete("1.0", tk.END)
    source_entry.delete("1.0", tk.END)
    meaning_entry.delete("1.0", tk.END)
    image_path = None
    img_label.config(image='')  # Limpiar vista previa


def paste_from_clipboard_text():
    try:
        clipboard = pyperclip.paste()
        phrase_entry.delete("1.0", tk.END)
        phrase_entry.insert("1.0", clipboard)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo acceder al portapapeles: {e}")


def paste_image(event=None):
    global image_path, img_tk
    # Intentar obtener imagen del portapapeles
    img = ImageGrab.grabclipboard()
    if not img or not isinstance(img, Image.Image):
        messagebox.showwarning("Advertencia", "No hay imagen en el portapapeles.")
        return
    # Guardar en archivo temporal
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    img.save(tmp.name, 'PNG')
    image_path = tmp.name
    # Vista previa
    img.thumbnail((100, 100))
    img_tk = ImageTk.PhotoImage(img)
    img_label.config(image=img_tk)


def select_image():
    global image_path, img_tk
    path = filedialog.askopenfilename(
        title="Selecciona una imagen",
        filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.gif")]
    )
    if not path:
        return
    image_path = path
    img = Image.open(path)
    img.thumbnail((100, 100))
    img_tk = ImageTk.PhotoImage(img)
    img_label.config(image=img_tk)


def remove_image():
    global image_path
    image_path = None
    img_label.config(image='')

# Iniciar GUI
root = tk.Tk()
root.title("Minado de Oraciones con Imágenes")

# Bindings para pegar texto e imagen
def bind_shortcuts():
    root.bind('<Control-v>', lambda e: paste_image())
    root.bind('<Control-V>', lambda e: paste_image())
    root.bind('<Control-t>', lambda e: paste_from_clipboard_text())  # por si se quiere texto separado

bind_shortcuts()

# Widgets de texto y botones
phrase_label = tk.Label(root, text="Frase copiada:")
phrase_label.pack()
phrase_entry = tk.Text(root, height=5, width=50)
phrase_entry.pack()

paste_btn = tk.Button(root, text="Pegar texto (Ctrl+T)", command=paste_from_clipboard_text)
paste_btn.pack()

word_label = tk.Label(root, text="Palabra/Frase desconocida:")
word_label.pack()
word_entry = tk.Text(root, height=2, width=50)
word_entry.pack()

source_label = tk.Label(root, text="Fuente (tags separados por coma):")
source_label.pack()
source_entry = tk.Text(root, height=2, width=50)
source_entry.pack()

fetch_button = tk.Button(root, text="Obtener Significado", command=fetch_meaning)
fetch_button.pack()

meaning_label = tk.Label(root, text="Significado:")
meaning_label.pack()
meaning_entry = tk.Text(root, height=10, width=50)
meaning_entry.pack()

# Area para seleccionar imagen
def_img_frame = tk.Frame(root)
def_img_frame.pack(pady=5)

img_btn = tk.Button(def_img_frame, text="Seleccionar Imagen", command=select_image)
img_btn.pack(side=tk.LEFT, padx=5)

rmv_btn = tk.Button(def_img_frame, text="Quitar Imagen", command=remove_image)
rmv_btn.pack(side=tk.LEFT, padx=5)

img_label = tk.Label(root)
img_label.pack()

add_button = tk.Button(root, text="Agregar a Anki", command=on_add_to_anki)
add_button.pack(pady=10)

root.mainloop()
