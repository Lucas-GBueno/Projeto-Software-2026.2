from abc import ABC, abstractmethod

# RF10 (POLIMORFISMO / padrão Strategy): cada critério de ordenação é um OBJETO
# que sabe calcular a "chave de comparação" de uma mídia. A Biblioteca ordena
# chamando criterio.chave(midia) sem saber qual critério concreto está usando —
# então adicionar um critério novo significa criar uma nova subclasse e
# registrá-la, sem editar nenhuma das existentes nem o método de ordenação.
class CriterioOrdenacao(ABC):
    def __init__(self, nome):
        self.nome = nome  # nome exibido no menu e usado como identificador no registro

    # ABSTRAÇÃO: cada subclasse define sua própria regra de comparação.
    @abstractmethod
    def chave(self, midia):
        pass


# HERANÇA + POLIMORFISMO: mesmo método chave(), uma regra diferente em cada subclasse.
class OrdenarPorTitulo(CriterioOrdenacao):
    def __init__(self):
        super().__init__('titulo')

    def chave(self, midia):
        return midia.titulo.lower()


class OrdenarPorDuracao(CriterioOrdenacao):
    def __init__(self):
        super().__init__('duracao')

    def chave(self, midia):
        return midia.calcular_duracao()


class OrdenarPorAvaliacao(CriterioOrdenacao):
    def __init__(self):
        super().__init__('avaliacao')

    def chave(self, midia):
        # Só FaixaMusical tem avaliação; os demais tipos contam como -1 (ficam antes das avaliadas).
        nota = getattr(midia, 'avaliacao', None)
        return nota if nota is not None else -1


class OrdenarPorAtributo(CriterioOrdenacao):
    """
    Critério genérico montado em tempo de execução (opção 12 do menu) a partir
    de dados estruturados — nome de um atributo ou método já existente na
    mídia, se ele precisa ser chamado, e um valor padrão para quem não tiver
    esse dado. Evita aceitar código digitado livremente (equivalente a um eval()).
    """
    def __init__(self, nome, atributo, eh_metodo=False, valor_padrao=None):
        super().__init__(nome)
        # ENCAPSULAMENTO: a configuração do critério fica privada, só chave() a usa.
        self._atributo = atributo
        self._eh_metodo = eh_metodo
        self._valor_padrao = valor_padrao

    def chave(self, midia):
        valor = getattr(midia, self._atributo, self._valor_padrao)
        if self._eh_metodo:
            valor = valor() if callable(valor) else self._valor_padrao
        return self._valor_padrao if valor is None else valor


# RF10: registro dos critérios disponíveis (nome -> objeto CriterioOrdenacao).
# Novos critérios são adicionados aqui (ou via registrar_criterio_ordenacao) sem
# que o método de ordenação da Biblioteca precise ser alterado.
CRITERIOS_ORDENACAO = {c.nome: c for c in (OrdenarPorTitulo(), OrdenarPorDuracao(), OrdenarPorAvaliacao())}


def registrar_criterio_ordenacao(criterio):
    """
    RF10: Adiciona um novo critério de ordenação sem tocar no código de
    ordenação existente (nem nos critérios já registrados). Recebe um OBJETO
    de qualquer subclasse de CriterioOrdenacao — o nome de registro é o
    próprio criterio.nome.

    Se já existir um critério com esse nome, NÃO sobrescreve (retorna False):
    assim, registrar um critério novo nunca altera um que já estava inserido.
    Retorna True quando o critério foi adicionado.

    Exemplo de uso, se o professor pedir ordenação por ano — basta uma nova
    subclasse, sem editar nenhuma das existentes:
        class OrdenarPorAno(CriterioOrdenacao):
            def __init__(self):
                super().__init__('ano')
            def chave(self, midia):
                return midia.ano
        registrar_criterio_ordenacao(OrdenarPorAno())
    """
    if not isinstance(criterio, CriterioOrdenacao):
        raise TypeError("O critério precisa ser uma instância de uma subclasse de CriterioOrdenacao.")
    if criterio.nome in CRITERIOS_ORDENACAO:
        return False
    CRITERIOS_ORDENACAO[criterio.nome] = criterio
    return True


def remover_criterio_ordenacao(nome):
    """
    RF10: Retira UM critério de ordenação pelo nome. Só a entrada indicada é
    removida do registro; todos os outros critérios continuam intactos e
    disponíveis. Retorna True se removeu, ou False se não existia um
    critério com esse nome.
    """
    return CRITERIOS_ORDENACAO.pop(nome, None) is not None


# classe abstrata para mídias gerais
class Midia(ABC):
    def __init__(self, id_externo, titulo):
        self.id_externo = id_externo
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
    def __init__(self, id_externo, titulo, artista, duracao_segundos, avaliacao=None, id_album=None, id_artista=None):
        super().__init__(id_externo, titulo)
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
class Album(Midia, Reproduzivel):
    def __init__(self, id_externo, titulo):
        super().__init__(id_externo, titulo)
        # ENCAPSULAMENTO / COMPOSIÇÃO: O álbum tem faixas escondidas internamente.
        self._faixas = []

    def adicionar_faixa(self, faixa):
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

    def play(self): #método para reprodução
            return f"> Tocando agora: {self.titulo} - {self.artista}"

