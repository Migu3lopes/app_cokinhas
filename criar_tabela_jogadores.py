import sqlite3

# Conectar à base de dados principal
conn = sqlite3.connect('assiduidade.db')
c = conn.cursor()

# Criar a tabela de jogadores (com equipa associada)
c.execute('''
CREATE TABLE IF NOT EXISTS jogadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    equipa TEXT NOT NULL
)
''')

# Inserir alguns jogadores da equipa Petizes (exemplo)
jogadores = [
    ('João Silva', 'Petizes'),
    ('Miguel Costa', 'Petizes'),
    ('André Marques', 'Petizes'),
    ('Tiago Santos', 'Petizes'),
    ('Ricardo Almeida', 'Petizes')
]

# Inserir apenas se ainda não existirem jogadores
c.execute("SELECT COUNT(*) FROM jogadores WHERE equipa = 'Petizes'")
if c.fetchone()[0] == 0:
    c.executemany("INSERT INTO jogadores (nome, equipa) VALUES (?, ?)", jogadores)
    print("Jogadores da equipa Petizes inseridos com sucesso.")
else:
    print("Já existem jogadores da equipa Petizes na base de dados.")

conn.commit()
conn.close()
