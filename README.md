# Projeto-Software-2026.2
### Visão Geral
Catálogo musical em Python (operado por menu de terminal) e conectado à **API Pública da Deezer**, que permite o usuário:
* Pesquisar (com desambiguação entre múltiplos resultados), avaliar e salvar músicas (faixas musicais) na biblioteca
* Adicionar álbuns a partir de faixas já salvas na biblioteca
* Adicionar artistas a partir de faixas já salvas na biblioteca, com a duração total de sua discografia
* Criar, salvar na biblioteca e adicionar itens à playlists (inclusive playlists dentro de playlists)
* Listar itens da biblioteca e seus respectivos tempos, com detalhamento recursivo de álbuns, playlists e artistas
* Remover itens da biblioteca, inclusive de forma aninhada (um componente específico dentro de uma playlist)
* Ordenação da biblioteca (título, duração e avaliação), com critérios extensíveis
* Simulação de player, que diferencia o que é reproduzível do que é apenas um metadado descritivo (por usar API gratuita, não permite reprodução real)

### Estrutura do Projeto
* **`modelos.py`**: Contém as classes do domínio musical.
* **`api.py`**: Gerencia a comunicação com a API da Deezer.
* **`main.py`**: Roda o menu interativo no terminal.

### Modelo de domínio e Classes aplicadas
* **`Midia`** (classe abstrata): Classe que define todas as classes que podem ser catalogadas. Atribui **id_deezer**, **titulo**, **calcular_duracao()** e **exibir_info()**. Também define **exibir_detalhado()**, com comportamento padrão de item "folha" (mostra só a si mesma), sobrescrito por quem tem componentes internos.
* **`Reproduzivel`** (interface abstrata): Define o contrato de **play()**. É separado de **`Midia`** pois ser uma mídia catalogável e poder ser reproduzida/ tocada são conceitos diferentes dentro do contexto do sistema. Permite consultar durante a execução se um item pode ser reproduzido (simulador de player) e também decide, estruturalmente, o que pode ou não ser adicionado a uma playlist.
* **`FaixaMusical`**(Midia, Reproduzivel): Presenta música/ faixa musical. Guarda **artista**, **duracao_segundos**, **id_album** e **id_artista** (para localizar depois o álbum e o artista de origem). A Avaliação é um atributo encapsulado que valida a nota antes de aceitá-la e salvar com a música.
* **`Album`**(Midia, Reproduzivel): Representa álbum (lista privada de faixas, inalterável, e **generos**). Sua duração total é calculada pela soma da duração de cada faixa musical que a compõe. Sabe exibir a si mesmo e, detalhadamente, cada uma de suas faixas.
* **`Playlist`**(Midia, Reproduzivel): Representa playlist (lista privada de itens). Só aceita itens que também sejam **Reproduzivel** (barra a adição de um `Artista`, que impediria a reprodução da playlist). Exibe a si mesma e, detalhadamente, cada um de seus itens (inclusive sub-playlists aninhadas), e sabe remover um item específico de si mesma ou recursivamente de suas sub-playlists.
* **`Artista`**(Midia): Representa um artista. Guarda sua discografia (lista de `Album`). **Não** implementa `Reproduzivel` (contraste com classes reproduzíveis). Na listagem da biblioteca, expande a discografia para exibir álbuns relacionados e suas informações padrões.
(O método **calcular_duracao()**, aplicado em Album, Playlist e Artista, executa comportamentos diferentes.)
* **`Biblioteca`**: Dicionário privado que usa o ID de cada item como chave, funciona como coleção central do sistema. Concentra as regras de negócio (adicionar, remover — inclusive tratando referências em playlists — listar de forma simples ou detalhada, e listar de forma ordenada por múltiplos critérios).

