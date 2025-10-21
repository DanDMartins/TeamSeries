from db import criar_tabelas, conectar
import streamlit as st

# Cria as tabelas do banco de dados (caso não existam)
criar_tabelas()

# 1. Selecionar Evento
def selecionar_evento():

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM evento")
    eventos = cursor.fetchall()
    conn.close()

    if not eventos:
        print("Nenhum evento cadastrado.")
        return None
    
    print("\nEventos Disponíveis:")
    for evento in eventos:
        print(f"{evento[0]}. {evento[1]}")
    while True:
        try:
            evento_id = int(input("Selecione o ID do Evento que deseja gerenciar: "))
            if any(evento[0] == evento_id for evento in eventos):
                return evento_id
            else:
                print("ID inválido. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Digite um número.")

# 2. Cadastrar Equipe
def cadastrar_equipe(evento_id):
    equipes_cadastradas = 0
    while True:
        nome = input("Digite o Nome da Equipe (ou Enter para finalizar, ou 'sair' para cancelar): ")
        if nome.lower() == 'sair':
            print("Cadastro de equipes cancelado.")
            break
        if not nome:
            if equipes_cadastradas == 0:
                print("Nenhuma equipe cadastrada. Retornando ao menu.")
                break
            else:
                break
        categoria = input("Digite a Categoria (RX/SC): ").strip().upper()
        if categoria not in ['RX', 'SC']:
            print("Categoria inválida. Use 'RX' ou 'SC'.")
            continue

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO equipe (nome, categoria, evento_id) VALUES (?, ?, ?)", (nome, categoria, evento_id))
        conn.commit()
        conn.close()
        equipes_cadastradas += 1
        print(f"Equipe '{nome}' cadastrada com sucesso!")

# 3. Cadastrar Provas
def cadastrar_provas(evento_id, num_provas):
    for i in range(1, num_provas + 1):
        nome_prova = input(f"Digite o nome da Prova {i}: ")
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO prova (nome, evento_id) VALUES (?, ?)", (nome_prova, evento_id))
        conn.commit()
        conn.close()
        print(f"Prova '{nome_prova}' cadastrada com sucesso!")

#. 4 - Cadastrar Eventos
def cadastro_evento():
    nome = input("Digite o Nome do Evento: ")
    print("Selecione o Sistema de Pontuação: (ex: 1:100, 2:95, 3:90, ...)")
    sistema = input("Pontuação: ")
    num_provas = int(input("Digite o Número de Provas: "))

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO evento (nome, sistema_pontuacao, num_provas) VALUES (?, ?, ?)", (nome, sistema, num_provas))
    evento_id = cursor.lastrowid
    conn.commit()
    conn.close()
    print("Evento cadastrado com sucesso!")

    print("Agora, cadastre as equipes para este evento.")
    cadastrar_equipe(evento_id)

    print("Agora, cadastre as provas para este evento.")
    cadastrar_provas(evento_id, num_provas)

# ...existing code...

def cadastro_evento_streamlit():
    st.header("Cadastrar Novo Evento")
    nome = st.text_input("Nome do Evento")
    sistema = st.text_input("Sistema de Pontuação (ex: 1:100, 2:95, 3:90, ...)")
    num_provas = st.number_input("Número de Provas", min_value=1, step=1)

    if st.button("Cadastrar Evento"):
        if not nome or not sistema or num_provas < 1:
            st.warning("Preencha todos os campos corretamente.")
        else:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO evento (nome, sistema_pontuacao, num_provas) VALUES (?, ?, ?)",
                (nome, sistema, num_provas)
            )
            evento_id = cursor.lastrowid
            conn.commit()
            conn.close()
            st.success("Evento cadastrado com sucesso!")
            st.info("Agora cadastre as equipes e provas para este evento.")

# ...existing code...

