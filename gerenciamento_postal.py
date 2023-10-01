import csv
import io
import tkinter as tk
import pandas as pd
import plotly.graph_objs as go
from PIL import ImageTk, Image
from plotly.subplots import make_subplots


def salvar_csv():
    # Obter os dados das caixas de texto
    tabela_distritos = texto_distritos.get("1.0", "end-1c")
    tabela_lista = texto_lista.get("1.0", "end-1c")

    # Salvar tabela_distritos em um arquivo CSV
    with open("dados_distritos.csv", "w", newline="",
              encoding="utf-8") as arquivo_distritos:

        writer = csv.writer(arquivo_distritos)
        linhas_distritos = tabela_distritos.split("\n")
        for linha in linhas_distritos:
            writer.writerow(linha.split("\t"))

    # Salvar tabela_lista em um arquivo CSV
    with open("dados_lista.csv", "w", newline="",
              encoding="utf-8") as arquivo_lista:
        writer = csv.writer(arquivo_lista)
        linhas_lista = tabela_lista.split("\n")
        for linha in linhas_lista:
            writer.writerow(linha.split("\t"))

    print("Tabelas salvas com sucesso!")

    # Limpar as caixas de texto
    texto_distritos.delete("1.0", tk.END)
    texto_lista.delete("1.0", tk.END)


def tratamento_de_dados():
    # Ler os dados dos arquivos CSV
    dados_distritos = pd.read_csv("dados_distritos.csv", header=None)
    dados = pd.read_csv("dados_lista.csv", header=None)

    # Preencher valores ausentes com 0
    dados_distritos = dados_distritos.fillna(0)
    dados = dados.fillna(0)

    # Remover colunas indesejadas
    dados_distritos = dados_distritos.drop(3, axis=1)
    dados_distritos = dados_distritos.drop(5, axis=1)
    dados_distritos = dados_distritos.drop(7, axis=1)
    dados = dados.drop(2, axis=1)
    dados = dados.drop(6, axis=1)

    # Renomear as colunas para melhorar a legibilidade
    dados_distritos.rename(
        columns={0: "distrito", 1: "mat/carteiro",
                 2: "qnt_obj", 4: "qnt_ar", 6: "num_lista"},
        inplace=True,
    )
    dados.rename(
        columns={0: "num_lista", 1: "cod_objeto",
                 3: "endereco", 4: "ar", 5: "cep"},
        inplace=True,
    )

    return dados_distritos, dados


def separar_dados_em_dict(dados, dados_distritos):
    # Dicionário para armazenar os dados separados por chave
    dados_dict = {}

    # Variáveis de controle para acompanhar a chave e a lista atual
    chave_atual = None
    lista_atual = []

    for _, linha in dados.iterrows():
        numero = linha["num_lista"]

        if numero != 0:
            # Se encontrarmos uma nova chave, atualizamos o dicionário
            # com a lista anterior
            if chave_atual:
                dados_dict[chave_atual] = lista_atual

            # Atualizamos a chave atual e reiniciamos a lista atual
            chave_atual = numero
            lista_atual = []

        elif chave_atual is not None:
            # Adicionamos a linha à lista atual
            lista_atual.append(linha.tolist())

    if chave_atual:
        # Adicionamos a última lista ao dicionário
        dados_dict[chave_atual] = lista_atual

    # Mapeamos os números de lista para os distritos correspondentes
    distrito_dict = dict(zip(dados_distritos["num_lista"],
                             dados_distritos["distrito"]))

    # Renomeamos as chaves do dicionário com os nomes dos distritos
    dados_dict = {
        distrito_dict.get(chave, "Distrito não encontrado"): valores
        for chave, valores in dados_dict.items()
    }

    return dados_dict


def criar_grafico_gauge(chave, quantidade_enderecos_unicos, total_objetos):
    if chave < "600 A":
        # Criação do gráfico gauge para chaves menores que "600 A"
        fig = make_subplots(
            rows=1,
            cols=1,
        )

        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=quantidade_enderecos_unicos,
                domain={"row": 1, "column": 1},
                title={"text": f"Pontos: {quantidade_enderecos_unicos}"},
                delta={"reference": 110},
                gauge={
                    "axis": {"range": [None, 220],
                             "tickvals": [0, 55, 110, 165, 220]},
                    "steps": [
                        {"range": [0, 100], "color": "#1919ff"},
                        {"range": [100, 110], "color": "#0000b3"},
                        {"range": [110, 220], "color": "white"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": 219,
                    },
                    "bar": {"color": "#00e000"}
                },
            )
        )

        fig.update_layout(
            width=400,  # Especifica a largura desejada em pixels
            height=300,  # Especifica a altura desejada em pixels
            paper_bgcolor='#FFFF70',  # Definindo a cor de fundo do gráfico
        )

        # Renderizar o gráfico em uma imagem
        img_bytes = fig.to_image(format="png", engine="kaleido")
        graph_img = ImageTk.PhotoImage(Image.open(io.BytesIO(img_bytes)))

        return graph_img
    else:
        # Criação do gráfico gauge para chaves maiores ou iguais a "600 A"
        fig = make_subplots(
            rows=1,
            cols=1,
        )

        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=quantidade_enderecos_unicos,
                domain={"row": 1, "column": 1},
                title={"text": f"Pontos: {quantidade_enderecos_unicos}"},
                delta={"reference": 50},
                gauge={
                    "axis": {"range": [None, 100]},
                    "steps": [
                        {"range": [0, 40], "color": "#1919ff"},
                        {"range": [40, 50], "color": "#0000b3"},
                        {"range": [50, 100], "color": "white"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": 99,
                    },
                },
            )
        )

        fig.update_layout(
            width=400,  # Especifica a largura desejada em pixels
            height=300,  # Especifica a altura desejada em pixels
            paper_bgcolor='#FFFF90',  # Definindo a cor de fundo do gráfico
        )

        # Renderizar o gráfico em uma imagem
        img_bytes = fig.to_image(format="png")
        graph_img = ImageTk.PhotoImage(Image.open(io.BytesIO(img_bytes)))

        return graph_img