### Observações Gerais:
* Antes de adicionar uma faixa musical à biblioteca (opção 2) é necessário pesquisar e salvá-la (opção 1). Se a busca retornar mais de um resultado, o sistema lista as opções numeradas para escolha antes da avaliação.
* Antes de qualquer operação envolvendo faixas musicais (3, 5, 7, 8, 9, 10, 11) é preciso certificar-se que a faixa foi devidamente adicionada à biblioteca (Opção 2 para adicionar, Opção 7 para listagem da biblioteca).
* Manipulação de playlist envolve as etapas: Criar Playlist Vazia (4), Adicionar Item na Playlist (5) e Adicionar Playlist na Biblioteca (6). Cada item a se adicionar deve estar devidamente cadastrado na biblioteca previamente. Um `Artista` nunca aparece como opção de item a adicionar aqui, já que não é reproduzível.
* Buscar e Guardar Álbum da Biblioteca (opção 3) e Buscar e Guardar Artista da Música (opção 11) selecionam, cada um, dentre as faixas musicais já presentes na biblioteca (não a última pesquisada) — o vínculo com o álbum/artista de origem é guardado na própria faixa desde a busca inicial.
* O processo de aninhamento de uma playlist dentro de outra segue as etapas: Criação e adição à biblioteca de uma primeira playlist (opção 4 e 6), criação de uma segunda playlist (opção 4) que é adicionada como conteúdo da primeira (opção 5) sem publicação na biblioteca.
* A Listagem da Biblioteca (opção 7) é recursiva para `Album` e `Playlist`: um álbum mostra suas faixas, e uma playlist mostra todos os seus componentes (inclusive sub-playlists e álbuns aninhados). Um `Artista`, por outro lado, mostra apenas a duração total de sua discografia — sem expandir os álbuns e faixas individuais.
* A Remoção de Item da Biblioteca (opção 9) também é aninhada: ao selecionar uma playlist, é possível escolher entre remover ela inteira ou entrar nela para remover um componente específico, descendo recursivamente por sub-playlists até encontrar o item certo.

### Conceitos de POO Aplicados
* **Abstração e Herança (RF3)**: A classe abstrata `Midia` serve de "molde" para `FaixaMusical`, `Album`, `Playlist` e `Artista`.
* **Interface e Abstração de comportamento (RF4)**: A classe abstrata `Reproduzivel` define o contrato `play()`, separado da hierarquia de `Midia`. Permite checar em tempo de execução (`isinstance(midia, Reproduzivel)`) se um item pode ser tocado, sem confundir mídia catalogável com mídia reproduzível — `Artista` é a prova prática disso, sendo uma `Midia` que o sistema sabe reconhecer como não reproduzível.
* **Encapsulamento (RF1 e RF2)**: As notas das músicas e a coleção da biblioteca são atributos privados (`_avaliacao`, `_colecao`). O acesso e a alteração são controlados (barrando notas inválidas e duplicatas, por exemplo).
* **Resultado vazio como condição recuperável (RF7)**: Uma busca sem resultados, ou qualquer falha de rede, nunca gera um erro bruto nem trava o programa — é tratada como uma condição normal e esperada, com uma mensagem amigável e o menu continuando normalmente.
* **Polimorfismo (RF3)**: O cálculo de duração e a exibição de informações (simples e detalhada) funcionam para qualquer item da biblioteca, já que cada classe filha sobrescreve os métodos `calcular_duracao()`, `exibir_info()` e `exibir_detalhado()` com suas próprias lógicas. O mesmo vale para `play()`, que se comporta de forma diferente em cada classe reproduzível.
* **Composição e padrão Composite**: Álbuns contêm faixas (`_faixas`) que são criadas e pertencem exclusivamente a eles (as faixas de um álbum não existem fora dele). A listagem detalhada e recursiva (opção 7) segue exatamente esse padrão para `Album` e `Playlist`: cada um sabe exibir a si mesmo e delega a exibição de cada componente interno. `Artista` é uma exceção deliberada: mesmo tendo uma discografia (`_discografia`), ele usa o comportamento padrão "folha" herdado de `Midia` — mostra só a duração total já somada, sem expandir álbuns e faixas.
* **Restrição estrutural por interface**: `Playlist.adicionar_item()` só aceita itens que implementem `Reproduzivel`, recusando qualquer mídia não reproduzível (como `Artista`) sem precisar checar o tipo explicitamente — a regra vem da interface, não de um `if` especial.
* **Ocultação de implementação e Baixo acoplamento (RF8)**: `main.py` e `modelos.py` não acessam a API Deezer diretamente, são usadas apenas as funções genéricas/ públicas `buscar_faixas()`, `buscar_album()` e `buscar_artista()` em `api.py`. Uma possível troca da fonte de dados no futuro exigiria mudar apenas esse arquivo.
* **Encapsulamento de regras de remoção (RF9)**: A `Biblioteca` e a `Playlist` são responsáveis por gerenciar sozinhas a consistência de suas próprias referências ao remover um item (removendo-o também de playlists que o contêm, inclusive sub-playlists aninhadas), em vez de expor essa lógica para fora das classes. Isso vale tanto para a remoção completa de um item da biblioteca quanto para a remoção aninhada de um componente específico de dentro de uma playlist.
* **Extensibilidade via composição de comportamento (RF10)**: A ordenação por múltiplos critérios é implementada como um dicionário de funções (`CRITERIOS_ORDENACAO`), assim adiciona novos critérios sem alterar o método de ordenação já existente na `Biblioteca`.
