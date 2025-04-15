import tkinter as tk
from tkinter import messagebox
import pyperclip
import requests
import json
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()  # take environment variables

gemini_key = os.getenv('GEMINI_KEY_API')

modelo = "gemini-2.0-flash"
# Configuración de Anki Connect
ANKI_CONNECT_URL = "http://localhost:8765"

def anki_connect(action, **params):
    request = {'action': action, 'version': 6, 'params': params}
    response = requests.post(ANKI_CONNECT_URL, data=json.dumps(request))
    return response.json()

def add_to_anki(deck_name, sentence, word, definition, tag):
    # Asegúrate de que el mazo existe
    anki_connect('createDeck', deck=deck_name)
    tags = [tag.strip() for tag in tag.split(",")] if tag else []
    # Añade la tarjeta
    note = {
        "deckName": deck_name,
        "modelName": "vocabsieve-notes",
        "fields": {
            "Sentence": sentence,
            "Word": word,
            "Definition": definition
        },
        "tags": tags,
        "options": {
            "allowDuplicate": False
        }
    }
    result = anki_connect('addNote', note=note)
    if result.get('error'):
        messagebox.showerror("Error", result['error'])
    else:
        messagebox.showinfo("Éxito", "Tarjeta añadida a Anki")

def fetch_meaning():
    phrase = phrase_entry.get("1.0", tk.END).strip()
    word = word_entry.get("1.0", tk.END).strip()
    source= source_entry.get("1.0",tk.END).strip()

    prompt1 = f"""
        I'm learning English through movies/series. Explain the meaning of '{word}' in this context:
        - Sentence: "{phrase}"
        {f"- Source: {source}" if source else ""}
        Answer concisely in English :
        1. Meaning in this context (max 15 words).
        2. Is it noun/verb/adjective/idiom/phrasal verb/slang? (1 word).
        3. Example in another simple sentence (max 15 words).
    
    """

    prompt2 = f"""
        I'm learning English through movies/series. Explain the meaning of this:
        - Sentence: "{phrase}"
        {f"- Source: {source}" if source else ""}
        Answer concisely in English :
        1. Meaning in this context (max 15 words).
        2. Is it noun/verb/adjective/idiom/phrasal verb/slang? (1 word).
        3. Example in another simple sentence (max 15 words).
    """

    if not phrase:
        messagebox.showwarning("Advertencia", "Por favor, copia una frase al portapapeles.")
        return
    
    # Construcción del mensaje
    if word:
        content = prompt1
    else:
        content = prompt2

    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    try:
        response = model.generate_content(content,
            generation_config=genai.types.GenerationConfig(
            temperature=0.2,
            top_p=0.3)
            )
            # Acceder a la respuesta generada
        meaning_entry.delete("1.0", tk.END)
        meaning_entry.insert("1.0", response.text)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar con la API: {e}")


def on_add_to_anki():
    phrase = phrase_entry.get("1.0", tk.END).strip()
    meaning = meaning_entry.get("1.0", tk.END).strip()
    word = word_entry.get("1.0", tk.END).strip()
    tag = source_entry.get("1.0", tk.END).strip()
    
    if not phrase or not meaning:
        messagebox.showwarning("Advertencia", "Por favor, asegúrate de que ambos campos (frase y significado) estén llenos.")
        return
    
    deck_name = "English"  # Cambia esto al nombre de tu mazo en Anki
    add_to_anki(deck_name, phrase, word, meaning, tag)
    clear_fields()

def clear_fields():
    # Borra el contenido de los widgets Text (para multislots)
    phrase_entry.delete("1.0", tk.END)
    meaning_entry.delete("1.0", tk.END)
    word_entry.delete("1.0", tk.END)
    

def paste_from_clipboard():
    try:
        clipboard_content = pyperclip.paste()
        phrase_entry.delete("1.0", tk.END)
        phrase_entry.insert("1.0", clipboard_content)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo acceder al portapapeles: {e}")

# Crear la ventana principal
root = tk.Tk()
root.title("Minado de Oraciones")

# Cuadro de texto para la frase
phrase_label = tk.Label(root, text="Frase copiada:")
phrase_label.pack()
phrase_entry = tk.Text(root, height=5, width=50)
phrase_entry.pack() 

# Botón para pegar desde el portapapeles
paste_button = tk.Button(root, text="Pegar desde Portapapeles", command=paste_from_clipboard)
paste_button.pack()

# Cuadro de texto para la palabra/frase desconocida
word_label = tk.Label(root, text="Palabra/Frase desconocida:")
word_label.pack()
word_entry = tk.Text(root, height=2, width=50)
word_entry.pack()

# Cuadro de texto para contexto
source_label = tk.Label(root, text="Fuente:")
source_label.pack()
source_entry = tk.Text(root, height=2,width=50)
source_entry.pack()

# Botón para iniciar la consulta
fetch_button = tk.Button(root, text="Obtener Significado", command=fetch_meaning)
fetch_button.pack()

# Cuadro de texto para el significado
meaning_label = tk.Label(root, text="Significado:")
meaning_label.pack()
meaning_entry = tk.Text(root, height=15, width=50)
meaning_entry.pack()

# Botón para agregar a Anki
add_button = tk.Button(root, text="Agregar a Anki", command=on_add_to_anki)
add_button.pack()

# Iniciar la aplicación
root.mainloop()
