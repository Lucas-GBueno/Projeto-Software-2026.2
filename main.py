import random #import para criação de IDs

from modelos import Biblioteca, Playlist, Reproduzivel, FaixaMusical, CRITERIOS_ORDENACAO, registrar_criterio_ordenacao, remover_criterio_ordenacao #import classes e estruturas do sistema

from api import buscar_faixas, buscar_album, buscar_artista, nome_provedor_atual

def simular_player(midia): #simula palyer para objetos reproduzíveis
    if isinstance(midia, Reproduzivel): #verifica se o objeto é reproduzível
        print(midia.play())
    else: #tratamento de erro caso não seja reproduzível
        print(f" Erro de Sistema: O item '{midia.titulo}' não é uma mídia reproduzível e não pode ser tocado diretamente.")

def avaliar_e_guardar(musica, musicas_avaliadas): 
    while True:
        entrada = input(f"⭐ Dê uma nota inteira de 0 a 5 para '{musica.titulo}': ").strip()
        try:
            nota = int(entrada)
        except ValueError:
            print("❌ Nota inválida! Digite um número inteiro de 0 a 5 (decimais como 4,5 não são aceitos).")
            continue
        try:
            musica.avaliacao = nota
        except ValueError as e:
            print(f"{e}")
            continue
        musicas_avaliadas.append(musica)
        print("🌟 Nota salva com sucesso!")
        break

def remover_de_dentro_da_playlist(playlist):
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
        print(f"\n📋 '{item_selecionado.titulo}' também é uma playlist. O que deseja fazer?")
        print("  1. Remover essa sub-playlist inteira (de dentro desta playlist)")
        print("  2. Entrar nela e remover um item específico")
        sub_opcao = input("👉 Escolha: ").strip()
        if sub_opcao == '1':
            playlist.remover_item(item_selecionado)
            print(f"\n🗑️  Sub-playlist '{item_selecionado.titulo}' removida de '{playlist.titulo}'.")
        elif sub_opcao == '2':
            remover_de_dentro_da_playlist(item_selecionado)
        else:
            print("❌ Opção inválida.")
    else:
        playlist.remover_item(item_selecionado)
        print(f"\n🗑️  '{item_selecionado.titulo}' removido da playlist '{playlist.titulo}'.")

def _converter_valor_padrao(texto):
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

def menu_principal():
    print("\n" + "═"*52)
    print(f"           🎧 CATÁLOGO MUSICAL & {nome_provedor_atual().upper()} 🎧")
    print("═"*52)
    print("┌──────────────────────────────────────────────────┐")
    print("│  1. 🔍 Buscar música e avaliar          (RF1)   │")
    print("│  2. ➕ Adicionar música à biblioteca    (RF2)   │")
    print("│  3. 💿 Buscar e guardar álbum da música (RF3)   │")
    print("│  4. 📋 Criar nova Playlist vazia                │")
    print("│  5. ✏️  Adicionar item na Playlist       (RF3)   │")
    print("│  6. 📥 Adicionar Playlist à biblioteca          │")
    print("│  7. 📚 Listar biblioteca e tempos       (RF3)   │")
    print("│  8. 📱 Testar Player                    (RF4)    │")
    print("│  9. 🗑️  Remover item da biblioteca      (RF9)    │")
    print("│ 10. 🔀 Listar biblioteca ordenada       (RF10)   │")
    print("│ 11. 🎤 Buscar e guardar Artista da música        │")
    print("│ 12. 📐 Editar critérios de ordenação             │")
    print("│  0. 🚪 Sair                                      │")
    print("└──────────────────────────────────────────────────┘")

