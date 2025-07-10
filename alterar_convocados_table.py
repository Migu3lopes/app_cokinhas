import sqlite3

# Conecta à base de dados
conn = sqlite3.connect('eventos_petizes.db')
c = conn.cursor()

# Adiciona a coluna evento_id, se ainda não existir
try:
    c.execute('ALTER TABLE convocados ADD COLUMN evento_id INTEGER')
    print("✅ Coluna 'evento_id' adicionada com sucesso à tabela 'convocados'.")
except sqlite3.OperationalError as e:
    print("⚠️ Erro:", e)

conn.commit()
conn.close()
