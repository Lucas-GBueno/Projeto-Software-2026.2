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
    RF10: Adiciona um novo critério de ordenação sem tocar no código de
    ordenação existente (nem nos critérios já registrados).

    Se já existir um critério com esse nome, NÃO sobrescreve (retorna False):
    assim, registrar um critério novo nunca altera um que já estava inserido.
    Retorna True quando o critério foi adicionado.
    """
    if not callable(funcao_chave):
        raise TypeError("A função-chave do critério precisa ser chamável (ex: lambda midia: midia.ano).")
    if nome in CRITERIOS_ORDENACAO:
        return False
    CRITERIOS_ORDENACAO[nome] = funcao_chave
    return True


def remover_criterio_ordenacao(nome):
    """
    RF10: Retira UM critério de ordenação pelo nome.
    """
    return CRITERIOS_ORDENACAO.pop(nome, None) is not None


class Midia(ABC):
    def __init__(self, id_externo, titulo):
        self.id_externo = id_externo
        self.titulo = titulo

    @abstractmethod
    def calcular_duracao(self):
        pass

    @abstractmethod
    def exibir_info(self):
        pass

    def exibir_detalhado(self, nivel=0):
        marcador = "▸" if nivel == 0 else "↳"
        return ("  " * nivel) + f"{marcador} " + self.exibir_info()

class Reproduzivel(ABC):
    @abstractmethod
    def play(self):
        pass

class FaixaMusical(Midia, Reproduzivel):
    def __init__(self, id_externo, titulo, artista, duracao_segundos, avaliacao=None, id_album=None, id_artista=None):
        super().__init__(id_externo, titulo)
        self.artista = artista
        self.duracao_segundos = duracao_segundos
        self.id_album = id_album
        self.id_artista = id_artista
        self._avaliacao = None
        
        if avaliacao is not None:
            self.avaliacao = avaliacao

    @property
    def avaliacao(self):
        return self._avaliacao

    @avaliacao.setter
    def avaliacao(self, valor):
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise ValueError(f"❌ Erro: A nota {valor} é inválida. Use apenas números inteiros de 0 a 5 (sem decimais).")
        if not (0 <= valor <= 5):
            raise ValueError(f"❌ Erro: A nota {valor} é impossível. Avalie entre 0 e 5.")
        self._avaliacao = valor

    def calcular_duracao(self):
        return self.duracao_segundos

    def exibir_info(self):
        nota = f"⭐ {self.avaliacao}/5" if self.avaliacao is not None else "⭐ Sem nota"
        return f"🎵 Faixa: {self.titulo} - {self.artista} ⏱️ {self.calcular_duracao()}s | {nota}"

    def play(self):
        return f"> Tocando agora: {self.titulo} - {self.artista}"
    
class Album(Midia, Reproduzivel):
    def __init__(self, id_externo, titulo):
        super().__init__(id_externo, titulo)
        self._faixas = []

    def adicionar_faixa(self, faixa):
        self._faixas.append(faixa)

    def calcular_duracao(self):
        return sum(faixa.calcular_duracao() for faixa in self._faixas)

    def exibir_info(self):
        return f"💿 Álbum: {self.titulo} ({len(self._faixas)} faixas) ⏱️ Duração total: {self.calcular_duracao()}s"

    def exibir_detalhado(self, nivel=0):
        linhas = [super().exibir_detalhado(nivel)]
        for faixa in self._faixas:
            linhas.append(faixa.exibir_detalhado(nivel + 1))
        return "\n".join(linhas)

    def play(self):
            return f"> Tocando agora: {self.titulo}"

class Playlist(Midia, Reproduzivel):
    def __init__(self, id_externo, titulo):
        super().__init__(id_externo, titulo)
        self._itens = []

    def adicionar_item(self, item):
        if not isinstance(item, Reproduzivel):
            print(f"\n🚫 [BLOQUEADO] '{item.titulo}' não pode ser adicionado a uma playlist (não é reproduzível).")
            return False
        self._itens.append(item)
        return True

    def obter_itens(self):
        return list(self._itens)

    def remover_item(self, item):
        if item in self._itens:
            self._itens.remove(item)
            return True
        return False

    def remover_item_recursivo(self, item):
        playlists_afetadas = 0
        if self.remover_item(item):
            playlists_afetadas += 1

        for sub_item in self._itens:
            if isinstance(sub_item, Playlist):
                playlists_afetadas += sub_item.remover_item_recursivo(item)

        return playlists_afetadas

    def calcular_duracao(self):
        return sum(item.calcular_duracao() for item in self._itens)

    def exibir_info(self):
        return f"📋 Playlist: {self.titulo} ({len(self._itens)} itens) ⏱️ Duração total: {self.calcular_duracao()}s"

    def exibir_detalhado(self, nivel=0):
        linhas = [super().exibir_detalhado(nivel)]
        for item in self._itens:
            linhas.append(item.exibir_detalhado(nivel + 1))
        return "\n".join(linhas)

    def play(self):
        return f"> Iniciando reprodução da playlist '{self.titulo}' ({len(self._itens)} itens)..."

class Artista(Midia):
    def __init__(self, id_externo, titulo, musica_maior_sucesso=None):
        super().__init__(id_externo, titulo)
        self.musica_maior_sucesso = musica_maior_sucesso
        self._generos = []
        self._discografia = []

    def adicionar_genero(self, genero):
        if genero not in self._generos:
            self._generos.append(genero)

    def adicionar_album(self, album):
        self._discografia.append(album)

    def obter_discografia(self):
        return list(self._discografia)

    def calcular_duracao(self):
        return sum(album.calcular_duracao() for album in self._discografia)

    def exibir_info(self):
        generos_str = ", ".join(self._generos) if self._generos else "gênero não informado"
        sucesso_str = self.musica_maior_sucesso or "não informado"
        return (f"🎤 Artista: {self.titulo} | 🏆 Maior sucesso: {sucesso_str} "
                f"| 🎼 Gêneros: {generos_str} | 💿 {len(self._discografia)} álbum(ns) na discografia")

    def exibir_detalhado(self, nivel=0):
        linhas = [super().exibir_detalhado(nivel)]
        marcador = "  " * (nivel + 1) + "↳"
        for album in self._discografia:
            linhas.append(f"{marcador} {album.titulo} (⏱️ {album.calcular_duracao()}s)")
        return "\n".join(linhas)


class Biblioteca:
    def __init__(self):
        self._colecao = {}

    def esta_vazia(self):
        return not self._colecao

    def obter_itens(self):
        return list(self._colecao.values())

    def adicionar_midia(self, midia):
        if midia.id_externo in self._colecao:
            print(f"\n🚫 [BLOQUEADO] '{midia.titulo}' já está na biblioteca! (Duplicata recusada)")
            return False
        
        self._colecao[midia.id_externo] = midia
        print(f"\n✅ [SUCESSO] '{midia.titulo}' adicionado à biblioteca!")
        return True

    def remover_midia(self, id_midia, playlists=None):
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
        if not self._colecao:
            print("\n┌─────────────────────────────────────────┐")
            print("│      📭 Sua biblioteca está vazia.      │")
            print("└─────────────────────────────────────────┘")
            return

        funcao_chave = CRITERIOS_ORDENACAO.get(criterio)
        if funcao_chave is None:
            if CRITERIOS_ORDENACAO:
                disponiveis = ", ".join(CRITERIOS_ORDENACAO.keys())
                print(f"\n⚠️  Critério '{criterio}' não existe. Critérios disponíveis: {disponiveis}")
            else:
                print("\n⚠️  Nenhum critério de ordenação está disponível no momento.")
            return

        try:
            itens_ordenados = sorted(self._colecao.values(), key=funcao_chave, reverse=decrescente)
        except (AttributeError, TypeError, ValueError, KeyError) as erro:
            print(f"\n⚠️  O critério '{criterio}' não pôde ser aplicado a todos os itens ({type(erro).__name__}). Escolha outro critério.")
            return

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
            print(midia.exibir_detalhado())
            duracao_total += midia.calcular_duracao() 
            
        minutos = duracao_total // 60
        segundos = duracao_total % 60
        
        print("╠══════════════════════════════════════════════════════════════════╣")
        print(f"║ ⏱️  Duração Total da Coleção: {duracao_total}s ({minutos}m {segundos}s)".ljust(67) + "║")
        print("╚══════════════════════════════════════════════════════════════════╝")