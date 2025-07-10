import sqlite3

# Conectar à base de dados
conn = sqlite3.connect('eventos_petizes.db')
c = conn.cursor()

# Criar tabela 'convocatorias'
c.execute('''
    CREATE TABLE IF NOT EXISTS convocatorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        evento_id INTEGER NOT NULL,
        data TEXT NOT NULL,
        FOREIGN KEY (evento_id) REFERENCES eventos(id)
    )
''')

# Eliminar a tabela antiga (opcional, apenas se precisares recriar do zero)
c.execute("DROP TABLE IF EXISTS convocados")

# Criar a nova tabela 'convocados' com a coluna 'nome'
c.execute('''
    CREATE TABLE IF NOT EXISTS convocados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        evento_id INTEGER,
        jogador_id INTEGER,
        nome TEXT,
        estado TEXT,
        FOREIGN KEY (evento_id) REFERENCES eventos(id)
    )
''')

conn.commit()
conn.close()

print("✅ Tabelas 'convocatorias' e 'convocados' criadas com sucesso em eventos_petizes.db.")
