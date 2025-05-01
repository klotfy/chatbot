import os
import json
import glob
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Paths change to proper file path for all three
RAW_DIR = "/chatbot-rag/data/raw"
COMBINED_JSONL = "/chatbot-rag/data/combined_chunks.jsonl"
VECTOR_STORE_DIR = "/chatbot-rag/vector_store"

def load_jsonl_files():
    docs = []
    files = glob.glob(os.path.join(RAW_DIR, "*.jsonl"))
    print(f"📂 Found {len(files)} JSONL files in {RAW_DIR}")

    for path in files:
        print(f"🔍 Reading {path}")
        with open(path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                try:
                    record = json.loads(line)
                    text = record.get("content") or record.get("text")
                    if text and len(text.strip()) > 20:
                        metadata = {
                            "source": os.path.basename(path),
                            "author": record.get("author", ""),
                            "book": record.get("book", "")
                        }
                        docs.append(Document(page_content=text.strip(), metadata=metadata))
                except json.JSONDecodeError:
                    print(f"⚠️ Skipped malformed line {i} in {path}")
    return docs

def chunk_documents(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    return splitter.split_documents(docs)

def save_chunks_to_jsonl(docs):
    with open(COMBINED_JSONL, "w", encoding="utf-8") as f:
        for doc in docs:
            f.write(json.dumps({
                "text": doc.page_content,
                "metadata": doc.metadata
            }) + "\n")
    print(f"💾 Saved {len(docs)} chunks to {COMBINED_JSONL}")

def build_faiss_index(docs):
    print("🧠 Embedding chunks and building FAISS index...")
    embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/multi-qa-MiniLM-L6-cos-v1")
    vectorstore = FAISS.from_documents(docs, embedder)
    vectorstore.save_local(VECTOR_STORE_DIR)
    print(f"✅ Saved FAISS index to {VECTOR_STORE_DIR}")

def main():
    print("📥 Starting JSONL ingestion pipeline...")
    docs = load_jsonl_files()
    print(f"📄 Loaded {len(docs)} raw documents.")

    if not docs:
        print("🚫 No documents to process. Exiting.")
        return

    print("✂️ Chunking documents...")
    chunks = chunk_documents(docs)
    print(f"🧩 Created {len(chunks)} total chunks.")

    if not chunks:
        print("🚫 No chunks created. Exiting.")
        return

    save_chunks_to_jsonl(chunks)
    build_faiss_index(chunks)

if __name__ == "__main__":
    main()
