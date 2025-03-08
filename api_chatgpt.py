import openai
import requests
from flask import Flask, request, jsonify
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 🌐 URL da sua API
API_URL = "https://api-excel-bot.onrender.com/buscar"

# Criando a API do bot
app = Flask(__name__)

# Função para buscar dados na sua API
def buscar_referencia(codigo):
    url = f"{API_URL}?Codigo%20da%20Referencia={codigo}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()  # Retorna os dados encontrados
    elif response.status_code == 404:
        return {"erro": "Referência não encontrada"}
    else:
        return {"erro": "Falha na comunicação com a API"}
        
@app.route('/ping')
def ping():
    return "pong", 200

# Função para chamar o ChatGPT
def chat_with_gpt(user_message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Você é um assistente que responde com base na API Excel Bot."},
                  {"role": "user", "content": user_message}],
        api_key=OPENAI_API_KEY
    )
    return response["choices"][0]["message"]["content"]

# Endpoint para o chatbot
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message")

    if "buscar" in user_message.lower():
        codigo = user_message.split()[-1]  # Supondo que o código seja a última palavra
        resultado = buscar_referencia(codigo)
        return jsonify({"response": resultado})
    
    resposta = chat_with_gpt(user_message)
    return jsonify({"response": resposta})

# Rodar o servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
