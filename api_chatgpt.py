import openai
import requests
from flask import Flask, request, jsonify
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# URL da API de referência
API_URL = "https://api-excel-bot.onrender.com/buscar"

# Criando a API do bot
app = Flask(__name__)

# Função para buscar dados na API de referência
def buscar_referencia(codigo):
    url = f"{API_URL}?Codigo%20da%20Referencia={codigo}"
    response = requests.get(url)
    
    if response.status_code == 200:
        dados = response.json()
        if dados:
            return dados[0]  # Retorna o primeiro item da lista
        return {"erro": "Nenhum dado encontrado para esta referência"}
    elif response.status_code == 404:
        return {"erro": "Referência não encontrada"}
    else:
        return {"erro": f"Falha na comunicação com a API: {response.status_code}"}

@app.route('/ping')
def ping():
    return "pong", 200

# Função para interpretar a mensagem do usuário e decidir se deve buscar na API ou usar a IA
def interpretar_mensagem(user_message):
    palavras_chave = ["referência", "código", "produto", "buscar", "detalhes", "informações"]
    for palavra in palavras_chave:
        if palavra in user_message.lower():
            palavras = user_message.split()
            for palavra in palavras:
                if palavra.isdigit():  # Se encontrar um número na mensagem
                    return buscar_referencia(palavra)
    
    # Se não encontrar palavras-chave, chamar o ChatGPT
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Você é um assistente que responde com base na API Excel Bot."},
                      {"role": "user", "content": user_message}]
        )
        return response.choices[0].message.content
    except openai.OpenAIError as e:
        return f"Erro ao se comunicar com OpenAI: {str(e)}"

# Endpoint do chatbot
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "").strip()
    
    if not user_message:
        return jsonify({"response": "Mensagem inválida ou vazia."}), 400
    
    resposta = interpretar_mensagem(user_message)
    return jsonify({"response": resposta})

# Rodar o servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
