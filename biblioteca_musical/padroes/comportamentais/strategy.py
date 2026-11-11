"""STRATEGY (comportamental): exibição configurável de uma mesma biblioteca.

Papel no GoF: FormatoExibicao = Strategy; FormatoDetalhado/Resumido/Compacto
= ConcreteStrategy. A classe Biblioteca é o Context, que delega `formatar`.
"""
from abc import ABC, abstractmethod

# STRATEGY — interface comum da família de algoritmos de apresentação.
# Os consumidores pedem `formatar(midia)` sem saber a estratégia concreta.
class FormatoExibicao(ABC):
    @abstractmethod
    def formatar(self, midia):
        pass


# STRATEGY concreta 1: percorre a árvore e imprime níveis de objetos.
class FormatoDetalhado(FormatoExibicao):
    def formatar(self, midia):
        return midia.exibir_detalhado()


# STRATEGY concreta 2: exibe o resumo fornecido pela mídia.
class FormatoResumido(FormatoExibicao):
    def formatar(self, midia):
        return midia.exibir_info()


# STRATEGY concreta 3: mostra apenas classe e título.
class FormatoCompacto(FormatoExibicao):
    def formatar(self, midia):
        return f"{type(midia).__name__}: {midia.titulo}"
