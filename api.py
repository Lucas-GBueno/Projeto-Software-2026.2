import requests
# Importa as classes puras do nosso outro arquivo
from modelos import FaixaMusical, Album

def buscar_faixa_deezer(nome_musica):
    url = f"https://api.deezer.com/search?q={nome_musica}"
    try:
        dados = requests.get(url).json()
        if dados.get('data'):
            f = dados['data'][0]
            # INSTANCIAÇÃO: Cria o objeto da classe FaixaMusical com os dados da API
            faixa = FaixaMusical(f['id'], f['title'], f['artist']['name'], f['duration'])
            return faixa, f['album']['id']
    except Exception:
        pass
    
    print("Música não encontrada.")
    return None, None

def buscar_album_deezer(id_album):
    url = f"https://api.deezer.com/album/{id_album}"
    try:
        dados = requests.get(url).json()
        # INSTANCIAÇÃO: Cria o objeto do Álbum
        album = Album(dados['id'], dados['title'])
        
        for t in dados['tracks']['data']:
            faixa = FaixaMusical(t['id'], t['title'], t['artist']['name'], t['duration'])
            # AGREGAÇÃO: Adiciona os objetos FaixaMusical para dentro do Album
            album.adicionar_faixa(faixa)
            
        return album
    except Exception:
        return None