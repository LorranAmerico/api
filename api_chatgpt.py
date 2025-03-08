import openai
import requests
from flask import Flask, request, jsonify
import os

# Obtendo a chave da OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# URL da API de busca de referências
API_URL = "https://api-excel-bot.onrender.com/buscar"

# Criando a API Flask
app = Flask(__name__)

# Função para buscar referência na API externa
def buscar_referencia(codigo):
    try:
        url = f"{API_URL}?Codigo%20da%20Referencia={codigo}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"erro": f"Falha na comunicação com a API: {str(e)}"}

# Rota de teste
@app.route('/ping')
def ping():
    return "pong", 200

# Função para interpretar a intenção da mensagem usando OpenAI
def interpretar_mensagem(user_message):
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": "Você é um assistente que responde com base na API Excel Bot."},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content
    except openai.OpenAIError as e:
        return f"Erro ao se comunicar com OpenAI: {str(e)}"

# Rota do chatbot
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"response": "Mensagem inválida. Tente novamente."}), 400

        # Primeiro, tentar extrair uma referência
        palavras = user_message.lower().split()
        for palavra in palavras:
            if palavra.isdigit():  # Se encontrar um número, assume que é uma referência
                resultado = buscar_referencia(palavra)
                return jsonify({"response": resultado})
        
        # Se não for uma busca, chama a OpenAI
        resposta_chatgpt = interpretar_mensagem(user_message)
        return jsonify({"response": resposta_chatgpt})
    except Exception as e:
        return jsonify({"response": f"Erro interno do servidor: {str(e)}"}), 500

# Iniciar o servidor Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


