import random
# Importa do nosso arquivo de modelos lógicos
from modelos import Biblioteca, Playlist, Reproduzivel
# Importa do nosso arquivo de comunicação web
from api import buscar_faixa_deezer, buscar_album_deezer

def simular_player(midia):
    # Checa se o objeto tem a interface Reproduzivel
    if isinstance(midia, Reproduzivel):
        print(midia.play())
    else:
        print(f" Erro de Sistema: O item '{midia.titulo}' é um metadado descritivo e não pode ser tocado diretamente.")

def menu_principal():
    print("\n" + "═"*52)
    print("           🎧 CATÁLOGO MUSICAL & DEEZER 🎧")
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
    print("│  0. 🚪 Sair                                      │")
    print("└──────────────────────────────────────────────────┘")

if __name__ == "__main__":
    # INSTANCIAÇÃO: Cria a biblioteca central que vai gerenciar tudo
    bib = Biblioteca()
    
    # Listas para guardar as coisas em memória antes de mandar pra biblioteca final
    musicas_avaliadas = []
    albuns_buscados = []
    playlists_criadas = []
    ultimo_id_album = None

    while True:
        menu_principal()
        opcao = input("👉 Escolha uma opção: ").strip()
        
        if opcao == '1':
            print("\n🔍 --- BUSCA NA DEEZER ---")
            nome = input("Digite o nome da música: ").strip()
            
            if nome:
                musica_encontrada, id_album = buscar_faixa_deezer(nome)
                
                if musica_encontrada:
                    ultimo_id_album = id_album
                    print(f"\n✨ Encontrada: 🎵 {musica_encontrada.titulo} - 🎤 {musica_encontrada.artista} (⏱️ {musica_encontrada.duracao_segundos}s)")
                    
                    while True:
                        try:
                            # ENCAPSULAMENTO NA PRÁTICA: O setter da FaixaMusical fará a validação por baixo dos panos.
                            nota = float(input(f"⭐ Dê uma nota de 0 a 5 para '{musica_encontrada.titulo}': ").replace(',', '.'))
                            musica_encontrada.avaliacao = nota
                            musicas_avaliadas.append(musica_encontrada)
                            print("🌟 Nota salva com sucesso!")
                            break
                        except ValueError as e:
                            print(f"{e}")
                else:
                    # RF7: resultado vazio é uma condição normal e recuperável — a aplicação continua.
                    print(f"🔍 Nenhum resultado encontrado para '{nome}' — tente outra grafia.")

        elif opcao == '2':
            print("\n➕ --- ADICIONAR MÚSICA À BIBLIOTECA ---")
            if not musicas_avaliadas:
                print("⚠️  Busque e avalie uma música primeiro (Opção 1).")
            else:
                for i, m in enumerate(musicas_avaliadas):
                    print(f"  {i+1}. 🎵 {m.titulo} ({m.artista})")
                
                try:
                    escolha = int(input("\n✍️  Digite o número da música: ")) - 1
                    bib.adicionar_midia(musicas_avaliadas[escolha])
                except (ValueError, IndexError):
                    print("❌ Opção inválida.")

        elif opcao == '3':
            print("\n💿 --- BUSCAR ÁLBUM COMPLETO ---")
            if ultimo_id_album:
                print("🌐 Buscando o álbum completo na API da Deezer...")
                album = buscar_album_deezer(ultimo_id_album)
                if album:
                    albuns_buscados.append(album)
                    bib.adicionar_midia(album)
                else:
                    # RF7: resultado vazio é uma condição normal e recuperável — a aplicação continua.
                    print("🔍 Nenhum resultado encontrado para o álbum — tente buscar a música novamente.")
            else:
                print("⚠️  Busque uma música primeiro para encontrar o álbum correspondente.")

        elif opcao == '4':
            print("\n📋 --- CRIAR PLAYLIST ---")
            nome_pl = input("✍️  Digite o nome da sua nova Playlist: ").strip()
            if nome_pl:
                id_pl = random.randint(1000, 9999)
                # INSTANCIAÇÃO: Cria o objeto vazio
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
                        escolha_m = int(input("👉 Qual música? (Número): ")) - 1
                        # AGREGAÇÃO E POLIMORFISMO: A playlist aceita a FaixaMusical sem problemas.
                        pl_selecionada.adicionar_item(musicas_avaliadas[escolha_m])
                        print("✅ Música adicionada à playlist!")
                        
                elif tipo == '2':
                    if not albuns_buscados:
                        print("⚠️ Nenhum álbum buscado ainda.")
                    else:
                        for i, a in enumerate(albuns_buscados):
                            print(f"  {i+1}. {a.titulo}")
                        escolha_a = int(input("👉 Qual álbum? (Número): ")) - 1
                        # AGREGAÇÃO E POLIMORFISMO: A MESMA função aceita um Álbum, porque ambos são Midia.
                        pl_selecionada.adicionar_item(albuns_buscados[escolha_a])
                        print("✅ Álbum adicionado à playlist!")

                elif tipo == '3':
                    # RF6: Adicionando uma Playlist dentro de outra Playlist
                    outras = [p for p in playlists_criadas if p != pl_selecionada]
                    if not outras:
                        print("⚠️ Não há outras playlists disponíveis para incluir.")
                    else:
                        for i, p in enumerate(outras):
                            print(f"  {i+1}. {p.titulo}")
                        escolha_p = int(input("👉 Qual playlist quer incluir dentro desta? (Número): ")) - 1
                        pl_selecionada.adicionar_item(outras[escolha_p])
                        print("✅ Sub-playlist adicionada com sucesso! Duração e itens vinculados recursivamente.")
                else:
                    print("❌ Inválido.")
                    
            except (ValueError, IndexError):
                print("❌ Opção inválida.")

        elif opcao == '6':
            print("\n📥 --- ADICIONAR PLAYLIST À BIBLIOTECA ---")
            if not playlists_criadas:
                print("⚠️  Crie uma playlist primeiro.")
            else:
                for i, pl in enumerate(playlists_criadas):
                    print(f"  {i+1}. {pl.titulo}")
                try:
                    escolha_pl = int(input("👉 Qual playlist vai pra biblioteca? (Número): ")) - 1
                    bib.adicionar_midia(playlists_criadas[escolha_pl])
                except (ValueError, IndexError):
                    print("❌ Inválido.")

        elif opcao == '7':
            # POLIMORFISMO NA PRÁTICA: O método calcular_duracao resolve a vida de qualquer mídia que estiver na lista.
            bib.listar_biblioteca()

        elif opcao == '8':
            print("\n🎧 --- SIMULADOR DE PLAYER ---")
            if not bib._colecao:
                print("⚠️  A biblioteca está vazia. Adicione algo antes de tentar reproduzir (Opções 2 ou 6).")
                continue

            itens_biblioteca = list(bib._colecao.values())
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

        elif opcao == '0':
            print("\n👋 Saindo do sistema... Até logo!")
            break
            
        else:
            print("\n⚠️  Opção inválida! Escolha um número do menu.")