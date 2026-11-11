"""Biblioteca: encapsulamento, consistência, remoção em cascata e ordenação.

A Biblioteca conhece as mídias; não conhece HTTP nem o menu do terminal.
Ela utiliza estratégias de exibição passadas por quem a chama.
"""

from biblioteca_musical.dominio.midias import Playlist
from biblioteca_musical.dominio.ordenacao import CRITERIOS_ORDENACAO
from biblioteca_musical.padroes.comportamentais.strategy import FormatoDetalhado, FormatoResumido

# CONSISTÊNCIA: um único gestor da coleção e de suas referências em playlists.
# STRATEGY: usa um objeto de formatação, não codifica formatos na listagem.
class Biblioteca:
    def __init__(self):
        # ENCAPSULAMENTO: Coleção protegida contra alterações externas.
        self._colecao = {}

    def esta_vazia(self):
        return not self._colecao

    def obter_itens(self):
        """Retorna uma cópia dos itens, sem expor o dicionário interno."""
        return list(self._colecao.values())

    def adicionar_midia(self, midia):
        # CONSISTÊNCIA (RF2): dicionário indexado pelo identificador evita
        # que a mesma mídia seja adicionada duas vezes à biblioteca.
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

        # Varre todas as playlists sob controle da biblioteca, além das
        # ainda não armazenadas mas explicitamente informadas pelo menu.
        # REMOÇÃO EM CASCATA: descubra todas as raízes de playlists sob
        # controle da biblioteca antes de apagar o objeto do índice principal.
        raizes = [item for item in self._colecao.values() if isinstance(item, Playlist)]
        raizes.extend(playlists or [])
        playlists_afetadas = 0
        visitadas = set()
        for playlist in raizes:
            # RECURSÃO: desce por qualquer profundidade de sub-playlists.
            # `visitadas` é compartilhado para não percorrer repetidamente.
            playlists_afetadas += playlist.remover_item_recursivo(midia, visitadas)

        del self._colecao[id_midia]

        if playlists_afetadas:
            print(f"\n🗑️  '{midia.titulo}' removido da biblioteca e de {playlists_afetadas} playlist(s) (incluindo sub-playlists) que o continham.")
        else:
            print(f"\n🗑️  '{midia.titulo}' removido da biblioteca.")
        return True

    def listar_biblioteca_ordenada(self, criterio='titulo', decrescente=False, formato=None):
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

        # ORDENAÇÃO EXTENSÍVEL: obter a função de chave no registro; uma nova
        # regra não exige alterar esta função da Biblioteca.
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
            # Um critério recém-adicionado pode não servir para todos os tipos de mídia
            # (ex: valor padrão de tipo incompatível). A falha fica isolada nele: não
            # derruba o programa e não afeta os demais critérios.
            print(f"\n⚠️  O critério '{criterio}' não pôde ser aplicado a todos os itens ({type(erro).__name__}). Escolha outro critério.")
            return

        formato = formato or FormatoResumido()
        print("\n╔══════════════════════════════════════════════════════════════════╗")
        print(f"║  📚 BIBLIOTECA ORDENADA POR '{criterio.upper()}'".ljust(69) + "║")
        print("╠══════════════════════════════════════════════════════════════════╣")
        for midia in itens_ordenados:
            # STRATEGY: o algoritmo de listagem delega a apresentação.
            print(f"  ▸ {formato.formatar(midia)}")
        print("╚══════════════════════════════════════════════════════════════════╝")

    def listar_biblioteca(self, formato=None):
        if not self._colecao:
            print("\n┌─────────────────────────────────────────┐")
            print("│      📭 Sua biblioteca está vazia.      │")
            print("└─────────────────────────────────────────┘")
            return

        print("\n╔══════════════════════════════════════════════════════════════════╗")
        print("║                     📚 SUA BIBLIOTECA MUSICAL                     ║")
        print("╠══════════════════════════════════════════════════════════════════╣")
        
        formato = formato or FormatoDetalhado()
        duracao_total = 0
        for midia in self._colecao.values():
            # STRATEGY: trocar o objeto formato muda a apresentação em runtime.
            print(formato.formatar(midia))
            # POLIMORFISMO: A chamada funciona para Faixa, Album ou Playlist, e cada objeto sabe o que fazer.
            duracao_total += midia.calcular_duracao() 
            
        minutos = duracao_total // 60
        segundos = duracao_total % 60
        
        print("╠══════════════════════════════════════════════════════════════════╣")
        print(f"║ ⏱️  Duração Total da Coleção: {duracao_total}s ({minutos}m {segundos}s)".ljust(67) + "║")
        print("╚══════════════════════════════════════════════════════════════════╝")
