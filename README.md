# Projeto-Software-2026.2

## Implementações Recentes

O projeto foi refatorado e modularizado para aplicar os conceitos de Programação Orientada a Objetos exigidos na especificação.

### Estrutura do Projeto
* **`modelos.py`**: Contém as classes do domínio musical.
* **`api.py`**: Gerencia a comunicação com a API da Deezer.
* **`main.py`**: Roda o menu interativo no terminal.

### Conceitos de POO Aplicados
* **Abstração e Herança (RF3)**: Criamos a classe abstrata `Midia` servindo de molde para `FaixaMusical`, `Album` e `Playlist`.
* **Encapsulamento (RF1 e RF2)**: As notas das músicas e a coleção da biblioteca são atributos privados (`_avaliacao`, `_colecao`). O acesso e a alteração são controlados (ex: barrando notas inválidas e duplicatas).
* **Polimorfismo (RF3)**: O cálculo de duração e a exibição de informações funcionam para qualquer item da biblioteca, já que cada classe filha sobrescreve os métodos `calcular_duracao()` e `exibir_info()` com sua própria lógica.
* **Agregação**: Álbuns contêm faixas, e Playlists contêm álbuns ou faixas, conectando os objetos do sistema.

 
 *Diagrama de classes*

<img width="1333" height="1911" alt="diagrama_1208 png" src="https://github.com/user-attachments/assets/751b4313-2b33-44de-9f4b-37cd6f117e49" />


