# Mining Phrases with AI and Anki

This application allows you to mine phrases, fetch their meanings using Google GenAI, and add them to Anki as flashcards, including images.

## Features

-   **Modular Design**: Clean code structure.
-   **Improved UI**: User-friendly interface with `ttk` widgets.
-   **Google GenAI**: Uses the latest `google-genai` library and free `gemini-2.0-flash` model.
-   **Anki Integration**: Connects to Anki via AnkiConnect.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install .
    ```
    Or manually:
    ```bash
    pip install google-genai pillow pyperclip requests python-dotenv
    ```

2.  **Environment Variables**:
    Create a `.env` file in the root directory with:
    ```env
    GEMINI_KEY_API=your_google_api_key
    ANKI_CONNECT_URL=http://localhost:8765
    ```

3.  **Run**:
    ```bash
    python main.py
    ```

## Requirements

-   Anki with AnkiConnect installed.
-   Google AI Studio API Key.
