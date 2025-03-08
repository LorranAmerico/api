import openai
import requests
from flask import Flask, request, jsonify
import os
import re

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# URL da API de referência
API_URL = "https://api-excel-bot.onrender.com/buscar"

# Criando a API do bot
app = Flask(__name__)

# Função para buscar dados na API de referência
def buscar_referencia(codigo):
    url = f"{API_URL}?Codigo%20da%20Referencia={codigo}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        dados = response.json()
        if dados:
            return dados[0]  # Retorna o primeiro item da lista
        return {"erro": "Nenhum dado encontrado para esta referência"}
    except requests.exceptions.RequestException as e:
        return {"erro": f"Falha na comunicação com a API: {str(e)}"}

@app.route('/ping')
def ping():
    return "pong", 200

# Função para interpretar a mensagem do usuário e decidir se deve buscar na API ou usar a IA
def interpretar_mensagem(user_message):
    numeros = re.findall(r'\d+', user_message)
    palavras_chave = ["referência", "buscar", "produto", "item", "código"]
    
    if numeros and any(palavra in user_message.lower() for palavra in palavras_chave):
        codigo = numeros[0]  # Pega o primeiro número encontrado
        resultado = buscar_referencia(codigo)
        if "erro" in resultado:
            return resultado["erro"]
        return (f"Aqui estão os detalhes da referência {codigo}:\n"
                f"- Descrição: {resultado.get('Descricao da Referencia', 'N/A')}\n"
                f"- Grupo: {resultado.get('Grupo', 'N/A')}\n"
                f"- SubGrupo: {resultado.get('SubGrupo1', 'N/A')}\n"
                f"- Valor de Venda: R${resultado.get('Venda_Valor', 'N/A')}")
    
    # Se não encontrar números relevantes, chamar o ChatGPT
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


