import tkinter as tk
from tkinter import ttk  # Importar ttk para usar combobox
import winsound
import pygame
from PIL import Image, ImageTk
from bd_proxy import BancoDeDadosProxy
import re  # Importar re para validação de CPF
from bd import BancoDeDados  # Importar a instância Singleton

# Instanciar o banco de dados
bd = BancoDeDados()

cpf_digitado = ""
numero_digitado = "" 
modo_admin = False  # Variável para controlar o modo administrador
interface_atual = None  # Guardar referência para restaurar a interface anterior

# Simulação de um usuário administrador
usuario_admin = {"nome": "Admin", "is_admin": True}

# Simulação de um eleitor comum
usuario_comum = {"nome": "Eleitor", "is_admin": False}

# Instância do proxy usando um usuário específico
bd_proxy = BancoDeDadosProxy(usuario_admin)  # Ou usuario_comum, dependendo do usuário logado

# Funções relacionadas à interface gráfica e lógica


# Funções relacionadas à interface gráfica e lógica
def tocar_som_confirmacao():
    pygame.mixer.init()
    pygame.mixer.music.load("urna.mp3")
    pygame.mixer.music.play()

def tocar_som_erro():
    winsound.PlaySound("erro.wav", winsound.SND_ASYNC)

def confirmar_voto():
    global numero_digitado, cpf_digitado
    candidato = bd_proxy.buscar_candidato(numero_digitado)
    if candidato:
        # Registrar o voto
        bd_proxy.registrar_voto(cpf_digitado, numero_digitado)
        
        tocar_som_confirmacao()
        mostrar_fim()
    else:
        tocar_som_erro()

def mostrar_dados_candidato():
    global numero_digitado
    candidato = bd_proxy.buscar_candidato(numero_digitado)
    if candidato:
        label_numero.config(text=f"Número:")
        label_nome.config(text=f"Nome: {candidato[1]}")
        label_partido.config(text=f"Partido: {candidato[2]}")
        mostrar_imagem(candidato[3])
    else:
        label_nome.config(text="Número inválido")
        label_partido.config(text="")
        mostrar_imagem(None)

def mostrar_imagem(caminho_imagem):
    if caminho_imagem:
        img = Image.open(caminho_imagem)
        img = img.resize((200, 200))
        img_tk = ImageTk.PhotoImage(img)
        label_imagem.config(image=img_tk)
        label_imagem.image = img_tk
    else:
        label_imagem.config(image="")
        label_imagem.image = None

def mostrar_fim():
    for widget in root.winfo_children():
        widget.destroy()
    label_fim = tk.Label(root, text="FIM!", font=("Arial", 90))
    label_fim.pack(expand=True)

def voto_branco():
    global cpf_digitado
    label_nome.config(text="VOTO EM BRANCO")
    label_partido.config(text="")
    mostrar_imagem(None)
    bd_proxy.registrar_voto(cpf_digitado, "branco")  # Registrar voto em branco
    tocar_som_confirmacao()
    mostrar_fim()

def corrigir_voto():
    global numero_digitado
    numero_digitado = ""
    entry_numero.delete(0, tk.END)
    label_nome.config(text="")
    label_partido.config(text="")
    mostrar_imagem(None)

def reiniciar_interface():
    corrigir_voto()

def digitar_numero(event):
    global numero_digitado
    numero_digitado = entry_numero.get()
    if len(numero_digitado) == 2:
        mostrar_dados_candidato()

# Função para validar o CPF
def validar_cpf(cpf):
    return re.fullmatch(r'\d{11}', cpf) is not None

# Função para limitar a entrada de CPF a 11 dígitos
def limitar_cpf(*args):
    cpf = cpf_var.get()
    if len(cpf) > 11:
        cpf_var.set(cpf[:11])

# Função para verificar o CPF e prosseguir com a votação
def verificar_cpf():
    global cpf_digitado
    cpf_digitado = entry_cpf.get()
    
    if not validar_cpf(cpf_digitado):
        label_cpf_feedback.config(text="CPF inválido. Deve conter exatamente 11 números.")
        tocar_som_erro()
        return
    
    if bd_proxy.cpf_ja_votou(cpf_digitado):
        label_cpf_feedback.config(text="CPF já votou. Você não pode votar novamente.")
        tocar_som_erro()
    else:
        mostrar_tela_votacao()  # Vai para a tela de votação

