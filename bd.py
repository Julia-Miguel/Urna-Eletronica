import sqlite3

# Singleton
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
        CREATE TABLE IF NOT EXISTS vereadores (
            numero TEXT PRIMARY KEY,
            nome TEXT,
            partido TEXT,
            imagem TEXT
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS prefeitos (
            numero TEXT PRIMARY KEY,
            nome TEXT,
            partido TEXT,
            imagem TEXT,
            vice_nome TEXT,
            vice_imagem TEXT
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS votos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cpf TEXT,
            numero_candidato_vereador TEXT,
            numero_candidato_prefeito TEXT,
            FOREIGN KEY (numero_candidato_vereador) REFERENCES vereadores(numero),
            FOREIGN KEY (numero_candidato_prefeito) REFERENCES prefeitos(numero)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS eleitores (
            cpf TEXT PRIMARY KEY
        )
        ''')

        # Inserção inicial de vereadores e prefeitos (somente se ainda não existirem)
        vereadores = [
            ('10000', 'Dustin Henderson', 'ST', 'dustin.jpeg'),
            ('20000', 'Elizabeth Bennet', 'PP', 'elizabeth.jpg'),
            ('30000', 'Jacob Peralta', 'B99', 'peralta.jpg')
        ]

        prefeitos = [
            ('17', 'Gandalf Olórin', 'LOTR', 'gandalf.jpg', 'Frodo Baggins', 'Frodo.png'),
            ('22', 'Gamora Titan', 'GOTG', 'gamora.png', 'Nebula', 'nebula.png'),
            ('25', 'Blair Waldorf', 'GG', 'blair.jpg', 'Serena Van Der Woodsen', 'serena.jpg')
        ]

        for vereador in vereadores:
            cursor.execute('''
            INSERT OR IGNORE INTO vereadores (numero, nome, partido, imagem) 
            VALUES (?, ?, ?, ?)
            ''', vereador)

        for prefeito in prefeitos:
            cursor.execute('''
            INSERT OR IGNORE INTO prefeitos (numero, nome, partido, imagem, vice_nome, vice_imagem) 
            VALUES (?, ?, ?, ?, ?, ?)
            ''', prefeito)

        self._conn.commit()

    def buscar_candidato(self, numero):
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM vereadores WHERE numero = ?", (numero,))
        return cursor.fetchone()

    def buscar_prefeito(self, numero):
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM prefeitos WHERE numero = ?", (numero,))
        return cursor.fetchone()

    def cpf_ja_votou(self, cpf):
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM eleitores WHERE cpf = ?", (cpf,))
        return cursor.fetchone() is not None

    def registrar_voto(self, cpf, numero_candidato_vereador=None, numero_candidato_prefeito=None):
        cursor = self._conn.cursor()

        # Verificar se o CPF já votou
        if self.cpf_ja_votou(cpf):
            print("Erro: CPF já registrou um voto.")
            return "Erro: CPF já registrou um voto."

        # Registrar o CPF na tabela eleitores
        cursor.execute("INSERT INTO eleitores (cpf) VALUES (?)", (cpf,))

        # Registrar o voto na tabela votos
        cursor.execute("INSERT INTO votos (cpf, numero_candidato_vereador, numero_candidato_prefeito) VALUES (?, ?, ?)", (cpf, numero_candidato_vereador, numero_candidato_prefeito))

        self._conn.commit()
        print("Voto registrado com sucesso!")
        return "Voto registrado com sucesso!"

    def buscar_cpfs_votos(self):
        cursor = self._conn.cursor()
        cursor.execute('''
        SELECT votos.cpf, votos.numero_candidato_vereador, votos.numero_candidato_prefeito
        FROM votos
        ''')
        return cursor.fetchall()

    def excluir_voto(self, cpf):
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM votos WHERE cpf = ?", (cpf,))
        cursor.execute("DELETE FROM eleitores WHERE cpf = ?", (cpf,))
        self._conn.commit()

    def editar_voto(self, cpf, novo_numero_candidato_vereador=None, novo_numero_candidato_prefeito=None):
        cursor = self._conn.cursor()

        # Buscar os votos atuais para o CPF
        cursor.execute("SELECT numero_candidato_vereador, numero_candidato_prefeito FROM votos WHERE cpf = ?", (cpf,))
        resultado = cursor.fetchone()
        if not resultado:
            return False

        numero_vereador_atual, numero_prefeito_atual = resultado

        # Atualizar apenas o campo fornecido, preservando o outro
        if novo_numero_candidato_vereador is not None:
            numero_vereador_atual = novo_numero_candidato_vereador
        if novo_numero_candidato_prefeito is not None:
            numero_prefeito_atual = novo_numero_candidato_prefeito

        cursor.execute("""
            UPDATE votos
            SET numero_candidato_vereador = ?, numero_candidato_prefeito = ?
            WHERE cpf = ?
        """, (numero_vereador_atual, numero_prefeito_atual, cpf))
        self._conn.commit()
        return cursor.rowcount > 0

    def buscar_numeros_candidatos(self, tipo):
        cursor = self._conn.cursor()
        if tipo == 'vereador':
            cursor.execute("SELECT numero FROM vereadores")
        elif tipo == 'prefeito':
            cursor.execute("SELECT numero FROM prefeitos")
        else:
            raise ValueError("Tipo de candidato inválido. Use 'vereador' ou 'prefeito'.")
        return [row[0] for row in cursor.fetchall()]