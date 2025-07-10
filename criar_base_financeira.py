import sqlite3

conn = sqlite3.connect('financeiro.db')
c = conn.cursor()

# Criar tabela de jogadores (centralizada)
c.execute('''
CREATE TABLE IF NOT EXISTS jogadores (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    equipa TEXT
)
''')

# Opcional: inserir jogadores dos Petizes já existentes (caso necessário)
jogadores_petizes = [
    (1, 'João Silva', 'Petizes'),
    (2, 'Miguel Ferreira', 'Petizes'),
    (3, 'Tiago Santos', 'Petizes'),
    (4, 'Rafael Costa', 'Petizes')
]

for jogador in jogadores_petizes:
    c.execute("INSERT OR IGNORE INTO jogadores (id, nome, equipa) VALUES (?, ?, ?)", jogador)

conn.commit()
conn.close()


