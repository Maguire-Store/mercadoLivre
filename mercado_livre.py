import re
import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fuzzywuzzy import fuzz

class BaseMercadoLivre:
    def __init__(self):
        self.servico = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.servico)
        self.driver.maximize_window()


class MercadoLivre(BaseMercadoLivre):
    def __init__(self, nome_planilha):
        super().__init__()
        self.nome_planilha = nome_planilha
        self.planilha = pd.read_excel(f'arquivos/{nome_planilha}')
        self.produtos_analisados = dict()
    
    @property
    def quantidade_produtos(self):
        tamanho_planilha = len(self.planilha['Nome'])
        return tamanho_planilha
    
        
    def procurar_produto(self, indice_atual):
        self.indice_atual = indice_atual
        self.nome_produto = self.planilha['Nome'][indice_atual].upper()
        self.produtos_analisados[self.nome_produto] = dict() # infos de cada produto
        
        nome_formatado = self.nome_produto.replace(' ', '-')
        url = f'https://lista.mercadolivre.com.br/{nome_formatado}_OrderId_PRICE_NoIndex_True'
        self.driver.get(url)
        sleep(3)
        
    def conteudo_pagina(self):
        html = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        try:
            precos = html.findAll('span', attrs={'class': 'andes-money-amount ui-search-price__part ui-search-price__part--medium andes-money-amount--cents-superscript'})
            links = html.findAll('a', attrs={'class': 'ui-search-item__group__element ui-search-link__title-card ui-search-link'})
        except:
            pass
        
        for indice in range(3):
            if precos is not None:
                self.produtos_analisados[self.nome_produto][f'Anúncio {indice}'] = dict()
                self.produtos_analisados[self.nome_produto][f'Anúncio {indice}']['Preço anunciado'] = self.preco_formatado(precos[indice].text)
                self.produtos_analisados[self.nome_produto][f'Anúncio {indice}']['URL'] = links[indice]['href']
        
    def preco_formatado(self, preco_desformatado):
        if '.' in preco_desformatado:
            padrao_preco = r'(\d+\.\d+)'
        elif ',' in preco_desformatado:
            padrao_preco = r'(\d+\,\d+)'
        else:
            padrao_preco = r'(\d+)'
        
        try:
            correspondencia = re.search(padrao_preco, preco_desformatado)
            preco = correspondencia.group()
            
        except:
            return None
        
        if '.' in preco:
            preco = preco.replace('.', '')
            
        if ',' in preco:
            preco = preco.replace(',', '.')
            
        return float(preco) 
    
    def calculadora_lucro(self):
        preco_planilha = self.planilha['Preço'][self.indice_atual]
        
        despesas_fixas = 0
        frete = 10 # Calcular dependendo do peso
        if preco_planilha < 80:
            despesas_fixas += 6
            
        despesas_fixas += frete

        imposto = 0.07
        porcentagem_ml = 0.15
        lucro_desejado = 0.2
        
        valor_minimo_venda = (preco_planilha + despesas_fixas) / (1 - porcentagem_ml - lucro_desejado)
        
        menor_preco_anunciado = self.produtos_analisados[self.nome_produto]['Anúncio 0']['Preço anunciado']
        
        lucro_condicao_atual  = (menor_preco_anunciado - preco_planilha - despesas_fixas - (menor_preco_anunciado * porcentagem_ml)) / menor_preco_anunciado * 100
        
        preco_fornecedor_desejavel = menor_preco_anunciado - despesas_fixas - (menor_preco_anunciado * porcentagem_ml) - (lucro_desejado * menor_preco_anunciado)
        
        
        
        
        
    def gerar_planilha(self):
        pass

teste = MercadoLivre('teste.xlsx')
teste.procurar_produto(0)
teste.conteudo_pagina()
teste.calculadora_lucro()

tarifas = 'https://www.mercadolivre.com.br/landing/costos-venta-producto'