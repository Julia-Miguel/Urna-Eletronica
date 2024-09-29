from bd import BancoDeDados  # Classe que implementa o Singleton

# Criando várias instâncias
instancia1 = BancoDeDados()
instancia2 = BancoDeDados()
instancia3 = BancoDeDados()

# Verificando se todas apontam para o mesmo objeto (comparando o id)
print(id(instancia1))  # Exibe o endereço de memória da instância 1
print(id(instancia2))  # Deve ser igual ao id da instância 1
print(id(instancia3))  # Deve ser igual ao id das instâncias anteriores

# Também pode usar uma verificação explícita
if instancia1 is instancia2 is instancia3:
    print("O padrão Singleton está funcionando corretamente!")
else:
    print("Erro: múltiplas instâncias foram criadas!")
