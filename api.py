import requests
# importa classes puras de modelos.py
from modelos import FaixaMusical, Album


def buscar_faixa_deezer(nome_musica):

    url = f"https://api.deezer.com/search?q={nome_musica}"
    try:
        dados = requests.get(url, timeout=10).json()
    except Exception:
        # erros recuperáveis (falha de rede, timeout, etc)
        return None, None

    if not dados.get('data'):
        # Busca sem resultados com retorno normal (sem erro bruto)
        return None, None

    f = dados['data'][0]
    # cria o objeto faixa musical com dados da API
    faixa = FaixaMusical(f['id'], f['title'], f['artist']['name'], f['duration'])
    return faixa, f['album']['id']


def buscar_album_deezer(id_album):
    url = f"https://api.deezer.com/album/{id_album}"
    try:
        dados = requests.get(url, timeout=10).json()
        if 'id' not in dados or 'tracks' not in dados:
            return None

        # cria o objeto album
        album = Album(dados['id'], dados['title'])

        for t in dados['tracks']['data']:
            faixa = FaixaMusical(t['id'], t['title'], t['artist']['name'], t['duration'])
            # adiciona o objeto faixa musical dentro do album
            album.adicionar_faixa(faixa)

        return album
    except Exception:
        return None