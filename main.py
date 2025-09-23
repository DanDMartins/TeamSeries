from db import criar_tabelas, conectar

# Cria as tabelas do banco de dados (caso não existam)
criar_tabelas()

# Iniciar o Menu

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
            if evento_id:
                menu_eventos(evento_id)
        elif escolha == '3':
            print("Saindo do programa. Até mais!")
            break
        else:
            print("Opção inválida. Tente novamente.")

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

if __name__ == "__main__":
    criar_tabelas()
    menu_principal()

def cadastrar_provas(evento_id, num_provas):
    for i in range(1, num_provas + 1):
        nome_prova = input(f"Digite o nome da Prova {i}: ")
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO prova (nome, evento_id) VALUES (?, ?)", (nome_prova, evento_id))
        conn.commit()
        conn.close()
        print(f"Prova '{nome_prova}' cadastrada com sucesso!")

def cadastrar_equipe(evento_id):
    while True:
        nome = input("Digite o Nome da Equipe: ")
        if not nome:
            print("É necessário criar um nome pra equipe.")
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
        print("Equipe '{nome}' cadastrada com sucesso!")

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

# Função para visualizar resultados por categoria
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











































'''# Dicionario para pontuacao
pontuacao = {1: 100, 2: 95, 3: 90, 4: 85, 5: 80}
provas = ["Prova 1.A", "Prova 1.B"]

# Lista para os Times
times_rx = ["Time Bianca", "Time Marcella", "Time Julia", "Time Ludimila"]
times_sc = ["Time Leticia", "Time Amanda", "Time Marco", "Time Sara"]

# Dicionario para pontuacao total
pontuacao_total = {
    "Time Bianca": 0,
    "Time Marcella": 0,
    "Time Julia": 0,
    "Time Ludimila": 0,
    "Time Leticia": 0,
    "Time Amanda": 0,
    "Time Marco": 0,
    "Time Sara": 0
}

for prova in provas:
    print(f"\n--- {prova} ---")
    
    # Coletar resultados para RX
    print("\nResultados RX:")
    for i in range(1, 5):
        while True:
            atleta = input(f"Digite o nome do atleta que ficou em {i}º lugar (RX): ")
            if atleta in times_rx:
                pontuacao_total[atleta] += pontuacao[i]
                break
            else:
                print("Atleta não encontrado no Time RX. Tente novamente.")
    
    # Coletar resultados para SC
    print("\nResultados SC:")
    for i in range(1, 5):
        while True:
            atleta = input(f"Digite o nome do atleta que ficou em {i}º lugar (SC): ")
            if atleta in times_sc:
                pontuacao_total[atleta] += pontuacao[i]
                break
            else:
                print("Atleta não encontrado no Time SC. Tente novamente.")

# --- Exibir o Resultado Final ---
print("\n--- Ranking Final de Pontuação RX ---")
print("-" * 35)
sorted_rx = sorted(
    [(time, pontuacao_total[time]) for time in times_rx],
    key=lambda x: x[1],
    reverse=True
)
for time, pontos in sorted_rx:
    print(f"{time}: {pontos} pontos")
print(f"\nO vencedor RX é o {sorted_rx[0][0]} com {sorted_rx[0][1]} pontos!")

print("\n--- Ranking Final de Pontuação SC ---")
print("-" * 35)
sorted_sc = sorted(
    [(time, pontuacao_total[time]) for time in times_sc],
    key=lambda x: x[1],
    reverse=True
)
for time, pontos in sorted_sc:
    print(f"{time}: {pontos} pontos")
print(f"\nO vencedor SC é o {sorted_sc[0][0]} com {sorted_sc[0][1]} pontos!")
'''