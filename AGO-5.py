import requests
import random
from abc import ABC, abstractmethod

#RF3: Abstração e Herança [A/H]

class Midia(ABC):
    def __init__(self, id_deezer, titulo):
        self.id_deezer = id_deezer
        self.titulo = titulo

    @abstractmethod
    def calcular_duracao(self):
        pass

    @abstractmethod
    def exibir_info(self):
        pass

class FaixaMusical(Midia):
    def __init__(self, id_deezer, titulo, artista, duracao_segundos, avaliacao=None):
        super().__init__(id_deezer, titulo)
        self.artista = artista
        self.duracao_segundos = duracao_segundos
        self._avaliacao = None
        
        if avaliacao is not None:
            self.avaliacao = avaliacao

    #RF1: Avaliações validadas (Encapsulamento) [E]
    @property #getter
    def avaliacao(self):
        return self._avaliacao

    @avaliacao.setter
    def avaliacao(self, valor):
        if not (0 <= valor <= 5):
            raise ValueError(f"Erro: A nota {valor} é impossível. Avalie entre 0 e 5.")
        self._avaliacao = valor

    def calcular_duracao(self):
        return self.duracao_segundos

    def exibir_info(self):
        nota = f"{self.avaliacao}/5" if self.avaliacao else "Sem nota"
        return f"Faixa: {self.titulo} - {self.artista} ({self.calcular_duracao()}s) | Nota: {nota}"

class Album(Midia):
    def __init__(self, id_deezer, titulo):
        super().__init__(id_deezer, titulo)
        self._faixas = []

    def adicionar_faixa(self, faixa):
        self._faixas.append(faixa)

    def calcular_duracao(self):
        duracao = 0
        for faixa in self._faixas:
            duracao += faixa.calcular_duracao()
        return duracao

    def exibir_info(self):
        return f"Álbum: {self.titulo} ({len(self._faixas)} faixas) - Duração: {self.calcular_duracao()}s"

class Playlist(Midia):
    def __init__(self, id_deezer, titulo):
        super().__init__(id_deezer, titulo)
        self._itens = []

    def adicionar_item(self, item):
        self._itens.append(item)

    def calcular_duracao(self):
        duracao = 0
        for item in self._itens:
            duracao += item.calcular_duracao()
        return duracao

    def exibir_info(self):
        return f"Playlist: {self.titulo} ({len(self._itens)} itens) - Duração: {self.calcular_duracao()}s"

#RF2: Biblioteca Controlada (Encapsulamento) [E]

class Biblioteca:
    def __init__(self):
        self._colecao = {}

    def adicionar_midia(self, midia):
        if midia.id_deezer in self._colecao:
            print(f"\n[BLOQUEADO] '{midia.titulo}' já está na biblioteca (Duplicata recusada).")
            return False
        
        self._colecao[midia.id_deezer] = midia
        print(f"\n[SUCESSO] '{midia.titulo}' adicionado à biblioteca.")
        return True

    def listar_biblioteca(self):
        if not self._colecao:
            print("\nSua biblioteca está vazia.")
            return

        print("\n=== SUA BIBLIOTECA ===")
        duracao_total = 0
        for midia in self._colecao.values():
            print(f" - {midia.exibir_info()}")
            duracao_total += midia.calcular_duracao() 
        print(f"\nDuração total da biblioteca: {duracao_total} segundos")

#Integração com a API

def buscar_faixa_deezer(nome_musica):
    url = f"https://api.deezer.com/search?q={nome_musica}"
    try:
        dados = requests.get(url).json()
        if dados.get('data'):
            f = dados['data'][0]
            faixa = FaixaMusical(f['id'], f['title'], f['artist']['name'], f['duration'])
            return faixa, f['album']['id'] # Retorna a faixa e o ID do álbum para usarmos depois
    except Exception:
        pass
    
    print("Música não encontrada.")
    return None, None

def buscar_album_deezer(id_album):
    url = f"https://api.deezer.com/album/{id_album}"
    try:
        dados = requests.get(url).json()
        album = Album(dados['id'], dados['title'])
        
        # Puxa todas as faixas do álbum para somar a duração
        for t in dados['tracks']['data']:
            faixa = FaixaMusical(t['id'], t['title'], t['artist']['name'], t['duration'])
            album.adicionar_faixa(faixa)
            
        return album
    except Exception:
        return None

#Menu

if __name__ == "__main__":
    bib = Biblioteca()
    musicas_avaliadas = []
    ultimo_id_album = None

    while True:
        print("\n" + "="*45)
        print("             CATÁLOGO MUSICAL")
        print("="*45)
        print("1. Buscar música e avaliar (RF1)")
        print("2. Adicionar Música à Biblioteca (RF2)")
        print("3. Adicionar o Álbum dessa música à Biblioteca (RF3)")
        print("4. Criar Playlist com as músicas avaliadas (RF3)")
        print("5. Listar Biblioteca e Duração Total (RF3)")
        print("0. Sair")
        print("="*45)
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == '1':
            nome = input("Qual música você quer buscar? ")
            musica_encontrada, id_album = buscar_faixa_deezer(nome)
            
            if musica_encontrada:
                ultimo_id_album = id_album
                print(f"\nEncontrada: {musica_encontrada.titulo} - {musica_encontrada.artista}")
                while True:
                    try:
                        nota = float(input(f"Avalie '{musica_encontrada.titulo}' (0 a 5): ").replace(',', '.'))
                        musica_encontrada.avaliacao = nota
                        musicas_avaliadas.append(musica_encontrada)
                        print("Nota salva! Música pronta para ir pra biblioteca.")
                        break
                    except ValueError as e:
                        print(e)
                        
        elif opcao == '2':
            if not musicas_avaliadas:
                print("Busque e avalie uma música primeiro (Opção 1).")
            else:
                print("\nMúsicas avaliadas:")
                for m in musicas_avaliadas:
                    print(f" - {m.titulo}")
                
                escolha = input("\nDigite o nome da música para adicionar à biblioteca: ")
                musica = next((m for m in musicas_avaliadas if escolha.lower() in m.titulo.lower()), None)
                
                if musica:
                    bib.adicionar_midia(musica)
                else:
                    print("Música não encontrada na lista.")
                    
        elif opcao == '3':
            if ultimo_id_album:
                print("\nBuscando o álbum completo na Deezer...")
                album = buscar_album_deezer(ultimo_id_album)
                if album:
                    bib.adicionar_midia(album)
            else:
                print("Busque uma música primeiro para o sistema achar o álbum dela.")
                
        elif opcao == '4':
            if not musicas_avaliadas:
                print("Você precisa avaliar algumas músicas primeiro.")
            else:
                nome_pl = input("Digite o nome da sua nova Playlist: ")
                id_pl = random.randint(1000, 9999) # ID fictício só para controle da biblioteca
                playlist = Playlist(id_pl, nome_pl)
                
                for m in musicas_avaliadas:
                    playlist.adicionar_item(m)
                    
                bib.adicionar_midia(playlist)
                print(f"Playlist '{nome_pl}' criada com suas {len(musicas_avaliadas)} músicas e adicionada à biblioteca!")
                
        elif opcao == '5':
            bib.listar_biblioteca()
            
        elif opcao == '0':
            break
        else:
            print("Opção inválida.")