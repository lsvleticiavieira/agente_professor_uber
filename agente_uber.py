# app.py

import os
import sys
import google.generativeai as genai
from flask import Flask, render_template_string, request, jsonify

# Configura o caminho de busca para que o Python encontre a pasta 'config'
projeto_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(projeto_raiz)
from config import settings

app = Flask(__name__)

# Variáveis globais para o chat e o modelo
conversation_model = None
chat = None

# Configura a API do Gemini
try:
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    
    conversation_model = genai.GenerativeModel(
        'gemini-1.5-flash-latest',
        system_instruction="""
        Você é um assistente simpático e paciente, que ensina pessoas idosas a usar o aplicativo do Uber para pedir uma corrida. 
        Use uma linguagem simples, clara e sem jargões. 
        Evite frases muito longas e use uma abordagem passo a passo. 
        Sua primeira mensagem deve ser: 'Olá! Eu sou o seu professor particular para usar o Uber. Para começar, diga "pronto".'
        """
    )
    
    # Inicia o chat uma vez, quando o aplicativo for carregado
    chat = conversation_model.start_chat(history=[])
    
    print("Modelos Gemini e chat inicializados com sucesso.")
except Exception as e:
    print(f"Erro ao inicializar o modelo Gemini: {e}")
    
# Código HTML da interface do chat
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Chat com o Professor Uber</title>
    <style>
        body { font-family: sans-serif; margin: 2em; }
        #chat-box { border: 1px solid #ccc; padding: 1em; height: 400px; overflow-y: scroll; margin-bottom: 1em; }
        .user-message { text-align: right; color: blue; }
        .assistant-message { text-align: left; color: green; }
        input[type="text"] { width: 80%; padding: 0.5em; }
        button { padding: 0.5em 1em; }
    </style>
</head>
<body>
    <h1>Professor Particular do Uber</h1>
    <div id="chat-box"></div>
    <form id="chat-form">
        <input type="text" id="user-input" placeholder="Digite sua mensagem...">
        <button type="submit">Enviar</button>
    </form>

    <script>
        document.addEventListener("DOMContentLoaded", function() {
            const chatForm = document.getElementById("chat-form");
            const chatBox = document.getElementById("chat-box");
            const userInput = document.getElementById("user-input");

            function addMessage(sender, message) {
                const p = document.createElement("p");
                p.textContent = message;
                p.className = sender + "-message";
                chatBox.appendChild(p);
                chatBox.scrollTop = chatBox.scrollHeight;
            }

            // Exibe a mensagem inicial do assistente
            addMessage("assistant", "Olá! Eu sou o seu professor particular para usar o Uber. Para começar, diga 'pronto'.");
            
            chatForm.addEventListener("submit", function(event) {
                event.preventDefault();
                const message = userInput.value;
                if (message.trim() === "") return;

                addMessage("user", message);
                userInput.value = "";

                fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_message: message })
                })
                .then(response => response.json())
                .then(data => {
                    addMessage("assistant", data.assistant_response);
                });
            });
        });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/chat", methods=["POST"])
def chat_route():
    if chat is None:
        return jsonify({"assistant_response": "Erro: O chat não foi inicializado corretamente."}), 500
        
    data = request.json
    user_message = data.get("user_message")

    try:
        gemini_response = chat.send_message(user_message)
        assistant_response = gemini_response.text
        return jsonify({"assistant_response": assistant_response})
    except Exception as e:
        return jsonify({"assistant_response": f"Ocorreu um erro na API: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)