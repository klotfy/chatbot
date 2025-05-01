// ✅ chat.js – Updated to buffer entire response before rendering Markdown

const chatBox = document.getElementById('chat-box');
const input = document.getElementById('question-input');
const button = document.getElementById('send-button');

function appendMessage(content, sender) {
  const msg = document.createElement('div');
  msg.className = `message ${sender}`;

  if (sender === 'bot') {
    msg.innerHTML = marked.parse(content, { sanitize: false });
  } else {
    msg.textContent = content;
  }

  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function askQuestion() {
  const question = input.value.trim();
  const mode = document.getElementById('mode-select').value;
  if (!question) return;

  appendMessage(question, 'user');
  input.value = '';

  const response = await fetch(`/ask_stream?question=${encodeURIComponent(question)}&mode=${encodeURIComponent(mode)}`);
  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');

  let buffer = '';
  let fullAnswer = '';
  appendMessage('', 'bot');
  const botMessage = chatBox.querySelector('.message.bot:last-child');

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const chunks = buffer.split('\n\n');
    buffer = chunks.pop(); // preserve incomplete piece

    chunks.forEach(chunk => {
      if (chunk.startsWith('data: ')) {
        const content = chunk.slice(6);
        fullAnswer += content;
      }
    });
  }

  // ✅ Render after full response is complete
  botMessage.innerHTML = marked.parse(fullAnswer, { sanitize: false });
  chatBox.scrollTop = chatBox.scrollHeight;
}

button.addEventListener('click', askQuestion);
input.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') askQuestion();
});
