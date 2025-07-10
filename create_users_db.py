import sqlite3

# Conectar ou criar a base de dados
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Criar a tabela de utilizadores
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')

# Inserir alguns utilizadores
c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ('admin', '1234'))
c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ('treinador', 'senha123'))

conn.commit()
conn.close()

print("Base de dados criada com sucesso.")
