import sqlite3

def get_db_connection():
    conn = sqlite3.connect('petshop.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('DROP TABLE IF EXISTS animais')
    conn.execute('DROP TABLE IF EXISTS relatorios')
    conn.execute('DROP TABLE IF EXISTS estoque')
    conn.execute('DROP TABLE IF EXISTS usuarios')
    
    conn.execute('''CREATE TABLE animais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_dono TEXT NOT NULL,
        telefone TEXT NOT NULL,
        email TEXT,
        nome TEXT NOT NULL,
        tipo TEXT NOT NULL,
        idade INTEGER NOT NULL,
        raca TEXT,
        descricao TEXT,
        servicos TEXT
    )''')
    conn.execute('''CREATE TABLE relatorios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT NOT NULL,
        tipo TEXT NOT NULL,
        quantidade INTEGER NOT NULL,
        total TEXT NOT NULL
    )''')
    conn.execute('''CREATE TABLE estoque (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        quantidade INTEGER NOT NULL,
        preco REAL NOT NULL
    )''')
    conn.execute('''CREATE TABLE usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        senha TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

def adicionar_animal(animal):
    conn = get_db_connection()
    conn.execute('INSERT INTO animais (nome_dono, telefone, email, nome, tipo, idade, raca, descricao, servicos) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                 (animal['nome_dono'], animal['telefone'], animal['email'], animal['nome'], 
                  animal['tipo'], animal['idade'], animal['raca'], animal['descricao'], animal['servicos']))
    conn.commit()
    conn.close()

def listar_animais():
    conn = get_db_connection()
    animais = conn.execute('SELECT * FROM animais').fetchall()
    conn.close()
    return [dict(animal) for animal in animais]

def obter_animal(id):
    conn = get_db_connection()
    animal = conn.execute('SELECT * FROM animais WHERE id = ?', (id,)).fetchone()
    conn.close()
    return dict(animal) if animal else None

def editar_animal(id, animal):
    conn = get_db_connection()
    conn.execute('UPDATE animais SET nome_dono = ?, telefone = ?, email = ?, nome = ?, tipo = ?, idade = ?, raca = ?, descricao = ?, servicos = ? WHERE id = ?',
                 (animal['nome_dono'], animal['telefone'], animal['email'], animal['nome'], 
                  animal['tipo'], animal['idade'], animal['raca'], animal['descricao'], animal['servicos'], id))
    conn.commit()
    conn.close()

def excluir_animal(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM animais WHERE id = ?', (id,))
    conn.commit()
    conn.close()

def adicionar_relatorio(relatorio):
    conn = get_db_connection()
    conn.execute('INSERT INTO relatorios (data, tipo, quantidade, total) VALUES (?, ?, ?, ?)',
                 (relatorio['data'], relatorio['tipo'], relatorio['quantidade'], relatorio['total']))
    conn.commit()
    conn.close()

def listar_relatorios():
    conn = get_db_connection()
    relatorios = conn.execute('SELECT * FROM relatorios').fetchall()
    conn.close()
    return [dict(relatorio) for relatorio in relatorios]

def adicionar_produto(produto):
    conn = get_db_connection()
    conn.execute('INSERT INTO estoque (nome, quantidade, preco) VALUES (?, ?, ?)',
                 (produto['nome'], produto['quantidade'], produto['preco']))
    conn.commit()
    conn.close()

def listar_produtos():
    conn = get_db_connection()
    produtos = conn.execute('SELECT * FROM estoque').fetchall()
    conn.close()
    return [dict(produto) for produto in produtos]

def atualizar_produto(id, quantidade):
    conn = get_db_connection()
    conn.execute('UPDATE estoque SET quantidade = ? WHERE id = ?', (quantidade, id))
    conn.commit()
    conn.close()

def excluir_produto(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM estoque WHERE id = ?', (id,))
    conn.commit()
    conn.close()

def adicionar_usuario(usuario):
    conn = get_db_connection()
    conn.execute('INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)',
                 (usuario['nome'], usuario['email'], usuario['senha']))
    conn.commit()
    conn.close()

def obter_usuario_por_email(email):
    conn = get_db_connection()
    usuario = conn.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()
    conn.close()
    return dict(usuario) if usuario else None