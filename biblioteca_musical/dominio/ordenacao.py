"""Registro extensível de critérios de ordenação da biblioteca.

A biblioteca consulta este dicionário em vez de codificar um if/else por critério.
"""

# ORDENAÇÃO EXTENSÍVEL (RF10): registrador de critérios de ordenação. Novos critérios são
# adicionados aqui (ou via registrar_criterio_ordenacao) sem que o método
# de ordenação da Biblioteca precise ser alterado.
CRITERIOS_ORDENACAO = {
    'titulo': lambda midia: midia.titulo.lower(),
    'duracao': lambda midia: midia.calcular_duracao(),
    'avaliacao': lambda midia: getattr(midia, 'avaliacao', None) if getattr(midia, 'avaliacao', None) is not None else -1,
}


def registrar_criterio_ordenacao(nome, funcao_chave):
    """
    RF10: Adiciona um novo critério de ordenação sem tocar no código de
    ordenação existente (nem nos critérios já registrados).

    Se já existir um critério com esse nome, NÃO sobrescreve (retorna False):
    assim, registrar um critério novo nunca altera um que já estava inserido.
    Retorna True quando o critério foi adicionado.

    Exemplo de uso, se o professor pedir ordenação por ano:
        registrar_criterio_ordenacao('ano', lambda midia: midia.ano)
    """
    if not callable(funcao_chave):
        raise TypeError("A função-chave do critério precisa ser chamável (ex: lambda midia: midia.ano).")
    if nome in CRITERIOS_ORDENACAO:
        return False
    CRITERIOS_ORDENACAO[nome] = funcao_chave
    return True


def remover_criterio_ordenacao(nome):
    """
    RF10: Retira UM critério de ordenação pelo nome. Só a entrada indicada é
    removida do registro; todos os outros critérios continuam intactos e
    disponíveis. Retorna True se removeu, ou False se não existia um
    critério com esse nome.
    """
    return CRITERIOS_ORDENACAO.pop(nome, None) is not None
