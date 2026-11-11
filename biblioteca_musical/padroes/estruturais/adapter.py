"""ADAPTER (estrutural): converte Deezer/iTunes para a interface FonteMusical.

FonteMusical = Target; serviços remotos = Adaptees; AdaptadorDeezer e
AdaptadorITunes = Adapters. Os métodos retornam sempre objetos do domínio.
"""
from abc import ABC, abstractmethod
import requests

from biblioteca_musical.dominio.midias import Album, Artista, FaixaMusical

# ADAPTER: a interface-alvo é definida aqui, independente do formato Deezer/iTunes.
class FonteMusical(ABC):
    """Contrato comum esperado pelo programa (alvo do Adapter)."""

    @abstractmethod
    def buscar_faixas(self, nome_musica):
        """Retorna [(FaixaMusical, id_album), ...]."""

    @abstractmethod
    def buscar_album(self, id_album):
        """Retorna Album ou None."""

    @abstractmethod
    def buscar_artista(self, id_artista):
        """Retorna Artista ou None."""


# Infraestrutura compartilhada, NÃO é o Adapter específico de um provedor.
# Permite injetar ClienteFake nos testes, sem acesso real à internet.
def _registros(dados, chave):
    itens = dados.get(chave) if isinstance(dados, dict) else None
    if not isinstance(itens, list):
        return []
    return [item for item in itens if isinstance(item, dict)]


class AdaptadorHTTP(FonteMusical):
    """Infraestrutura HTTP compartilhada; conversão pertence aos adapters."""

    def __init__(self, cliente=None):
        self._cliente = cliente if cliente is not None else requests

    def _obter_json(self, url, **parametros):
        try:
            resposta = self._cliente.get(url, params=parametros or None, timeout=10)
            resposta.raise_for_status()
            dados = resposta.json()
            return dados if isinstance(dados, dict) else {}
        except (requests.exceptions.RequestException, ValueError, TypeError):
            # RF7: falha de conexão, HTTP ou JSON não derruba o programa.
            return {}


# ADAPTER concreto 1: traduz as chaves Deezer (title, duration, artist ...)
# para os objetos FaixaMusical/Album/Artista do domínio.
class AdaptadorDeezer(AdaptadorHTTP):
    """Adapter estrutural: converte o formato Deezer em objetos de domínio."""

    BASE = "https://api.deezer.com"

    def buscar_faixas(self, nome_musica):
        if not nome_musica or not nome_musica.strip():
            return []
        dados = self._obter_json(f"{self.BASE}/search", q=nome_musica)
        resultados = []
        for registro in _registros(dados, "data")[:10]:
            try:
                album_id = registro["album"]["id"]
                faixa = FaixaMusical(
                    registro["id"], registro["title"],
                    registro["artist"]["name"], registro["duration"],
                    id_album=album_id, id_artista=registro["artist"].get("id"),
                )
                resultados.append((faixa, album_id))
            except (KeyError, TypeError, ValueError):
                continue
        return resultados

    def buscar_album(self, id_album):
        if id_album is None:
            return None
        dados = self._obter_json(f"{self.BASE}/album/{id_album}")
        if not all(chave in dados for chave in ("id", "title", "tracks")):
            return None
        generos = [g["name"] for g in _registros(dados.get("genres"), "data")
                   if "name" in g]
        album = Album(dados["id"], dados["title"], generos=generos)
        for registro in _registros(dados.get("tracks"), "data"):
            try:
                faixa = FaixaMusical(
                    registro["id"], registro["title"],
                    registro["artist"]["name"], registro["duration"],
                    id_album=id_album, id_artista=registro["artist"].get("id"),
                )
                album.adicionar_faixa(faixa)
            except (KeyError, TypeError, ValueError):
                continue
        return album

    def buscar_artista(self, id_artista):
        if id_artista is None:
            return None
        dados = self._obter_json(f"{self.BASE}/artist/{id_artista}")
        if not all(chave in dados for chave in ("id", "name")):
            return None
        return Artista(dados["id"], dados["name"])


# ADAPTER concreto 2: traduz trackName, artistName, trackTimeMillis ...
# do iTunes para EXATAMENTE o mesmo contrato público do AdaptadorDeezer.
class AdaptadorITunes(AdaptadorHTTP):
    """Adapter estrutural: converte formatos e milissegundos do iTunes."""

    BASE = "https://itunes.apple.com"

    def buscar_faixas(self, nome_musica):
        if not nome_musica or not nome_musica.strip():
            return []
        dados = self._obter_json(f"{self.BASE}/search", term=nome_musica,
                                entity="song", limit=10)
        resultados = []
        for registro in _registros(dados, "results"):
            try:
                album_id = registro.get("collectionId")
                faixa = FaixaMusical(
                    registro["trackId"], registro["trackName"],
                    # ADAPTER: iTunes devolve milissegundos, domínio usa segundos.
                    registro["artistName"], registro.get("trackTimeMillis", 0) // 1000,
                    id_album=album_id, id_artista=registro.get("artistId"),
                )
                resultados.append((faixa, album_id))
            except (KeyError, TypeError, ValueError):
                continue
        return resultados

    def buscar_album(self, id_album):
        if id_album is None:
            return None
        dados = self._obter_json(f"{self.BASE}/lookup", id=id_album, entity="song")
        registros = _registros(dados, "results")
        info = next((r for r in registros if r.get("wrapperType") == "collection"
                     and "collectionId" in r and "collectionName" in r), None)
        if info is None:
            return None
        generos = [info["primaryGenreName"]] if info.get("primaryGenreName") else []
        album = Album(info["collectionId"], info["collectionName"], generos=generos)
        for registro in registros:
            if registro.get("wrapperType") != "track":
                continue
            try:
                faixa = FaixaMusical(
                    registro["trackId"], registro["trackName"],
                    # ADAPTER: iTunes devolve milissegundos, domínio usa segundos.
                    registro["artistName"], registro.get("trackTimeMillis", 0) // 1000,
                    id_album=id_album, id_artista=registro.get("artistId"),
                )
                album.adicionar_faixa(faixa)
            except (KeyError, TypeError, ValueError):
                continue
        return album

    def buscar_artista(self, id_artista):
        if id_artista is None:
            return None
        dados = self._obter_json(f"{self.BASE}/lookup", id=id_artista)
        info = next((r for r in _registros(dados, "results")
                     if r.get("wrapperType") == "artist" and "artistId" in r
                     and "artistName" in r), None)
        if info is None:
            return None
        return Artista(info["artistId"], info["artistName"])
