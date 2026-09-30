import requests
from modelos import FaixaMusical, Album

# ==========================================
# 1. IMPLEMENTAÇÃO DEEZER
# ==========================================
def _buscar_faixas_deezer(nome_musica): # RF8: Fonte oculta (prefixo _). O restante da aplicação não sabe que é a Deezer. Encapsulamento de módulo.
    url = f"https://api.deezer.com/search?q={nome_musica}"
    try:
        dados = requests.get(url, timeout=10).json()
    except requests.exceptions.RequestException: # Tratamento de exceção focado apenas em falhas reais de conexão, evitando anti-padrão.
        return []

    resultados = []
    for f in dados.get('data', [])[:10]: 
        faixa = FaixaMusical(f['id'], f['title'], f['artist']['name'], f['duration'])
        faixa.id_artista = f['artist']['id'] # <-- Injeta o ID do artista aqui
        faixa.id_album = f['album']['id']  
        resultados.append((faixa, f['album']['id']))
    return resultados


def _buscar_album_deezer(id_album): # RF8: Função protegida limitando o vazamento de estruturas da API para fora.
    url = f"https://api.deezer.com/album/{id_album}"
    try:
        dados = requests.get(url, timeout=10).json()
        if 'id' not in dados or 'tracks' not in dados: # RF7: Detecta dados incompletos ou vazios e não quebra o sistema.
            return None

        album = Album(dados['id'], dados['title']) # Instanciação do objeto principal (Todo).
        for t in dados['tracks']['data']:
            faixa = FaixaMusical(t['id'], t['title'], t['artist']['name'], t['duration'])
            album.adicionar_faixa(faixa) # Composição: Inserindo as partes (Faixas) no todo (Álbum).
        return album
    except requests.exceptions.RequestException: # Tolerância a falhas esperadas.
        return None


# ==========================================
# 2. IMPLEMENTAÇÃO ITUNES (APPLE)
# ==========================================
def _buscar_faixas_itunes(nome_musica): # RF8: Nova fonte de dados também oculta sob a mesma assinatura.
    url = f"https://itunes.apple.com/search?term={nome_musica}&entity=song&limit=10"
    try:
        dados = requests.get(url, timeout=10).json()
    except requests.exceptions.RequestException: # Tratamento de exceção de rede.
        return []

    resultados = []
    for f in dados.get('results', []):
        duracao = f.get('trackTimeMillis', 0) // 1000
        faixa = FaixaMusical(f['trackId'], f['trackName'], f['artistName'], duracao)
        faixa.id_artista = f.get('artistId') # <-- Injeta o ID do artista aqui
        faixa.id_album = f.get('collectionId') 
        resultados.append((faixa, f.get('collectionId')))
    return resultados


def _buscar_album_itunes(id_album): # RF8: Busca de álbum específica do iTunes escondida do restante do código.
    url = f"https://itunes.apple.com/lookup?id={id_album}&entity=song"
    try:
        dados = requests.get(url, timeout=10).json()
        if not dados.get('results'): # RF7: Tratamento de dados inexistentes sem falha bruta.
            return None
        
        resultados = dados['results']
        info_album = resultados[0] 
        album = Album(info_album['collectionId'], info_album['collectionName']) # Instanciação do Álbum.
        
        for t in resultados[1:]: 
            if t.get('wrapperType') == 'track':
                duracao_segundos = t.get('trackTimeMillis', 0) // 1000
                faixa = FaixaMusical(t['trackId'], t['trackName'], t['artistName'], duracao_segundos)
                album.adicionar_faixa(faixa) # Composição: Inserindo as faixas no álbum.
                
        return album
    except requests.exceptions.RequestException: # Tolerância a falhas de rede.
        return None


# ==========================================
# 3. FACHADA (O que o resto do sistema enxerga)
# ==========================================

# Mude para "deezer" ou "itunes". O main.py não faz ideia de qual está sendo usado.
PROVEDOR_ATUAL = "itunes" 

def buscar_faixas(nome_musica): # RF8: Fachada pública que esconde a real fonte dos dados.
    if PROVEDOR_ATUAL == "deezer":
        return _buscar_faixas_deezer(nome_musica)
    elif PROVEDOR_ATUAL == "itunes":
        return _buscar_faixas_itunes(nome_musica)
    return []

def buscar_album(id_album): # RF8: Interface de obtenção de dados totalmente desacoplada da implementação.
    if PROVEDOR_ATUAL == "deezer":
        return _buscar_album_deezer(id_album)
    elif PROVEDOR_ATUAL == "itunes":
        return _buscar_album_itunes(id_album)
    return None


def _buscar_artista_deezer(id_artista):
    url = f"https://api.deezer.com/artist/{id_artista}"
    try:
        dados = requests.get(url, timeout=10).json()
        if 'id' not in dados:
            return None
            
        from modelos import Artista 
        return Artista(dados['id'], dados['name'])
    except requests.exceptions.RequestException:
        return None


def _buscar_artista_itunes(id_artista):
    url = f"https://itunes.apple.com/lookup?id={id_artista}"
    try:
        dados = requests.get(url, timeout=10).json()
        if not dados.get('results'):
            return None
            
        info = dados['results'][0]
        from modelos import Artista
        return Artista(info['artistId'], info['artistName'])
    except requests.exceptions.RequestException:
        return None


def buscar_artista(id_artista):
    if PROVEDOR_ATUAL == "deezer":
        return _buscar_artista_deezer(id_artista)
    elif PROVEDOR_ATUAL == "itunes":
        return _buscar_artista_itunes(id_artista)
    return None