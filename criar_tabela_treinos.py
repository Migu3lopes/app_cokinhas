import sqlite3

conn = sqlite3.connect('treinos_petizes.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS treinos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero INTEGER UNIQUE NOT NULL,
    data TEXT NOT NULL,
    hora TEXT NOT NULL,
    local TEXT,
    objetivos TEXT,
    material TEXT,
    exercicios TEXT
)
''')

conn.commit()
conn.close()

print("Tabela 'treinos' criada com sucesso.")
