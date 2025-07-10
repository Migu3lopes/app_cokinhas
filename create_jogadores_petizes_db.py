import sqlite3

# Conectar ou criar a base de dados
conn = sqlite3.connect('jogadores_petizes.db')
c = conn.cursor()

# Criar a tabela de jogadores
c.execute('''
CREATE TABLE IF NOT EXISTS jogadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    data_nascimento TEXT NOT NULL,
    encarregado TEXT NOT NULL,
    contacto TEXT NOT NULL,
    escola TEXT NOT NULL
)
''')

conn.commit()
conn.close()

print("Base de dados 'jogadores_petizes.db' criada com sucesso.")
