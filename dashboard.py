import json
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Dashboard:
    def __init__(self, arquivo, janela):
        self.ler_json(arquivo)
        self.numero = 0

    def ler_json(self, arquivo):
        with open(f'{arquivo}', 'r') as f:
            self.dados = json.load(f)
    
    def selecionar_produto(self, numero):
        self.numero = numero

    def plotar_grafico(self, categoria):
        if self.dados[f'Produto {self.numero}'][f'{categoria}']['Lucro'] >= 0:
            lucro_preju = 'Lucro'
        
        else:
            lucro_preju = 'Prejuízo'
        
        frete = self.dados[f'Produto {self.numero}'][f'{categoria}']['Frete'] 
        comis = self.dados[f'Produto {self.numero}'][f'{categoria}']['Frete'] 
        frete = self.dados[f'Produto {self.numero}'][f'{categoria}']['Frete'] 

        
        labels = [f'{lucro_preju}', 'Frete', 'Comissão', 'Imposto']
    
    
teste = Dashboard('produtos_analisados.json')
teste.ler_json()
# teste.estimativa()
