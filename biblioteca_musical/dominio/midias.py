"""Entidades musicais: POO, polimorfismo e organização recursiva (Composite).

Não há código de terminal nem HTTP neste módulo. A mesma mídia pode existir
na biblioteca e ser referenciada em playlists: playlists agregam referências.
"""
from abc import ABC, abstractmethod

# POO: a classe abstrata oferece o mesmo contrato a todas as mídias.
# COMPOSITE (estrutura): objetos individuais e agrupamentos usam as mesmas operações
# exibir_detalhado() e calcular_duracao(); playlists podem conter outras playlists.
# É uma organização de árvore inspirada no Composite GoF.
class Midia(ABC):
    def __init__(self, id_deezer, titulo):
        self.id_deezer = id_deezer
        self.titulo = titulo

    # ABSTRAÇÃO: Métodos sem corpo que obrigam as subclasses a implementarem.
    @abstractmethod
    def calcular_duracao(self):
        pass

    @abstractmethod
    def exibir_info(self):
        pass

    def exibir_detalhado(self, nivel=0):
        """
        Representação detalhada e recursiva desta mídia (padrão Composite).
        Por padrão, uma mídia "folha" (sem componentes internos, como
        FaixaMusical) só mostra a si mesma — quem tem componentes (Album,
        Playlist) sobrescreve este método para também listar seus itens.
        """
        marcador = "▸" if nivel == 0 else "↳"
        return ("  " * nivel) + f"{marcador} " + self.exibir_info()

#classe abstrata para midias reproduziveis 
class Reproduzivel(ABC):
    @abstractmethod
    def play(self):
        pass

# HERANÇA: FaixaMusical "é uma" Midia reproduzivel
class FaixaMusical(Midia, Reproduzivel):
    def __init__(self, id_deezer, titulo, artista, duracao_segundos, avaliacao=None, id_album=None, id_artista=None):
        super().__init__(id_deezer, titulo)
        self.artista = artista
        self.duracao_segundos = duracao_segundos
        # Guarda o id do álbum de origem, para que a faixa "saiba" de onde veio
        # mesmo depois de já estar na biblioteca (usado na opção 3 do menu).
        self.id_album = id_album
        # Guarda o id do artista de origem, pelo mesmo motivo acima
        # (usado na opção 11 do menu, para buscar o Artista).
        self.id_artista = id_artista
        # ENCAPSULAMENTO: Atributo privado, protegido de acessos externos.
        self._avaliacao = None
        
        if avaliacao is not None:
            self.avaliacao = avaliacao

    # ENCAPSULAMENTO: Getter exposto para ler o dado com segurança.
    @property
    def avaliacao(self):
        return self._avaliacao

    # ENCAPSULAMENTO: Setter para validar o dado antes de alterar o estado interno.
    @avaliacao.setter
    def avaliacao(self, valor):
        # RF1: a nota precisa ser um número INTEIRO. Floats (mesmo "4.0") e
        # booleanos são recusados; a regra fica no modelo, então vale para
        # qualquer código que tente atribuir nota, não só para o menu.
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise ValueError(f"❌ Erro: A nota {valor} é inválida. Use apenas números inteiros de 0 a 5 (sem decimais).")
        if not (0 <= valor <= 5):
            raise ValueError(f"❌ Erro: A nota {valor} é impossível. Avalie entre 0 e 5.")
        self._avaliacao = valor

    # POLIMORFISMO: Implementação específica do método abstrato da classe mãe.
    def calcular_duracao(self):
        return self.duracao_segundos

    def exibir_info(self):
        nota = f"⭐ {self.avaliacao}/5" if self.avaliacao is not None else "⭐ Sem nota"
        return f"🎵 Faixa: {self.titulo} - {self.artista} ⏱️ {self.calcular_duracao()}s | {nota}"

    def play(self): #método para reprodução
        return f"> Tocando agora: {self.titulo} - {self.artista}"
    
