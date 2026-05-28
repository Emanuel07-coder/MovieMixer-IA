import os
import json
from flask import Flask, request, jsonify
from groq import Groq
from dotenv import load_dotenv
from flask_cors import CORS

# Carrega variáveis do .env localmente
load_dotenv()

app = Flask(__name__)
CORS(app)

# Inicializa o cliente Groq
# Usamos get() para evitar que o app quebre se a chave não existir
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    print("❌ ERRO: GROQ_API_KEY não encontrada no arquivo .env")

client = Groq(api_key=api_key)

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        # 1. Validação de Input
        data = request.get_json()
        if not data:
            return jsonify({"error": "Corpo da requisição vazio"}), 400

        filme_a = data.get('filmeA')
        filme_b = data.get('filmeB')

        if not filme_a or not filme_b:
            return jsonify({"error": "Por favor, forneça os dois filmes (filmeA e filmeB)"}), 400

        # 2. Prompt Especializado (Refinado para evitar lixo no JSON)
        system_prompt = (
            "Você é um curador de cinema especialista em análise temática e estética. "
            "Seu objetivo é criar a 'Mistura Perfeita' entre dois filmes. "
            "Analise o tom, a estética, os temas e a atmosfera de ambos. "
            "Sugerir 5 filmes que representem a intersecção desses dois mundos. "
            "Responda OBRIGATORIAMENTE apenas o objeto JSON puro, sem explicações externas, "
            "sem markdown (como ```json), seguindo exatamente este modelo: "
            "{\"filmes\": [{\"titulo\": \"Nome do Filme\", \"motivo\": \"Explicação da mistura\", \"vibe\": \"A vibe resultante\"}]}"
        )

        user_prompt = f"Misture os filmes: '{filme_a}' e '{filme_b}'."

        # 3. Chamada à API da Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"} 
        )

        # 4. Processamento da Resposta
        content = chat_completion.choices[0].message.content
        
        # Tentamos converter a string da IA em um dicionário Python real
        # Isso garante que o Flask envie um JSON válido e não apenas uma string
        parsed_json = json.loads(content)

        return jsonify(parsed_json), 200

    except json.JSONDecodeError:
        return jsonify({"error": "A IA gerou um formato de resposta inválido. Tente novamente."}), 500
    except Exception as e:
        # Log do erro no console para o desenvolvedor
        print(f"Erro interno: {str(e)}")
        # Resposta genérica para o usuário por segurança
        return jsonify({"error": "Ocorreu um erro interno ao processar a recomendação."}), 500

# Para rodar localmente
if __name__ == '__main__':
    app.run(port=3000, debug=True)
