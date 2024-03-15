import os
import threading
from PIL import Image
from amazon import Amazon
import customtkinter as ctk
from mercado_livre import MercadoLivre
from tkinter.filedialog import askopenfilename
import json
import tkinter as tk
from tkinter import ttk
import openpyxl

path_imagem_mercado = os.path.join(os.path.dirname(__file__), 'imagens/mercado-livre-logo.png')
path_imagem_amazon = os.path.join(os.path.dirname(__file__), 'imagens/amazon-logo.png')
path_imagem_excel = os.path.join(os.path.dirname(__file__), 'imagens/excel.png')

class Interface:
    def __init__(self):
        janela = ctk.CTk()
        janela.title('BITHOME')
        
        screen_width = janela.winfo_screenwidth()
        screen_height = janela.winfo_screenheight()
        
        
        janela.geometry(f'{screen_width}x{screen_height}')
        
        janela.tk.call('source','forest-dark.tcl')
        ttk.Style().theme_use('forest-dark')
        style = ttk.Style()
        style.configure("mystyle.Treeview", font=('Roboto', 18), rowheight=40) 
        
        self.tabview = ctk.CTkTabview(janela, width=screen_width, height=screen_height)
        
        self.tabview.pack()
        
        self.analises()
        self.amazon()
        self.mercado_livre()
        
        janela.mainloop()
    
    
    def select_file_mercado(self):
        filepath = askopenfilename()
        filepath = filepath.split('/')
        self.planilha_mercado = filepath[-1]
        self.span_mercado.configure(text=f'{self.planilha_mercado}')
        
    def executar_mercado_livre(self):
        if self.planilha_mercado:
            threading.Thread(target=self.executar_mercado_livre_thread).start()

    def executar_mercado_livre_thread(self):
        if self.planilha_mercado:
            navegador = MercadoLivre(self.planilha_mercado)
            self.quantidade_produtos_mercado.configure(text=f'Quantidade de produtos: {navegador.quantidade_produtos}')
            
            indice_atual = 0
            while True:
                if navegador.quantidade_produtos == indice_atual:
                    break
                
                self.progesso_mercado.configure(text=f'Índice atual: {indice_atual+1}')
                navegador.procurar_produto(indice_atual)
                navegador.conteudo_pagina()
                indice_atual += 1
                
            navegador.gerar_planilha()                   
            
    def executar_amazon(self):
        if self.planilha_mercado:
            threading.Thread(target=self.executar_amazon_thread).start()

    def executar_amazon_thread(self):
        if self.planilha_amazon:
            navegador = Amazon(self.planilha_amazon)
            self.quantidade_produtos_amazon.configure(text=f'Quantidade de produtos: {navegador.quantidade_produtos}')
    
            indice_atual = 0
            while True:
                if navegador.quantidade_produtos == indice_atual:
                    break
                self.progesso_amazon.configure(text=f'Índice atual: {indice_atual+1}')
    
                navegador.procurar_produto(indice_atual)
                navegador.conteudo_pagina()
                indice_atual += 1
                
            navegador.gerar_planilha()
            
    def select_file_amazon(self):
        filepath = askopenfilename()
        filepath = filepath.split('/')
        self.planilha_amazon = filepath[-1]
        self.span_amazon.configure(text=f'{self.planilha_amazon}')
        
    def select_file_json(self):
        filepath = askopenfilename()
        filepath = filepath.split('/')
        self.dados = self.ler_json(filepath[-1])
        self.numero = 0
        self.indicadores_mercado()
        
    def mercado_livre(self):
        # adiciona a aba
        self.tabview.add('Mercado Livre')
        self.tabview.tab('Mercado Livre').configure(fg_color='#F5D244')
        
        # Logo
        image = ctk.CTkImage(light_image = Image.open(path_imagem_mercado), size=(500, 100)) # Logo mercado livre
        imagem = ctk.CTkLabel(self.tabview.tab('Mercado Livre'), image=image, text='')
        imagem.place(x=700, y= 60) 

        ### Parte Web    
        # Excel
        image = ctk.CTkImage(light_image = Image.open(path_imagem_excel), size=(50, 50)) # icone excel
        imagem = ctk.CTkLabel(self.tabview.tab('Mercado Livre'), image=image, text='')
        imagem.place(x=520, y=550 )
        
        # Caixa nome do arquivo
        self.span_mercado = ctk.CTkLabel(self.tabview.tab('Mercado Livre'), text='Nenhum arquivo selecionado', text_color='Black', fg_color='white', corner_radius=10, width=400, height=50, font=('Arial',16))
        self.span_mercado.place(x=100, y=550)

        # Botao para ler nome do arquivo
        botao_arquivo = ctk.CTkButton(self.tabview.tab('Mercado Livre'), text='Selecionar arquivo', command=self.select_file_mercado, corner_radius=10, width=400, height=50, font=('Arial',16))
        botao_arquivo.place(x=100, y= 610)

        # Botao para iniciar web scraping
        botao_play = ctk.CTkButton(self.tabview.tab('Mercado Livre'), text='Executar', command=self.executar_mercado_livre, corner_radius=10, width=400, height=50, fg_color='red', font=('Arial',16))
        botao_play.place(x=100, y= 670)

        # Contador de progresso
        self.progesso_mercado = ctk.CTkLabel(self.tabview.tab('Mercado Livre'), text='Índice atual: 0', text_color='Black', fg_color='white', corner_radius=10, width=50, height=50, font=('Arial',16))
        self.progesso_mercado.place(x=400, y=350)

        # Quantidade de produto
        self.quantidade_produtos_mercado = ctk.CTkLabel(self.tabview.tab('Mercado Livre'), text='Quantidade produtos: 0', text_color='Black', fg_color='white', corner_radius=10, width=50, height=50, font=('Arial',16))
        self.quantidade_produtos_mercado.place(x=100, y=350)  
        
    def analises(self):
        self.tabview.add('Análises')
        self.tabview.tab('Análises').configure(fg_color='#5C5A51')
        
        frame_esquerda = ttk.LabelFrame(self.tabview.tab('Análises'), text='Planilha: ')
        frame_esquerda.pack(side='left', padx=10, pady=10)
        
        frame_planilha =  ttk.LabelFrame(frame_esquerda)
        frame_planilha.pack(side='top')
        
        scroll = ttk.Scrollbar(frame_planilha)  
        scroll.pack(side='right', fill='y')
        
        self.nomes_planilha = ttk.Treeview(frame_planilha, show="headings",height=14, columns=('Nome'), yscrollcommand=scroll.set, style='mystyle.Treeview')
        self.nomes_planilha.pack()
        self.nomes_planilha.column('Nome', width=700)
        
        scroll.config(command=self.nomes_planilha.yview)
        
        
        botao_planilha = ttk.Button(frame_esquerda, text='Selecionar arquivo', command=self.load_files, width=32)
        botao_planilha.pack(side='bottom', pady=2, padx=2)

        
        frame_direita = ttk.LabelFrame(self.tabview.tab('Análises'))
        frame_direita.pack(side='right',padx=10, pady=10)
        
        self.itens = ttk.Treeview(frame_direita, show="headings", columns=('Indicadores', 'Valores'), height=16, style='mystyle.Treeview')
        self.itens.column('Indicadores', width=300)
        self.itens.column('Valores', width=100)
        self.itens.pack()
    
        
        self.nomes_planilha.bind("<<TreeviewSelect>>", self.exibir_informacoes)
        
        
    def load_files(self):
        filepath = askopenfilename()
        workbook = openpyxl.load_workbook(filepath)
        sheet = workbook.active
        self.list_values = list(sheet.values)
        
        self.limpar_treeview('nomes_planilha')
        
        self.nomes_planilha.heading(self.list_values[0][0], text=f'{self.list_values[0][0]}' )
        
        for produto in self.list_values[1:]:
            self.nomes_planilha.insert('', tk.END, values=produto)
            

    def limpar_treeview(self, nome):
        treeview = getattr(self, nome)
        for item in treeview.get_children():
            treeview.delete(item)
            
    def exibir_informacoes(self, event):
        item_selecionado = self.nomes_planilha.focus()
        indice = self.nomes_planilha.item(item_selecionado)
        
        self.limpar_treeview('itens')  # Limpa a Treeview de itens

        for atributo, linha in enumerate(self.list_values[0][1:]):
            self.itens.insert('', tk.END, values=(linha, indice['values'][atributo+1]))
        
        
    def amazon(self):
        self.tabview.add('Amazon')
        self.tabview.tab('Amazon').configure(fg_color='#5C5A51')
        
        # Logo
        image = ctk.CTkImage(light_image = Image.open(path_imagem_amazon), size=(300, 150)) # Logo Amazon
        imagem = ctk.CTkLabel(self.tabview.tab('Amazon'), image=image, text='')
        imagem.place(x=200, y= 60)
        
        # Excel
        image = ctk.CTkImage(light_image = Image.open(path_imagem_excel), size=(50, 50)) # icone excel
        imagem = ctk.CTkLabel(self.tabview.tab('Amazon'), image=image, text='')
        imagem.place(x=570, y=450 )
        
        # Caixa com nome do arquivo
        self.span_amazon = ctk.CTkLabel(self.tabview.tab('Amazon'), text='Nenhum arquivo selecionado', text_color='Black', fg_color='white', corner_radius=10, width=400, height=50, font=('Arial',16))
        self.span_amazon.place(x=150, y=450)

        # Botao para ler nome do arquivo
        botao_arquivo = ctk.CTkButton(self.tabview.tab('Amazon'), text='Selecionar arquivo', command=self.select_file_amazon, corner_radius=10, width=400, height=50, font=('Arial',16))
        botao_arquivo.place(x=150, y= 510)

        # botao para iniciar web scraping
        botao_play = ctk.CTkButton(self.tabview.tab('Amazon'), text='Executar', command=self.executar_amazon, corner_radius=10, width=400, height=50, fg_color='red', font=('Arial',16))
        botao_play.place(x=150, y= 570)

        # Contador de progresso
        self.progesso_amazon = ctk.CTkLabel(self.tabview.tab('Amazon'), text='Índice atual: 0', text_color='Black', fg_color='white', corner_radius=10, width=50, height=50, font=('Arial',16))
        self.progesso_amazon.place(x=400, y=250)

        # quantidade de produtos
        self.quantidade_produtos_amazon = ctk.CTkLabel(self.tabview.tab('Amazon'), text='Quantidade produtos: 0', text_color='Black', fg_color='white', corner_radius=10, width=50, height=50, font=('Arial',16))
        self.quantidade_produtos_amazon.place(x=150, y=250)
    
    
    def ler_json(self, nome):
        with open(f'json/{nome}', 'r') as f:
            return json.load(f)
        
        
teste = Interface()