# HERANÇA: Album "é uma" Midia.
class Album(Midia):
    def __init__(self, id_deezer, titulo, generos=None):
        super().__init__(id_deezer, titulo)
        # ENCAPSULAMENTO / COMPOSIÇÃO: O álbum tem faixas escondidas internamente.
        self._faixas = []
        # Gêneros musicais do álbum, usados para compor os gêneros de um Artista.
        self.generos = generos if generos is not None else []

    def adicionar_faixa(self, faixa):
        # Todo/parte: o álbum administra uma coleção de faixas.
        self._faixas.append(faixa)

    # POLIMORFISMO: Calcula do seu próprio jeito (somando as faixas).
    def calcular_duracao(self):
        return sum(faixa.calcular_duracao() for faixa in self._faixas)

    def exibir_info(self):
        return f"💿 Álbum: {self.titulo} ({len(self._faixas)} faixas) ⏱️ Duração total: {self.calcular_duracao()}s"

    def exibir_detalhado(self, nivel=0):
        """POLIMORFISMO/COMPOSIÇÃO: além de si mesmo, lista cada faixa (nivel+1)."""
        linhas = [super().exibir_detalhado(nivel)]
        for faixa in self._faixas:
            linhas.append(faixa.exibir_detalhado(nivel + 1))
        return "\n".join(linhas)

# HERANÇA: Playlist "é uma" Midia.
class Playlist(Midia, Reproduzivel):
    def __init__(self, id_deezer, titulo):
        super().__init__(id_deezer, titulo)
        self._itens = []

    @staticmethod
    def aceita_item(item):
        return isinstance(item, (Reproduzivel, Album))

    def adicionar_item(self, item):
        """
        Aceita mídias reproduzíveis e álbuns de catálogo.
        Retorna True se adicionou, False se recusou.
        """
        if not self.aceita_item(item):
            print("\n🚫 [BLOQUEADO] Playlists aceitam itens reproduzíveis e álbuns.")
            return False
        # CONSISTÊNCIA: proíbe ciclos (A contém B que contém A). Sem isso,
        # calcular_duracao() e exibir_detalhado() poderiam recursar para sempre.
        if isinstance(item, Playlist) and (item is self or item._contem_playlist(self)):
            print("\n🚫 [BLOQUEADO] A inclusão criaria um ciclo de playlists.")
            return False
        self._itens.append(item)
        return True

    def _contem_playlist(self, alvo, visitadas=None):
        """RECURSÃO: percorre sub-playlists procurando `alvo`.

        `visitadas` impede visitar novamente o mesmo objeto, mesmo se ele
        for alcançado por múltiplos caminhos.
        """
        visitadas = set() if visitadas is None else visitadas
        if id(self) in visitadas:
            return False
        visitadas.add(id(self))
        return any(
            isinstance(item, Playlist) and (item is alvo or item._contem_playlist(alvo, visitadas))
            for item in self._itens
        )

    def obter_itens(self):
        """Retorna uma cópia da lista de itens, para navegação externa segura sem expor _itens diretamente."""
        return list(self._itens)

    def remover_item(self, item):
        # CONSISTÊNCIA: remove TODAS as ocorrências da mesma referência, mas
        # preserva as outras mídias e não apaga o objeto da biblioteca.
        """RF9: Remove uma referência direta a 'item' desta playlist, se existir."""
        if item not in self._itens:
            return False
        # Remove todas as ocorrências para não deixar referências penduradas.
        self._itens[:] = [existente for existente in self._itens if existente is not item]
        return True

    def remover_item_recursivo(self, item, _visitadas=None):
        """
        RF9: Remove referências a 'item' nesta playlist E em qualquer
        sub-playlist aninhada dentro dela (RF6 permite playlist dentro de
        playlist). Retorna quantas playlists tiveram o item removido, para
        que quem chamou saiba o alcance real da remoção.
        """
        # RECURSÃO/COMPOSITE: primeiro limpa o nó atual; depois visita filhos.
        # O mesmo conjunto `visitadas` evita contar uma sub-playlist duas vezes.
        _visitadas = set() if _visitadas is None else _visitadas
        if id(self) in _visitadas:
            return 0
        _visitadas.add(id(self))
        quantidade_anterior = len(self._itens)
        self._itens[:] = [
            existente for existente in self._itens
            if type(existente) is not type(item) or existente.id_deezer != item.id_deezer
        ]
        playlists_afetadas = int(len(self._itens) != quantidade_anterior)
        for sub_item in list(self._itens):
            if isinstance(sub_item, Playlist):
                playlists_afetadas += sub_item.remover_item_recursivo(item, _visitadas)
        return playlists_afetadas

    # POLIMORFISMO: Forma própria de calcular a duração.
    def calcular_duracao(self):
        # COMPOSITE: a chamada funciona em folhas (faixas) e agregados
        # (álbuns/sub-playlists). A soma entra recursivamente nos agrupamentos.
        return sum(item.calcular_duracao() for item in self._itens)

    def exibir_info(self):
        return f"📋 Playlist: {self.titulo} ({len(self._itens)} itens) ⏱️ Duração total: {self.calcular_duracao()}s"

    def exibir_detalhado(self, nivel=0):
        """POLIMORFISMO/COMPOSIÇÃO: além de si mesma, lista cada item (nivel+1).
        Como cada item chama seu próprio exibir_detalhado(), a recursão
        continua sozinha para Albuns e sub-Playlists aninhadas."""
        linhas = [super().exibir_detalhado(nivel)]
        for item in self._itens:
            # Cada componente é responsável por exibir sua própria subárvore.
            linhas.append(item.exibir_detalhado(nivel + 1))
        return "\n".join(linhas)

    def play(self): #método para reprodução
        return f"> Iniciando reprodução da playlist '{self.titulo}' ({len(self._itens)} itens)..."

