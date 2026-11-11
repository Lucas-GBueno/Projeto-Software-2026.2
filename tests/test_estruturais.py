"""Adapter e Facade: contratos comuns e tradução entre formatos externos."""
import unittest
from unittest.mock import patch
import requests
from tests.auxiliares import ClienteFake, RespostaFake
from biblioteca_musical.dominio.midias import Reproduzivel
from biblioteca_musical.padroes.estruturais.adapter import AdaptadorDeezer, AdaptadorITunes
from biblioteca_musical.integracoes.catalogo import buscar_faixas, configurar_provedor

# TESTES ESTRUTURAIS: a fonte HTTP é falsa, mas o Adapter e a Facade são reais.
class TesteAdaptadores(unittest.TestCase):
    def test_deezer_converte_faixa_com_ids(self):
        cliente = ClienteFake({"data": [
            {"id": 1, "title": "Música", "artist": {"id": 8, "name": "A"},
             "album": {"id": 9}, "duration": 200},
            {"id": 2, "title": "Incompleta"},
        ]})
        resposta = AdaptadorDeezer(cliente).buscar_faixas("Música & Sol")
        self.assertEqual(len(resposta), 1)
        self.assertEqual(resposta[0][0].id_album, 9)
        self.assertEqual(resposta[0][0].id_artista, 8)
        self.assertEqual(cliente.chamadas[0][1]["params"]["q"], "Música & Sol")

    def test_itunes_converte_milissegundos_e_metadados(self):
        cliente = ClienteFake({"results": [{
            "trackId": 40, "trackName": "Música", "artistName": "B",
            "trackTimeMillis": 125000, "collectionId": 80, "artistId": 100,
        }]})
        achadas = AdaptadorITunes(cliente).buscar_faixas("Música")
        self.assertEqual(achadas[0][0].duracao_segundos, 125)
        self.assertEqual(achadas[0][0].id_album, 80)
        self.assertEqual(achadas[0][0].id_artista, 100)

    def test_itunes_constroi_album(self):
        cliente = ClienteFake({"results": [
            {"wrapperType": "collection", "collectionId": 80,
             "collectionName": "Disco", "primaryGenreName": "Rock"},
            {"wrapperType": "track", "trackId": 40, "trackName": "Música",
             "artistName": "B", "artistId": 100, "trackTimeMillis": 61000},
        ]})
        album = AdaptadorITunes(cliente).buscar_album(80)
        self.assertEqual(album.titulo, "Disco")
        self.assertEqual(album.generos, ["Rock"])
        self.assertEqual(album.calcular_duracao(), 61)
        self.assertEqual(len(album._faixas), 1)

    def test_deezer_constroi_album(self):
        cliente = ClienteFake({"id": 8, "title": "Disco", "tracks": {"data": [
            {"id": 3, "title": "Música", "artist": {"name": "A", "id": 7}, "duration": 50}
        ]}})
        album = AdaptadorDeezer(cliente).buscar_album(8)
        self.assertEqual(album.calcular_duracao(), 50)
        self.assertNotIsInstance(album, Reproduzivel)

    def test_itunes_busca_artista(self):
        cliente = ClienteFake({"results": [{"wrapperType": "artist", "artistId": 11,
                                            "artistName": "Pessoa"}]})
        artista = AdaptadorITunes(cliente).buscar_artista(11)
        self.assertEqual(artista.titulo, "Pessoa")
        self.assertFalse(isinstance(artista, Reproduzivel))

    def test_deezer_busca_artista(self):
        cliente = ClienteFake({"id": 11, "name": "Pessoa"})
        artista = AdaptadorDeezer(cliente).buscar_artista(11)
        self.assertEqual(artista.titulo, "Pessoa")
        self.assertTrue(hasattr(artista, "adicionar_album"))

    def test_falha_de_rede_e_http_retornam_resultado_vazio(self):
        for cliente in (ClienteFake(erro=requests.exceptions.Timeout()),
                        ClienteFake(dados={}, erro_http=True)):
            fonte = AdaptadorITunes(cliente)
            self.assertEqual(fonte.buscar_faixas("Testar"), [])
            self.assertIsNone(fonte.buscar_album(1))
            self.assertIsNone(fonte.buscar_artista(1))

    def test_listas_nulas_ou_invalidas_nas_respostas(self):
        deezer = AdaptadorDeezer(ClienteFake({"data": None}))
        self.assertEqual(deezer.buscar_faixas("nome"), [])
        itunes = AdaptadorITunes(ClienteFake({"results": [None, "inválido"]}))
        self.assertEqual(itunes.buscar_faixas("nome"), [])
        self.assertIsNone(itunes.buscar_album(1))
        self.assertIsNone(itunes.buscar_artista(1))

    def test_dados_incompletos_nao_interrompem(self):
        fonte = AdaptadorDeezer(ClienteFake({"data": [{"id": 5}]}))
        self.assertEqual(fonte.buscar_faixas("nome"), [])
        self.assertIsNone(AdaptadorDeezer(ClienteFake({})).buscar_album(5))

    def test_fachada_troca_de_fonte(self):
        from biblioteca_musical.integracoes import catalogo as api
        from biblioteca_musical.padroes.estruturais import adapter as modulo_adapters
        anterior = api.nome_provedor_atual()
        try:
            with patch.object(modulo_adapters.requests, "get", return_value=RespostaFake({"results": []})):
                configurar_provedor("itunes")
                self.assertEqual(buscar_faixas("nome"), [])
            with patch.object(modulo_adapters.requests, "get", return_value=RespostaFake({"data": []})):
                configurar_provedor("deezer")
                self.assertEqual(buscar_faixas("nome"), [])
            with self.assertRaises(ValueError):
                configurar_provedor("desconhecida")
        finally:
            configurar_provedor(anterior)

    def test_facade_delega_as_tres_operacoes_a_fonte(self):
        """FACADE: o cliente depende só das três operações comuns."""
        from biblioteca_musical.padroes.estruturais.adapter import FonteMusical
        from biblioteca_musical.padroes.estruturais.facade import CatalogoMusical
        class FonteExemplo(FonteMusical):
            def __init__(self):
                self.chamadas = []
            def buscar_faixas(self, nome):
                self.chamadas.append(("faixas", nome)); return []
            def buscar_album(self, chave):
                self.chamadas.append(("album", chave)); return None
            def buscar_artista(self, chave):
                self.chamadas.append(("artista", chave)); return None
        fonte = FonteExemplo()
        fachada = CatalogoMusical(fonte)
        self.assertEqual(fachada.buscar_faixas("teste"), [])
        self.assertIsNone(fachada.buscar_album(12))
        self.assertIsNone(fachada.buscar_artista(34))
        self.assertEqual(fonte.chamadas, [("faixas", "teste"), ("album", 12), ("artista", 34)])
