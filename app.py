from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
import json  # ✅ Adiciona aqui
from flask import send_from_directory
from werkzeug.utils import secure_filename



app = Flask(__name__)
app.secret_key = 'bL#f32v@9Xz!82aJkR^5'  # podes escolher outra string segura

# Função para verificar se o utilizador existe na base de dados
def verificar_credenciais(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if verificar_credenciais(username, password):
            return redirect(url_for('dashboard'))
        else:
            error = 'Credenciais inválidas. Tente novamente.'
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/equipas')
def equipas():
    return render_template('equipas.html')

@app.route('/logout')
def logout():
    return redirect(url_for('login'))

@app.route('/petizes')
def petizes():
    return render_template('petizes.html')

@app.route('/petizes/plantel')
def plantel_petizes():
    return render_template('plantel_petizes.html')

@app.route('/petizes/plantel/lista')
def lista_jogadores_petizes():
    conn = sqlite3.connect('jogadores_petizes.db')
    c = conn.cursor()
    c.execute("SELECT id, nome, data_nascimento, encarregado, contacto, escola FROM jogadores")
    jogadores = c.fetchall()
    conn.close()
    return render_template('lista_jogadores_petizes.html', jogadores=jogadores)


@app.route('/petizes/plantel/editar', methods=['GET', 'POST'])
def editar_plantel_petizes():
    mensagem = None

    if request.method == 'POST':
        nome = request.form['nome']
        data_nascimento = request.form['data_nascimento']
        encarregado = request.form['encarregado']
        contacto = request.form['contacto']
        escola = request.form['escola']

        conn = sqlite3.connect('jogadores_petizes.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO jogadores (nome, data_nascimento, encarregado, contacto, escola)
            VALUES (?, ?, ?, ?, ?)
        ''', (nome, data_nascimento, encarregado, contacto, escola))
        conn.commit()
        conn.close()

        mensagem = "Jogador adicionado com sucesso!"

    return render_template('editar_plantel_petizes.html', mensagem=mensagem)

@app.route('/petizes/plantel/apagar/<int:id>')
def apagar_jogador_petizes(id):
    conn = sqlite3.connect('jogadores_petizes.db')
    c = conn.cursor()
    c.execute("DELETE FROM jogadores WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('lista_jogadores_petizes'))
@app.route('/petizes/plantel/editar/<int:id>', methods=['GET', 'POST'])
def editar_jogador_petizes(id):
    conn = sqlite3.connect('jogadores_petizes.db')
    c = conn.cursor()

    if request.method == 'POST':
        nome = request.form['nome']
        data_nascimento = request.form['data_nascimento']
        encarregado = request.form['encarregado']
        contacto = request.form['contacto']
        escola = request.form['escola']

        c.execute('''
            UPDATE jogadores
            SET nome = ?, data_nascimento = ?, encarregado = ?, contacto = ?, escola = ?
            WHERE id = ?
        ''', (nome, data_nascimento, encarregado, contacto, escola, id))

        conn.commit()
        conn.close()

        return redirect(url_for('lista_jogadores_petizes'))

    else:
        c.execute("SELECT * FROM jogadores WHERE id = ?", (id,))
        jogador = c.fetchone()
        conn.close()

        return render_template('editar_jogador_petizes.html', jogador=jogador)

@app.route('/petizes/assiduidade', methods=['GET', 'POST'])
def assiduidade_petizes():
    mensagem = None

    # Buscar todos os jogadores da equipa
    conn_j = sqlite3.connect('jogadores_petizes.db')
    c_j = conn_j.cursor()
    c_j.execute("SELECT * FROM jogadores")
    jogadores = c_j.fetchall()
    conn_j.close()

    if request.method == 'POST':
        data = request.form['data']

        conn_a = sqlite3.connect('assiduidade_petizes.db')
        c_a = conn_a.cursor()

        registo_feito = False  # flag para saber se algum registo novo foi feito

        for jogador in jogadores:
            jogador_id = jogador[0]
            estado = request.form.get(f'estado_{jogador_id}')

            # Verifica se já existe registo para esse jogador na mesma data
            c_a.execute("SELECT COUNT(*) FROM registos WHERE jogador_id = ? AND data = ?", (jogador_id, data))
            existe = c_a.fetchone()[0] > 0

            if not existe and estado:
                c_a.execute("INSERT INTO registos (jogador_id, data, estado) VALUES (?, ?, ?)",
                            (jogador_id, data, estado))
                registo_feito = True

        if registo_feito:
            conn_a.commit()
            mensagem = "O Registo de assiduidade foi efetuado com sucesso."
        else:
            mensagem = "Já existe registo de assiduidade para esta data."

        conn_a.close()

    return render_template('registo_assiduidade_petizes.html', jogadores=jogadores, mensagem=mensagem)


@app.route('/petizes/historico')
def historico_petizes():
    conn_j = sqlite3.connect('jogadores_petizes.db')
    c_j = conn_j.cursor()
    c_j.execute("SELECT id, nome FROM jogadores")
    jogadores = c_j.fetchall()
    conn_j.close()

    historico = []
    conn_a = sqlite3.connect('assiduidade_petizes.db')
    c_a = conn_a.cursor()

    for jogador in jogadores:
        jogador_id = jogador[0]
        nome = jogador[1]

        c_a.execute("SELECT estado FROM registos WHERE jogador_id = ?", (jogador_id,))
        registos = c_a.fetchall()

        presencas = sum(1 for r in registos if r[0] == "Presente")
        justificadas = sum(1 for r in registos if r[0] == "Falta Justificada")
        injustificadas = sum(1 for r in registos if r[0] == "Falta Injustificada")
        total = presencas + justificadas + injustificadas

        if total > 0:
            pontos = presencas + (justificadas * 0.5)
            percentagem = round((pontos / total) * 100, 1)
        else:
            percentagem = 0.0

        historico.append({
            'nome': nome,
            'presencas': presencas,
            'justificadas': justificadas,
            'injustificadas': injustificadas,
            'percentagem': percentagem
        })

    conn_a.close()
    return render_template('historico_assiduidade_petizes.html', historico=historico)

from datetime import datetime  # ✅ Adiciona este import no topo se ainda não tiveres

from datetime import datetime  # ✅ Adiciona este import no topo se ainda não tiveres

from flask import render_template, jsonify
import sqlite3
import json

@app.route('/petizes/calendario')
def calendario_petizes():
    eventos = []

    # --- Assiduidade (verde) ---
    try:
        conn = sqlite3.connect('assiduidade_petizes.db')
        c = conn.cursor()
        c.execute("SELECT DISTINCT data FROM registos")
        datas_assiduidade = [linha[0] for linha in c.fetchall()]
        conn.close()

        for data in datas_assiduidade:
            eventos.append({
                'title': 'Assiduidade',
                'start': data,
                'color': 'green',
                'url': url_for('detalhes_assiduidade_data', data=data)
            })
    except Exception as e:
        print("Erro ao carregar assiduidade:", e)

    # --- Treinos (azul) ---
    try:
        conn = sqlite3.connect('treinos_petizes.db')
        c = conn.cursor()
        c.execute("SELECT numero, data FROM treinos")
        treinos = c.fetchall()
        conn.close()

        for treino in treinos:
            eventos.append({
                'title': f'Treino {treino[0]}',
                'start': treino[1],
                'color': 'blue',
                'url': url_for('imprimir_treino_petizes', numero=treino[0])
            })
    except Exception as e:
        print("Erro ao carregar treinos:", e)

    # --- Eventos (vermelho) ---
    try:
        conn = sqlite3.connect('eventos_petizes.db')
        c = conn.cursor()
        c.execute("SELECT id, data FROM eventos")
        eventos_db = c.fetchall()
        conn.close()

        for ev in eventos_db:
            eventos.append({
                'title': 'Jogo',
                'start': ev[1],
                'color': 'red',
                'textColor': 'white',
                'url': url_for('detalhes_evento_petizes', evento_id=ev[0])
            })
    except Exception as e:
        print("Erro ao carregar eventos:", e)

    return render_template("calendario_assiduidade_petizes.html", datas_json=json.dumps(eventos))



@app.route('/petizes/calendario/<data>')
def detalhes_assiduidade_data(data):
    # Conecta à base de dados de assiduidade
    conn_a = sqlite3.connect('assiduidade_petizes.db')
    c_a = conn_a.cursor()
    c_a.execute("SELECT jogador_id, estado FROM registos WHERE data = ?", (data,))
    registos = c_a.fetchall()
    conn_a.close()

    # Conecta à base de dados dos jogadores
    conn_j = sqlite3.connect('jogadores_petizes.db')
    c_j = conn_j.cursor()

    resultados = []
    for jogador_id, estado in registos:
        c_j.execute("SELECT nome FROM jogadores WHERE id = ?", (jogador_id,))
        jogador = c_j.fetchone()
        nome = jogador[0] if jogador else "Desconhecido"
        resultados.append((nome, estado))
    
    conn_j.close()

    return render_template('detalhes_assiduidade_petizes.html', data=data, resultados=resultados)



@app.route('/petizes/assiduidade/detalhes/<data>')
def detalhes_assiduidade_petizes(data):
    # Liga à base de assiduidade
    conn_assid = sqlite3.connect('assiduidade_petizes.db')
    c_assid = conn_assid.cursor()
    c_assid.execute("SELECT jogador_id, estado FROM registos WHERE data = ?", (data,))
    registos = c_assid.fetchall()
    conn_assid.close()

    # Liga à base de jogadores
    conn_jogadores = sqlite3.connect('jogadores_petizes.db')
    c_jogadores = conn_jogadores.cursor()

    resultados = []
    for jogador_id, estado in registos:
        c_jogadores.execute("SELECT nome FROM jogadores WHERE id = ?", (jogador_id,))
        jogador = c_jogadores.fetchone()
        if jogador:
            resultados.append((jogador[0], estado))

    conn_jogadores.close()

    # Gera HTML com as cores por estado
    html = f"<h3>Assiduidade em {data}</h3>"
    html += "<table><tr><th>Jogador</th><th>Estado</th></tr>"
    for nome, estado in resultados:
        if estado == "Presente":
            classe = "estado-presente"
        elif estado == "Falta Justificada":
            classe = "estado-justificada"
        else:
            classe = "estado-injustificada"
        
        html += f"<tr><td>{nome}</td><td class='{classe}'>{estado}</td></tr>"
    html += "</table>"

    return html


@app.route('/petizes/planeamento')
def planeamento_petizes():
    return render_template('planeamento_petizes.html')



@app.route('/petizes/planeamento/criar_treino', methods=['GET', 'POST'])
def criar_treino_petizes():
    mensagem = None
    if request.method == 'POST':
        numero = request.form['numero']
        data = request.form['data']
        hora = request.form['hora']
        local = request.form['local']
        objetivos = request.form['objetivos']
        material = request.form['material']

        aquecimento = request.form['aquecimento']
        parte_fundamental = request.form['parte_fundamental']
        retorno_calma = request.form['retorno_calma']

        exercicios = (
            f"Aquecimento:\n{aquecimento}\n\n"
            f"Parte Fundamental:\n{parte_fundamental}\n\n"
            f"Retorno à Calma:\n{retorno_calma}"
        )

        conn = sqlite3.connect('treinos_petizes.db')
        c = conn.cursor()

        c.execute("SELECT * FROM treinos WHERE numero = ? OR (data = ? AND hora = ?)", (numero, data, hora))
        if c.fetchone():
            mensagem = "Já existe um treino com esse número ou nesse dia/hora!"
        else:
            c.execute("INSERT INTO treinos (numero, data, hora, local, objetivos, material, exercicios) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (numero, data, hora, local, objetivos, material, exercicios))
            conn.commit()
            mensagem = "Sessão de Treino guardada com sucesso!"

        conn.close()

    return render_template('criar_treino_petizes.html', mensagem=mensagem)

@app.route('/petizes/lista_treinos')
def lista_treinos_petizes():
    conn = sqlite3.connect('treinos_petizes.db')
    c = conn.cursor()
    c.execute("SELECT numero, data, hora, local, objetivos, material, exercicios FROM treinos ORDER BY numero")
    treinos = c.fetchall()
    conn.close()
    return render_template('lista_treinos_petizes.html', treinos=treinos)

@app.route('/petizes/imprimir_treino/<int:numero>')
def imprimir_treino_petizes(numero):
    conn = sqlite3.connect('treinos_petizes.db')
    c = conn.cursor()
    c.execute("SELECT numero, data, hora, local, objetivos, material, exercicios FROM treinos WHERE numero = ?", (numero,))
    treino = c.fetchone()
    conn.close()

    if not treino:
        return "Treino não encontrado", 404

    try:
        partes = treino[6].split("Parte Fundamental:")
        aquecimento = partes[0].replace("Aquecimento:\n", "").strip()
        restante = partes[1].split("Retorno à Calma:")
        parte_fundamental = restante[0].strip()
        retorno_calma = restante[1].strip()
    except Exception as e:
        aquecimento = ""
        parte_fundamental = ""
        retorno_calma = ""

    return render_template('imprimir_treino_petizes.html',
                           treino=treino,
                           aquecimento_texto=aquecimento,
                           parte_fundamental_texto=parte_fundamental,
                           retorno_calma_texto=retorno_calma)


@app.route('/petizes/editar_treino/<int:numero>', methods=['GET', 'POST'])
def editar_treino_petizes(numero):
    conn = sqlite3.connect('treinos_petizes.db')
    c = conn.cursor()

    if request.method == 'POST':
        # Recolher dados do formulário
        data = request.form['data']
        hora = request.form['hora']
        local = request.form['local']
        objetivos = request.form['objetivos']
        material = request.form['material']
        aquecimento = request.form['aquecimento']
        parte_fundamental = request.form['parte_fundamental']
        retorno_calma = request.form['retorno_calma']

        # Juntar os exercícios no mesmo formato usado na criação
        exercicios = f"Aquecimento:\n{aquecimento}\n\nParte Fundamental:\n{parte_fundamental}\n\nRetorno à Calma:\n{retorno_calma}"

        # Atualizar a base de dados
        c.execute('''
            UPDATE treinos
            SET data = ?, hora = ?, local = ?, objetivos = ?, material = ?, exercicios = ?
            WHERE numero = ?
        ''', (data, hora, local, objetivos, material, exercicios, numero))

        conn.commit()
        conn.close()
        return redirect(url_for('lista_treinos_petizes'))

    # Método GET — buscar dados para pré-preencher o formulário
    c.execute("SELECT * FROM treinos WHERE numero = ?", (numero,))
    treino = c.fetchone()
    conn.close()

    if not treino:
        return "Treino não encontrado", 404

    # Separar os blocos do campo exercícios
    try:
        partes = treino[7].split("Parte Fundamental:")
        aquecimento = partes[0].replace("Aquecimento:\n", "").strip()
        restante = partes[1].split("Retorno à Calma:")
        parte_fundamental = restante[0].strip()
        retorno_calma = restante[1].strip()
    except Exception as e:
        print("Erro ao processar os blocos de exercício:", e)
        aquecimento = ""
        parte_fundamental = ""
        retorno_calma = ""

    return render_template('editar_treino_petizes.html',
                           treino=treino,
                           aquecimento=aquecimento,
                           parte_fundamental=parte_fundamental,
                           retorno_calma=retorno_calma)

@app.route('/petizes/eventos_treinos')
def eventos_treinos_petizes():
    conn = sqlite3.connect('treinos_petizes.db')
    c = conn.cursor()
    c.execute("SELECT numero, data FROM treinos")
    treinos = c.fetchall()
    conn.close()

    eventos = []
    for treino in treinos:
        numero = treino[0]
        data = treino[1]
        eventos.append({
            "title": f"Treino {numero}",
            "start": data,
            "color": "blue"
        })

    return jsonify(eventos)

@app.route('/petizes/criar_evento', methods=['GET', 'POST'])
def criar_evento_petizes():
    sucesso = False

    if request.method == 'POST':
        competicao = request.form['competicao']
        jornada = request.form['jornada']
        data = request.form['data']
        hora = request.form['hora']
        local = request.form['local']

        conn = sqlite3.connect('eventos_petizes.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS eventos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competicao TEXT NOT NULL,
                jornada TEXT,
                data TEXT NOT NULL,
                hora TEXT NOT NULL,
                local TEXT NOT NULL
            )
        ''')
        c.execute('''
            INSERT INTO eventos (competicao, jornada, data, hora, local)
            VALUES (?, ?, ?, ?, ?)
        ''', (competicao, jornada, data, hora, local))
        conn.commit()
        conn.close()
        sucesso = True

    return render_template("criar_evento_petizes.html", sucesso=sucesso)

@app.route('/petizes/lista_eventos')
def lista_eventos_petizes():
    conn = sqlite3.connect('eventos_petizes.db')
    c = conn.cursor()
    c.execute("SELECT id, competicao, jornada, data, hora, local FROM eventos ORDER BY data")
    eventos = c.fetchall()
    conn.close()
    return render_template("lista_eventos_petizes.html", eventos=eventos)

@app.route('/petizes/convocatoria/<int:evento_id>', methods=['GET', 'POST'])
def criar_convocatoria(evento_id):
    conn_j = sqlite3.connect('jogadores_petizes.db')
    cj = conn_j.cursor()
    cj.execute("SELECT id, nome FROM jogadores")
    jogadores = cj.fetchall()
    conn_j.close()

    if request.method == 'POST':
        convocados = []
        for jogador in jogadores:
            jogador_id = jogador[0]
            nome = jogador[1]
            estado = request.form.get(f'convocado_{jogador_id}')
            if estado:
                convocados.append((evento_id, jogador_id, nome, 'Convocado' if estado == 'Sim' else 'Não Convocado'))

        conn = sqlite3.connect('eventos_petizes.db')
        c = conn.cursor()

        # Eliminar registros anteriores (caso reenvio)
        c.execute("DELETE FROM convocados WHERE evento_id = ?", (evento_id,))

        # Inserir novos registros
        c.executemany(
            "INSERT INTO convocados (evento_id, jogador_id, nome, estado) VALUES (?, ?, ?, ?)",
            convocados
        )

        conn.commit()
        conn.close()

        flash("Convocatória guardada com sucesso!", "success")
        return redirect(url_for('lista_eventos_petizes'))

    return render_template("criar_convocatoria_petizes.html", jogadores=jogadores, evento_id=evento_id)


@app.route('/petizes/imprimir_convocatoria/<int:evento_id>')
def imprimir_convocatoria_petizes(evento_id):
    conn = sqlite3.connect('eventos_petizes.db')
    c = conn.cursor()

    # Obter dados do evento
    c.execute("SELECT competicao, jornada, data, hora, local FROM eventos WHERE id = ?", (evento_id,))
    evento = c.fetchone()

    # Obter nomes e estado diretamente da tabela convocados
    c.execute("""
        SELECT nome, estado
        FROM convocados
        WHERE evento_id = ?
    """, (evento_id,))
    jogadores = c.fetchall()

    conn.close()

    return render_template("imprimir_convocatoria_petizes.html", evento=evento, jogadores=jogadores)

@app.route('/petizes/assiduidade-json')
def assiduidade_json():
    conn = sqlite3.connect('assiduidade_petizes.db')
    c = conn.cursor()
    c.execute("SELECT DISTINCT data FROM registos")
    datas = [row[0] for row in c.fetchall()]
    conn.close()

    return jsonify([
        {
            "title": "Assiduidade",
            "start": data,
            "url": url_for('detalhes_assiduidade_data', data=data)
        } for data in datas
    ])

@app.route('/petizes/treinos-json')
def treinos_json():
    conn = sqlite3.connect('treinos_petizes.db')
    c = conn.cursor()
    c.execute("SELECT numero, data FROM treinos")
    treinos = c.fetchall()
    conn.close()

    return jsonify([
        {
            "title": f"Treino {numero}",
            "start": data,
            "url": url_for('imprimir_treino_petizes', numero=numero)
        } for numero, data in treinos
    ])


@app.route('/petizes/eventos-json')
def eventos_json():
    conn = sqlite3.connect('eventos_petizes.db')
    c = conn.cursor()
    c.execute("SELECT id, data FROM eventos")
    eventos = c.fetchall()
    conn.close()

    eventos_formatados = []
    for evento in eventos:
        eventos_formatados.append({
            'title': 'Jogo',
            'start': evento[1],
            'color': 'red',
            'textColor': 'white',
            'url': url_for('detalhes_evento', evento_id=evento[0])
        })

    return jsonify(eventos_formatados)

@app.route('/petizes/evento/<int:evento_id>')
def detalhes_evento(evento_id):
    conn = sqlite3.connect('eventos_petizes.db')
    c = conn.cursor()
    c.execute('''
        SELECT competicao, jornada, data, hora, local, "hora e local de concentração"
        FROM eventos WHERE id = ?
    ''', (evento_id,))
    evento = c.fetchone()
    conn.close()

    return render_template("detalhes_evento_petizes.html", evento=evento)

@app.route('/petizes/eliminar_evento/<int:evento_id>', methods=['POST'])
def eliminar_evento_petizes(evento_id):
    conn = sqlite3.connect('eventos_petizes.db')
    c = conn.cursor()
    c.execute("DELETE FROM eventos WHERE id = ?", (evento_id,))
    conn.commit()
    conn.close()
    flash("Evento eliminado com sucesso!", "success")
    return redirect(url_for('lista_eventos_petizes'))

@app.route('/petizes/plantel/gestao')
def gestao_financeira_petizes():
    conn = sqlite3.connect('jogadores_petizes.db')
    c = conn.cursor()
    c.execute("SELECT id, nome FROM jogadores")
    jogadores = c.fetchall()
    conn.close()
    return render_template("gestao_financeira_petizes.html", jogadores=jogadores)

@app.route('/petizes/pagamentos/<int:jogador_id>', methods=['GET', 'POST'])
def pagamentos_jogador_petizes(jogador_id):
    conn = sqlite3.connect('financeiro.db')
    c = conn.cursor()

    # Obter nome do jogador
    c.execute("SELECT nome FROM jogadores WHERE id = ?", (jogador_id,))
    jogador = c.fetchone()
    if not jogador:
        conn.close()
        return "Jogador não encontrado", 404
    nome_jogador = jogador[0]

    # Processar novo pagamento
    if request.method == 'POST':
        data = request.form['data_pagamento']
        valor = float(request.form['valor'])
        descricao = request.form['descricao']
        c.execute("INSERT INTO pagamentos (jogador_id, data, valor, descricao) VALUES (?, ?, ?, ?)",
                  (jogador_id, data, valor, descricao))
        conn.commit()

    # Obter pagamentos existentes
    c.execute("SELECT data, valor, descricao FROM pagamentos WHERE jogador_id = ? ORDER BY data DESC", (jogador_id,))
    pagamentos = c.fetchall()
    conn.close()

    return render_template("pagamentos_jogador.html", nome_jogador=nome_jogador, pagamentos=pagamentos)

@app.route('/petizes/plantel/pagamentos/<int:jogador_id>/<nome>', methods=['GET', 'POST'])
def pagamentos_jogador(jogador_id, nome):
    if request.method == 'POST':
        data = request.form['data_pagamento']
        valor = request.form['valor']
        descricao = request.form['descricao']

        conn = sqlite3.connect('financeiro.db')
        c = conn.cursor()
        c.execute("""
            INSERT INTO pagamentos (jogador_id, nome_jogador, equipa, data_pagamento, valor, descricao)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (jogador_id, nome, 'Petizes', data, float(valor), descricao))
        conn.commit()
        conn.close()

    # Buscar pagamentos, agora incluindo o ID
    conn = sqlite3.connect('financeiro.db')
    c = conn.cursor()
    c.execute("SELECT data_pagamento, valor, descricao, id FROM pagamentos WHERE jogador_id = ?", (jogador_id,))
    pagamentos = c.fetchall()
    conn.close()

    return render_template("pagamentos_jogador.html", nome=nome, pagamentos=pagamentos)


# Eliminar pagamento
@app.route('/petizes/plantel/pagamento/eliminar/<int:pagamento_id>')
def eliminar_pagamento(pagamento_id):
    conn = sqlite3.connect('financeiro.db')
    c = conn.cursor()
    c.execute("DELETE FROM pagamentos WHERE id = ?", (pagamento_id,))
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for('gestao_financeira_petizes'))

# Gerar recibo
@app.route('/petizes/plantel/pagamento/recibo/<int:pagamento_id>')
def emitir_recibo(pagamento_id):
    conn = sqlite3.connect('financeiro.db')
    c = conn.cursor()
    c.execute("""
        SELECT nome_jogador, data_pagamento, valor, descricao
        FROM pagamentos
        WHERE id = ?
    """, (pagamento_id,))
    pagamento = c.fetchone()
    conn.close()

    if not pagamento:
        return "Pagamento não encontrado", 404

    return render_template("recibo_pagamento.html",
                           nome=pagamento[0],
                           data_pagamento=pagamento[1],
                           valor=pagamento[2],
                           descricao=pagamento[3])
@app.route('/petizes/plantel/mapa_pagamento')
def mapa_pagamento_petizes():
    conn = sqlite3.connect('financeiro.db')
    c = conn.cursor()

    # Obter todos os pagamentos
    c.execute('''
SELECT nome_jogador, descricao, valor FROM pagamentos
    ''')
    resultados = c.fetchall()
    conn.close()

    # Códigos de pagamento esperados
    categorias = [
        'Mensalidades',
        'Anuidade',
        'Equipamentos',
        'Exames médicos',
        'Torneios',
        'Outros eventos'
    ]

    resumo = {}
    total_geral = 0.0

    for nome, descricao, valor in resultados:
        if nome not in resumo:
            resumo[nome] = {cat: 0.0 for cat in categorias}
            resumo[nome]['Total'] = 0.0

        if descricao in resumo[nome]:
            resumo[nome][descricao] += valor
        else:
            resumo[nome]['Outros eventos'] += valor

        resumo[nome]['Total'] += valor
        total_geral += valor

    return render_template(
        'mapa_pagamento_petizes.html',
        resumo=resumo,
        categorias=categorias,
        total_geral=total_geral
    )

@app.route('/administracao')
def administracao():
    return render_template('admin.html')
@app.route('/administracao/documentos')
def gestao_documentos():
    equipa_selecionada = request.args.get('equipa', '')

    base_dados_jogadores = {
        'Petizes': 'jogadores_petizes.db',
        'Traquinas': 'jogadores_traquinas.db',
        'Benjamins': 'jogadores_benjamins.db',
        'Infantis': 'jogadores_infantis.db'
    }

    atletas = []

    # Caso uma equipa específica esteja selecionada
    if equipa_selecionada in base_dados_jogadores:
        equipas_a_processar = [equipa_selecionada]
    else:
        # Se estiver vazio ou "todas", percorremos todas
        equipas_a_processar = base_dados_jogadores.keys()

    for equipa in equipas_a_processar:
        db_jogadores = base_dados_jogadores[equipa]

        try:
            conn_j = sqlite3.connect(db_jogadores)
            c_j = conn_j.cursor()
            conn_d = sqlite3.connect('documentos.db')
            c_d = conn_d.cursor()

            c_j.execute("SELECT id, nome FROM jogadores")
            todos_atletas = c_j.fetchall()

            for atleta in todos_atletas:
                atleta_id = atleta[0]
                nome = atleta[1]

                c_d.execute("""
                    SELECT fotografia, mod2_fpf, exame_medico, cc_atleta, cc_ee
                    FROM documentos_atletas
                    WHERE atleta_id = ? AND equipa = ?
                """, (atleta_id, equipa))

                doc = c_d.fetchone()

                if doc:
                    atletas.append((atleta_id, nome, equipa, doc[0], doc[1], doc[2], doc[3], doc[4]))
                else:
                    atletas.append((atleta_id, nome, equipa, '', '', '', '', ''))

            conn_j.close()
            conn_d.close()

        except Exception as e:
            print(f"Erro ao carregar documentos da equipa {equipa}:", e)

    return render_template('gestao_documentos.html', atletas=atletas, equipa_selecionada=equipa_selecionada)



@app.route('/upload_documento', methods=['POST'])
def upload_documento():
    atleta_id = request.form['atleta_id']
    tipo = request.form['tipo_documento']
    equipa = request.form['equipa']
    ficheiro = request.files['ficheiro']

    if ficheiro and tipo in ['fotografia', 'mod2_fpf', 'exame_medico', 'cc_atleta', 'cc_ee']:
        filename = secure_filename(ficheiro.filename)
        caminho = os.path.join(UPLOAD_FOLDER, filename)
        ficheiro.save(caminho)

        conn = sqlite3.connect('documentos.db')
        c = conn.cursor()

        # Verifica se já existe entrada para o atleta
        c.execute("SELECT id FROM documentos_atletas WHERE atleta_id = ? AND equipa = ?", (atleta_id, equipa))
        existente = c.fetchone()

        if existente:
            c.execute(f"UPDATE documentos_atletas SET {tipo} = ? WHERE atleta_id = ? AND equipa = ?", (caminho, atleta_id, equipa))
        else:
            c.execute(f"""
                INSERT INTO documentos_atletas (atleta_id, equipa, {tipo})
                VALUES (?, ?, ?)
            """, (atleta_id, equipa, caminho))

        conn.commit()
        conn.close()

    return redirect('/administracao/documentos')


UPLOAD_FOLDER = 'uploads/documentos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/uploads/documentos/<path:filename>')
def documentos_uploads(filename):
    return send_from_directory('uploads/documentos', filename)

import os
from flask import request, redirect

@app.route('/eliminar_documento', methods=['POST'])
def eliminar_documento():
    atleta_id = request.form['atleta_id']
    tipo_documento = request.form['tipo_documento']
    equipa = request.form['equipa']

    # Conectar à base de dados onde os caminhos estão guardados
    conn = sqlite3.connect('documentos.db')
    c = conn.cursor()

    # Obter o caminho atual do ficheiro
    c.execute(f"SELECT {tipo_documento} FROM documentos_atletas WHERE atleta_id = ? AND equipa = ?", (atleta_id, equipa))
    resultado = c.fetchone()

    if resultado and resultado[0]:
        caminho_ficheiro = resultado[0]
        if os.path.exists(caminho_ficheiro):
            os.remove(caminho_ficheiro)  # Apagar do disco

    # Limpar o campo na base de dados
    c.execute(f"UPDATE documentos_atletas SET {tipo_documento} = NULL WHERE atleta_id = ? AND equipa = ?", (atleta_id, equipa))
    conn.commit()
    conn.close()

    return redirect('/administracao/documentos')

import os

@app.route('/relatorio/documentos_em_falta')
def relatorio_documentos_em_falta():
    equipa_filtro = request.args.get('equipa', '')  # Pode ser 'Petizes', 'Traquinas', etc.
    
    # Conectar à base de dados dos documentos
    conn_doc = sqlite3.connect('documentos.db')
    c_doc = conn_doc.cursor()

    if equipa_filtro:
        c_doc.execute("SELECT * FROM documentos_atletas WHERE equipa = ?", (equipa_filtro,))
    else:
        c_doc.execute("SELECT * FROM documentos_atletas")

    registos = c_doc.fetchall()
    conn_doc.close()

    atletas = []

    for r in registos:
        atleta_id = r[1]
        equipa = r[2]

        # Determinar a base de dados correta para o nome
        if equipa == 'Petizes':
            db_path = 'jogadores_petizes.db'
        elif equipa == 'Traquinas':
            db_path = 'jogadores_traquinas.db'
        elif equipa == 'Benjamins':
            db_path = 'jogadores_benjamins.db'
        elif equipa == 'Infantis':
            db_path = 'jogadores_infantis.db'
        else:
            continue

        try:
            conn_eq = sqlite3.connect(db_path)
            c_eq = conn_eq.cursor()
            c_eq.execute("SELECT nome FROM jogadores WHERE id = ?", (atleta_id,))
            row = c_eq.fetchone()
            nome = row[0] if row else "Desconhecido"
            conn_eq.close()
        except:
            nome = "Desconhecido"

        atleta = {
            'nome': nome,
            'equipa': equipa,
            'fotografia': r[3],
            'mod2_fpf': r[4],
            'exame_medico': r[5],
            'cc_atleta': r[6],
            'cc_ee': r[7]
        }

        atletas.append(atleta)

    return render_template('relatorio_documentos_em_falta.html', atletas=atletas, equipa_selecionada=equipa_filtro)

@app.route('/administracao/financeiro')
def gestao_movimentos_financeiros():
    return render_template('gestao_movimentos_financeiros.html')


@app.route('/financeiros/despesas')
def despesas():
    conn = sqlite3.connect('financeiro.db')
    conn.row_factory = sqlite3.Row  # Permite acesso por nome de coluna (ex: despesa.valor)
    c = conn.cursor()
    c.execute("SELECT id, item, mes, valor, comentario FROM despesas_detalhadas")
    dados = c.fetchall()
    conn.close()

    return render_template("despesas.html", despesas=dados)

@app.route('/despesas/guardar', methods=['POST'])
def guardar_despesa():
    item = request.form['item']
    data = request.form['data']
    valor_str = request.form['valor'].replace("€", "").replace(",", ".").strip()
    comentario = request.form.get('comentario', '')

    try:
        valor = float(valor_str)
    except ValueError:
        flash("Valor inválido.", "erro")
        return redirect('/despesas')

    # Extrai o mês da data (ex: "2025-06-27" → "Junho")
    import datetime
    try:
        dt = datetime.datetime.strptime(data, "%Y-%m-%d")
        mes = dt.strftime("%B").capitalize()
    except:
        mes = ""

    conn = sqlite3.connect('financeiro.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO despesas_detalhadas (item, mes, valor, comentario, data)
        VALUES (?, ?, ?, ?, ?)
    ''', (item, mes, valor, comentario, data))
    conn.commit()
    conn.close()

    flash("Despesa guardada com sucesso!", "sucesso")
    return redirect('/tabela_despesas')

@app.route('/despesas/eliminar/<int:despesa_id>', methods=['POST'])
def eliminar_despesa(despesa_id):
    conn = sqlite3.connect('financeiro.db')
    c = conn.cursor()
    c.execute("DELETE FROM despesas_detalhadas WHERE id = ?", (despesa_id,))
    conn.commit()
    conn.close()

    flash("Despesa eliminada com sucesso.", "sucesso")
    return redirect(request.referrer)

@app.route('/tabela_despesas', methods=['GET'])
def tabela_despesas():
    conn = sqlite3.connect('financeiro.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Obter filtros do formulário
    item_filtro = request.args.get('item', '')
    palavra_chave = request.args.get('palavra', '')
    mes_filtro = request.args.get('mes', '')

    query = "SELECT id, data, item, valor, comentario FROM despesas_detalhadas WHERE 1=1"
    params = []

    if item_filtro:
        query += " AND item = ?"
        params.append(item_filtro)

    if palavra_chave:
        query += " AND comentario LIKE ?"
        params.append(f"%{palavra_chave}%")

    if mes_filtro:
        query += " AND strftime('%m', data) = ?"
        params.append(mes_filtro.zfill(2))

    query += " ORDER BY data DESC"

    c.execute(query, params)
    despesas = c.fetchall()
    conn.close()

    return render_template("tabela_despesas.html", despesas=despesas, item_filtro=item_filtro, palavra_chave=palavra_chave, mes_filtro=mes_filtro)


@app.route('/despesas/relatorio')
def relatorio_despesas():
    conn = sqlite3.connect('financeiro.db')
    c = conn.cursor()
    c.execute("SELECT data, item, valor, comentario FROM despesas_detalhadas ORDER BY data")
    dados = c.fetchall()
    conn.close()

    despesas = [
        {
            'data': row[0],
            'item': row[1],
            'valor': row[2],
            'comentario': row[3]
        }
        for row in dados
    ]

    return render_template('relatorio_despesas.html', despesas=despesas)

@app.route('/receitas/guardar', methods=['POST'])
def guardar_receita():
    origem = request.form['item']
    data = request.form['data']
    valor_str = request.form['valor'].replace("€", "").replace(",", ".").strip()
    comentario = request.form.get('comentario', '')

    try:
        valor = float(valor_str)
    except ValueError:
        flash("Valor inválido.", "erro")
        return redirect('/receitas')

    # Extrair o mês da data (ex: 2025-06-30 → Junho)
    import datetime
    try:
        dt = datetime.datetime.strptime(data, "%Y-%m-%d")
        mes = dt.strftime("%B").capitalize()
    except:
        mes = ""

    conn = sqlite3.connect('financeiro.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO receitas (origem, mes, valor, comentario)
        VALUES (?, ?, ?, ?)
    ''', (origem, mes, valor, comentario))
    conn.commit()
    conn.close()

    flash("Receita guardada com sucesso!", "sucesso")
    return redirect('/tabela_receitas')


@app.route('/receitas')
def pagina_receitas():
    return render_template('receitas.html')

import datetime

@app.route('/tabela_receitas')
def tabela_receitas():
    conn = sqlite3.connect('financeiro.db')
    c = conn.cursor()

    origem_filtro = request.args.get('origem')
    palavra_chave = request.args.get('palavra')
    mes_filtro = request.args.get('mes')

    receitas = []

    # Tradução de mês
    meses_en_to_pt = {
        'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março', 'April': 'Abril',
        'May': 'Maio', 'June': 'Junho', 'July': 'Julho', 'August': 'Agosto',
        'September': 'Setembro', 'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
    }

    # =====================
    # RECEITAS MANUAIS
    # =====================
    if origem_filtro not in ['Petizes', 'Traquinas', 'Benjamins', 'Infantis'] or not origem_filtro:
        query = "SELECT origem, valor, comentario, mes FROM receitas"
        condicoes = []
        valores = []

        if origem_filtro:
            condicoes.append("origem = ?")
            valores.append(origem_filtro)

        if palavra_chave:
            condicoes.append("comentario LIKE ?")
            valores.append(f"%{palavra_chave}%")

        if mes_filtro:
            condicoes.append("mes = ?")
            valores.append(mes_filtro)

        if condicoes:
            query += " WHERE " + " AND ".join(condicoes)

        c.execute(query, valores)
        receitas_base = c.fetchall()

        for origem, valor, comentario, mes in receitas_base:
            mes_pt = meses_en_to_pt.get(mes, mes) if mes else '-'
            receitas.append({
                'origem': origem,
                'valor': valor,
                'comentario': comentario,
                'mes': mes_pt
            })

    # =====================
    # RECEITAS AUTOMÁTICAS (PAGAMENTOS DE ATLETAS)
    # =====================
    if origem_filtro in ['Petizes', 'Traquinas', 'Benjamins', 'Infantis'] or not origem_filtro:
        query_pag = "SELECT equipa, SUM(valor) FROM pagamentos"
        where = []
        params = []

        if origem_filtro in ['Petizes', 'Traquinas', 'Benjamins', 'Infantis']:
            where.append("equipa = ?")
            params.append(origem_filtro)

        if palavra_chave:
            where.append("descricao LIKE ?")
            params.append(f"%{palavra_chave}%")

        if mes_filtro:
            where.append("strftime('%m', data_pagamento) = ?")
            params.append(mes_filtro)

        if where:
            query_pag += " WHERE " + " AND ".join(where)

        query_pag += " GROUP BY equipa"
        c.execute(query_pag, params)
        pagamentos = c.fetchall()

        for equipa, valor in pagamentos:
            receitas.append({
                'origem': equipa,
                'valor': valor,
                'comentario': 'Pagamentos de atletas',
                'mes': '-'
            })

    conn.close()
    total_geral = sum(r['valor'] for r in receitas)

    return render_template('tabela_receitas.html', receitas=receitas, total_geral=total_geral)

@app.route('/totais')
def totais_financeiros():
    conn = sqlite3.connect('financeiro.db')
    c = conn.cursor()

    c.execute("SELECT SUM(valor) FROM receitas")
    total_receitas = c.fetchone()[0] or 0

    c.execute("SELECT SUM(valor) FROM pagamentos")
    total_pagamentos = c.fetchone()[0] or 0
    total_receitas += total_pagamentos

    c.execute("SELECT SUM(valor) FROM despesas")
    total_despesas = c.fetchone()[0] or 0

    conn.close()

    saldo = total_receitas - total_despesas

    return render_template("totais_financeiros.html",
                           total_receitas=total_receitas,
                           total_despesas=total_despesas,
                           saldo=saldo)

if __name__ != '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    # Isto é necessário para o gunicorn reconhecer

app = Flask(__name__)

@app.route('/')
def home():
    return "A plataforma está online com sucesso!"