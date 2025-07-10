import sqlite3

# Conectar à base de dados financeira
conn = sqlite3.connect('financeiro.db')
c = conn.cursor()

# Criar tabela 'jogadores' se não existir
c.execute('''
CREATE TABLE IF NOT EXISTS jogadores (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    equipa TEXT
)
''')

# Exemplo de jogadores da equipa Petizes
jogadores = [
    (1, 'João Silva', 'Petizes'),
    (2, 'Miguel Ferreira', 'Petizes'),
    (3, 'Tiago Santos', 'Petizes'),
    (4, 'Rafael Costa', 'Petizes')
]

# Inserir jogadores apenas se ainda não existirem
for jogador in jogadores:
    c.execute("INSERT OR IGNORE INTO jogadores (id, nome, equipa) VALUES (?, ?, ?)", jogador)

conn.commit()
conn.close()

print("Tabela 'jogadores' criada com sucesso.")
