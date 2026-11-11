"""FACTORY METHOD (criacional): cada fábrica cria seu Adapter correspondente.

Creator = FabricaFonte; Factory Method = criar_fonte();
ConcreteCreators = FabricaDeezer/FabricaITunes;
Product = FonteMusical (implementada por AdaptadorDeezer/AdaptadorITunes).
"""
from abc import ABC, abstractmethod
from biblioteca_musical.padroes.estruturais.adapter import AdaptadorDeezer, AdaptadorITunes
from biblioteca_musical.padroes.estruturais.facade import CatalogoMusical

# FACTORY METHOD: o Creator define a operação geral e o método de fábrica.
class FabricaFonte(ABC):
    """FACTORY METHOD (criacional): subclasses decidem que Adapter criar."""

    def criar_catalogo(self):
        # Operação estável herdada; chama o Factory Method polimórfico.
        return CatalogoMusical(self.criar_fonte())

    @abstractmethod
    def criar_fonte(self):
        # FACTORY METHOD: ConcreteCreators escolhem qual produto criar.
        pass


# ConcreteCreator: devolve um produto que implementa FonteMusical.
class FabricaDeezer(FabricaFonte):
    def criar_fonte(self):
        return AdaptadorDeezer()


# ConcreteCreator alternativo: não altera criar_catalogo() nem main.py.
class FabricaITunes(FabricaFonte):
    def criar_fonte(self):
        return AdaptadorITunes()
