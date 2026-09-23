import requests #import módulo de conexão com API
from modelos import FaixaMusical, Album, Artista #import das classes


def _buscar_faixas_deezer(nome_musica, limite=10):
   
    """ Busca das faixas musicas pela API Pública Deezer
        Função principal de busca (privada), intermediada por buscar_faixas() (pública) (RF8)
        Retorna lista de faixas musicas com 10 resultados (limite máximo padronizado) na ordem retornada pela Deezer
        Ou None, caso a string não corresponder à nenhum resutaldo, ou ocorrer qualquer falha (RF7)
    """

    url = f"https://api.deezer.com/search?q={nome_musica}"
    try:
        dados = requests.get(url, timeout=10).json()
    except Exception: #(RF7) falha de rede ou formatação do resultado é erro recuperável
        return None

    resultados = dados.get('data')
    if not resultados: #(RF7): Busca sem resultados deve ser tratado como "esperável" (condição normal)
        return None

    faixas = [
        FaixaMusical(f['id'], f['title'], f['artist']['name'], f['duration'],
                     id_album=f['album']['id'], id_artista=f['artist']['id'])
        for f in resultados[:limite]
    ] #criação da lista de faixas encontradas, com ID, título, Artista, duração e álbum relacionado
    return faixas


def _buscar_album_deezer(id_album):
   
    """Busca dos álbuns pela API Pública Deezer
        Função principal de busca (privada), intermediada por buscar_album() (pública) (RF8)
        Retorna objeto Album com informações do álbum e suas faixas
        Ou None, caso a string não corresponder à nenhum resutaldo, ou ocorrer qualquer falha (RF7)
    """

    url = f"https://api.deezer.com/album/{id_album}"
    try:
        dados = requests.get(url, timeout=10).json()
        if 'id' not in dados or 'tracks' not in dados:
            return None

        album = Album(dados['id'], dados['title'], generos=[g['name'] for g in dados.get('genres', {}).get('data', [])])
        for t in dados['tracks']['data']:
            faixa = FaixaMusical(t['id'], t['title'], t['artist']['name'], t['duration'])
            album.adicionar_faixa(faixa)
        return album
    except Exception:
        return None

"""(RF8): Funções de busca (acesso direto à fontes de busca) separados das funções de acesso direto ao usuário
    Funções privadas separadas das públicas (públicas apenas recebem os retornos prontos das privadas)
    Facilita para troca de API utilizada (capenas alterações em api.py)
"""

def _buscar_artista_deezer(id_artista, limite_discografia=5):
    """
    Busca de um Artista pela API Pública Deezer.
    Função principal de busca (privada), intermediada por buscar_artista() (pública) (RF8)

    Monta um Artista com: nome, música de maior sucesso (top track na Deezer),
    gêneros musicais (agregados a partir dos álbuns da discografia) e a
    discografia em si (até `limite_discografia` álbuns, cada um já com suas
    próprias faixas — o mesmo limite existe em buscar_faixas(), para não
    disparar chamadas demais à API de uma vez só).

    Retorna None caso o artista não seja encontrado, ou ocorrer qualquer
    falha (RF7).
    """
    try:
        dados_artista = requests.get(f"https://api.deezer.com/artist/{id_artista}", timeout=10).json()
        if 'id' not in dados_artista:
            return None

        # Música de maior sucesso: primeiro item do "top" do artista na Deezer
        dados_top = requests.get(f"https://api.deezer.com/artist/{id_artista}/top?limit=1", timeout=10).json()
        top_tracks = dados_top.get('data') or []
        musica_top = top_tracks[0]['title'] if top_tracks else None

        artista = Artista(dados_artista['id'], dados_artista['name'], musica_maior_sucesso=musica_top)

        # Discografia: busca cada álbum completo (reaproveitando _buscar_album_deezer),
        # e aproveita os gêneros que já vêm junto de cada álbum.
        dados_discografia = requests.get(f"https://api.deezer.com/artist/{id_artista}/albums", timeout=10).json()
        resumo_albuns = (dados_discografia.get('data') or [])[:limite_discografia]

        for resumo in resumo_albuns:
            album_completo = _buscar_album_deezer(resumo['id'])
            if album_completo:
                artista.adicionar_album(album_completo)
                for genero in album_completo.generos:
                    artista.adicionar_genero(genero)

        return artista
    except Exception: #(RF7) falha de rede ou formatação do resultado é erro recuperável
        return None


def buscar_faixas(nome_musica): #função pública da busca de faixas musicais
    return _buscar_faixas_deezer(nome_musica) #acessa a função privada de faixas


def buscar_album(id_album): #função pública da busca de álbuns
    return _buscar_album_deezer(id_album) #acessa a função privada de álbuns


def buscar_artista(id_artista): #função pública da busca de artistas
    return _buscar_artista_deezer(id_artista) #acessa a função privada de artistas