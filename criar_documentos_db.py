import sqlite3

conn = sqlite3.connect('documentos.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS documentos_atletas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    atleta_id INTEGER NOT NULL,
    equipa TEXT NOT NULL,
    fotografia TEXT,
    mod2_fpf TEXT,
    exame_medico TEXT,
    cc_atleta TEXT,
    cc_ee TEXT
)
''')

conn.commit()
conn.close()

print("Base de dados 'documentos.db' criada com sucesso.")
