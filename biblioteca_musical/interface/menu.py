"""Interface de terminal: recebe comandos e COORDENA outros módulos.

Não faz requisição HTTP, não cria subclasses de provedor e não valida
internamente avaliações: essas responsabilidades ficam em outros módulos.
"""
from biblioteca_musical.dominio.midias import Album, Playlist, Reproduzivel, FaixaMusical
from biblioteca_musical.dominio.biblioteca import Biblioteca
from biblioteca_musical.dominio.ordenacao import (CRITERIOS_ORDENACAO,
    registrar_criterio_ordenacao, remover_criterio_ordenacao)
from biblioteca_musical.padroes.comportamentais.strategy import (
    FormatoDetalhado, FormatoResumido, FormatoCompacto)
from biblioteca_musical.padroes.criacionais.builder import PlaylistBuilder
from biblioteca_musical.integracoes.catalogo import (
    buscar_faixas, buscar_album, buscar_artista, nome_provedor_atual)

def simular_player(midia):
    """POO: exige interface Reproduzivel; não precisa conhecer cada subclasse."""
    if isinstance(midia, Reproduzivel): #verifica se o objeto é reproduzível
        print(midia.play())
    else: #tratamento de erro caso não seja reproduzível
        print(f" Erro de Sistema: O item '{midia.titulo}' não é uma mídia reproduzível e não pode ser tocado diretamente.")

def avaliar_e_guardar(musica, musicas_avaliadas): 
   
    """(RF1): Guarda faixas pesquisadas para adicionar a biblioteca
    Exige nota INTEIRA em [0;5] (decimais não são aceitos) e guarda.
    Permite selecionar uma faixa musical dentro diversos resultados
    """
    while True:
        entrada = input(f"⭐ Dê uma nota inteira de 0 a 5 para '{musica.titulo}': ").strip()

        try:
            nota = int(entrada) # apenas inteiros: "4,5", "4.5" e texto caem no except abaixo
        except ValueError:
            print("❌ Nota inválida! Digite um número inteiro de 0 a 5 (decimais como 4,5 não são aceitos).")
            continue

        try:
            """(encapsulamento): nota passa por validação interna (tipo inteiro e intervalo) antes de ser aceita"""
            musica.avaliacao = nota
        except ValueError as e: #nota inteira, mas fora do intervalo 0-5
            print(f"{e}")
            continue

        musicas_avaliadas.append(musica)
        print("🌟 Nota salva com sucesso!")
        break

# RECURSÃO: navega em sub-playlists para permitir remoção local de componentes.
# Diferente da remoção em cascata da Biblioteca, esta remove só do nó escolhido.
def remover_de_dentro_da_playlist(playlist):
    """
    RF9 (extensão): Remove um componente específico de dentro de uma playlist,
    descendo recursivamente em sub-playlists até encontrar o item certo —
    mesmo princípio de navegação da opção 5 (adicionar item na playlist).
    A remoção aqui é escopada a ESTA playlist (usa Playlist.remover_item,
    não a versão recursiva): o item continua existindo na biblioteca e em
    quaisquer outras playlists que também o contenham.
    """
    itens = playlist.obter_itens()
    if not itens:
        print(f"\n⚠️  A playlist '{playlist.titulo}' está vazia.")
        return

    print(f"\n📋 Itens dentro de '{playlist.titulo}':")
    for i, item in enumerate(itens):
        print(f"  {i + 1}. {item.exibir_info()}")

    try:
        escolha = int(input("👉 Digite o número do item que deseja remover (0 para voltar): ")) - 1
    except ValueError:
        print("❌ Entrada inválida! Digite apenas o número.")
        return

    if escolha == -1:
        return

    if not (0 <= escolha < len(itens)):
        print("❌ Número digitado não existe na lista de itens.")
        return

    item_selecionado = itens[escolha]

    if isinstance(item_selecionado, Playlist):
        # O item escolhido também é uma playlist: pergunta de novo, como pedido.
        print(f"\n📋 '{item_selecionado.titulo}' também é uma playlist. O que deseja fazer?")
        print("  1. Remover essa sub-playlist inteira (de dentro desta playlist)")
        print("  2. Entrar nela e remover um item específico")
        sub_opcao = input("👉 Escolha: ").strip()

        if sub_opcao == '1':
            playlist.remover_item(item_selecionado)
            print(f"\n🗑️  Sub-playlist '{item_selecionado.titulo}' removida de '{playlist.titulo}'.")
        elif sub_opcao == '2':
            remover_de_dentro_da_playlist(item_selecionado)  # RECURSÃO: desce mais um nível
        else:
            print("❌ Opção inválida.")
    else:
        # Faixa ou Álbum: remove de uma vez, como pedido.
        playlist.remover_item(item_selecionado)
        print(f"\n🗑️  '{item_selecionado.titulo}' removido da playlist '{playlist.titulo}'.")

