
import sqlite3

# Conectar ou criar a base de dados
conn = sqlite3.connect('assiduidade_petizes.db')
c = conn.cursor()

# Criar a tabela de registos de assiduidade
c.execute('''
    CREATE TABLE IF NOT EXISTS registos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        jogador_id INTEGER NOT NULL,
        data TEXT NOT NULL,
        estado TEXT NOT NULL
    )
''')

conn.commit()
conn.close()

print("Base de dados 'assiduidade_petizes.db' criada com sucesso.")