#. 5 - Adicionar/Editar pontuação de prova
def adicionar_pontuacao(evento_id):
    # Buscar provas do evento
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM prova WHERE evento_id = ?", (evento_id,))
    provas = cursor.fetchall()
    if not provas:
        print("Nenhuma prova cadastrada para este evento.")
        conn.close()
        return
    
    print("\nProvas Disponíveis:")
    for prova in provas:
        print(f"{prova[0]}. {prova[1]}")
    try:
        prova_id = int(input("Selecione o ID da Prova para adicionar/editar pontuação: "))
    except ValueError:
        print("Entrada inválida.")
        conn.close()
        return
    if not any(p[0] == prova_id for p in provas):
        print("ID de prova inválido.")
        conn.close()
        return
    
    # Buscar equipes do evento

    cursor.execute("SELECT id, nome FROM equipe WHERE evento_id = ?", (evento_id,))
    equipes = cursor.fetchall()
    if not equipes:
        print("Nenhuma equipe cadastrada para este evento.")
        conn.close()
        return
    print("\nEquipes Disponíveis:")
    for equipe in equipes:
        print(f"{equipe[0]}. {equipe[1]}")
    
    print("Digite a colocação de cada equipe na prova (ou 'sair' para terminar):")
    colocacoes = {}
    for equipe in equipes:
        while True:
            try:
                colocacao = int(input(f"{equipe[1]} ({equipe[2]}): "))
                if colocacao < 1 or colocacao > len(equipes):
                    print("Colocação inválida. Tente novamente.")
                    continue
                if colocacao in colocacoes.values():
                    print("Colocação já atribuída. Tente novamente.")
                    continue
                colocacoes[equipe[0]] = colocacao
                break
            except ValueError:
                print("Entrada inválida. Digite um número ou 'sair'.")

    # Obter sistema de pontuação do evento
    cursor.execute("SELECT sistema_pontuacao FROM evento WHERE id = ?", (evento_id,))
    sistema = cursor.fetchone()[0]
    # Exemplo: sistema = "1:100, 2:95, 3:90, 4:85, 5:80"
    pontos_dict = {}
    for item in sistema.split(','):
        pos, pts = item.split(':')
        pontos_dict[int(pos)] = int(pts)

    # Salvar pontuações no DB
    for equipe_id, colocacao in colocacoes.items():
        pontos = pontos_dict.get(colocacao, 0)
        cursor.execute(
            "SELECT id FROM pontuacao WHERE equipe_id = ? AND prova_id = ?",
            (equipe_id, prova_id)
        )
        existe = cursor.fetchone()
        if existe:
            cursor.execute(
                "UPDATE pontuacao SET colocacao = ?, pontos = ? WHERE id = ?",
                (colocacao, pontos, existe[0])
            )
        else:
            cursor.execute(
                "INSERT INTO pontuacao (equipe_id, prova_id, colocacao, pontos) VALUES (?, ?, ?, ?)",
                (equipe_id, prova_id, colocacao, pontos)
            )
    conn.commit()
    conn.close()
    print("Pontuações registradas com sucesso!")

#. 6 - Visualizar resultados por categoria
def visualizar_resultados(evento_id):
    conn = conectar()
    cursor = conn.cursor()
    # Buscar equipes e categorias
    cursor.execute("SELECT id, nome, categoria FROM equipe WHERE evento_id = ?", (evento_id,))
    equipes = cursor.fetchall()
    if not equipes:
        print("Nenhuma equipe cadastrada para este evento.")
        conn.close()
        return
    
    # Inicializar dicionários de pontuação por categoria
    resultados = {'RX': [], 'SC': []}
    for equipe in equipes:
        equipe_id, nome, categoria = equipe
        cursor.execute("SELECT SUM(pontos) FROM pontuacao WHERE equipe_id = ?", (equipe_id,))
        total = cursor.fetchone()[0] or 0
        resultados[categoria].append((nome, total))

    # Exibir ranking RX
    print("\n--- Ranking RX ---")
    for nome, total in sorted(resultados['RX'], key=lambda x: x[1], reverse=True):
        print(f"{nome}: {total} pontos")
    # Exibir ranking SC
    print("\n--- Ranking SC ---")
    for nome, total in sorted(resultados['SC'], key=lambda x: x[1], reverse=True):
        print(f"{nome}: {total} pontos")
    conn.close()

#. 7 - Menu dos Eventos
def menu_eventos(evento_id):
    while True:
        print("\n--- Gerenciamento de Eventos ---")
        print("1. Adicionar/Editar pontuação de prova")
        print("2. Visualizar resultados por categoria")
        print("3. Voltar ao Menu Principal")
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            adicionar_pontuacao(evento_id)
        elif escolha == '2':
            visualizar_resultados(evento_id)
        elif escolha == '3':
            break
        else:
            print("Opção inválida. Tente novamente.")

#. 8 - Menu Principal
def menu_principal():
    while True:
        print("\n--- TEAMSERIES - Menu Principal ---")
        print("1. Cadastrar Evento")
        print("2. Selecionar Evento para Gerenciar")
        print("3. Sair")
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            cadastro_evento()
        elif escolha == '2':
            evento_id = selecionar_evento()
            if evento_id is not None:
                menu_eventos(evento_id)
            else:
                print("Nenhum evento disponível.")
        elif escolha == '3':
            print("Saindo do programa. Até mais!")
            break
        else:
            print("Opção inválida. Tente novamente.")

