import sqlite3

def inicializar_banco():
    conn = sqlite3.connect("urna.db")
    cursor = conn.cursor()

    # Criar tabelas se elas ainda não existirem
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS candidatos (
        numero TEXT PRIMARY KEY,
        nome TEXT,
        partido TEXT,
        imagem TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS votos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cpf TEXT,
        numero_candidato TEXT,
        FOREIGN KEY (numero_candidato) REFERENCES candidatos(numero)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS eleitores (
        cpf TEXT PRIMARY KEY
    )
    ''')

    candidatos = [
        ('17', 'Gandalf', 'LOTR', 'gandalf.jpg'),
        ('22', 'Gamora', 'GOTG', 'gamora.png'),
        ('25', 'Neymar', 'GOAT', 'ney.png')
    ]
    
    for candidato in candidatos:
        cursor.execute('''
        INSERT OR IGNORE INTO candidatos (numero, nome, partido, imagem) 
        VALUES (?, ?, ?, ?)
        ''', candidato)

    conn.commit()
    conn.close()


def buscar_candidato(numero):
    conn = sqlite3.connect("urna.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidatos WHERE numero = ?", (numero,))
    candidato = cursor.fetchone()
    conn.close()
    return candidato

def cpf_ja_votou(cpf):
    conn = sqlite3.connect("urna.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM eleitores WHERE cpf = ?", (cpf,))
    eleitor = cursor.fetchone()
    conn.close()
    return eleitor is not None

def registrar_voto(cpf, numero_candidato):
    conn = sqlite3.connect("urna.db")
    cursor = conn.cursor()
    
    # Registrar o CPF na tabela eleitores
    cursor.execute("INSERT INTO eleitores (cpf) VALUES (?)", (cpf,))
    
    # Registrar o voto na tabela votos
    cursor.execute("INSERT INTO votos (cpf, numero_candidato) VALUES (?, ?)", (cpf, numero_candidato))
    
    conn.commit()
    conn.close()

def buscar_cpfs_votos():
    conn = sqlite3.connect("urna.db")
    cursor = conn.cursor()
    cursor.execute('''
    SELECT votos.cpf, candidatos.nome
    FROM votos
    JOIN candidatos ON votos.numero_candidato = candidatos.numero
    ''')
    cpfs_votos = cursor.fetchall()
    conn.close()
    return cpfs_votos

def excluir_voto(cpf):
    conn = sqlite3.connect("urna.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM votos WHERE cpf = ?", (cpf,))
    cursor.execute("DELETE FROM eleitores WHERE cpf = ?", (cpf,))
    conn.commit()
    conn.close()

def editar_voto(cpf, novo_numero_candidato):
    conn = sqlite3.connect("urna.db")
    cursor = conn.cursor()
    
    # Verificar se o novo número do candidato existe
    cursor.execute("SELECT * FROM candidatos WHERE numero = ?", (novo_numero_candidato,))
    candidato = cursor.fetchone()
    
    if candidato:
        cursor.execute("UPDATE votos SET numero_candidato = ? WHERE cpf = ?", (novo_numero_candidato, cpf))
        conn.commit()
        print(f"Voto atualizado para CPF {cpf} com novo número {novo_numero_candidato}")
    else:
        print(f"Erro: Candidato com número {novo_numero_candidato} não encontrado.")
    
    conn.close()
    return candidato is not None

def buscar_numeros_candidatos():
    conn = sqlite3.connect("urna.db")
    cursor = conn.cursor()
    cursor.execute("SELECT numero FROM candidatos")
    numeros = [row[0] for row in cursor.fetchall()]
    conn.close()
    return numeros