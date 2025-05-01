from flask import Flask, request, Response, render_template
from chatbot_llama3 import KnowledgeBase, Chatbot

# Initialize Flask app
app = Flask(__name__)

# Updated FAISS index folder path (not .idx file)
####Upate File Path below if needed or location changed#####
FAISS_INDEX_DIR = "/chatbot-rag/vector_store"

# Initialize chatbot
print("Initializing chatbot with Llama 3.2...")
knowledge_base = KnowledgeBase(FAISS_INDEX_DIR)
chatbot = Chatbot(knowledge_base)
print("Chatbot initialized successfully!")

@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/ask_stream")
def ask_stream():
    question = request.args.get("question", "")
    mode = request.args.get("mode", "traditional") # fallback to 'traditional'
    
    def generate():
        for chunk in chatbot.stream_answer(question, mode):
            yield f"data: {chunk}\n\n"

    return Response(generate(), content_type='text/event-stream')

@app.route("/fallback", methods=["POST"])
def fallback():
    data = request.json
    question = data.get("question", "")
    answer = chatbot._fallback_response(question)
    return {"answer": f"<pre>{answer}</pre>"}  # Wrap fallback in <pre> for nicer formatting

if __name__ == "__main__":
    app.run(debug=True, port=5001, threaded=True)
