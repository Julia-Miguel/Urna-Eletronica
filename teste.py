import unittest
from bd import BancoDeDados  # Classe que implementa o Singleton

class TestBancoDeDados(unittest.TestCase):
    def setUp(self):
        self.bd = BancoDeDados()

    def test_inicializacao_banco(self):
        candidatos = self.bd.buscar_numeros_candidatos('vereador')
        self.assertGreater(len(candidatos), 0, "Nenhum vereador encontrado no banco de dados.")
        
        prefeitos = self.bd.buscar_numeros_candidatos('prefeito')
        self.assertGreater(len(prefeitos), 0, "Nenhum prefeito encontrado no banco de dados.")

    def test_registrar_voto(self):
        cpf = '12345678900'
        self.bd.registrar_voto(cpf, '10000', '17')
        
        votos = self.bd.buscar_cpfs_votos()
        self.assertIn((cpf, '10000', '17'), votos, "Voto não registrado corretamente.")

    def test_cpf_ja_votou(self):
        cpf = '12345678901'
        self.bd.registrar_voto(cpf, '20000', '22')
        
        # Tentar registrar o mesmo CPF novamente
        resultado = self.bd.registrar_voto(cpf, '30000', '25')
        self.assertEqual(resultado, "Erro: CPF já registrou um voto.", "O sistema não impediu o CPF de votar novamente.")

    def test_excluir_voto(self):
        cpf = '12345678902'
        self.bd.registrar_voto(cpf, '10000', '17')
        
        # Excluir o voto
        self.bd.excluir_voto(cpf)
        self.assertFalse(self.bd.cpf_ja_votou(cpf), "O voto não foi excluído corretamente.")

    def test_editar_voto(self):
        cpf = '12345678903'
        self.bd.registrar_voto(cpf, '20000', '22')
        
        # Editar o voto
        self.bd.editar_voto(cpf, novo_numero_candidato_vereador='30000')
        votos = self.bd.buscar_cpfs_votos()
        self.assertIn((cpf, '30000', '22'), votos, "O voto não foi editado corretamente.")

    def test_buscar_candidato(self):
        candidato = self.bd.buscar_candidato('10000')
        self.assertIsNotNone(candidato, "Candidato não encontrado.")
        self.assertEqual(candidato[1], 'Dustin Henderson', "O nome do candidato não é o esperado.")

    def test_buscar_prefeito(self):
        prefeito = self.bd.buscar_prefeito('17')
        self.assertIsNotNone(prefeito, "Prefeito não encontrado.")
        self.assertEqual(prefeito[1], 'Gandalf Olórin', "O nome do prefeito não é o esperado.")

if __name__ == '__main__':
    unittest.main()