# Função para mostrar a tela de votação após CPF ser verificado
def mostrar_tela_votacao():
    global label_numero, label_nome, label_partido, label_imagem, entry_numero

    for widget in root.winfo_children():
        widget.destroy()

    label_titulo = tk.Label(root, text="PRESIDENTE(A)", font=("Arial", 20))
    label_titulo.pack(pady=(20, 30), padx=(80, 0), anchor="w")

    frame_numero = tk.Frame(root)
    frame_numero.pack(pady=10, anchor="w")

    label_numero = tk.Label(frame_numero, text="Número:", font=("Arial", 16), anchor="w")
    label_numero.pack(side="left", padx=(10, 0))

    entry_numero = tk.Entry(frame_numero, font=("Arial", 16))
    entry_numero.pack(side="left")
    entry_numero.bind("<KeyRelease>", digitar_numero)

    label_nome = tk.Label(root, text="", font=("Arial", 16), anchor="w")
    label_nome.pack(pady=10, anchor="w", padx=(10, 0))

    label_partido = tk.Label(root, text="", font=("Arial", 16), anchor="w")
    label_partido.pack(pady=10, anchor="w", padx=(10, 0))

    label_imagem = tk.Label(root)
    label_imagem.place(x=620, y=10)

    frame_acoes = tk.Frame(root)
    frame_acoes.pack(pady=10)

    botao_confirmar = tk.Button(frame_acoes, text="CONFIRMAR", font=("Arial", 14), bg="green", command=confirmar_voto)
    botao_confirmar.grid(row=0, column=0, padx=5)

    botao_branco = tk.Button(frame_acoes, text="BRANCO", font=("Arial", 14), bg="white", command=voto_branco)
    botao_branco.grid(row=0, column=1, padx=5)

    botao_corrigir = tk.Button(frame_acoes, text="CORRIGIR", font=("Arial", 14), bg="red", command=corrigir_voto)
    botao_corrigir.grid(row=0, column=2, padx=5)

    frame_divisor = tk.Frame(root, height=2, bd=1, relief="sunken")
    frame_divisor.pack(fill="x", pady=10)

    label_instrucoes = tk.Label(root, text="Aperte a tecla:\nVERDE para CONFIRMAR este voto\nVERMELHO para REINICIAR este voto\nBRANCO para votar em branco", font=("Arial", 14), anchor="w", justify="left")
    label_instrucoes.pack(pady=10, anchor="w", padx=20, fill="x")

# Função para mostrar a tela inicial de CPF
def mostrar_tela_cpf():
    global entry_cpf, label_cpf_feedback, cpf_var
    
    for widget in root.winfo_children():
        widget.destroy()

    label_cpf = tk.Label(root, text="Digite seu CPF para votar:", font=("Arial", 16))
    label_cpf.pack(pady=20)

    cpf_var = tk.StringVar()
    cpf_var.trace("w", limitar_cpf)

    entry_cpf = tk.Entry(root, font=("Arial", 16), textvariable=cpf_var)
    entry_cpf.pack(pady=10)

    label_cpf_feedback = tk.Label(root, text="", font=("Arial", 12), fg="red")
    label_cpf_feedback.pack(pady=10)

    botao_verificar_cpf = tk.Button(root, text="Verificar CPF", font=("Arial", 14), command=verificar_cpf)
    botao_verificar_cpf.pack(pady=20)

# Função para alternar entre modo administrador e modo votação
def alternar_modo(event):
    global modo_admin, interface_atual
    if modo_admin:
        mostrar_tela_cpf()
        modo_admin = False
    else:
        salvar_interface_atual()
        mostrar_modo_admin()
        modo_admin = True

# Função para salvar a interface atual
def salvar_interface_atual():
    global interface_atual
    interface_atual = [widget.pack_info() for widget in root.winfo_children()]

# Função para exibir a tela de administrador
def mostrar_modo_admin():
    for widget in root.winfo_children():
        widget.destroy()

    label_admin = tk.Label(root, text="Modo Administrador", font=("Arial", 20))
    label_admin.pack(pady=20)

    # Exibir CPFs e votos
    cpfs_votos = bd_proxy.buscar_cpfs_votos()
    for cpf, nome_candidato in cpfs_votos:
        frame_voto = tk.Frame(root)
        frame_voto.pack(pady=5, fill="x")

        label_voto = tk.Label(frame_voto, text=f"CPF: {cpf} - Votou em: {nome_candidato}", font=("Arial", 14))
        label_voto.pack(side="left", padx=5)

        botao_excluir = tk.Button(frame_voto, text="Excluir", command=lambda cpf=cpf: excluir_voto(cpf))
        botao_excluir.pack(side="right", padx=5)

        botao_editar = tk.Button(frame_voto, text="Editar", command=lambda cpf=cpf: editar_voto(cpf))
        botao_editar.pack(side="right", padx=5)

def excluir_voto(cpf):
    bd_proxy.excluir_voto(cpf)
    mostrar_modo_admin()

def editar_voto(cpf):
    numeros_candidatos = bd_proxy.buscar_numeros_candidatos()
    if not numeros_candidatos:
        tk.messagebox.showerror("Erro", "Nenhum candidato encontrado.")
        return

    janela_editar = tk.Toplevel(root)
    janela_editar.title("Editar Voto")

    label_selecione = tk.Label(janela_editar, text="Selecione o novo número do candidato:")
    label_selecione.pack(pady=10)

    combobox_numeros = ttk.Combobox(janela_editar, values=numeros_candidatos)
    combobox_numeros.pack(pady=10)

    def confirmar_edicao():
        novo_numero_candidato = combobox_numeros.get()
        if novo_numero_candidato:
            sucesso = bd_proxy.editar_voto(cpf, novo_numero_candidato)
            if sucesso:
                janela_editar.destroy()
                mostrar_modo_admin()
            else:
                tk.messagebox.showerror("Erro", "Número do candidato inválido. Tente novamente.")

    botao_confirmar = tk.Button(janela_editar, text="Confirmar", command=confirmar_edicao)
    botao_confirmar.pack(pady=10)

# Inicializar a janela e banco de dados
root = tk.Tk()
root.title("Urna Eletrônica")
root.geometry("840x480")

bd_proxy.bd._inicializar_banco()

root.bind("<Control-b>", lambda event: mostrar_modo_admin())
root.bind("<Control-n>", lambda event: mostrar_tela_cpf())

# Mostrando a tela de CPF primeiro
mostrar_tela_cpf()

root.mainloop()