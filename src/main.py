import tkinter as tk
from tkinter import messagebox
import pyperclip
import requests
import json
from dotenv import dotenv_values

config = dotenv_values(".env")

API = config["API"]
modelo = "llama-3.3-70b-versatile"
# Configuración de Anki Connect
ANKI_CONNECT_URL = "http://localhost:8765"

def anki_connect(action, **params):
    request = {'action': action, 'version': 6, 'params': params}
    response = requests.post(ANKI_CONNECT_URL, data=json.dumps(request))
    return response.json()

def add_to_anki(deck_name, sentence, word, definition):
    # Asegúrate de que el mazo existe
    anki_connect('createDeck', deck=deck_name)
    
    # Añade la tarjeta
    note = {
        "deckName": deck_name,
        "modelName": "vocabsieve-notes",
        "fields": {
            "Sentence": sentence,
            "Word": word,
            "Definition": definition
        },
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
    
    if not phrase:
        messagebox.showwarning("Advertencia", "Por favor, copia una frase al portapapeles.")
        return
    
    # Construcción del mensaje
    if word:
        content = f"What does '{word}' mean in the context of the following sentence in a concise way: '{phrase}'?"
    else:
        content = f"What does the following sentence mean in a concise and clear way: '{phrase}'?"
    
    # Llamada a la API de GroqCloud
    api_url = "https://api.groq.com/openai/v1/chat/completions"  # Endpoint de GroqCloud
    headers = {
        "Authorization": f"Bearer {API}",  # Reemplaza con tu clave
        "Content-Type": "application/json"
    }
    data = {
        "model": modelo,  # Modelo soportado por GroqCloud
        "messages": [
            {"role": "user", "content": content}
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=data)
        if response.status_code == 200:
            # Acceder a la respuesta generada
            completion = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No se pudo obtener el significado.")
            meaning_entry.delete("1.0", tk.END)
            meaning_entry.insert("1.0", completion.strip())
        else:
            error_message = response.json().get("error", {}).get("message", "Error desconocido.")
            messagebox.showerror("Error", f"No se pudo obtener el significado: {error_message}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar con la API de GroqCloud: {e}")


def on_add_to_anki():
    phrase = phrase_entry.get("1.0", tk.END).strip()
    meaning = meaning_entry.get("1.0", tk.END).strip()
    word = word_entry.get("1.0", tk.END).strip()
    
    if not phrase or not meaning:
        messagebox.showwarning("Advertencia", "Por favor, asegúrate de que ambos campos (frase y significado) estén llenos.")
        return
    
    deck_name = "English"  # Cambia esto al nombre de tu mazo en Anki
    add_to_anki(deck_name, phrase, word, meaning)
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

# Botón para iniciar la consulta
fetch_button = tk.Button(root, text="Obtener Significado", command=fetch_meaning)
fetch_button.pack()

# Cuadro de texto para el significado
meaning_label = tk.Label(root, text="Significado:")
meaning_label.pack()
meaning_entry = tk.Text(root, height=5, width=50)
meaning_entry.pack()

# Botón para agregar a Anki
add_button = tk.Button(root, text="Agregar a Anki", command=on_add_to_anki)
add_button.pack()

# Iniciar la aplicación
root.mainloop()