def criar_container_grafico(container, chave, valores):
    # Cria um frame para envolver o conteúdo do container
    container_borda = tk.Frame(container, bd=1,
                               relief=tk.SOLID,
                               background="#00008f")
    container_borda.pack()

    # Cria um label para exibir o nome do distrito
    label_distrito = tk.Label(container_borda, text=chave,
                              font=("Arial", 20, "bold"),
                              background="#00008f",
                              # defindo a cor do texto como branco
                              fg="white",)
    label_distrito.pack(pady=5)

    # Obtém a lista de endereços únicos e calcula as estatísticas
    enderecos = [valor[2] for valor in valores]
    enderecos_unicos = set(enderecos)
    quantidade_enderecos_unicos = len(enderecos_unicos)
    total_objetos = len(valores)

    # Conta a quantidade de "AR" onde a coluna "ar" tem o valor "X"
    ar_valores = [valor[3] for valor in valores]
    quantidade_ar = ar_valores.count('  X')

    # Cria um label para exibir as informações de total de objetos,
    # pontos e quantidade de "AR"
    label_info = tk.Label(
        container_borda,
        font=("Arial", 16),
        text=f"Total de objetos: {total_objetos}\nAR: {quantidade_ar}",
        fg="white",  # defindo a cor do texto como branco
        background="#00008f",
    )
    label_info.pack(pady=5)

    # Cria o gráfico gauge
    graph_img = criar_grafico_gauge(chave,
                                    quantidade_enderecos_unicos, total_objetos)

    # Cria um label para exibir a imagem do gráfico
    graph_label = tk.Label(container_borda, image=graph_img)
    # Mantém uma referência para evitar a coleta de lixo
    graph_label.image = graph_img
    graph_label.pack()


def abrir_janela_conta_ponto():
    # Cria uma nova janela para exibir os dados de conta ponto
    nova_janela = tk.Toplevel(janela)
    nova_janela.title("Conta Pontos")
    nova_janela.state('normal')

    # Chama a função conta_ponto para exibir os dados na nova janela
    conta_ponto(nova_janela)


