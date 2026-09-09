from abc import ABC, abstractmethod

# RF10: registrador de critérios de ordenação. Novos critérios são
# adicionados aqui (ou via registrar_criterio_ordenacao) sem que o método
# de ordenação da Biblioteca precise ser alterado.
CRITERIOS_ORDENACAO = {
    'titulo': lambda midia: midia.titulo.lower(),
    'duracao': lambda midia: midia.calcular_duracao(),
    'avaliacao': lambda midia: getattr(midia, 'avaliacao', None) if getattr(midia, 'avaliacao', None) is not None else -1,
}


def registrar_criterio_ordenacao(nome, funcao_chave):
    """
    RF10: Permite estender a ordenação com um novo critério sem tocar no
    código de ordenação existente (nem nos critérios já registrados).

    Exemplo de uso futuro, se o professor pedir ordenação por ano:
        registrar_criterio_ordenacao('ano', lambda midia: midia.ano)
    """
    CRITERIOS_ORDENACAO[nome] = funcao_chave


# classe abstrata para mídias gerais
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

#classe abstrata para midias reproduziveis 
class Reproduzivel(ABC):
    @abstractmethod
    def play(self):
        pass

# HERANÇA: FaixaMusical "é uma" Midia reproduzivel
class FaixaMusical(Midia, Reproduzivel):
    def __init__(self, id_deezer, titulo, artista, duracao_segundos, avaliacao=None):
        super().__init__(id_deezer, titulo)
        self.artista = artista
        self.duracao_segundos = duracao_segundos
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
class Album(Midia, Reproduzivel):
    def __init__(self, id_deezer, titulo):
        super().__init__(id_deezer, titulo)
        # ENCAPSULAMENTO / COMPOSIÇÃO: O álbum tem faixas escondidas internamente.
        self._faixas = []

    def adicionar_faixa(self, faixa):
        self._faixas.append(faixa)

    # POLIMORFISMO: Calcula do seu próprio jeito (somando as faixas).
    def calcular_duracao(self):
        return sum(faixa.calcular_duracao() for faixa in self._faixas)

    def exibir_info(self):
        return f"💿 Álbum: {self.titulo} ({len(self._faixas)} faixas) ⏱️ Duração total: {self.calcular_duracao()}s"

    def play(self): #método para reprodução
            return f"> Tocando agora: {self.titulo} - {self.artista}"

# HERANÇA: Playlist "é uma" Midia.
class Playlist(Midia, Reproduzivel):
    def __init__(self, id_deezer, titulo):
        super().__init__(id_deezer, titulo)
        self._itens = []

    def adicionar_item(self, item):
        self._itens.append(item)

    def remover_item(self, item):
        """RF9: Remove uma referência direta a 'item' desta playlist, se existir."""
        if item in self._itens:
            self._itens.remove(item)
            return True
        return False

    def remover_item_recursivo(self, item):
        """
        RF9: Remove referências a 'item' nesta playlist E em qualquer
        sub-playlist aninhada dentro dela (RF6 permite playlist dentro de
        playlist). Retorna quantas playlists tiveram o item removido, para
        que quem chamou saiba o alcance real da remoção.
        """
        playlists_afetadas = 0
        if self.remover_item(item):
            playlists_afetadas += 1

        for sub_item in self._itens:
            if isinstance(sub_item, Playlist):
                playlists_afetadas += sub_item.remover_item_recursivo(item)

        return playlists_afetadas

    # POLIMORFISMO: Forma própria de calcular a duração.
    def calcular_duracao(self):
        return sum(item.calcular_duracao() for item in self._itens)

    def exibir_info(self):
        return f"📋 Playlist: {self.titulo} ({len(self._itens)} itens) ⏱️ Duração total: {self.calcular_duracao()}s"

    def play(self): #método para reprodução
        return f"> Iniciando reprodução da playlist '{self.titulo}' ({len(self._itens)} itens)..."

