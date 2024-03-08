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
        self.produtos_encontrados = list()
    
    @property
    def quantidade_produtos(self):
        tamanho_planilha = len(self.planilha['Nome'])
        return tamanho_planilha
        
    def procurar_produto(self, indice_atual):
        self.indice_atual = indice_atual
        self.nome_produto = self.planilha['Nome'][indice_atual].upper()
        nome_formatado = self.nome_produto.replace(' ', '-')
        url = f'https://lista.mercadolivre.com.br/{nome_formatado}'
        self.driver.get(url)
        sleep(3)
        
    def conteudo_pagina(self):
        html = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        try:
            nome_produto = html.findAll('h2', attrs={'class': 'ui-search-item__title'})
            preco_produto = html.findAll('span', attrs={'class': 'andes-money-amount ui-search-price__part ui-search-price__part--medium andes-money-amount--cents-superscript'})
            link_produto = html.findAll('a', attrs={'class': 'ui-search-item__group__element ui-search-link__title-card ui-search-link'})
        except:
            pass
        
        for indice, texto_anuncio  in enumerate(nome_produto):
            texto_anuncio = texto_anuncio.text.upper()
            compatibilidade_do_texto = fuzz.ratio(texto_anuncio, self.nome_produto)
            if compatibilidade_do_texto >= 60:
                preco = self.preco_formatado(preco_produto[indice].text)
                if preco is not None:
                    self.link_produto = link_produto[indice]['href']
                    self.calculadora_lucro(preco)
    
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
    
    def calculadora_lucro(self, preco_de_venda):
        preco_planilha = self.planilha['Preço'][self.indice_atual]
        
        if preco_planilha < 80:
            custo_fixo = 6
            porcentagem_ml = 0.15
            custo_ml = preco_planilha * porcentagem_ml + custo_fixo
            custo_final = preco_planilha + custo_ml 

        else:
            porcentagem_ml = 0.15
            custo_ml = preco_planilha * porcentagem_ml 
            custo_final = preco_planilha + custo_ml
        
        
        lucro_desejado = 1
        preco_minimo_venda = lucro_desejado * custo_final
        
        if preco_de_venda >= preco_minimo_venda:
            self.produtos_encontrados.append([self.nome_produto, preco_planilha, custo_ml, preco_de_venda, self.link_produto])
            
    def gerar_planilha(self):
        df = pd.DataFrame(self.produtos_encontrados, columns=(['Nome', 'Preço de custo', 'Porcentagem ML', 'Preço de venda', 'Link anúncio']))
        df.to_excel(f'analises/analise_ml_{self.nome_planilha}', index=False)


# teste = MercadoLivre('teste.xlsx')
# teste.procurar_produto(0)
# teste.conteudo_pagina()
