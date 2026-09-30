import requests
import time
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
# 3. IMPLEMENTAÇÃO MUSICBRAINZ
# ==========================================
# MusicBrainz é gratuito e sem chave, mas exige um User-Agent identificável e
# limita a ~1 requisição por segundo por IP — passar disso gera erro 503.
# Por isso, toda chamada passa por _mb_get(), que centraliza User-Agent,
# fmt=json e o intervalo mínimo entre requisições.
_MB_BASE_URL = "https://musicbrainz.org/ws/2"
_MB_HEADERS = {"User-Agent": "CatalogoMusical/1.0 ( contato@exemplo.com )"}
_mb_ultimo_acesso = 0.0

def _mb_get(caminho, **params): # RF8: única porta de saída do MusicBrainz — nenhuma outra função monta URL diretamente.
    global _mb_ultimo_acesso
    espera = 1.0 - (time.time() - _mb_ultimo_acesso)
    if espera > 0:
        time.sleep(espera)

    params["fmt"] = "json"
    try:
        resposta = requests.get(f"{_MB_BASE_URL}/{caminho}", params=params, headers=_MB_HEADERS, timeout=10)
        resposta.raise_for_status() # RF7: 503 (limite excedido) e 404 viram exceção, tratada abaixo.
        return resposta.json()
    except (requests.exceptions.RequestException, ValueError): # ValueError cobre JSON malformado.
        return None
    finally:
        _mb_ultimo_acesso = time.time()


def _buscar_faixas_musicbrainz(nome_musica): # RF8: Terceira fonte de dados, também oculta sob a mesma assinatura.
    dados = _mb_get("recording", query=nome_musica, limit=10)
    if not dados:
        return []

    resultados = []
    for r in dados.get('recordings', []):
        artist_credit = r.get('artist-credit') or []
        nome_artista = artist_credit[0]['name'] if artist_credit else "Artista desconhecido"
        id_artista = artist_credit[0].get('artist', {}).get('id') if artist_credit else None

        duracao_ms = r.get('length')
        duracao_segundos = duracao_ms // 1000 if duracao_ms else 0 # RF7: faixa sem duração informada vira 0, não quebra.

        releases = r.get('releases') or []
        id_album = releases[0]['id'] if releases else None # Uma gravação pode estar em vários lançamentos; usamos o primeiro.

        faixa = FaixaMusical(r['id'], r.get('title', '(sem título)'), nome_artista, duracao_segundos)
        faixa.id_artista = id_artista # <-- Injeta o ID do artista aqui
        faixa.id_album = id_album     # <-- Injeta o ID do álbum aqui
        resultados.append((faixa, id_album))
    return resultados


def _buscar_album_musicbrainz(id_album): # RF8: Busca de álbum (release) específica do MusicBrainz escondida do restante do código.
    dados = _mb_get(f"release/{id_album}", inc="recordings")
    if not dados or 'media' not in dados: # RF7: lançamento inexistente ou sem faixas não quebra o sistema.
        return None

    album = Album(dados['id'], dados.get('title', '(sem título)'))
    for midia in dados.get('media', []):
        for faixa_bruta in midia.get('tracks', []):
            gravacao = faixa_bruta.get('recording', {})
            duracao_ms = faixa_bruta.get('length') or gravacao.get('length')
            duracao_segundos = duracao_ms // 1000 if duracao_ms else 0
            nome_artista = (dados.get('artist-credit') or [{}])[0].get('name', 'Artista desconhecido')
            faixa = FaixaMusical(gravacao.get('id', faixa_bruta.get('id')), faixa_bruta.get('title', '(sem título)'),
                                  nome_artista, duracao_segundos)
            album.adicionar_faixa(faixa) # Composição: Inserindo as faixas no álbum.
    return album


def _buscar_artista_musicbrainz(id_artista, limite_discografia=3): # RF8: Busca de artista específica do MusicBrainz.
    """
    Limite baixo de discografia (3, contra 5 da Deezer) porque, no
    MusicBrainz, cada álbum exige DUAS chamadas extras (o grupo de
    lançamento não tem faixas; é preciso achar um release concreto dele e
    então buscar esse release) — e o limite de 1 req/s da API tornaria a
    busca de um artista com muitos álbuns bem lenta.
    """
    dados_artista = _mb_get(f"artist/{id_artista}", inc="genres")
    if not dados_artista:
        return None

    from modelos import Artista
    artista = Artista(dados_artista['id'], dados_artista.get('name', '(desconhecido)'))

    for genero in dados_artista.get('genres', []):
        artista.adicionar_genero(genero['name'])

    dados_discografia = _mb_get("release-group", artist=id_artista, type="album")
    grupos = (dados_discografia or {}).get('release-groups', [])[:limite_discografia]

    for grupo in grupos:
        dados_lancamentos = _mb_get("release", **{"release-group": grupo['id']})
        lancamentos = (dados_lancamentos or {}).get('releases', [])
        if lancamentos:
            album_completo = _buscar_album_musicbrainz(lancamentos[0]['id'])
            if album_completo:
                artista.adicionar_album(album_completo)

    return artista


# ==========================================
# 4. FACHADA (O que o resto do sistema enxerga)
# ==========================================

