import tkinter as tk
from tkinter import ttk
import winsound
import pygame
from PIL import Image, ImageTk
from bd_proxy import BancoDeDadosProxy
import re
from bd import BancoDeDados

bd = BancoDeDados()

cpf_digitado = ""
numero_digitado_vereador = ""
numero_digitado_prefeito = ""
modo_admin = False
interface_atual = None

usuario_admin = {"nome": "Admin", "is_admin": True}

usuario_comum = {"nome": "Eleitor", "is_admin": False}

bd_proxy = BancoDeDadosProxy(usuario_admin)  # usuario_admin ou usuario_comum

def tocar_som_confirmacao():
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    pygame.mixer.music.load("urna.mp3")
    pygame.mixer.music.play()

def tocar_som_erro():
    winsound.PlaySound("erro.wav", winsound.SND_ASYNC)

def confirmar_voto(tipo):
    global numero_digitado_vereador, numero_digitado_prefeito, cpf_digitado

    if tipo == 'vereador':
        if numero_digitado_vereador or numero_digitado_vereador == "branco":
            mostrar_tela_votacao('prefeito')
        else:
            tocar_som_erro()
            corrigir_voto()
    elif tipo == 'prefeito':
        if numero_digitado_prefeito or numero_digitado_prefeito == "branco":
            bd_proxy.registrar_voto(cpf_digitado, numero_digitado_vereador, numero_digitado_prefeito)
            tocar_som_confirmacao()
            mostrar_fim()
        else:
            tocar_som_erro()
            corrigir_voto()
        
def mostrar_dados_candidato(tipo):
    global numero_digitado_vereador, numero_digitado_prefeito
    if tipo == 'vereador':
        candidato = bd_proxy.buscar_candidato(numero_digitado_vereador)
        label_tipo.config(text="Vereador(a)")
    else:
        candidato = bd_proxy.buscar_prefeito(numero_digitado_prefeito)
        label_tipo.config(text="Prefeito(a)")
        label_vice.config(text="Vice-Prefeito(a)")

    if candidato:
        label_nome.config(text=f"Nome: {candidato[1]}")
        label_partido.config(text=f"Partido: {candidato[2]}")
        mostrar_imagem(candidato[3])
        if tipo == 'prefeito':
            label_nome_vice.config(text=f"Vice-Prefeito(a): {candidato[4]}")
            mostrar_imagem_vice(candidato[5])
        else:
            label_nome_vice.config(text="")
            mostrar_imagem_vice(None)
    else:
        label_nome.config(text="Número inválido")
        label_partido.config(text="")
        mostrar_imagem(None)
        label_nome_vice.config(text="")
        mostrar_imagem_vice(None)

def mostrar_imagem(caminho_imagem):
    if caminho_imagem:
        img = Image.open(caminho_imagem)
        img = img.resize((150, 150))
        img_tk = ImageTk.PhotoImage(img)
        label_imagem.config(image=img_tk)
        label_imagem.image = img_tk
    else:
        label_imagem.config(image="")
        label_imagem.image = None
        
def mostrar_imagem_vice(caminho_imagem):
    if caminho_imagem:
        img = Image.open(caminho_imagem)
        img = img.resize((120, 120))
        img_tk = ImageTk.PhotoImage(img)
        label_imagem_vice.config(image=img_tk)
        label_imagem_vice.image = img_tk
    else:
        label_imagem_vice.config(image="")
        label_imagem_vice.image = None

def mostrar_fim():
    for widget in root.winfo_children():
        widget.destroy()
    label_fim = tk.Label(root, text="FIM!", font=("Arial", 90))
    label_fim.pack(expand=True)

def voto_branco(tipo):
    global numero_digitado_vereador, numero_digitado_prefeito, cpf_digitado

    if tipo == 'vereador':
        numero_digitado_vereador = "branco"
        mostrar_tela_votacao('prefeito')
    elif tipo == 'prefeito':
        numero_digitado_prefeito = "branco"
        bd_proxy.registrar_voto(cpf_digitado, numero_digitado_vereador, numero_digitado_prefeito)
        mostrar_fim()

    tocar_som_confirmacao()

def corrigir_voto():
    global numero_digitado_vereador, numero_digitado_prefeito
    numero_digitado_vereador = ""
    numero_digitado_prefeito = ""
    entry_numero.delete(0, tk.END)
    label_nome.config(text="")
    label_nome_vice.config(text="")
    label_partido.config(text="")
    label_tipo.config(text="")
    
    mostrar_imagem(None)
    mostrar_imagem_vice(None)

def reiniciar_interface():
    corrigir_voto()

def digitar_numero(event):
    global numero_digitado_vereador, numero_digitado_prefeito
    numero = entry_numero.get()
    
    if entry_tipo == 'Vereador':
        numero_digitado_vereador = numero[:5]
        entry_numero.delete(0, tk.END)
        entry_numero.insert(0, numero_digitado_vereador)
        if len(numero_digitado_vereador) == 5:
            mostrar_dados_candidato('vereador')
    elif entry_tipo == 'Prefeito':
        numero_digitado_prefeito = numero[:2]
        entry_numero.delete(0, tk.END)
        entry_numero.insert(0, numero_digitado_prefeito)
        if len(numero_digitado_prefeito) == 2:
            mostrar_dados_candidato('prefeito')

def validar_cpf(cpf):
    return re.fullmatch(r'\d{11}', cpf) is not None

