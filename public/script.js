document.getElementById('btnMix').addEventListener('click', async () => {
    const filmeA = document.getElementById('filmeA').value;
    const filmeB = document.getElementById('filmeB').value;
    const resultList = document.getElementById('result-list');
    const loading = document.getElementById('loading');

    if (!filmeA || !filmeB) {
        alert("Por favor, insira os dois filmes!");
        return;
    }

    // --- LÓGICA DE URL INTELIGENTE ---
    // Se estiver no computador local, usa a porta 3000 do Flask.
    // Se estiver na Vercel, usa a rota relativa /recommend.
    const isLocal = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost';
    const API_URL = isLocal ? 'http://127.0.0.1:3000/recommend' : '/recommend';
    // --------------------------------

    resultList.innerHTML = '';
    loading.classList.remove('hidden');

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filmeA, filmeB })
        });

        if (!response.ok) {
            throw new Error(`Erro no servidor: ${response.status}`);
        }

        const data = await response.json();
        
        // A IA pode retornar o JSON como string ou como objeto. 
        // Tratamos as duas possibilidades para evitar erros.
        let movies = [];
        if (typeof data === 'string') {
            const parsed = JSON.parse(data);
            movies = parsed.filmes || parsed;
        } else {
            movies = data.filmes || data;
        }

        loading.classList.add('hidden');

        if (!movies || movies.length === 0) {
            resultList.innerHTML = '<p>Nenhuma recomendação encontrada. Tente outros filmes!</p>';
            return;
        }

        movies.forEach(movie => {
            const card = document.createElement('div');
            card.className = 'movie-card';
            card.innerHTML = `
                <h3>${movie.titulo}</h3>
                <p>${movie.motivo}</p>
                <span class="vibe-tag">${movie.vibe}</span>
            `;
            resultList.appendChild(card);
        });

    } catch (error) {
        console.error("Erro detalhado:", error);
        alert("Erro ao buscar recomendações. Verifique se o servidor Python está rodando no terminal!");
        loading.classList.add('hidden');
    }
});