def _converter_valor_padrao(texto):
    """
    Tenta converter o texto digitado pro tipo mais compatível (int, depois
    float); se não for número, mantém como string. Um valor padrão do TIPO
    CERTO evita que sorted() quebre comparando None com número/texto.
    Texto vazio vira None (o próprio try/except da ordenação cobre esse caso).
    """
    if texto == "":
        return None
    try:
        return int(texto)
    except ValueError:
        pass
    try:
        return float(texto.replace(",", "."))
    except ValueError:
        return texto


def _adicionar_criterio_interativo():
    """
    RF10 (extensão): monta um novo critério de ordenação a partir de dados
    estruturados fornecidos pelo usuário (nome, atributo/método, se precisa
    ser chamado, e um valor padrão) — nunca a partir de código digitado
    livremente, o que seria um risco de segurança (equivalente a um eval()).
    """
    print("\n➕ --- NOVO CRITÉRIO DE ORDENAÇÃO ---")
    nome = input("👉 Nome do novo critério (ex: 'artista'): ").strip().lower()
    if not nome:
        print("❌ O nome não pode ser vazio.")
        return
    if nome in CRITERIOS_ORDENACAO:
        print(f"🚫 Já existe um critério chamado '{nome}'. Escolha outro nome.")
        return

    atributo = input("👉 Nome do atributo/método já existente na mídia (ex: 'titulo', 'artista', 'calcular_duracao'): ").strip()
    if not atributo:
        print("❌ O atributo não pode ser vazio.")
        return

    eh_metodo = input("👉 Isso é um MÉTODO que precisa ser chamado, como calcular_duracao? (s/N): ").strip().lower() == 's'

    valor_padrao = _converter_valor_padrao(
        input("👉 Valor padrão para itens que não tiverem esse dado (ex: 0 — deixe em branco se não fizer sentido): ").strip()
    )

    def chave(midia, _attr=atributo, _metodo=eh_metodo, _padrao=valor_padrao):
        valor = getattr(midia, _attr, _padrao)
        if _metodo:
            valor = valor() if callable(valor) else _padrao
        return _padrao if valor is None else valor

    if registrar_criterio_ordenacao(nome, chave):
        print(f"✅ Critério '{nome}' adicionado com sucesso!")
    else:
        print(f"🚫 Não foi possível adicionar '{nome}' (nome já existe).")


def _remover_criterio_interativo():
    """RF10 (extensão): lista os critérios atuais numerados e remove só o escolhido."""
    criterios_atuais = list(CRITERIOS_ORDENACAO.keys())
    if not criterios_atuais:
        print("\n⚠️  Não há critérios para remover.")
        return

    print("\n🗑️  Qual critério deseja remover?")
    for i, nome_criterio in enumerate(criterios_atuais):
        print(f"  {i + 1}. {nome_criterio.capitalize()}")

    try:
        escolha = int(input("👉 Digite o número: ")) - 1
    except ValueError:
        print("❌ Entrada inválida! Digite apenas o número.")
        return

    if 0 <= escolha < len(criterios_atuais):
        nome = criterios_atuais[escolha]
        remover_criterio_ordenacao(nome)
        print(f"✅ Critério '{nome}' removido.")
    else:
        print("❌ Número digitado não existe na lista de critérios.")