# HERANÇA: Playlist "é uma" Midia.
class Playlist(Midia, Reproduzivel):
    def __init__(self, id_externo, titulo):
        super().__init__(id_externo, titulo)
        self._itens = []

    def adicionar_item(self, item):
        """
        Uma playlist só faz sentido conter itens REPRODUZÍVEIS (faixas,
        álbuns, ou outras playlists). Um Artista, por exemplo, é uma Midia
        mas não implementa Reproduzivel — por isso é estruturalmente
        recusado aqui, sem precisar checar "é um Artista" explicitamente.
        Retorna True se adicionou, False se recusou.
        """
        if not isinstance(item, Reproduzivel):
            print(f"\n🚫 [BLOQUEADO] '{item.titulo}' não pode ser adicionado a uma playlist (não é reproduzível).")
            return False
        self._itens.append(item)
        return True

    def obter_itens(self):
        """Retorna uma cópia da lista de itens, para navegação externa segura sem expor _itens diretamente."""
        return list(self._itens)

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

    def exibir_detalhado(self, nivel=0):
        """POLIMORFISMO/COMPOSIÇÃO: além de si mesma, lista cada item (nivel+1).
        Como cada item chama seu próprio exibir_detalhado(), a recursão
        continua sozinha para Albuns e sub-Playlists aninhadas."""
        linhas = [super().exibir_detalhado(nivel)]
        for item in self._itens:
            linhas.append(item.exibir_detalhado(nivel + 1))
        return "\n".join(linhas)

    def play(self): #método para reprodução
        return f"> Iniciando reprodução da playlist '{self.titulo}' ({len(self._itens)} itens)..."

# HERANÇA: Artista "é uma" Midia — mas, propositalmente, NÃO herda de
# Reproduzivel. Um artista não pode ser tocado diretamente, só suas faixas e
# álbuns podem. Essa classe existe justamente para provar, na prática, que o
# simulador de player (isinstance(midia, Reproduzivel)) sabe diferenciar o
# que é reproduzível do que é só um metadado descritivo.
class Artista(Midia):
    def __init__(self, id_externo, titulo, musica_maior_sucesso=None):
        super().__init__(id_externo, titulo)
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


class Biblioteca:
    def __init__(self):
        # ENCAPSULAMENTO: Dicionário protegido para garantir que ninguém adicione duplicatas burlando a regra.
        self._colecao = {}

    def esta_vazia(self):
        """RF2: permite checar se há itens na biblioteca sem expor _colecao diretamente."""
        return not self._colecao

    def obter_itens(self):
        """
        RF2: retorna uma CÓPIA da lista de itens, para navegação externa segura
        (mesmo princípio de Playlist.obter_itens()). Uma cópia impede que
        alguém mute o estado real da biblioteca por fora dos métodos
        controlados (ex: bib.obter_itens().clear() nunca afeta a coleção real).
        """
        return list(self._colecao.values())

    def adicionar_midia(self, midia):
        if midia.id_externo in self._colecao:
            print(f"\n🚫 [BLOQUEADO] '{midia.titulo}' já está na biblioteca! (Duplicata recusada)")
            return False
        
        self._colecao[midia.id_externo] = midia
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
        basta criar uma subclasse de CriterioOrdenacao e registrá-la com
        registrar_criterio_ordenacao() — este método não precisa ser modificado,
        porque só conhece o contrato chave(midia), nunca um critério específico.
        """
        if not self._colecao:
            print("\n┌─────────────────────────────────────────┐")
            print("│      📭 Sua biblioteca está vazia.      │")
            print("└─────────────────────────────────────────┘")
            return

        criterio_escolhido = CRITERIOS_ORDENACAO.get(criterio)
        if criterio_escolhido is None:
            if CRITERIOS_ORDENACAO:
                disponiveis = ", ".join(CRITERIOS_ORDENACAO.keys())
                print(f"\n⚠️  Critério '{criterio}' não existe. Critérios disponíveis: {disponiveis}")
            else:
                print("\n⚠️  Nenhum critério de ordenação está disponível no momento.")
            return

        try:
            # POLIMORFISMO: sorted() chama criterio_escolhido.chave(midia) para cada item,
            # sem saber qual subclasse de CriterioOrdenacao é (título, duração, atributo...).
            itens_ordenados = sorted(self._colecao.values(), key=criterio_escolhido.chave, reverse=decrescente)
        except (AttributeError, TypeError, ValueError, KeyError) as erro:
            # Um critério recém-adicionado pode não servir para todos os tipos de mídia
            # (ex: valor padrão de tipo incompatível). A falha fica isolada nele: não
            # derruba o programa e não afeta os demais critérios.
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
            # POLIMORFISMO: A chamada funciona para Faixa, Album ou Playlist, e cada objeto sabe o que fazer.
            duracao_total += midia.calcular_duracao() 
            
        minutos = duracao_total // 60
        segundos = duracao_total % 60
        
        print("╠══════════════════════════════════════════════════════════════════╣")
        print(f"║ ⏱️  Duração Total da Coleção: {duracao_total}s ({minutos}m {segundos}s)".ljust(67) + "║")
        print("╚══════════════════════════════════════════════════════════════════╝")