#. 9 - Iniciar o Programa

st.title("TeamSeries - Menu Principal")

opcao = st.sidebar.radio(
    "Escolha uma opção:",
    ["Cadastrar Evento", "Selecionar Evento para Gerenciar", "Sair"]
)

# Cadastro de Eventos via Streamlit

def cadastro_evento_streamlit():
    st.header("Cadastrar Novo Evento")
    nome = st.text_input("Nome do Evento")
    sistema = st.text_input("Sistema de Pontuação (ex: 1:100, 2:95, 3:90, ...)")
    num_provas = st.number_input("Número de Provas", min_value=1, step=1)

    if st.button("Cadastrar Evento"):
        if not nome or not sistema or num_provas < 1:
            st.warning("Preencha todos os campos corretamente.")
        else:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO evento (nome, sistema_pontuacao, num_provas) VALUES (?, ?, ?)",
                (nome, sistema, num_provas)
            )
            evento_id = cursor.lastrowid
            conn.commit()
            conn.close()
            st.success("Evento cadastrado com sucesso!")
            st.info("Agora cadastre as equipes e provas para este evento.")

# Selecionar Evento via Streamlit

def selecionar_evento_streamlit():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM evento")
    eventos = cursor.fetchall()
    conn.close()

    if not eventos:
        st.warning("Nenhum evento cadastrado.")
        return None
    
    opcoes = {f"{evento[1]} (ID: {evento[0]})": evento[0] for evento in eventos}
    escolhido = st.selectbox("Selecione o Evento que deseja gerenciar:", list(opcoes.keys()))
    if escolhido:
        evento_id = opcoes[escolhido]
        st.success(f"Evento '{escolhido}' selecionado.")
        return evento_id
    return None

# Visualizar resultados via Streamlit

def visualizar_resultados_streamlit(evento_id):
    conn = conectar()
    cursor = conn.cursor()
    # Buscar equipes e categorias
    cursor.execute("SELECT id, nome, categoria FROM equipe WHERE evento_id = ?", (evento_id,))
    equipes = cursor.fetchall()
    if not equipes:
        st.warning("Nenhuma equipe cadastrada para este evento.")
        conn.close()
        return
    
    # Inicializar dicionários de pontuação por categoria
    resultados = {'RX': [], 'SC': []}
    for equipe in equipes:
        equipe_id, nome, categoria = equipe
        cursor.execute("SELECT SUM(pontos) FROM pontuacao WHERE equipe_id = ?", (equipe_id,))
        total = cursor.fetchone()[0] or 0
        resultados[categoria].append((nome, total))

    # Exibir ranking RX
    st.subheader("Ranking RX")
    for nome, total in sorted(resultados['RX'], key=lambda x: x[1], reverse=True):
        st.write(f"{nome}: {total} pontos")
    # Exibir ranking SC
    st.subheader("Ranking SC")
    for nome, total in sorted(resultados['SC'], key=lambda x: x[1], reverse=True):
        st.write(f"{nome}: {total} pontos")
    conn.close()

# Menu de Gerenciamento de eventos -- todo adaptar para Streamlit depois

def menu_eventos_streamlit(evento_id):
    # buscar nome do evento
    conn = conectar()
    cursor = conn.cursor()  
    cursor.execute("SELECT nome FROM evento WHERE id = ?", (evento_id,))
    evento_nome = cursor.fetchone()
    conn.close()
    nome_evento = evento_nome[0] if evento_nome else f"ID {evento_id}"

    st.header(f"Gerenciamento do Evento: {nome_evento}")

    escolha = st.radio(
        "Escolha uma opção:", [
            "Adicionar/Editar pontuação de prova",
            "Visualizar resultados por categoria",
            "Voltar ao Menu Principal"
        ])
    if escolha == "Adicionar/Editar pontuação de prova":
        visualizar_resultados_streamlit(evento_id)
    elif escolha == "Visualizar resultados por categoria":
        st.info("Funcionalidade de adicionar/editar pontuação via Streamlit ainda não implementada.")
    elif escolha == "Voltar ao Menu Principal":
        st.info("Retornando ao Menu Principal.")

# Menu Principal Streamlit

if opcao == "Cadastrar Evento":
    cadastro_evento_streamlit()
elif opcao == "Selecionar Evento para Gerenciar":
    evento_id = selecionar_evento_streamlit()
    if evento_id:
        # chama o menu do evento (sub-menu) em vez de apenas mostrar um info
        menu_eventos_streamlit(evento_id)
elif opcao == "Sair":
    st.write("Obrigado por usar o TeamSeries!")