def editar_criterios_ordenacao():
    """
    Tela de edição dos critérios (RF10 extensão): mostra os critérios atuais
    e a opção de adicionar/remover; depois de cada ação, volta para esta
    mesma tela (mostrando a lista já atualizada) — até o usuário escolher
    voltar ao menu principal.
    """
    while True:
        print("\n📐 --- CRITÉRIOS DE ORDENAÇÃO ATUAIS ---")
        criterios_atuais = list(CRITERIOS_ORDENACAO.keys())
        if criterios_atuais:
            for i, nome_criterio in enumerate(criterios_atuais):
                print(f"  {i + 1}. {nome_criterio.capitalize()}")
        else:
            print("  (nenhum critério registrado no momento)")

        print("\nO que deseja fazer?")
        print("  1. ➕ Adicionar critério")
        print("  2. ➖ Remover critério")
        print("  0. 🚪 Voltar ao menu principal")
        escolha = input("👉 Escolha: ").strip()

        if escolha == '1':
            _adicionar_criterio_interativo()
        elif escolha == '2':
            _remover_criterio_interativo()
        elif escolha == '0':
            return
        else:
            print("❌ Opção inválida.")



def escolher_formato():
    """STRATEGY: escolhe um algoritmo de apresentação em tempo de execução.

    Não há condicionais dentro de Biblioteca para cada estilo de exibição.
    """
    print("\n🖥️  Formato de exibição:")
    print("  1. Detalhado (árvore de álbuns e playlists)")
    print("  2. Resumido (uma linha por item)")
    print("  3. Compacto (tipo e título)")
    escolha = input("👉 Escolha [1]: ").strip() or '1'
    formatos = {
        '1': FormatoDetalhado,
        '2': FormatoResumido,
        '3': FormatoCompacto,
    }
    if escolha not in formatos:
        print("⚠️  Opção inválida; exibindo no formato detalhado.")
    return formatos.get(escolha, FormatoDetalhado)()


def criar_playlist_guiada(musicas_avaliadas, albuns_buscados, playlists_criadas):
    """BUILDER: o menu escolhe as peças; PlaylistBuilder monta o objeto.

    Opção 13: demonstra explicitamente o padrão sem confundir UI e construção.
    """
    print("\n🏗️  --- MONTAGEM GUIADA DE PLAYLIST (BUILDER) ---")
    titulo = input("✍️  Nome da nova playlist: ").strip()
    try:
        builder = PlaylistBuilder(titulo)
    except ValueError as erro:
        print(f"❌ {erro}")
        return

    while True:
        print("\nAdicione componentes à playlist ou finalize:")
        print("  1. Música avaliada")
        print("  2. Álbum buscado")
        print("  3. Playlist existente")
        print("  0. Finalizar playlist")
        opcao = input("👉 Escolha: ").strip()
        if opcao == '0':
            break
        grupos = {
            '1': musicas_avaliadas,
            '2': albuns_buscados,
            '3': playlists_criadas,
        }
        if opcao not in grupos:
            print("❌ Escolha inválida.")
            continue
        candidatos = grupos[opcao]
        if not candidatos:
            print("⚠️  Não há itens disponíveis nessa categoria.")
            continue
        for i, item in enumerate(candidatos, 1):
            print(f"  {i}. {item.titulo}")
        try:
            indice = int(input("👉 Número do componente: ")) - 1
        except ValueError:
            print("❌ Informe um número inteiro.")
            continue
        if not 0 <= indice < len(candidatos):
            print("❌ Componente inexistente.")
            continue
        builder.adicionar(candidatos[indice])
        print("✅ Componente incluído na montagem.")

    playlist = builder.construir()
    playlists_criadas.append(playlist)
    print(f"✅ Playlist '{playlist.titulo}' criada com {len(playlist.obter_itens())} item(ns).")


