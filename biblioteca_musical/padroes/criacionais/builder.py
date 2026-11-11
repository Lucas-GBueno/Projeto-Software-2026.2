"""Builder criacional para construir playlists com validação incremental."""
from uuid import uuid4

from biblioteca_musical.dominio.midias import Playlist


# BUILDER: montagem incremental; o menu não precisa construir a Playlist
# detalhe por detalhe. `construir()` entrega o produto final.
class PlaylistBuilder:
    """Constrói uma Playlist em etapas, validando tudo antes de entregá-la.

    Exemplo:
        pl = (PlaylistBuilder('Estudo')
              .adicionar(faixa1)
              .adicionar(album1)
              .construir())
    """

    def __init__(self, titulo):
        titulo = titulo.strip()
        if not titulo:
            raise ValueError("O título da playlist não pode estar vazio.")
        self._titulo = titulo
        self._itens = []

    def adicionar(self, item):
        # Passo de montagem: valida o contrato e prepara a lista de partes.
        if not Playlist.aceita_item(item):
            raise TypeError("A playlist aceita itens reproduzíveis e álbuns.")
        self._itens.append(item)
        return self  # Permite encadeamento: .adicionar(a).adicionar(b)

    def adicionar_varios(self, itens):
        for item in itens:
            self.adicionar(item)
        return self

    def construir(self):
        # Finalização: cria uma NOVA playlist, sem alterar outros objetos.
        # IDs prefixados distinguem playlists locais dos IDs de APIs externas.
        playlist = Playlist(f"pl-{uuid4().hex}", self._titulo)
        for item in self._itens:
            if not playlist.adicionar_item(item):
                raise ValueError("Não foi possível adicionar um componente à playlist.")
        return playlist
