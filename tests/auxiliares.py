"""Dublês de HTTP e dados de exemplo usados para testar sem internet.

ClienteFake registra URLs/parâmetros e devolve respostas simuladas, permitindo
validar o Adapter sem depender de serviços externos ou da rede.
"""
import requests
from biblioteca_musical.dominio.midias import FaixaMusical

class RespostaFake:
    def __init__(self, dados=None, erro_http=False):
        self.dados = dados
        self.erro_http = erro_http

    def raise_for_status(self):
        if self.erro_http:
            raise requests.exceptions.HTTPError("HTTP 503")

    def json(self):
        return self.dados


class ClienteFake:
    def __init__(self, dados=None, erro=None, erro_http=False):
        self.dados = dados
        self.erro = erro
        self.erro_http = erro_http
        self.chamadas = []

    def get(self, url, **kwargs):
        self.chamadas.append((url, kwargs))
        if self.erro:
            raise self.erro
        return RespostaFake(self.dados, self.erro_http)


def faixa(identificador=1, nome="Canção"):
    return FaixaMusical(identificador, nome, "Artista", 150, id_album=19, id_artista=11)
