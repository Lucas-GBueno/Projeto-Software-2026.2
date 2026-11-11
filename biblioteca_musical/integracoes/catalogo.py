"""Configuração do provedor e funções simples utilizadas pelo menu.

Esta camada faz a ligação entre os padrões criacionais/estruturais e a UI.
"""
from functools import lru_cache
from biblioteca_musical.padroes.criacionais.factory_method import FabricaDeezer, FabricaITunes

# Integração de alto nível: escolhe UMA fábrica por nome, aplica o Factory
# Method e entrega à interface a mesma Facade, independente da API externa.
PROVEDOR_ATUAL = "deezer"
FABRICAS = {
    "deezer": FabricaDeezer,
    "itunes": FabricaITunes,
}


def configurar_provedor(nome):
    """Troca a fonte sem editar a lógica de pesquisa e sem reiniciar o programa."""
    global PROVEDOR_ATUAL
    nome = nome.strip().lower()
    if nome not in FABRICAS:
        raise ValueError(f"Provedor desconhecido: {nome}. Disponíveis: {', '.join(FABRICAS)}")
    PROVEDOR_ATUAL = nome


def nome_provedor_atual():
    return PROVEDOR_ATUAL


@lru_cache(maxsize=2)
def _catalogo_por_nome(nome):
    # O cache evita reinstanciar a fachada e o adaptador a cada pesquisa.
    # O nome, não o estado global, é a chave: alternar fontes continua seguro.
    return FABRICAS[nome]().criar_catalogo()


def buscar_faixas(nome_musica):
    # API pública usada pelo menu: esconde todas as escolhas de implementação.
    return _catalogo_por_nome(PROVEDOR_ATUAL).buscar_faixas(nome_musica)


def buscar_album(id_album):
    return _catalogo_por_nome(PROVEDOR_ATUAL).buscar_album(id_album)


def buscar_artista(id_artista):
    return _catalogo_por_nome(PROVEDOR_ATUAL).buscar_artista(id_artista)