class Biblioteca:
    def __init__(self):
        # ENCAPSULAMENTO: Dicionário protegido para garantir que ninguém adicione duplicatas burlando a regra.
        self._colecao = {}

    def adicionar_midia(self, midia):
        if midia.id_deezer in self._colecao:
            print(f"\n🚫 [BLOQUEADO] '{midia.titulo}' já está na biblioteca! (Duplicata recusada)")
            return False
        
        self._colecao[midia.id_deezer] = midia
        print(f"\n✅ [SUCESSO] '{midia.titulo}' adicionado à biblioteca!")
        return True

    def remover_midia(self, id_midia, playlists=None):
        """
        RF9: Remove um item da biblioteca tratando corretamente as
        referências existentes em playlists.

        Política adotada (documentada aqui por ser uma decisão de design):
        REMOÇÃO EM CASCATA. Ao remover um item da biblioteca, o item também
        é removido de todas as playlists (e sub-playlists aninhadas) que o
        referenciam, para nunca deixar uma playlist apontando para um item
        que não existe mais. O chamador é avisado de quantas playlists
        foram afetadas.
        """
        midia = self._colecao.get(id_midia)
        if midia is None:
            print("\n⚠️  Nenhum item com esse identificador foi encontrado na biblioteca.")
            return False

        playlists_afetadas = 0
        if playlists:
            for playlist in playlists:
                playlists_afetadas += playlist.remover_item_recursivo(midia)

        del self._colecao[id_midia]

        if playlists_afetadas:
            print(f"\n🗑️  '{midia.titulo}' removido da biblioteca e de {playlists_afetadas} playlist(s) (incluindo sub-playlists) que o continham.")
        else:
            print(f"\n🗑️  '{midia.titulo}' removido da biblioteca.")
        return True

    def listar_biblioteca_ordenada(self, criterio='titulo', decrescente=False):
        """
        RF10: Ordena a biblioteca por qualquer critério presente em
        CRITERIOS_ORDENACAO. Para adicionar um novo critério (ex: 'ano'),
        basta registrá-lo com registrar_criterio_ordenacao() — este método
        não precisa ser modificado.
        """
        if not self._colecao:
            print("\n┌─────────────────────────────────────────┐")
            print("│      📭 Sua biblioteca está vazia.      │")
            print("└─────────────────────────────────────────┘")
            return

        funcao_chave = CRITERIOS_ORDENACAO.get(criterio)
        if funcao_chave is None:
            disponiveis = ", ".join(CRITERIOS_ORDENACAO.keys())
            print(f"\n⚠️  Critério '{criterio}' não existe. Critérios disponíveis: {disponiveis}")
            return

        itens_ordenados = sorted(self._colecao.values(), key=funcao_chave, reverse=decrescente)

        print("\n╔══════════════════════════════════════════════════════════════════╗")
        print(f"║  📚 BIBLIOTECA ORDENADA POR '{criterio.upper()}'".ljust(69) + "║")
        print("╠══════════════════════════════════════════════════════════════════╣")
        for midia in itens_ordenados:
            print(f"  ▸ {midia.exibir_info()}")
        print("╚══════════════════════════════════════════════════════════════════╝")

    def listar_biblioteca(self):
        if not self._colecao:
            print("\n┌─────────────────────────────────────────┐")
            print("│      📭 Sua biblioteca está vazia.      │")
            print("└─────────────────────────────────────────┘")
            return

        print("\n╔══════════════════════════════════════════════════════════════════╗")
        print("║                     📚 SUA BIBLIOTECA MUSICAL                     ║")
        print("╠══════════════════════════════════════════════════════════════════╣")
        
        duracao_total = 0
        for midia in self._colecao.values():
            print(f"  ▸ {midia.exibir_info()}")
            # POLIMORFISMO: A chamada funciona para Faixa, Album ou Playlist, e cada objeto sabe o que fazer.
            duracao_total += midia.calcular_duracao() 
            
        minutos = duracao_total // 60
        segundos = duracao_total % 60
        
        print("╠══════════════════════════════════════════════════════════════════╣")
        print(f"║ ⏱️  Duração Total da Coleção: {duracao_total}s ({minutos}m {segundos}s)".ljust(67) + "║")
        print("╚══════════════════════════════════════════════════════════════════╝")