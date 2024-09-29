import sqlite3

 #Singleton
class BancoDeDados:
    _instance = None  # Armazenará a única instância da classe
    _conn = None      # Armazenará a conexão com o banco de dados

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BancoDeDados, cls).__new__(cls)
            cls._instance._conn = sqlite3.connect("urna.db")  # Conecta com o banco de dados
            cls._instance._inicializar_banco()  # Inicializa as tabelas, se necessário
        return cls._instance

    def _inicializar_banco(self):
        cursor = self._conn.cursor()
        
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

        self._conn.commit()

    def buscar_candidato(self, numero):
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM candidatos WHERE numero = ?", (numero,))
        return cursor.fetchone()

    def cpf_ja_votou(self, cpf):
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM eleitores WHERE cpf = ?", (cpf,))
        return cursor.fetchone() is not None

    def registrar_voto(self, cpf, numero_candidato):
        cursor = self._conn.cursor()
        
        # Verificar se o CPF já votou
        if self.cpf_ja_votou(cpf):
            print("Erro: CPF já registrou um voto.")
            return "Erro: CPF já registrou um voto."
        
        # Registrar o CPF na tabela eleitores
        cursor.execute("INSERT INTO eleitores (cpf) VALUES (?)", (cpf,))
        
        # Registrar o voto na tabela votos
        cursor.execute("INSERT INTO votos (cpf, numero_candidato) VALUES (?, ?)", (cpf, numero_candidato))
        
        self._conn.commit()
        print("Voto registrado com sucesso!")
        return "Voto registrado com sucesso!"


    def buscar_cpfs_votos(self):
        cursor = self._conn.cursor()
        cursor.execute('''
        SELECT votos.cpf, candidatos.nome
        FROM votos
        JOIN candidatos ON votos.numero_candidato = candidatos.numero
        ''')
        return cursor.fetchall()

    def excluir_voto(self, cpf):
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM votos WHERE cpf = ?", (cpf,))
        cursor.execute("DELETE FROM eleitores WHERE cpf = ?", (cpf,))
        self._conn.commit()

    def editar_voto(self, cpf, novo_numero_candidato):
        cursor = self._conn.cursor()
        
        # Verificar se o novo número do candidato existe
        cursor.execute("SELECT * FROM candidatos WHERE numero = ?", (novo_numero_candidato,))
        candidato = cursor.fetchone()
        
        if candidato:
            cursor.execute("UPDATE votos SET numero_candidato = ? WHERE cpf = ?", (novo_numero_candidato, cpf))
            self._conn.commit()
            print(f"Voto atualizado para CPF {cpf} com novo número {novo_numero_candidato}")
        else:
            print(f"Erro: Candidato com número {novo_numero_candidato} não encontrado.")
        
        return candidato is not None

    def buscar_numeros_candidatos(self):
        cursor = self._conn.cursor()
        cursor.execute("SELECT numero FROM candidatos")
        return [row[0] for row in cursor.fetchall()]



 