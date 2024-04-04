import os
import threading
from PIL import Image
from amazon import Amazon
from mercado_livre import MercadoLivre
from tkinter.filedialog import askopenfilename
import tkinter as tk
from tkinter import ttk
import openpyxl
from tkinter.font import Font

class Interface:
    def __init__(self):
        janela = tk.Tk()
        janela.title('BITHOME')
        janela.attributes("-fullscreen", "True")
        
        janela.tk.call('source','forest-dark.tcl')

        # Set the theme with the theme_use method
        ttk.Style().theme_use('forest-dark')
        style = ttk.Style()
        style.configure("mystyle.Treeview", font=('Roboto', 18), rowheight=40) 

        self.fonte = Font(family='Roboto')
    
        self.master = ttk.Frame(janela)
        self.master.pack()
        
        self.analises()
        
        janela.mainloop()
        
    
    def analises(self):
        frame_esquerda = ttk.LabelFrame(self.master, text='Planilha: ')
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
   
        frame_direita = ttk.LabelFrame(self.master)
        frame_direita.pack(side='right',padx=10, pady=10)
        
        
        self.itens = ttk.Treeview(frame_direita, show="headings", columns=('Indicadores', 'Valores'), height=16, style='mystyle.Treeview')
        self.itens.column('Indicadores', width=300)
        self.itens.column('Valores', width=70)
        self.itens.pack()
    
        
        self.nomes_planilha.bind("<<TreeviewSelect>>", self.exibir_informacoes)
        
        
    def load_files(self):
        filepath = askopenfilename()
        workbook = openpyxl.load_workbook(filepath)
        sheet = workbook.active
        self.list_values = list(sheet.values)
        print(self.list_values)
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
            
            
    
    
teste = Interface()