def exibir_recomendacoes(faixas, albuns, playlists):
    """Ordena sugestões da sessão pelas avaliações das faixas relacionadas."""
    notas_faixas = {}
    notas_albuns = {}
    faixas_por_id = {}
    for faixa in faixas:
        nota = faixa.avaliacao if faixa.avaliacao is not None else -1
        if nota > notas_faixas.get(faixa.id_deezer, -2):
            faixas_por_id[faixa.id_deezer] = faixa
            notas_faixas[faixa.id_deezer] = nota
        if faixa.id_album is not None:
            notas_albuns[faixa.id_album] = max(nota, notas_albuns.get(faixa.id_album, -1))

    def pontuacao(midia):
        if isinstance(midia, FaixaMusical):
            return notas_faixas.get(midia.id_deezer, -1)
        if isinstance(midia, Album):
            return notas_albuns.get(midia.id_deezer, -1)
        return max((pontuacao(item) for item in midia.obter_itens()), default=-1)

    def ordem(midia):
        return -pontuacao(midia), midia.titulo.casefold()

    feed = []
    for grupo in (faixas_por_id.values(), albuns, playlists):
        feed.extend(sorted(grupo, key=ordem)[:5])

    print("\n🎧 --- FEED DE RECOMENDAÇÕES ---")
    if not feed:
        print("Avalie faixas, busque álbuns ou crie playlists para receber sugestões.")
        return
    for midia in sorted(feed, key=ordem):
        print(f"  ▸ {midia.exibir_info()}")


def menu_principal():
    print("\n" + "═"*52)
    print(f"    🎧 CATÁLOGO MUSICAL & {nome_provedor_atual().upper()} 🎧")
    print("═"*52)
    print("┌──────────────────────────────────────────────────┐")
    print("│  1. 🔍 Buscar música e avaliar          (RF1)   │")
    print("│  2. ➕ Adicionar música à biblioteca    (RF2)   │")
    print("│  3. 💿 Buscar e guardar álbum da música (RF3)   │")
    print("│  4. 📋 Criar nova Playlist vazia                │")
    print("│  5. ✏️  Adicionar item na Playlist       (RF3)   │")
    print("│  6. 📥 Adicionar Playlist à biblioteca          │")
    print("│  7. 📚 Listar biblioteca e tempos       (RF3)   │")
    print("│  8. 📱 Testar Player                    (RF5)    │")
    print("│  9. 🗑️  Remover item da biblioteca      (RF9)    │")
    print("│ 10. 🔀 Listar biblioteca ordenada       (RF10)   │")
    print("│ 11. 🎤 Buscar e guardar Artista da música        │")
    print("│ 12. 📐 Editar critérios de ordenação             │")
    print("│ 13. 🏗️  Montar Playlist guiada (Builder)         │")
    print("│ 14. 🎧 Feed de recomendações            (RF4)    │")
    print("│  0. 🚪 Sair                                      │")
    print("└──────────────────────────────────────────────────┘")

