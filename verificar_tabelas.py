import sqlite3

conn = sqlite3.connect('assiduidade.db')
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tabelas = c.fetchall()

conn.close()

print("Tabelas existentes:")
for tabela in tabelas:
    print("-", tabela[0])
