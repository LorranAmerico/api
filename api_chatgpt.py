import openai
import requests
from flask import Flask, request, jsonify
import os

# Obtendo a chave da OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# URL da API de busca
API_URL = "https://api-excel-bot.onrender.com/buscar"

# Criando a API Flask
app = Flask(__name__)

# Função para buscar referência na API

def buscar_referencia(codigo):
    try:
        url = f"{API_URL}?Codigo%20da%20Referencia={codigo}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"erro": f"Falha na comunicação com a API: {str(e)}"}

# Endpoint para verificar status do servidor
@app.route('/ping', methods=['GET'])
def ping():
    return "pong", 200

# Função para chamar o ChatGPT

def chat_with_gpt(user_message):
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente que responde com base na API Excel Bot."},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content
    except openai.OpenAIError as e:
        return f"Erro ao se comunicar com OpenAI: {str(e)}"
    except Exception as e:
        return f"Erro inesperado: {str(e)}"

# Endpoint para o chatbot
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"erro": "Campo 'message' ausente na requisição"}), 400

        user_message = data["message"].strip()
        if not user_message:
            return jsonify({"erro": "Mensagem vazia não é permitida"}), 400

        if "buscar" in user_message.lower():
            codigo = user_message.split()[-1]
            resultado = buscar_referencia(codigo)
            return jsonify({"response": resultado})
        
        resposta = chat_with_gpt(user_message)
        return jsonify({"response": resposta})
    except Exception as e:
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

# Iniciando o servidor Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