def executar():
    """Inicializa o estado da sessão e executa as opções do menu.

    O `main.py` da raiz chama esta função. Os estados permanecem em memória,
    preservando a experiência anterior do usuário.
    """
    bib = Biblioteca() #criação da biblioteca (objeto que gerencia todos os outros)
    
    # Listas para guardar as coisas em memória antes de mandar pra biblioteca final
    musicas_avaliadas = []
    albuns_buscados = []
    playlists_criadas = []

    while True:
        menu_principal()
        opcao = input("👉 Escolha uma opção: ").strip()
        
        # INTEGRAÇÃO: a UI conhece buscar_faixas(), mas não Deezer nem iTunes.
        if opcao == '1':
            print("\n🔍 --- BUSCA DE MÚSICA ---")
            nome = input("Digite o nome da música: ").strip()
            
            if nome:
                # Agora retorna uma lista com (FaixaMusical, id_album)
                resultados = buscar_faixas(nome)

                if not resultados:
                    print(f"🔍 Nenhum resultado encontrado para '{nome}' — Verifique grafia e conexão à internet e tente novamente.")

                elif len(resultados) == 1:
                    musica_encontrada, id_album = resultados[0]
                    ultimo_id_album = id_album
                    print(f"\n✨ Encontrada: 🎵 {musica_encontrada.titulo} - 🎤 {musica_encontrada.artista} (⏱️ {musica_encontrada.duracao_segundos}s)")
                    avaliar_e_guardar(musica_encontrada, musicas_avaliadas)

                else:
                    print(f"\n🔎 {len(resultados)} resultados encontrados para '{nome}':")
                    # Desempacota o 'm' (música) e 'id_alb' (ID do álbum)
                    for i, (m, id_alb) in enumerate(resultados):
                        print(f"  {i + 1}. 🎵 {m.titulo} - 🎤 {m.artista} (⏱️ {m.duracao_segundos}s)")

                    try:
                        escolha = int(input("\n👉 Digite o número da música desejada: ")) - 1

                        if 0 <= escolha < len(resultados):
                            musica_encontrada, id_album = resultados[escolha]
                            ultimo_id_album = id_album # Guarda o ID do álbum escolhido para a opção 3
                            print(f"\n✨ Selecionada: 🎵 {musica_encontrada.titulo} - 🎤 {musica_encontrada.artista}")
                            avaliar_e_guardar(musica_encontrada, musicas_avaliadas)
                        else:
                            print("❌ Número digitado não existe na lista de resultados.")
                    except ValueError:
                        print("❌ Entrada inválida! Digite apenas o número.")

        elif opcao == '2':
            print("\n➕ --- ADICIONAR MÚSICA À BIBLIOTECA ---")
            if not musicas_avaliadas:
                print("⚠️  Busque e avalie uma música primeiro (Opção 1).")
            else:
                for i, m in enumerate(musicas_avaliadas):
                    print(f"  {i+1}. 🎵 {m.titulo} ({m.artista})")
                
                try:
                    escolha = int(input("\n✍️  Digite o número da música: ")) - 1
                    if 0 <= escolha < len(musicas_avaliadas):
                        bib.adicionar_midia(musicas_avaliadas[escolha])
                    else:
                        print("❌ Número digitado não existe na lista de músicas.")
                except ValueError:
                    print("❌ Entrada inválida! Digite apenas o número.")

        elif opcao == '3':
            print("\n💿 --- BUSCAR ÁLBUM COMPLETO ---")
            # RF3 (correção): lista as faixas que já estão na BIBLIOTECA (não mais
            # "a última pesquisada"), seguindo o mesmo padrão de índice das outras opções.
            faixas_na_biblioteca = [m for m in bib.obter_itens() if isinstance(m, FaixaMusical)]

            if not faixas_na_biblioteca:
                print("⚠️  Nenhuma música na biblioteca ainda. Adicione uma primeiro (Opção 2).")
            else:
                print("🎵 Músicas na biblioteca:")
                for i, m in enumerate(faixas_na_biblioteca):
                    print(f"  {i + 1}. {m.titulo} - {m.artista}")

                try:
                    escolha = int(input("\n👉 Digite o número da música cujo álbum você quer buscar: ")) - 1

                    if 0 <= escolha < len(faixas_na_biblioteca):
                        faixa_selecionada = faixas_na_biblioteca[escolha]

                        if faixa_selecionada.id_album is None:
                            print("⚠️  Essa música não tem um álbum de origem associado.")
                        else:
                            print(f"🌐 Buscando o álbum completo via {nome_provedor_atual()}...")
                            album = buscar_album(faixa_selecionada.id_album)
                            if album:
                                # Evita duplicar o mesmo álbum na lista de álbuns buscados
                                # (ex: buscar o álbum de 2 faixas diferentes do mesmo álbum).
                                ja_buscado = any(a.id_deezer == album.id_deezer for a in albuns_buscados)
                                if not ja_buscado:
                                    albuns_buscados.append(album)
                                bib.adicionar_midia(album)
                            else:
                                # RF7: resultado vazio é uma condição normal e recuperável — a aplicação continua.
                                print("🔍 Nenhum resultado encontrado para o álbum — tente buscar a música novamente.")
                    else:
                        print("❌ Número digitado não existe na lista de músicas.")
                except ValueError:
                    print("❌ Entrada inválida! Digite apenas o número.")

        elif opcao == '4':
            print("\n📋 --- CRIAR PLAYLIST ---")
            nome_pl = input("✍️  Digite o nome da sua nova Playlist: ").strip()
            if nome_pl:
                # BUILDER: o criador não precisa conhecer os detalhes da Playlist.
                playlist = PlaylistBuilder(nome_pl).construir()
                playlists_criadas.append(playlist)
                print(f"✅ Playlist '{nome_pl}' criada! Ela está vazia, use a Opção 5 para encher.")

        elif opcao == '5':
            print("\n✏️  --- EDITAR PLAYLIST ---")
            if not playlists_criadas:
                print("⚠️  Você precisa criar uma playlist primeiro (Opção 4).")
                continue
                
            print("📋 Suas Playlists:")
            for i, pl in enumerate(playlists_criadas):
                print(f"  {i+1}. {pl.titulo}")
                
            try:
                escolha_pl = int(input("👉 Qual playlist quer editar? (Número): ")) - 1
            except ValueError:
                print("❌ Entrada inválida! Digite apenas o número.")
                continue

            if not (0 <= escolha_pl < len(playlists_criadas)):
                print("❌ Número digitado não existe na lista de playlists.")
                continue

            pl_selecionada = playlists_criadas[escolha_pl]

            print("\nO que você quer adicionar nela?")
            print("1. 🎵 Música avaliada")
            print("2. 💿 Álbum buscado")
            print("3. 📋 Outra Playlist ")
            tipo = input("👉 Escolha: ").strip()

            if tipo == '1':
                if not musicas_avaliadas:
                    print("⚠️ Nenhuma música avaliada ainda.")
                else:
                    for i, m in enumerate(musicas_avaliadas):
                        print(f"  {i+1}. {m.titulo}")
                    try:
                        escolha_m = int(input("👉 Qual música? (Número): ")) - 1
                        if 0 <= escolha_m < len(musicas_avaliadas):
                            # AGREGAÇÃO E POLIMORFISMO: A playlist aceita a FaixaMusical sem problemas.
                            if pl_selecionada.adicionar_item(musicas_avaliadas[escolha_m]):
                                print("✅ Música adicionada à playlist!")
                        else:
                            print("❌ Número digitado não existe na lista de músicas.")
                    except ValueError:
                        print("❌ Entrada inválida! Digite apenas o número.")

            elif tipo == '2':
                if not albuns_buscados:
                    print("⚠️ Nenhum álbum buscado ainda.")
                else:
                    for i, a in enumerate(albuns_buscados):
                        print(f"  {i+1}. {a.titulo}")
                    try:
                        escolha_a = int(input("👉 Qual álbum? (Número): ")) - 1
                        if 0 <= escolha_a < len(albuns_buscados):
                            # AGREGAÇÃO E POLIMORFISMO: A MESMA função aceita um Álbum, porque ambos são Midia.
                            if pl_selecionada.adicionar_item(albuns_buscados[escolha_a]):
                                print("✅ Álbum adicionado à playlist!")
                        else:
                            print("❌ Número digitado não existe na lista de álbuns.")
                    except ValueError:
                        print("❌ Entrada inválida! Digite apenas o número.")

            elif tipo == '3':
                # RF6: Adicionando uma Playlist dentro de outra Playlist
                outras = [p for p in playlists_criadas if p != pl_selecionada]
                if not outras:
                    print("⚠️ Não há outras playlists disponíveis para incluir.")
                else:
                    for i, p in enumerate(outras):
                        print(f"  {i+1}. {p.titulo}")
                    try:
                        escolha_p = int(input("👉 Qual playlist quer incluir dentro desta? (Número): ")) - 1
                        if 0 <= escolha_p < len(outras):
                            if pl_selecionada.adicionar_item(outras[escolha_p]):
                                print("✅ Sub-playlist adicionada com sucesso! Duração e itens vinculados recursivamente.")
                        else:
                            print("❌ Número digitado não existe na lista de playlists.")
                    except ValueError:
                        print("❌ Entrada inválida! Digite apenas o número.")
            else:
                print("❌ Inválido.")

        elif opcao == '6':
            print("\n📥 --- ADICIONAR PLAYLIST À BIBLIOTECA ---")
            if not playlists_criadas:
                print("⚠️  Crie uma playlist primeiro.")
            else:
                for i, pl in enumerate(playlists_criadas):
                    print(f"  {i+1}. {pl.titulo}")
                try:
                    escolha_pl = int(input("👉 Qual playlist vai pra biblioteca? (Número): ")) - 1
                    if 0 <= escolha_pl < len(playlists_criadas):
                        bib.adicionar_midia(playlists_criadas[escolha_pl])
                    else:
                        print("❌ Número digitado não existe na lista de playlists.")
                except ValueError:
                    print("❌ Entrada inválida! Digite apenas o número.")

        # STRATEGY: escolha de formatação na opção 7.
        elif opcao == '7':
            # POLIMORFISMO NA PRÁTICA: O método calcular_duracao resolve a vida de qualquer mídia que estiver na lista.
            if bib.esta_vazia():
                bib.listar_biblioteca()
            else:
                bib.listar_biblioteca(formato=escolher_formato())

        elif opcao == '8':
            print("\n🎧 --- SIMULADOR DE PLAYER ---")
            if bib.esta_vazia():
                print("⚠️  A biblioteca está vazia. Adicione algo antes de tentar reproduzir (Opções 2 ou 6).")
                continue

            itens_biblioteca = bib.obter_itens()
            print("📚 Itens na biblioteca:")
            for i, item in enumerate(itens_biblioteca):
                print(f"  {i + 1}. {item.exibir_info()}")

            try:
                escolha = int(input("👉 Digite o número do item que deseja reproduzir: ")) - 1

                if 0 <= escolha < len(itens_biblioteca):
                    item_selecionado = itens_biblioteca[escolha]
                    print(f"\n▶️ Solicitando reprodução ao Player...")
                    simular_player(item_selecionado)
                else:
                    print("❌ Número digitado não existe na lista de resultados.")
            except ValueError:
                print("❌ Entrada inválida! Digite apenas o número.")

        # CONSISTÊNCIA/REMOÇÃO: operação de biblioteca usa cascata em sub-playlists.
        elif opcao == '9':
            print("\n🗑️  --- REMOVER ITEM DA BIBLIOTECA (RF9) ---")
            if bib.esta_vazia():
                print("⚠️  A biblioteca está vazia.")
                continue

            itens_biblioteca = bib.obter_itens()
            print("📚 Itens na biblioteca:")
            for i, item in enumerate(itens_biblioteca):
                print(f"  {i + 1}. {item.exibir_info()}")

            try:
                escolha = int(input("👉 Digite o número do item que deseja remover: ")) - 1

                if 0 <= escolha < len(itens_biblioteca):
                    item_selecionado = itens_biblioteca[escolha]

                    if isinstance(item_selecionado, Playlist):
                        print(f"\n📋 Você selecionou a playlist '{item_selecionado.titulo}'. O que deseja fazer?")
                        print("  1. Remover a playlist inteira da biblioteca")
                        print("  2. Remover um item específico de dentro dela")
                        sub_opcao = input("👉 Escolha: ").strip()

                        if sub_opcao == '1':
                            # RF9: remoção consistente — a Biblioteca trata sozinha as
                            # referências existentes em playlists (inclusive aninhadas).
                            bib.remover_midia(item_selecionado.id_deezer, playlists_criadas)
                        elif sub_opcao == '2':
                            # RF9 (extensão): remoção aninhada de um componente específico.
                            remover_de_dentro_da_playlist(item_selecionado)
                        else:
                            print("❌ Opção inválida.")
                    else:
                        # Faixa ou Álbum selecionados diretamente da biblioteca: remove de uma vez.
                        bib.remover_midia(item_selecionado.id_deezer, playlists_criadas)
                else:
                    print("❌ Número digitado não existe na lista de resultados.")
            except ValueError:
                print("❌ Entrada inválida! Digite apenas o número.")


        elif opcao == '10':
            print("\n🔀 --- LISTAR BIBLIOTECA ORDENADA (RF10) ---")
            if bib.esta_vazia():
                print("⚠️  A biblioteca está vazia.")
                continue

            criterios_disponiveis = list(CRITERIOS_ORDENACAO.keys())
            print("📐 Critérios de ordenação disponíveis:")
            for i, nome_criterio in enumerate(criterios_disponiveis):
                print(f"  {i + 1}. {nome_criterio.capitalize()}")

            try:
                escolha = int(input("\n👉 Digite o número do critério: ")) - 1

                if 0 <= escolha < len(criterios_disponiveis):
                    criterio_selecionado = criterios_disponiveis[escolha]
                    ordem = input("👉 Ordem decrescente? (s/N): ").strip().lower()
                    bib.listar_biblioteca_ordenada(criterio_selecionado, decrescente=(ordem == 's'), formato=escolher_formato())
                else:
                    print("❌ Número digitado não existe na lista de critérios.")
            except ValueError:
                print("❌ Entrada inválida! Digite apenas o número.")

        elif opcao == '11':
            print("\n🎤 --- BUSCAR E GUARDAR ARTISTA DA MÚSICA ---")
            # Mesmo padrão da opção 3: lista as faixas da BIBLIOTECA por índice,
            # e usa o id_artista guardado na faixa para buscar o artista completo.
            faixas_na_biblioteca = [m for m in bib.obter_itens() if isinstance(m, FaixaMusical)]

            if not faixas_na_biblioteca:
                print("⚠️  Nenhuma música na biblioteca ainda. Adicione uma primeiro (Opção 2).")
            else:
                print("🎵 Músicas na biblioteca:")
                for i, m in enumerate(faixas_na_biblioteca):
                    print(f"  {i + 1}. {m.titulo} - {m.artista}")

                try:
                    escolha = int(input("\n👉 Digite o número da música cujo artista você quer buscar: ")) - 1

                    if 0 <= escolha < len(faixas_na_biblioteca):
                        faixa_selecionada = faixas_na_biblioteca[escolha]

                        if faixa_selecionada.id_artista is None:
                            print("⚠️  Essa música não tem um artista de origem associado.")
                        else:
                            print(f"🌐 Buscando os dados do artista via {nome_provedor_atual()}...")
                            artista = buscar_artista(faixa_selecionada.id_artista)
                            if artista:
                                # Um Artista entra na biblioteca (RF2 vale igual: sem duplicatas),
                                # e fica fora das playlists (ver Playlist.adicionar_item).
                                bib.adicionar_midia(artista)
                            else:
                                # RF7: resultado vazio é uma condição normal e recuperável — a aplicação continua.
                                print("🔍 Nenhum resultado encontrado para o artista — tente buscar a música novamente.")
                    else:
                        print("❌ Número digitado não existe na lista de músicas.")
                except ValueError:
                    print("❌ Entrada inválida! Digite apenas o número.")

        elif opcao == '12':
            editar_criterios_ordenacao()

        # BUILDER: construção guiada em etapas (opção 13).
        elif opcao == '13':
            criar_playlist_guiada(musicas_avaliadas, albuns_buscados, playlists_criadas)

        elif opcao == '14':
            exibir_recomendacoes(musicas_avaliadas, albuns_buscados, playlists_criadas)

        elif opcao == '0':
            print("\n👋 Saindo do sistema... Até logo!")
            break
            
        else:
            print("\n⚠️  Opção inválida! Escolha um número do menu.")