def conta_ponto(nova_janela):
    # Realiza o tratamento dos dados
    dados_distritos, dados = tratamento_de_dados()
    resultado = separar_dados_em_dict(dados, dados_distritos)

    # Adiciona uma borda ao redor do conteúdo
    frame_borda = tk.Frame(nova_janela, bd=1, relief=tk.SOLID)
    frame_borda.pack(padx=10, pady=10)

    # Ordena as chaves para exibição
    sorted_chaves = sorted(resultado.keys(), key=lambda x: (x.split()[1],
                                                            int(x.split()[0])))

    # Define o número de colunas para exibição
    num_colunas = 4

    # Cria um componente de ScrollView vertical
    scroll_y = tk.Scrollbar(nova_janela)
    scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    # Cria um componente de ScrollView horizontal
    scroll_x = tk.Scrollbar(nova_janela, orient=tk.HORIZONTAL)
    scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

    # Cria um componente de Canvas para o conteúdo
    canvas = tk.Canvas(nova_janela, yscrollcommand=scroll_y.set,
                       xscrollcommand=scroll_x.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Configura a barra de rolagem vertical para controlar o Canvas
    scroll_y.config(command=canvas.yview)

    # Configura a barra de rolagem horizontal para controlar o Canvas
    scroll_x.config(command=canvas.xview)

    # Cria um componente de Frame para o conteúdo dentro do Canvas
    frame_conta_pontos = tk.Frame(canvas)

    # Configura o Canvas para conter o Frame
    canvas.create_window((0, 0), window=frame_conta_pontos, anchor="nw")

    # Configura o Frame para ajustar seu tamanho de acordo com o conteúdo
    frame_conta_pontos.bind("<Configure>", lambda event:
                            canvas.configure(scrollregion=canvas.bbox("all")))

    # Função para rolagem com o mouse
    def on_mousewheel(event):
        canvas.yview_scroll(-int(event.delta / 120), "units")

    # Associa a rolagem do mouse ao Canvas
    canvas.bind_all("<MouseWheel>", on_mousewheel)

    # Itera sobre as chaves e valores para criar os contêineres com gráficos
    for i, chave in enumerate(sorted_chaves):
        valores = resultado[chave]
        linha = i // num_colunas
        coluna = i % num_colunas

        container = tk.Frame(frame_conta_pontos)
        container.grid(row=linha, column=coluna, padx=10, pady=10)

        # Cria o contêiner do gráfico e insere no container principal
        criar_container_grafico(container, chave, valores)

    # Inicia o loop da nova janela
    nova_janela.mainloop()


def encontrar_duplicados():
    # Cria uma nova janela para exibir os endereços duplicados
    nova_janela = tk.Toplevel(janela)
    nova_janela.title("Duplicados")

    # Realiza o tratamento dos dados
    dados_distritos, dados = tratamento_de_dados()
    resultado = separar_dados_em_dict(dados, dados_distritos)

    # Remove endereços duplicados em cada chave
    for chave, valores in resultado.items():
        endereco_set = set()
        valores_sem_duplicados = []
        for valor in valores:
            endereco = valor[2]
            if endereco not in endereco_set:
                endereco_set.add(endereco)
                valores_sem_duplicados.append(valor)

        resultado[chave] = valores_sem_duplicados

    # Compara chaves e encontra endereços duplicados entre as chaves
    enderecos_duplicados = set()
    for chave1, valores1 in resultado.items():
        for chave2, valores2 in resultado.items():
            if chave1 != chave2:
                for valor1 in valores1:
                    endereco1 = valor1[2]
                    for valor2 in valores2:
                        endereco2 = valor2[2]
                        if endereco1 == endereco2:
                            if chave1 > "600 A":
                                enderecos_duplicados.add(chave1 + " >> "
                                                         + chave2 + "  "
                                                         + endereco1)
                            else:
                                enderecos_duplicados.add(chave2 + " >> "
                                                         + chave1 + "  "
                                                         + endereco1)

    # Exibe endereços duplicados
    if enderecos_duplicados:
        # Cria uma label para exibir a mensagem
        label_duplicados = tk.Label(nova_janela, text="Endereços Duplicados:",
                                    font=("Arial", 16, "bold"))
        label_duplicados.pack(pady=10)

        # Cria um frame para conter a caixa de texto
        frame_texto = tk.Frame(nova_janela)
        frame_texto.pack(padx=10, pady=10)

        # Cria uma barra de rolagem vertical
        scrollbar = tk.Scrollbar(frame_texto)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Cria uma caixa de texto para exibir os endereços duplicados
        texto_duplicados = tk.Text(frame_texto, height=15, width=70,
                                   yscrollcommand=scrollbar.set)
        texto_duplicados.pack(side=tk.LEFT, padx=5)

        # Associa a barra de rolagem à caixa de texto
        scrollbar.config(command=texto_duplicados.yview)

        # Ordena a lista de endereços duplicados em ordem crescente
        enderecos_ordenados = sorted(enderecos_duplicados)

        # Insere os endereços duplicados na caixa de texto
        for endereco in enderecos_ordenados:
            texto_duplicados.insert(tk.END, endereco + "\n")

    else:
        # Cria uma label para exibir a mensagem de nenhum endereço
        # duplicado encontrado
        label_nenhum_duplicado = tk.Label(
            nova_janela,
            font=("Arial", 16, "bold"),
            text="Nenhum endereço duplicado encontrado."
        )
        label_nenhum_duplicado.pack(pady=10)

    # Inicia o loop da nova janela
    nova_janela.mainloop()


# Cria a janela principal
janela = tk.Tk()
janela.title("Gerencial")
janela.geometry("800x500")

# Cria as caixas de texto
texto_distritos = tk.Text(janela, height=10, width=30)
texto_distritos.pack(side="left", padx=10, pady=10)

texto_lista = tk.Text(janela, height=10, width=30)
texto_lista.pack(side="right", padx=10, pady=10)

# Cria o botão de salvar
botao_salvar = tk.Button(janela, text="Salvar", command=salvar_csv)
botao_salvar.pack(pady=10)

# Cria o botão para abrir uma nova janela de conta ponto
botao_nova_janela = tk.Button(janela, text="Conta Pontos",
                              command=abrir_janela_conta_ponto)
botao_nova_janela.pack(pady=10)

# Cria o botão para encontrar duplicados
botao_duplicados = tk.Button(janela, text="Duplicados",
                             command=encontrar_duplicados)
botao_duplicados.pack(pady=10)

# Inicia o loop da janela principal
janela.mainloop()