# Artista representa metadados de catálogo e fica fora do player.
class Artista(Midia):
    def __init__(self, id_deezer, titulo, musica_maior_sucesso=None):
        super().__init__(id_deezer, titulo)
        self.musica_maior_sucesso = musica_maior_sucesso
        # ENCAPSULAMENTO: listas privadas, alteradas só pelos métodos da classe.
        self._generos = []       # gêneros musicais que o artista participa
        self._discografia = []   # AGREGAÇÃO: álbuns do artista (podem existir fora dele)

    def adicionar_genero(self, genero):
        if genero not in self._generos:
            self._generos.append(genero)

    def adicionar_album(self, album):
        self._discografia.append(album)

    def obter_discografia(self):
        """Retorna a discografia (lista de Album) do artista."""
        return list(self._discografia)

    # POLIMORFISMO: a "duração" de um artista é a soma de toda a discografia conhecida.
    def calcular_duracao(self):
        return sum(album.calcular_duracao() for album in self._discografia)

    def exibir_info(self):
        generos_str = ", ".join(self._generos) if self._generos else "gênero não informado"
        sucesso_str = self.musica_maior_sucesso or "não informado"
        return (f"🎤 Artista: {self.titulo} | 🏆 Maior sucesso: {sucesso_str} "
                f"| 🎼 Gêneros: {generos_str} | 💿 {len(self._discografia)} álbum(ns) na discografia")

    def exibir_detalhado(self, nivel=0):
        """COMPOSIÇÃO/POLIMORFISMO: além de si mesmo, lista cada álbum da discografia (nivel+1),
        e cada álbum, por sua vez, lista suas próprias faixas — a recursão do RF7 continua valendo."""
        linhas = [super().exibir_detalhado(nivel)]
        marcador = "  " * (nivel + 1) + "↳"
        for album in self._discografia:
            linhas.append(f"{marcador} {album.titulo} (⏱️ {album.calcular_duracao()}s)")
        return "\n".join(linhas)

    # PROPOSITALMENTE SEM play(): Artista não implementa Reproduzivel.
    # Tentar chamar simular_player() nele cai no ramo "não pode ser tocado".
