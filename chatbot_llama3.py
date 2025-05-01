import os
import json
import faiss
import requests
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

class KnowledgeBase:
     def __init__(self, vector_store_path: str):
        # Load FAISS index and embedding model
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/multi-qa-MiniLM-L6-cos-v1"
        )
        self.db = FAISS.load_local(
            folder_path=vector_store_path,
            embeddings=self.embedding_model,
            allow_dangerous_deserialization=True
        )

        self.retriever = self.db.as_retriever(search_kwargs={"k": 5})
        print("FAISS index and embedding model loaded.")

    def get_relevant_contexts(self, query: str) -> List[str]:
        results: List[Document] = self.retriever.get_relevant_documents(query)
        return [doc.page_content for doc in results if doc.page_content.strip()]
class Chatbot:
    def __init__(self, knowledge_base: KnowledgeBase, model_name: str = "llama3.2"):
        self.knowledge_base = knowledge_base
        self.model_name = model_name

        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                print(f"Connected to Ollama, model: {self.model_name}")
            else:
                print("Ollama API responded, but not with 200 OK.")
        except Exception as e:
            print(f" Could not connect to Ollama: {e}")
            print("Run: `ollama run llama3.2` if not already running.")
    #print(f"Using prompt: prompts/{mode}.md")
  
    def build_prompt(self, question: str, context_chunks: List[str], mode: str = "formal") -> str:
        from pathlib import Path

        context_text = "\n\n".join(context_chunks[:5]).strip()
        prompt_path = Path(f"/chatbot-rag/prompts/coptic_{mode}.md") ##update with your naming convention
        ##changePathabove
        if not prompt_path.exists():
            prompt_path = Path("/chatbot-rag/prompts/formal.md")
            ## Update Path above

        template = prompt_path.read_text()

        prompt = template.format(
            context=context_text,
            question=question.strip()
        ).strip() + "\n\n"

        return prompt
    def stream_answer(self, question: str, mode: str = "traditional"):
        contexts = self.knowledge_base.get_relevant_contexts(question)
        if not contexts:
            yield "Sorry, I couldn't find anything relevant in the database. Try rephrasing."

        prompt = self.build_prompt(question, contexts, mode)

        try:
            with requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": True,
                    "temperature": 0.3,
                    "system": "You are a Coptic Orthodox assistant. Using only strict set of data",

                },
                stream=True,
            ) as r:
                for line in r.iter_lines():
                    if line:
                        try:
                            parsed = json.loads(line.decode("utf-8"))
                            chunk = parsed.get("response", "")
                            #print("Raw model output chunk:", chunk)
                            if chunk:
                                yield chunk
                        except Exception as e:
                            print(f"[Stream Parse Error] {e}")
                            continue
        except Exception as e:
            yield f"Failed to connect to model: {e}"