# Mude para "deezer", "itunes" ou "musicbrainz". O main.py não faz ideia de qual está sendo usado.
PROVEDOR_ATUAL = "itunes" 
NOMES_PROVEDORES = {"deezer": "Deezer", "itunes": "iTunes", "musicbrainz": "MusicBrainz"}

def nome_provedor_atual():
    return NOMES_PROVEDORES.get(PROVEDOR_ATUAL, "fonte de dados")

def buscar_faixas(nome_musica): # RF8: Fachada pública que esconde a real fonte dos dados.
    if PROVEDOR_ATUAL == "deezer":
        return _buscar_faixas_deezer(nome_musica)
    elif PROVEDOR_ATUAL == "itunes":
        return _buscar_faixas_itunes(nome_musica)
    elif PROVEDOR_ATUAL == "musicbrainz":
        return _buscar_faixas_musicbrainz(nome_musica)
    return []

def buscar_album(id_album): # RF8: Interface de obtenção de dados totalmente desacoplada da implementação.
    if PROVEDOR_ATUAL == "deezer":
        return _buscar_album_deezer(id_album)
    elif PROVEDOR_ATUAL == "itunes":
        return _buscar_album_itunes(id_album)
    elif PROVEDOR_ATUAL == "musicbrainz":
        return _buscar_album_musicbrainz(id_album)
    return None


def _buscar_generos_album_deezer(id_album):
    """
    Busca só os nomes dos gêneros de um álbum na Deezer, sem montar o Album
    inteiro. Existe separada de _buscar_album_deezer porque o Album nunca
    exibe seus próprios gêneros — esse dado só serve pra alimentar os
    gêneros do Artista.
    """
    url = f"https://api.deezer.com/album/{id_album}"
    try:
        dados = requests.get(url, timeout=10).json()
        return [g['name'] for g in dados.get('genres', {}).get('data', [])]
    except requests.exceptions.RequestException:
        return []


def _buscar_artista_deezer(id_artista, limite_discografia=5):
    """
    Busca de um Artista pela API Pública Deezer: nome, música de maior
    sucesso (top track na Deezer), discografia (até `limite_discografia`
    álbuns, cada um já com suas próprias faixas) e os gêneros agregados a
    partir de cada álbum da discografia.
    """
    url = f"https://api.deezer.com/artist/{id_artista}"
    try:
        dados_artista = requests.get(url, timeout=10).json()
        if 'id' not in dados_artista:
            return None

        # Música de maior sucesso: primeiro item do "top" do artista na Deezer
        dados_top = requests.get(f"https://api.deezer.com/artist/{id_artista}/top?limit=1", timeout=10).json()
        top_tracks = dados_top.get('data') or []
        musica_top = top_tracks[0]['title'] if top_tracks else None

        from modelos import Artista
        artista = Artista(dados_artista['id'], dados_artista['name'], musica_maior_sucesso=musica_top)

        dados_discografia = requests.get(f"https://api.deezer.com/artist/{id_artista}/albums", timeout=10).json()
        resumo_albuns = (dados_discografia.get('data') or [])[:limite_discografia]

        for resumo in resumo_albuns:
            album_completo = _buscar_album_deezer(resumo['id'])
            if album_completo:
                artista.adicionar_album(album_completo)
            for genero in _buscar_generos_album_deezer(resumo['id']):
                artista.adicionar_genero(genero)

        return artista
    except requests.exceptions.RequestException:
        return None


def _buscar_artista_itunes(id_artista, limite_discografia=5):
    """
    Busca de um Artista pela API do iTunes: nome, discografia e gêneros.

    IMPORTANTE: o iTunes não tem um endpoint de "faixa mais popular" (dado de
    popularidade real, como o /top da Deezer) — por isso musica_maior_sucesso
    fica None aqui. Não inventamos um substituto (ex: "primeira faixa
    encontrada") pra não fingir um dado que a fonte não tem.
    """
    url_artista = f"https://itunes.apple.com/lookup?id={id_artista}"
    try:
        dados_artista = requests.get(url_artista, timeout=10).json()
        if not dados_artista.get('results'):
            return None

        info = dados_artista['results'][0]
        from modelos import Artista
        artista = Artista(info['artistId'], info['artistName'])

        # entity=album já devolve discografia E gênero de cada álbum
        # (primaryGenreName) numa chamada só — não precisa de request extra.
        url_discografia = f"https://itunes.apple.com/lookup?id={id_artista}&entity=album&limit={limite_discografia}"
        dados_discografia = requests.get(url_discografia, timeout=10).json()

        for resumo_album in dados_discografia.get('results', []):
            if resumo_album.get('wrapperType') != 'collection':
                continue  # o 1º item às vezes é o próprio artista, não um álbum

            genero = resumo_album.get('primaryGenreName')
            if genero:
                artista.adicionar_genero(genero)

            album_completo = _buscar_album_itunes(resumo_album['collectionId'])
            if album_completo:
                artista.adicionar_album(album_completo)

        return artista
    except requests.exceptions.RequestException:
        return None


def buscar_artista(id_artista):
    if PROVEDOR_ATUAL == "deezer":
        return _buscar_artista_deezer(id_artista)
    elif PROVEDOR_ATUAL == "itunes":
        return _buscar_artista_itunes(id_artista)
    elif PROVEDOR_ATUAL == "musicbrainz":
        return _buscar_artista_musicbrainz(id_artista)
    return None