"""FACADE (estrutural): API simples para consultar músicas, álbuns e artistas.

Diferente do Adapter (que TRADUZ dados), a Facade SIMPLIFICA o acesso ao
subsistema. Pode receber qualquer implementação da interface FonteMusical.
"""
from biblioteca_musical.padroes.estruturais.adapter import FonteMusical

# FACADE: oferece apenas operações de catálogo e delega os detalhes
# da comunicação HTTP e conversões ao Adapter já injetado.
class CatalogoMusical:
    """FACADE (estrutural): oferece um único ponto para consultar mídias."""

    def __init__(self, fonte):
        if not isinstance(fonte, FonteMusical):
            raise TypeError("A fonte musical deve implementar FonteMusical.")
        # A fachada depende de uma INTERFACE (FonteMusical), não de um provedor.
        self._fonte = fonte

    def buscar_faixas(self, nome_musica):
        return self._fonte.buscar_faixas(nome_musica)

    def buscar_album(self, id_album):
        return self._fonte.buscar_album(id_album)

    def buscar_artista(self, id_artista):
        return self._fonte.buscar_artista(id_artista)
