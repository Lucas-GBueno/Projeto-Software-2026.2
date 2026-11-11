"""Factory Method e Builder: criação correta, validação e encadeamento."""
import unittest
from tests.auxiliares import faixa
from biblioteca_musical.dominio.midias import Album, Artista
from biblioteca_musical.padroes.criacionais.factory_method import FabricaDeezer, FabricaITunes
from biblioteca_musical.padroes.criacionais.builder import PlaylistBuilder
from biblioteca_musical.padroes.estruturais.adapter import AdaptadorDeezer, AdaptadorITunes
from biblioteca_musical.padroes.estruturais.facade import CatalogoMusical

# TESTES CRIACIONAIS: validam as fábricas e montagem incremental.
class TesteCriacionais(unittest.TestCase):
    def test_factory_method_seleciona_implementacao(self):
        self.assertIsInstance(FabricaDeezer().criar_fonte(), AdaptadorDeezer)
        self.assertIsInstance(FabricaITunes().criar_fonte(), AdaptadorITunes)
        self.assertIsInstance(FabricaITunes().criar_catalogo(), CatalogoMusical)

    def test_builder_monta_itens_de_tipos_diferentes(self):
        musica = faixa()
        album = Album(19, "Disco")
        album.adicionar_faixa(musica)
        pl = PlaylistBuilder("Estudar").adicionar(musica).adicionar(album).construir()
        self.assertEqual(pl.titulo, "Estudar")
        self.assertEqual(pl.calcular_duracao(), 300)
        self.assertEqual(pl.obter_itens(), [musica, album])
        self.assertTrue(pl.id_deezer.startswith("pl-"))

    def test_builder_sem_itens_e_ids_unicos(self):
        p1 = PlaylistBuilder("Um").construir()
        p2 = PlaylistBuilder("Dois").construir()
        self.assertEqual(p1.obter_itens(), [])
        self.assertNotEqual(p1.id_deezer, p2.id_deezer)

    def test_builder_valida_titulo_e_componentes(self):
        with self.assertRaises(ValueError):
            PlaylistBuilder("  ")
        with self.assertRaises(TypeError):
            PlaylistBuilder("Músicas").adicionar(Artista(99, "Cantor"))

    def test_builder_reutilizado_cria_playlists_independentes(self):
        """BUILDER: a etapa construir() entrega novos objetos a cada chamada."""
        m = faixa()
        construtor = PlaylistBuilder("Favoritas").adicionar(m)
        primeira = construtor.construir()
        segunda = construtor.construir()
        self.assertIsNot(primeira, segunda)
        self.assertNotEqual(primeira.id_deezer, segunda.id_deezer)
        self.assertEqual(primeira.obter_itens(), [m])
        self.assertEqual(segunda.obter_itens(), [m])
