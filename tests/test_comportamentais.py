"""Strategy: mesmo conjunto de objetos, múltiplas representações."""
import unittest
import contextlib
import io
from tests.auxiliares import faixa
from biblioteca_musical.dominio.midias import Album
from biblioteca_musical.dominio.biblioteca import Biblioteca
from biblioteca_musical.padroes.comportamentais.strategy import (FormatoDetalhado, FormatoResumido, FormatoCompacto)

class TesteStrategy(unittest.TestCase):
    # STRATEGY: prova que o Context (Biblioteca) delega à estratégia recebida.
    def test_estrategias_de_exibicao(self):
        album = Album(4, "Disco")
        album.adicionar_faixa(faixa())
        self.assertIn("Faixa", FormatoDetalhado().formatar(album))
        self.assertIn("Álbum", FormatoResumido().formatar(album))
        self.assertEqual(FormatoCompacto().formatar(album), "Album: Disco")
        bib = Biblioteca()
        with contextlib.redirect_stdout(io.StringIO()):
            bib.adicionar_midia(album)
        fluxo = io.StringIO()
        with contextlib.redirect_stdout(fluxo):
            bib.listar_biblioteca(formato=FormatoCompacto())
            bib.listar_biblioteca_ordenada("titulo", formato=FormatoCompacto())
        self.assertEqual(fluxo.getvalue().count("Album: Disco"), 2)

    def test_strategy_aceita_novo_formato_sem_mudar_biblioteca(self):
        """EXTENSIBILIDADE: uma ConcreteStrategy nova funciona sem editar Context."""
        from biblioteca_musical.padroes.comportamentais.strategy import FormatoExibicao
        class FormatoMaiusculo(FormatoExibicao):
            def formatar(self, midia):
                return midia.titulo.upper()
        b = Biblioteca()
        with contextlib.redirect_stdout(io.StringIO()):
            b.adicionar_midia(faixa())
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            b.listar_biblioteca(formato=FormatoMaiusculo())
        self.assertIn("CANÇÃO", saida.getvalue())
