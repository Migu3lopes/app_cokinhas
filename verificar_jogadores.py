import sqlite3

conn = sqlite3.connect('assiduidade.db')
c = conn.cursor()

# Verifica se a tabela existe
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jogadores'")
if c.fetchone():
    # Verifica jogadores da equipa Petizes
    c.execute("SELECT id, nome, equipa FROM jogadores WHERE equipa = 'Petizes'")
    jogadores = c.fetchall()

    if jogadores:
        print("Jogadores da equipa Petizes encontrados:")
        for jogador in jogadores:
            print(jogador)
    else:
        print("⚠️ Nenhum jogador da equipa Petizes foi encontrado.")
else:
    print("⚠️ A tabela 'jogadores' não existe na base de dados assiduidade.db.")

conn.close()
