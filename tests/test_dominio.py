"""Domínio: avaliação, duplicações, integridade de playlists e recursão."""
import contextlib
import io
import unittest
from tests.auxiliares import faixa
from biblioteca_musical.dominio.midias import Album, Artista, Playlist
from biblioteca_musical.dominio.biblioteca import Biblioteca

# TESTES DE DOMÍNIO: encapsulamento, Composite, recursão e remoção em cascata.
class TesteDominio(unittest.TestCase):
    def test_avaliacao_integral(self):
        musica = faixa()
        for nota in (0, 3, 5):
            musica.avaliacao = nota
            self.assertEqual(musica.avaliacao, nota)
        for nota in (True, 2.5, -1, 6, "2"):
            with self.assertRaises(ValueError):
                musica.avaliacao = nota

    def test_playlist_impede_ciclos_diretos_e_indiretos(self):
        a = Playlist("a", "A")
        b = Playlist("b", "B")
        c = Playlist("c", "C")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertFalse(a.adicionar_item(a))
            self.assertTrue(a.adicionar_item(b))
            self.assertTrue(b.adicionar_item(c))
            self.assertFalse(c.adicionar_item(a))
        self.assertEqual(a.calcular_duracao(), 0)

    def test_playlist_recusa_artista(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertFalse(Playlist("p", "Lista").adicionar_item(Artista(3, "Pessoa")))

    def test_biblioteca_encapsula_duplicatas(self):
        bib = Biblioteca()
        self.assertTrue(bib.esta_vazia())
        musica = faixa()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(bib.adicionar_midia(musica))
            self.assertFalse(bib.adicionar_midia(musica))
        copia = bib.obter_itens()
        copia.clear()
        self.assertEqual(len(bib.obter_itens()), 1)

    def test_remocao_cascata_e_aninhada(self):
        musica = faixa()
        sub = Playlist("sub", "Sub")
        raiz = Playlist("raiz", "Principal")
        sub.adicionar_item(musica)
        raiz.adicionar_item(sub)
        bib = Biblioteca()
        with contextlib.redirect_stdout(io.StringIO()):
            bib.adicionar_midia(musica)
            self.assertTrue(bib.remover_midia(1, [raiz]))
        self.assertTrue(bib.esta_vazia())
        self.assertEqual(sub.obter_itens(), [])

    def test_composite_percorre_tres_niveis_e_soma_duracoes(self):
        """COMPOSITE: playlist -> sub-playlist -> álbum -> faixa."""
        m = faixa(7, "Trilha")
        album = Album(8, "Álbum")
        album.adicionar_faixa(m)
        sub = Playlist("sub", "Subplaylist")
        raiz = Playlist("raiz", "Principal")
        sub.adicionar_item(album)
        raiz.adicionar_item(sub)
        self.assertEqual(raiz.calcular_duracao(), 150)
        descricao = raiz.exibir_detalhado()
        self.assertIn("Principal", descricao)
        self.assertIn("Subplaylist", descricao)
        self.assertIn("Álbum", descricao)
        self.assertIn("Trilha", descricao)

    def test_remocao_compartilhada_atinge_subplaylist_apenas_uma_vez(self):
        """RECURSÃO + CONSISTÊNCIA: subárvore compartilhada é visitada uma vez."""
        m = faixa(6)
        sub = Playlist("sub", "Compartilhada")
        a, b = Playlist("a", "Raiz A"), Playlist("b", "Raiz B")
        sub.adicionar_item(m)
        a.adicionar_item(sub)
        b.adicionar_item(sub)
        biblioteca = Biblioteca()
        with contextlib.redirect_stdout(io.StringIO()):
            biblioteca.adicionar_midia(m)
            biblioteca.adicionar_midia(a)
            biblioteca.adicionar_midia(b)
            self.assertTrue(biblioteca.remover_midia(m.id_deezer))
        self.assertEqual(sub.obter_itens(), [])
