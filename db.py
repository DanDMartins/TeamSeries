import sqlite3

def conectar():
    return sqlite3.connect('teamseries.db')

def criar_tabelas():
    import sqlite3

def conectar():
    return sqlite3.connect("teamseries.db")

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            sistema_pontuacao TEXT NOT NULL,
            num_provas INTEGER NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            evento_id INTEGER,
            FOREIGN KEY(evento_id) REFERENCES evento(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prova (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            evento_id INTEGER,
            FOREIGN KEY(evento_id) REFERENCES evento(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pontuacao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipe_id INTEGER,
            prova_id INTEGER,
            colocacao INTEGER,
            pontos INTEGER,
            FOREIGN KEY(equipe_id) REFERENCES equipe(id),
            FOREIGN KEY(prova_id) REFERENCES prova(id)
        )
    """)
    conn.commit()
    conn.close()