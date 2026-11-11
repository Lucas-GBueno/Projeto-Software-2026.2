"""Fluxo completo do menu, integração dos módulos e critérios extensíveis."""
import unittest
import contextlib
import io
from unittest.mock import patch
from tests.auxiliares import faixa
from biblioteca_musical.dominio.midias import Album, Artista, Playlist
from biblioteca_musical.dominio.biblioteca import Biblioteca

# TESTES DE INTEGRAÇÃO: exercitam as opções reais do menu sem internet.
class TesteFluxoCompleto(unittest.TestCase):
    def test_menu_busca_album_e_artista_preserva_identificadores(self):
        """Simula o fluxo 1 -> 2 -> 3 -> 11 -> 0 sem internet."""
        import runpy
        album = Album(19, "Disco")
        album.adicionar_faixa(faixa())
        entradas = ["1", "Canção", "5", "2", "1", "3", "1", "11", "1", "0"]
        saida = io.StringIO()
        with patch("biblioteca_musical.interface.menu.buscar_faixas", return_value=[(faixa(), 19)]), \
             patch("biblioteca_musical.interface.menu.buscar_album", return_value=album), \
             patch("biblioteca_musical.interface.menu.buscar_artista", return_value=Artista(11, "Artista")), \
             patch("builtins.input", side_effect=entradas), \
             contextlib.redirect_stdout(saida):
            runpy.run_module("main", run_name="__main__")
        texto = saida.getvalue()
        self.assertIn("Disco", texto)
        self.assertIn("Artista", texto)
        self.assertIn("Saindo do sistema", texto)

    def test_biblioteca_limpa_referencias_sem_necessidade_de_lista_externa(self):
        musica = faixa()
        raiz = Playlist("p", "Principal")
        raiz.adicionar_item(musica)
        raiz.adicionar_item(musica)
        bib = Biblioteca()
        with contextlib.redirect_stdout(io.StringIO()):
            bib.adicionar_midia(musica)
            bib.adicionar_midia(raiz)
            self.assertTrue(bib.remover_midia(musica.id_deezer))
        self.assertEqual(raiz.obter_itens(), [])

    def test_menu_remove_faixa_obtida_em_buscas_diferentes(self):
        import runpy
        primeira = faixa()
        segunda = faixa()
        entradas = ["1", "Canção", "5", "2", "1", "1", "Canção", "4",
                    "4", "Lista", "5", "1", "1", "2", "6", "1", "9", "1",
                    "7", "1", "0"]
        saida = io.StringIO()
        with patch("biblioteca_musical.interface.menu.buscar_faixas", side_effect=[[(primeira, 19)], [(segunda, 19)]]), \
             patch("builtins.input", side_effect=entradas), \
             contextlib.redirect_stdout(saida):
            runpy.run_module("main", run_name="__main__")
        self.assertIn("removido da biblioteca e de 1 playlist", saida.getvalue())
        self.assertIn("Playlist: Lista (0 itens)", saida.getvalue())

    def test_menu_exibe_feed_misto_e_recusa_album_no_player(self):
        import runpy
        musica = faixa()
        album = Album(19, "Disco")
        album.adicionar_faixa(musica)
        entradas = ["1", "Canção", "5", "2", "1", "3", "1", "4", "Lista",
                    "5", "1", "2", "1", "8", "2", "14", "0"]
        saida = io.StringIO()
        with patch("biblioteca_musical.interface.menu.buscar_faixas", return_value=[(musica, 19)]), \
             patch("biblioteca_musical.interface.menu.buscar_album", return_value=album), \
             patch("builtins.input", side_effect=entradas), \
             contextlib.redirect_stdout(saida):
            runpy.run_module("main", run_name="__main__")
        texto = saida.getvalue()
        self.assertIn("'Disco' não é uma mídia reproduzível", texto)
        feed = texto.split("--- FEED DE RECOMENDAÇÕES ---")[1]
        self.assertIn("Faixa: Canção", feed)
        self.assertIn("Álbum: Disco", feed)
        self.assertIn("Playlist: Lista (1 itens)", feed)

    def test_criterios_extensiveis(self):
        from biblioteca_musical.dominio.ordenacao import (registrar_criterio_ordenacao,
                             remover_criterio_ordenacao, CRITERIOS_ORDENACAO)
        nome = "teste_criterio"
        try:
            self.assertTrue(registrar_criterio_ordenacao(nome, lambda m: len(m.titulo)))
            self.assertFalse(registrar_criterio_ordenacao(nome, lambda m: 0))
            self.assertIn(nome, CRITERIOS_ORDENACAO)
        finally:
            self.assertTrue(remover_criterio_ordenacao(nome))
