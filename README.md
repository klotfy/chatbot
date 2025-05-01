# Retrieval-Augmented Chatbot

This is a Flask-based chatbot that uses local document retrieval, FAISS indexing, and LLM-based answering via [Ollama](https://ollama.com/) to provide **structured, sourced responses** in Markdown format.

---

## Features
- Uses FAISS for semantic similarity search
- Renders AI answers with structured Markdown (`##` headers, `-` bullets, block quotes)
- Streamed responses (event-based)
- Supports multiple prompt styles (e.g., "traditional", "academic")
- Includes Dark Mode toggle

---

## Setup

### 1. Clone and set up virtual environment
```bash
git clone https://github.com/klotfy/chatbot
cd chatbot
python3 -m venv venv
source venv/bin/activate  # OR venv\Scripts\activate (Windows)
pip install -r requirements.txt
```

## Folder Structure For the Project
```
chatbot-rag/
├── app.py                  # Flask app
├── chatbot_llama3.py      # RAG + streaming logic
├── ingest_jsonl.py        # Vectorization and indexing
├── requirements.txt       # Python dependencies
│
├── data/
│   └── raw/               # Place your .jsonl files here
│
├── prompts/               # Markdown prompt templates per style
│   └── traditional.md
│
├── static/                # JS and CSS for frontend
│   ├── chat.js
│   └── chat.css
│
├── templates/             # Flask frontend HTML
│   └── chat.html
```

---
### 2. Install and run Ollama
Install Ollama from [ollama.com](https://ollama.com/) and run the model:
```bash
ollama run llama3
```

### 3. Prepare your data
- All data must be in `.jsonl` format.
- Each line must be a valid JSON object with fields like:
```json
{"author": "St. Cyril", "book": "On the Unity of Christ", "content": "Christ is one nature..."}
```
- Keep your files in the `/data/raw/` folder. ## add the full folder path
- Maintain consistent keys across all entries.

### 4. Ingest data into FAISS index
```bash
python ingest_jsonl.py
```

---

## Running the Chatbot
```bash
python app.py
```
Go to [http://localhost:5001](http://localhost:5001) in your browser.

---



## Prompt Templates
- Each prompt `.md` file should end with:
```markdown
---
### Context:
{context}

---
### Question:
{question}

---
### Answer:
```
- Include an example response using proper Markdown formatting above that.

---

## Things to Check
- Is your `.jsonl` data clean and structured?
- Do prompt files contain clear formatting examples?
- Are Markdown answers rendering with correct structure?
- Is the model being instructed to only answer using context?

---

## License
MIT

---
