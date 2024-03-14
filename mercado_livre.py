import re
import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from fuzzywuzzy import fuzz
from selenium.webdriver.common.by import By

class BaseMercadoLivre:
    def __init__(self):
        self.servico = Service(ChromeDriverManager().install())
        self.chrome_option = Options()
        self.chrome_option.add_extension('arquivos/avantpro.crx')
        self.driver = webdriver.Chrome(service=self.servico, options=self.chrome_option)
        self.driver.maximize_window()
        self.login_avant()

    def login_avant(self):
        self.driver.get('https://www.mercadolivre.com.br/messi-mini-adidas-cor-orange/p/MLB23998590?pdp_filters=official_store:3154#searchVariation=MLB23998590&position=1&search_layout=grid&type=product&tracking_id=2f89f6c1-1177-475b-9695-9485013512dd')
        while True:
            try:
                botao_link = self.driver.find_element(By.ID, 'openLogin').click()
                break
            except:
                sleep(1)

        email = self.driver.find_element(By.ID, 'userEmail')
        email.send_keys('lucascintra97@gmail.com')
        botao_entrar = self.driver.find_element(By.ID, 'btnSubmitLogin').click()
        sleep(3)

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
    
    def produto(self, indice_atual):
        self.indice_atual = indice_atual
        self.nome_produto = self.planilha['Nome'][indice_atual].upper()
        self.produtos_analisados[self.nome_produto] = dict() # infos de cada produto
        self.produtos_analisados[self.nome_produto]['menor_preco'] = dict()
        self.produtos_analisados[self.nome_produto]['mais_relevante'] = dict()
        
    def mais_relevante(self):
        nome_formatado = self.nome_produto.replace(' ', '-')
        url_mais_relevante = f'https://lista.mercadolivre.com.br/{nome_formatado}'
        self.driver.get(url_mais_relevante)
        sleep(3)
        self.conteudo_pesquisa('mais_relevante')
        self.pagina_produto('mais_relevante')

    def menor_preco(self):  
        nome_formatado = self.nome_produto.replace(' ', '-')
        url_menor_preco = f'https://lista.mercadolivre.com.br/{nome_formatado}_OrderId_PRICE_NoIndex_True'
        self.driver.get(url_menor_preco)
        sleep(3)
        self.conteudo_pesquisa('menor_preco')
        
    
    def conteudo_pesquisa(self, categoria):
        html = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        try:
            precos = html.findAll('span', attrs={'class': 'andes-money-amount ui-search-price__part ui-search-price__part--medium andes-money-amount--cents-superscript'})
            links = html.findAll('a', attrs={'class': 'ui-search-item__group__element ui-search-link__title-card ui-search-link'})
        except:
            pass
        
        for indice in range(3):
            if precos is not None:
                self.produtos_analisados[self.nome_produto][f'{categoria}'][f'Preço {indice}'] = self.preco_formatado(precos[indice].text)
                self.produtos_analisados[self.nome_produto][f'{categoria}'][f'URL {indice}'] = links[indice]['href']
    
    def pagina_produto(self, categoria):
        self.driver.get(self.produtos_analisados[self.nome_produto][f'{categoria}'][f'URL 0'])
        
        while True:
            try:
                botao = self.driver.find_element(By.ID, 'btnMostrarInfos').click()
                sleep(1)
                html = BeautifulSoup(self.driver.page_source, 'html.parser')
                break
            except:
                sleep(1)
       
        # preço do frete
        frete = html.find('div', attrs={'class', 'linha-3'}).text
        frete = frete.replace(' ', '').replace('\n', '').replace('\t', '').replace('\xa0', '')
        
        padrao_frete = r'(R\$+\d+\,\d+)'
        correspondencia = re.search(padrao_frete, frete)
        frete = correspondencia.group().replace('R$', '').replace(',', '.')
        self.produtos_analisados[self.nome_produto][f'{categoria}']['Frete'] = float(frete)
     
        # Pegas o numero de vendas no Mês
        atributos = html.findAll('div', attrs={'class', 'details-card'})
        for atributo in atributos:
            atributo = atributo.text
            atributo = atributo.replace(' ', '').replace('\t', '').replace('\n', '')  
            try:
                padrao_mes = r'\d+\/Mês'
                correspondencia = re.search(padrao_mes, atributo)
                mes = correspondencia.group().replace('/Mês', '')
                self.produtos_analisados[self.nome_produto][f'{categoria}']['Número vendas'] = int(mes)
            except:
                pass
        
    def calculadora_lucro(self):
        preco_planilha = self.planilha['Preço'][self.indice_atual]
        menor_preco_anunciado = self.produtos_analisados[self.nome_produto]['Preço 0']
        
        despesas_fixas = 0
        if menor_preco_anunciado < 80:
            despesas_fixas += 6
            
        frete = 10 # Calcular dependendo do peso
        despesas_fixas += frete

        imposto = 0.07
        comissao_ml = 0.15  # mudar dependendo da categoria
        despesas_variaveis = imposto + comissao_ml # mudar dependendo da categoria
        lucro_desejado = 0.05

        
        # preço minímo para obter o lucro desejado
        valor_minimo_venda = (preco_planilha + despesas_fixas) / (1 - despesas_variaveis - lucro_desejado)
        self.produtos_analisados[self.nome_produto]['Valor minímo venda'] = valor_minimo_venda
        
        # Lucro com as condições atuais
        lucro_condicao_atual  = (menor_preco_anunciado - preco_planilha - despesas_fixas - (menor_preco_anunciado * despesas_variaveis)) / menor_preco_anunciado * 100
        self.produtos_analisados[self.nome_produto]['Lucro atual'] = lucro_condicao_atual
        
        # preço que precisa conseguir do fornecedor para obter lucro vendendo com o menor preço anunciado
        preco_fornecedor_desejavel = menor_preco_anunciado - despesas_fixas - (menor_preco_anunciado * despesas_variaveis) - (lucro_desejado * menor_preco_anunciado)
        self.produtos_analisados[self.nome_produto]['Preço desejável fornecedor'] = preco_fornecedor_desejavel
        
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
        
    
    def gerar_planilha(self):
        pass

teste = MercadoLivre('teste.xlsx')
teste.produto(0)
teste.mais_relevante()
teste.menor_preco()

tarifas = 'https://www.mercadolivre.com.br/landing/costos-venta-producto'