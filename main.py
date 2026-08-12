import random
# Importa do nosso arquivo de modelos lógicos
from modelos import Biblioteca, Playlist
# Importa do nosso arquivo de comunicação web
from api import buscar_faixa_deezer, buscar_album_deezer

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

        elif opcao == '0':
            print("\n👋 Saindo do sistema... Até logo!")
            break
            
        else:
            print("\n⚠️  Opção inválida! Escolha um número do menu.")