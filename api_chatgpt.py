import openai
import requests
from flask import Flask, request, jsonify
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 🌐 URL da sua API de busca
API_URL = "https://api-excel-bot.onrender.com/buscar"

# Criando a API do bot
app = Flask(__name__)

# Função para buscar dados na API externa
def buscar_referencia(codigo):
    url = f"{API_URL}?Codigo%20da%20Referencia={codigo}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()  # Retorna os dados encontrados
    except requests.exceptions.HTTPError as http_err:
        return {"erro": f"Falha na comunicação com a API: {http_err}"}
    except requests.exceptions.RequestException as err:
        return {"erro": f"Erro inesperado ao conectar com a API: {err}"}

# Ping para testar se a API está no ar
@app.route('/ping')
def ping():
    return "pong", 200

# Função para chamar o ChatGPT e interpretar a intenção
def interpretar_mensagem(user_message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um assistente que interpreta a intenção do usuário. Se ele quiser buscar uma referência, extraia o código e informe isso."},
                {"role": "user", "content": user_message}
            ],
            api_key=OPENAI_API_KEY
        )
        return response["choices"][0]["message"]["content"]
    except openai.error.OpenAIError as e:
        return f"Erro ao se comunicar com OpenAI: {str(e)}"

# Endpoint do chatbot
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "").strip()  # Evita erro de NoneType

    if not user_message:
        return jsonify({"response": "Mensagem vazia. Por favor, envie uma pergunta válida."})

    # Primeiro, deixamos o ChatGPT interpretar a intenção
    resposta_chatgpt = interpretar_mensagem(user_message)

    # Se a resposta indicar que é uma busca, extraímos o código e buscamos na API
    if "buscar referência" in resposta_chatgpt.lower():
        codigo = "".join(filter(str.isdigit, user_message))  # Pega apenas os números da mensagem
        if codigo:
            resultado = buscar_referencia(codigo)
            return jsonify({"response": resultado})
        else:
            return jsonify({"response": "Não consegui identificar um código de referência na sua mensagem."})

    # Caso contrário, retornamos a resposta normal da IA
    return jsonify({"response": resposta_chatgpt})

# Rodar o servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

