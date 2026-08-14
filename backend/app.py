"""
BuildsHub - Tira-Dúvidas
Backend Flask que guarda a GEMINI_API_KEY em segurança e expõe um endpoint
/api/chat que o frontend do site chama. A chave NUNCA fica exposta no navegador.
"""

import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai


load_dotenv()

app = Flask(__name__)

# Em produção, troque "*" pelo domínio real do seu site
# (ex: origins=["https://buildshub.com.br"])
CORS(app, resources={r"/api/*": {"origins": "*"}})

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "Defina a variável de ambiente GEMINI_API_KEY antes de rodar o servidor."
    )

genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-3.5-flash"

SYSTEM_PROMPT = (
    "Você é o assistente de tira-dúvidas do BuildsHub, um site brasileiro de "
    "montagem de PC e comparação de preços. Responda perguntas sobre "
    "hardware, compatibilidade de peças, escolha de componentes, gargalo "
    "(bottleneck), fontes de alimentação, refrigeração e montagem de PC. "
    "Responda sempre em português do Brasil, de forma clara, direta e "
    "objetiva, sem enrolação. Se a pergunta não tiver relação com PCs/"
    "hardware, explique educadamente que você só ajuda com esse assunto."
)

model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    system_instruction=SYSTEM_PROMPT,
)

# Histórico em memória por sessão (simples, ideal para demo/portfólio).
# Para produção com muitos usuários, troque por Redis ou similar.
sessions = {}

MAX_HISTORY_MESSAGES = 20  # limita o tamanho do histórico guardado por sessão


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    session_id = (data.get("session_id") or "default").strip()

    if not user_message:
        return jsonify({"error": "Mensagem vazia."}), 400

    if len(user_message) > 2000:
        return jsonify({"error": "Mensagem muito longa (máx. 2000 caracteres)."}), 400

    history = sessions.get(session_id, [])

    try:
        chat_session = model.start_chat(history=history)
        response = chat_session.send_message(user_message)
        reply_text = response.text

        sessions[session_id] = chat_session.history[-MAX_HISTORY_MESSAGES:]

        return jsonify({"reply": reply_text})

    except Exception as exc:
        app.logger.error(f"Erro ao chamar Gemini: {exc}")
        return jsonify({"error": "Não foi possível obter resposta agora. Tente novamente."}), 502


@app.route("/api/chat/reset", methods=["POST"])
def reset_chat():
    data = request.get_json(silent=True) or {}
    session_id = (data.get("session_id") or "default").strip()
    sessions.pop(session_id, None)
    return jsonify({"status": "ok"})


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "up"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
