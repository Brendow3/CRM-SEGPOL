# Funções de database.py
import sqlite3
import os

def get_connection():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect('data/segpol.db')

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        tipo TEXT DEFAULT 'comum'
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        endereco TEXT,
        telefone TEXT,
        email TEXT,
        cpf_cnpj TEXT,
        status TEXT,
        prioridade TEXT,
        historico INTEGER DEFAULT 0
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS historico_atendimentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        data TEXT,
        descricao TEXT,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS visitas_tecnicas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        data TEXT,
        tecnico TEXT,
        descricao TEXT,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id)
        )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS negociacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        data TEXT,
        descricao TEXT,
        status TEXT,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS contratos_servicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        tipo_servico TEXT,
        data_inicio TEXT,
        data_fim TEXT,
        status TEXT,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS chamados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER,
    titulo TEXT,
    descricao TEXT,
    status TEXT,
    prioridade TEXT,
    FOREIGN KEY(cliente_id) REFERENCES clientes(id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS anexos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    nome_arquivo TEXT NOT NULL,
    caminho_arquivo TEXT NOT NULL,
    data_envio TEXT NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS visitas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        data_visita TEXT,
        observacoes TEXT,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
    )''')

    # Usuário admin padrão
    cursor.execute("SELECT * FROM usuarios WHERE email = 'admin'")
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO usuarios (nome, email, senha, tipo)
            VALUES (?, ?, ?, ?)''', ('Administrador', 'admin', 'admin', 'admin'))

    conn.commit()
    conn.close()


