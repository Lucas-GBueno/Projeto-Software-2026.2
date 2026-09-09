import requests
# Importa as classes puras do nosso outro arquivo
from modelos import FaixaMusical, Album


def _buscar_faixa_deezer(nome_musica): # RF8: Fonte oculta (uso do prefixo _) - O restante da aplicação não sabe que é a Deezer. Encapsulamento de módulo.
    """
    Implementação específica da fonte Deezer.
    RF8: função "privada" (prefixo _) — não deve ser chamada de fora deste
    arquivo. O restante da aplicação não sabe (nem precisa saber) que essa
    implementação existe.
    """
    url = f"https://api.deezer.com/search?q={nome_musica}"
    try:
        dados = requests.get(url, timeout=10).json()
    except requests.exceptions.RequestException: # Tratamento de exceção focado apenas em falhas reais de conexão, evitando anti-padrão.
        return None, None

    if not dados.get('data'): # RF7: Busca sem resultados tratada como condição normal e recuperável.
        # RF7: busca sem resultados -> condição normal
        return None, None

    f = dados['data'][0]
    faixa = FaixaMusical(f['id'], f['title'], f['artist']['name'], f['duration']) # Instanciação do objeto FaixaMusical.
    return faixa, f['album']['id']


def _buscar_album_deezer(id_album): # RF8: Função protegida limitando o vazamento de estruturas da API para fora.
    """
    Implementação específica da fonte Deezer.
    RF8: função "privada" (prefixo _) — não deve ser chamada de fora deste
    arquivo.
    """
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


# ------------------------------------------------------------------
# RF8: Camada de fachada — é isto (e SÓ isto) que o resto da aplicação
# conhece. main.py nunca importa nada com "deezer" no nome nem enxerga
# o formato bruto da resposta da API: ele só recebe FaixaMusical/Album
# prontos, ou None quando não há resultado.
#
# Se um dia a equipe migrar do Deezer para o MusicBrainz (ou qualquer
# outra fonte), basta trocar o corpo de buscar_faixa()/buscar_album()
# para apontar para uma nova implementação privada — a assinatura
# (nome, parâmetros e tipo de retorno) permanece igual, então main.py,
# modelos.py e a lógica de ordenação continuam intocados.
# ------------------------------------------------------------------
def buscar_faixa(nome_musica): # RF8: Fachada pública que esconde a real fonte dos dados.
    return _buscar_faixa_deezer(nome_musica)


def buscar_album(id_album): # RF8: Interface de obtenção de dados totalmente desacoplada da implementação.
    return _buscar_album_deezer(id_album)