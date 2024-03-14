import os
import threading
from PIL import Image
from amazon import Amazon
import customtkinter as ctk
from mercado_livre import MercadoLivre
from tkinter.filedialog import askopenfilename

path_imagem_mercado = os.path.join(os.path.dirname(__file__), 'imagens/mercado-livre-logo.png')
path_imagem_amazon = os.path.join(os.path.dirname(__file__), 'imagens/amazon-logo.png')
path_imagem_excel = os.path.join(os.path.dirname(__file__), 'imagens/excel.png')

class Interface:
    def __init__(self):
        janela = ctk.CTk()
        janela.title('BITHOME')
        janela.geometry('1400x900')
        
        self.tabview = ctk.CTkTabview(janela, width=1400, height=900)
        self.tabview.pack()
        
        self.mercado_livre()
        self.amazon()
        
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
        
        
    def mercado_livre(self):
        # adiciona a aba
        self.tabview.add('Mercado Livre')
        self.tabview.tab('Mercado Livre').configure(fg_color='#F5D244')
        
        
        # imagens
        image = ctk.CTkImage(light_image = Image.open(path_imagem_mercado), size=(500, 100)) # Logo mercado livre
        imagem = ctk.CTkLabel(self.tabview.tab('Mercado Livre'), image=image, text='')
        imagem.place(x=410, y= 60) 
        
        image = ctk.CTkImage(light_image = Image.open(path_imagem_excel), size=(50, 50)) # icone excel
        imagem = ctk.CTkLabel(self.tabview.tab('Mercado Livre'), image=image, text='')
        imagem.place(x=570, y=450 )
        
        
        # Caixa de texto variavel
        self.span_mercado = ctk.CTkLabel(
            self.tabview.tab('Mercado Livre'),
            text='Nenhum arquivo selecionado',
            text_color='Black',
            fg_color='white',
            corner_radius=10,
            width=400,
            height=50,
            font=('Arial',16)
            )
        self.span_mercado.place(x=150, y=450)

        
        # Botao para ler nome do arquivo
        botao_arquivo = ctk.CTkButton(
            self.tabview.tab('Mercado Livre'),
            text='Selecionar arquivo',
            command=self.select_file_mercado,
            corner_radius=10,
            width=400,
            height=50,
            font=('Arial',16)
            )
        botao_arquivo.place(x=150, y= 510)
        
        botao_play = ctk.CTkButton(
            self.tabview.tab('Mercado Livre'),
            text='Executar',
            command=self.executar_mercado_livre,
            corner_radius=10,
            width=400,
            height=50,
            fg_color='red',
            font=('Arial',16)
            )
        botao_play.place(x=150, y= 570)

        # Progresso
        self.progesso_mercado = ctk.CTkLabel(
            self.tabview.tab('Mercado Livre'),
            text='Índice atual: 0',
            text_color='Black',
            fg_color='white',
            corner_radius=10,
            width=50,
            height=50,
            font=('Arial',16)
            )
        self.progesso_mercado.place(x=400, y=250)
        
        self.quantidade_produtos_mercado = ctk.CTkLabel(
            self.tabview.tab('Mercado Livre'),
            text='Quantidade produtos: 0',
            text_color='Black',
            fg_color='white',
            corner_radius=10,
            width=50,
            height=50,
            font=('Arial',16)
            )
        self.quantidade_produtos_mercado.place(x=150, y=250)
        

    def amazon(self):
        self.tabview.add('Amazon')
        self.tabview.tab('Amazon').configure(fg_color='#5C5A51')
        
        # imagens
        image = ctk.CTkImage(light_image = Image.open(path_imagem_amazon), size=(300, 150)) # Logo Amazon
        imagem = ctk.CTkLabel(self.tabview.tab('Amazon'), image=image, text='')
        imagem.place(x=200, y= 60)
        
        image = ctk.CTkImage(light_image = Image.open(path_imagem_excel), size=(50, 50)) # icone excel
        imagem = ctk.CTkLabel(self.tabview.tab('Amazon'), image=image, text='')
        imagem.place(x=570, y=450 )
        
        # Caixa de texto variavel
        self.span_amazon = ctk.CTkLabel(
            self.tabview.tab('Amazon'),
            text='Nenhum arquivo selecionado',
            text_color='Black',
            fg_color='white',
            corner_radius=10,
            width=400,
            height=50,
            font=('Arial',16)
            )
        self.span_amazon.place(x=150, y=450)

        
        # Botao para ler nome do arquivo
        botao_arquivo = ctk.CTkButton(
            self.tabview.tab('Amazon'),
            text='Selecionar arquivo',
            command=self.select_file_amazon,
            corner_radius=10,
            width=400,
            height=50,
            font=('Arial',16)
            )
        botao_arquivo.place(x=150, y= 510)
        
        botao_play = ctk.CTkButton(
            self.tabview.tab('Amazon'),
            text='Executar',
            command=self.executar_amazon,
            corner_radius=10,
            width=400,
            height=50,
            fg_color='red',
            font=('Arial',16)
            )
        botao_play.place(x=150, y= 570)

        # Progresso
        self.progesso_amazon = ctk.CTkLabel(
            self.tabview.tab('Amazon'),
            text='Índice atual: 0',
            text_color='Black',
            fg_color='white',
            corner_radius=10,
            width=50,
            height=50,
            font=('Arial',16)
            )
        self.progesso_amazon.place(x=400, y=250)
        
        self.quantidade_produtos_amazon = ctk.CTkLabel(
            self.tabview.tab('Amazon'),
            text='Quantidade produtos: 0',
            text_color='Black',
            fg_color='white',
            corner_radius=10,
            width=50,
            height=50,
            font=('Arial',16)
            )
        self.quantidade_produtos_amazon.place(x=150, y=250)
        
    
teste = Interface()