if __name__ == "__main__":
    bib = Biblioteca()
    musicas_avaliadas = []
    albuns_buscados = []
    playlists_criadas = []

    while True:
        menu_principal()
        opcao = input("👉 Escolha uma opção: ").strip()
        
        if opcao == '1':
            print("\n🔍 --- BUSCA DE MÚSICA ---")
            nome = input("Digite o nome da música: ").strip()
            if nome:
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
                    for i, (m, id_alb) in enumerate(resultados):
                        print(f"  {i + 1}. 🎵 {m.titulo} - 🎤 {m.artista} (⏱️ {m.duracao_segundos}s)")
                    try:
                        escolha = int(input("\n👉 Digite o número da música desejada: ")) - 1
                        if 0 <= escolha < len(resultados):
                            musica_encontrada, id_album = resultados[escolha]
                            ultimo_id_album = id_album
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
                            print(f"🌐 Buscando o álbum completo na API {nome_provedor_atual()}...")
                            album = buscar_album(faixa_selecionada.id_album)
                            if album:
                                ja_buscado = any(a.id_externo == album.id_externo for a in albuns_buscados)
                                if not ja_buscado:
                                    albuns_buscados.append(album)
                                bib.adicionar_midia(album)
                            else:
                                print("🔍 Nenhum resultado encontrado para o álbum — tente buscar a música novamente.")
                    else:
                        print("❌ Número digitado não existe na lista de músicas.")
                except ValueError:
                    print("❌ Entrada inválida! Digite apenas o número.")

        elif opcao == '4':
            print("\n📋 --- CRIAR PLAYLIST ---")
            nome_pl = input("✍️  Digite o nome da sua nova Playlist: ").strip()
            if nome_pl:
                id_pl = random.randint(1000, 9999)
                playlist = Playlist(id_pl, nome_pl)
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
                            pl_selecionada.adicionar_item(musicas_avaliadas[escolha_m])
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
                            pl_selecionada.adicionar_item(albuns_buscados[escolha_a])
                            print("✅ Álbum adicionado à playlist!")
                        else:
                            print("❌ Número digitado não existe na lista de álbuns.")
                    except ValueError:
                        print("❌ Entrada inválida! Digite apenas o número.")
            elif tipo == '3':
                outras = [p for p in playlists_criadas if p != pl_selecionada]
                if not outras:
                    print("⚠️ Não há outras playlists disponíveis para incluir.")
                else:
                    for i, p in enumerate(outras):
                        print(f"  {i+1}. {p.titulo}")
                    try:
                        escolha_p = int(input("👉 Qual playlist quer incluir dentro desta? (Número): ")) - 1
                        if 0 <= escolha_p < len(outras):
                            pl_selecionada.adicionar_item(outras[escolha_p])
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

        elif opcao == '7':
            bib.listar_biblioteca()

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
                            bib.remover_midia(item_selecionado.id_externo, playlists_criadas)
                        elif sub_opcao == '2':
                            remover_de_dentro_da_playlist(item_selecionado)
                        else:
                            print("❌ Opção inválida.")
                    else:
                        bib.remover_midia(item_selecionado.id_externo, playlists_criadas)
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
                    bib.listar_biblioteca_ordenada(criterio_selecionado, decrescente=(ordem == 's'))
                else:
                    print("❌ Número digitado não existe na lista de critérios.")
            except ValueError:
                print("❌ Entrada inválida! Digite apenas o número.")

        elif opcao == '11':
            print("\n🎤 --- BUSCAR E GUARDAR ARTISTA DA MÚSICA ---")
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
                            print(f"🌐 Buscando os dados do artista na API {nome_provedor_atual()}...")
                            artista = buscar_artista(faixa_selecionada.id_artista)
                            if artista:
                                bib.adicionar_midia(artista)
                            else:
                                print("🔍 Nenhum resultado encontrado para o artista — tente buscar a música novamente.")
                    else:
                        print("❌ Número digitado não existe na lista de músicas.")
                except ValueError:
                    print("❌ Entrada inválida! Digite apenas o número.")

        elif opcao == '12':
            editar_criterios_ordenacao()

        elif opcao == '0':
            print("\n👋 Saindo do sistema... Até logo!")
            break
        else:
            print("\n⚠️  Opção inválida! Escolha um número do menu.")