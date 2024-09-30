from abc import ABC, abstractmethod
import bd  # Importa o arquivo original de banco de dados

class BancoDeDadosProxy(ABC):
    
    def __init__(self, usuario):
        self.usuario = usuario
        self.bd = bd.BancoDeDados()  # Instância correta da classe que acessa o banco diretamente

    def verificar_permissao(self):
        # Apenas administradores podem realizar certas operações
        if not self.usuario.get("is_admin", False):
            raise PermissionError("Você não tem permissão para realizar esta ação.")

    def registrar_voto(self, cpf, numero_candidato_vereador, numero_candidato_prefeito):
        # Permite o registro de voto
        self.bd.registrar_voto(cpf, numero_candidato_vereador, numero_candidato_prefeito)
        print(f"Voto de {cpf} registrado para o vereador {numero_candidato_vereador} e prefeito {numero_candidato_prefeito}.")

    def buscar_candidato(self, numero):
        # Permite buscar candidatos
        return self.bd.buscar_candidato(numero)
    
    def buscar_prefeito(self, numero):
        # Permite buscar candidatos
        return self.bd.buscar_prefeito(numero)
    
    def buscar_numeros_candidatos(self, tipo):
        # Delegar a chamada para a instância real de BancoDeDados
        return self.bd.buscar_numeros_candidatos(tipo)

    def editar_voto(self, cpf, novo_numero_candidato_vereador=None, novo_numero_candidato_prefeito=None):
        self.verificar_permissao()
        return self.bd.editar_voto(cpf, novo_numero_candidato_vereador, novo_numero_candidato_prefeito)

    def excluir_voto(self, cpf):
        # Somente administradores podem excluir votos
        self.verificar_permissao()
        self.bd.excluir_voto(cpf)
        print(f"Voto do CPF {cpf} excluído com sucesso.")

    def buscar_cpfs_votos(self):
        # Somente administradores podem buscar a lista de votos
        self.verificar_permissao()
        return self.bd.buscar_cpfs_votos()

    def cpf_ja_votou(self, cpf):
        # Verifica se o CPF já votou
        return self.bd.cpf_ja_votou(cpf)
