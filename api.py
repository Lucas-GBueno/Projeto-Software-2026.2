import requests
# Importa as classes puras do nosso outro arquivo
from modelos import FaixaMusical, Album


def _buscar_faixa_deezer(nome_musica):
    url = f"https://api.deezer.com/search?q={nome_musica}"
    try:
        dados = requests.get(url, timeout=10).json()
    except Exception:
        # RF7: falha de rede/formatação -> condição recuperável, não um erro fatal
        return None, None

    if not dados.get('data'):
        # RF7: busca sem resultados -> condição normal
        return None, None

    f = dados['data'][0]
    faixa = FaixaMusical(f['id'], f['title'], f['artist']['name'], f['duration'])
    return faixa, f['album']['id']


def _buscar_album_deezer(id_album):
    url = f"https://api.deezer.com/album/{id_album}"
    try:
        dados = requests.get(url, timeout=10).json()
        if 'id' not in dados or 'tracks' not in dados:
            return None

        album = Album(dados['id'], dados['title'])
        for t in dados['tracks']['data']:
            faixa = FaixaMusical(t['id'], t['title'], t['artist']['name'], t['duration'])
            album.adicionar_faixa(faixa)
        return album
    except Exception:
        return None

def buscar_faixa(nome_musica):
    return _buscar_faixa_deezer(nome_musica)


def buscar_album(id_album):
    return _buscar_album_deezer(id_album)