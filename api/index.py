import os
from flask import Flask, request, jsonify
from groq import Groq
from dotenv import load_dotenv
from flask_cors import CORS

# Carrega variáveis do .env localmente
load_dotenv()

app = Flask(__name__)
CORS(app)

# Inicializa o cliente Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    filme_a = data.get('filmeA')
    filme_b = data.get('filmeB')

    if not filme_a or not filme_b:
        return jsonify({"error": "Por favor, forneça os dois filmes"}), 400

    # PROMPT ESPECIALIZADO
    system_prompt = (
        "Você é um curador de cinema especialista em análise temática e estética. "
        "Seu objetivo é criar a 'Mistura Perfeita' entre dois filmes. "
        "Analise o tom, a estética, os temas e a atmosfera de ambos. "
        "Sugerir 5 filmes que representem a intersecção desses dois mundos. "
        "Responda OBRIGATORIAMENTE em formato JSON puro, seguindo este modelo: "
        "{\"filmes\": [{\"titulo\": \"Nome do Filme\", \"motivo\": \"Explicação da mistura\", \"vibe\": \"A vibe resultante\"}]}"
    )

    user_prompt = f"Misture os filmes: '{filme_a}' e '{filme_b}'."

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"} 
        )

        return chat_completion.choices[0].message.content
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Para rodar localmente, mantemos o app.run, mas a Vercel ignora isso
if __name__ == '__main__':
    app.run(port=3000, debug=True)
