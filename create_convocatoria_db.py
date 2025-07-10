import sqlite3

# Conexão à base de dados (será criada se não existir)
conn = sqlite3.connect('convocatoria_petizes.db')
c = conn.cursor()

# Criação da tabela
c.execute('''
CREATE TABLE IF NOT EXISTS convocatoria_petizes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_evento INTEGER,
    jogador TEXT NOT NULL,
    estado TEXT NOT NULL
)
''')

conn.commit()
conn.close()

print("Base de dados 'convocatoria_petizes.db' criada com sucesso.")