def limitar_cpf(*args):
    cpf = cpf_var.get()
    if len(cpf) > 11:
        cpf_var.set(cpf[:11])

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

def mostrar_tela_votacao(tipo='vereador'):
    global label_numero, label_nome, label_partido, label_imagem, label_imagem_vice, entry_numero, label_nome_vice, label_tipo, entry_tipo, label_vice
    
    for widget in root.winfo_children():
        widget.destroy()

    if tipo == 'vereador':
        entry_tipo = 'Vereador'
        titulo = "VOTAR EM VEREADOR(A)"
    else:
        entry_tipo = 'Prefeito'
        titulo = "VOTAR EM PREFEITO(A)"

    label_titulo = tk.Label(root, text=titulo, font=("Arial", 20))
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
    label_imagem.place(x=680, y=10)

    label_imagem_vice = tk.Label(root)
    label_imagem_vice.place(x=700, y=200)

    label_nome_vice = tk.Label(root, text="", font=("Arial", 14), anchor="w")
    label_nome_vice.pack(pady=(10, 0), anchor="w", padx=(10, 0))

    label_tipo = tk.Label(root, text="", font=("Arial", 12))
    label_tipo.place(x=718, y=170)
    
    label_vice = tk.Label(root, text="", font=("Arial", 12))
    label_vice.place(x=705, y=325)

    frame_acoes = tk.Frame(root)
    frame_acoes.pack(pady=10, anchor="w")

    botao_confirmar = tk.Button(frame_acoes, text="CONFIRMAR", font=("Arial", 12), bg="green", command=lambda: confirmar_voto(entry_tipo.lower()))
    botao_confirmar.pack(side="left", padx=(40, 0))

    botao_branco = tk.Button(frame_acoes, text="BRANCO", font=("Arial", 12), bg="white", command=lambda: voto_branco(entry_tipo.lower()))
    botao_branco.pack(side="left", padx=5)

    botao_corrigir = tk.Button(frame_acoes, text="CORRIGIR", font=("Arial", 12), bg="red", command=corrigir_voto)
    botao_corrigir.pack(side="left", padx=5)

    label_instrucoes = tk.Label(root, text="Aperte a tecla:\nVERDE para CONFIRMAR este voto\nVERMELHO para REINICIAR este voto\nBRANCO para votar em branco", font=("Arial", 14), anchor="w", justify="left")
    label_instrucoes.pack(pady=10, anchor="w", padx=20, fill="x", side="bottom")
    
    frame_divisor = tk.Frame(root, height=2, bd=1, relief="sunken")
    frame_divisor.pack(fill="x", side="bottom")

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

def alternar_modo(event):
    global modo_admin, interface_atual
    if modo_admin:
        mostrar_tela_cpf()
        modo_admin = False
    else:
        salvar_interface_atual()
        mostrar_modo_admin()
        modo_admin = True

def salvar_interface_atual():
    global interface_atual
    interface_atual = [widget.pack_info() for widget in root.winfo_children()]

def mostrar_modo_admin():
    for widget in root.winfo_children():
        widget.destroy()

    label_admin = tk.Label(root, text="Modo Administrador", font=("Arial", 20))
    label_admin.pack(pady=20)

    cpfs_votos = bd_proxy.buscar_cpfs_votos()
    for cpf, nome_vereador, nome_prefeito in cpfs_votos:
        frame_voto = tk.Frame(root)
        frame_voto.pack(pady=5, fill="x")

        label_voto = tk.Label(frame_voto, text=f"CPF: {cpf} - Votou em: {nome_vereador} | {nome_prefeito}", font=("Arial", 14))
        label_voto.pack(side="left", padx=5)

        botao_excluir = tk.Button(frame_voto, text="Excluir", command=lambda cpf=cpf: excluir_voto(cpf))
        botao_excluir.pack(side="right", padx=5)

        botao_editar_prefeito = tk.Button(frame_voto, text="Editar prefeito", command=lambda cpf=cpf: editar_voto(cpf, 'prefeito'))
        botao_editar_prefeito.pack(side="right", padx=5)

        botao_editar_vereador = tk.Button(frame_voto, text="Editar vereador", command=lambda cpf=cpf: editar_voto(cpf, 'vereador'))
        botao_editar_vereador.pack(side="right", padx=5)

def excluir_voto(cpf):
    bd_proxy.excluir_voto(cpf)
    mostrar_modo_admin()

def editar_voto(cpf, tipo):
    numeros_candidatos = bd_proxy.buscar_numeros_candidatos(tipo)
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
            if tipo == 'vereador':
                sucesso = bd_proxy.editar_voto(cpf, novo_numero_candidato_vereador=novo_numero_candidato)
            else:
                sucesso = bd_proxy.editar_voto(cpf, novo_numero_candidato_prefeito=novo_numero_candidato)
            if sucesso:
                janela_editar.destroy()
                mostrar_modo_admin()
            else:
                tk.messagebox.showerror("Erro", "Número do candidato inválido. Tente novamente.")

    botao_confirmar = tk.Button(janela_editar, text="Confirmar", command=confirmar_edicao)
    botao_confirmar.pack(pady=10)

root = tk.Tk()
root.title("Urna Eletrônica")
root.geometry("840x480")

bd_proxy.bd._inicializar_banco()

root.bind("<Control-b>", lambda event: mostrar_modo_admin())
root.bind("<Control-n>", lambda event: mostrar_tela_cpf())

mostrar_tela_cpf()

root.mainloop()