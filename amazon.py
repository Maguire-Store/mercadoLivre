import re
import pandas as pd
from time import sleep
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup
from selenium import webdriver
from fuzzywuzzy import fuzz
from amazoncaptcha import AmazonCaptcha
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

VERTICAL = 'a-section a-spacing-small puis-padding-left-small puis-padding-right-small' 
HORIZONTAL = 'sg-col sg-col-4-of-12 sg-col-8-of-16 sg-col-12-of-20 sg-col-12-of-24 s-list-col-right'
TITULO_CARD = 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'
DOGS = "Sorry! Something went wrong on our end. Please go back and try again or go to Amazon's home page."

class BaseAmazon:
    def __init__(self):
        # Cria o navegador
        servico = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=servico)
        self.driver.maximize_window()
        self.validar_captcha()
        
    def validar_captcha(self):
        self.driver.get('https://www.amazon.com.br/errors/validateCaptcha')
        link = self.driver.find_element(By.XPATH, "//div[@class = 'a-row a-text-center']//img").get_attribute('src')
        captcha = AmazonCaptcha.fromlink(link)
        captcha_value = AmazonCaptcha.solve(captcha)
        input_field = self.driver.find_element(By.ID, "captchacharacters").send_keys(captcha_value)
        button = self.driver.find_element(By.CLASS_NAME, "a-button-text").click()

    def stop_dogs(self):
        # Parar os dogs
        error = BeautifulSoup(self.driver.page_source, 'html.parser')
        error = error.find('img', attrs={'alt': DOGS})
        
        contador = 0
        if error is not None:
            while True:
                sleep(60) # Esperar 60 segundos
                contador += 1 # Tentar 5 vezes a pagina e passar pra próxima
                self.driver.refresh() # da reload na pagina
                error = BeautifulSoup(self.driver.page_source, 'html.parser') # verificar o erro 
                error = error.find('img', attrs={'alt': DOGS})
                if error is None or contador == 5: # 
                    break

class Amazon(BaseAmazon):
    def __init__(self, nome_planilha):
        super().__init__()
        self.planilha = self.dados_planilha(nome_planilha)  # lendo os produtos da planilha
        self.tamanho_plan = len(self.planilha['Nome']) # tamanho da planilha
        self.indice_atual = 0 # O ponto de partida onde vai começar a busca
        self.data_frame()
        
    def dados_planilha(self, nome):
        # ler dados da planilha em excel
        self.nome_excel = nome.split('/')[-1].split('.')[0]
        return pd.read_excel('arquivos/' + nome)

    def data_frame(self):
        # Criar DF de produtos relevantes
        self.produtos = pd.DataFrame(columns=['Nome', 'Preço de compra', 'Valor minímo', 
                                              'Preço 1', 'Preço 2', 'Preço 3',
                                              'Comissão', 'Lucro R$', 'Lucro %', 'Preço desejável'])
        # 'Vendas': [],
        # 'Estimativa': [],
        # 'Visitas': [],
        # 'Visitas pro venda': [],

    def gerar_planilha(self):
        # Escrever o DataFrame em um arquivo Excel
            self.produtos.to_excel(f'analises/analise-{self.nome_excel}-amazon.xlsx',index=False)
        
    def preco_formatado(self, preco_desformatado):
        # Tirar os caracteres de da string e transformar para float
        preco_desformatado = preco_desformatado.replace('R$\xa0','')
        # Se o numero for mais de 1000
        preco_desformatado = preco_desformatado.replace('.', '') if '.' in preco_desformatado else preco_desformatado
        # Se a parte decimal está em virgula e nao em ponto
        preco_desformatado = preco_desformatado.replace(',', '.') if ',' in preco_desformatado else preco_desformatado
  
        return float(preco_desformatado) 
    
    def tirar_virgula(self, preco):
        # tirar a virgula e colocar um ponto para transformar em float
        preco = preco.replace(',', '.') if ',' in preco else preco
        return float(preco)
 
    def analise_produto(self, preco):
        # calculadora de lucro do produto
        produto = list() # cria lista para adicionar as caracteristicas do produto
           
        despesas_fixas = 0 
        frete = 0 # Calcular dependendo do peso
        despesas_fixas += frete

        comissao_amaz = 0.11  # mudar dependendo da categoria
        despesas_variaveis =  comissao_amaz 
        lucro_desejado = 0.05 # Lucro que desejo obter no mínimo
        
        # preço minímo para obter o lucro desejado
        valor_minimo_venda = (self.preco_fornecedor + despesas_fixas) / (1 - despesas_variaveis - lucro_desejado)
        
        # Lucro com as condições atuais
        lucro_reais  = preco - (despesas_variaveis * preco) - despesas_fixas - self.preco_fornecedor
        
        # Lucro em porcentagem
        lucro_porcentagem  = lucro_reais / preco * 100
        
        # preço que precisa conseguir do fornecedor para obter lucro vendendo com o menor preço anunciado
        preco_fornecedor = preco - despesas_fixas - (preco * despesas_variaveis) - (lucro_desejado * preco)
        
        # Comissao em reais
        comissao = comissao_amaz * preco
        
        produto.append([self.nome_produto, 
                        self.preco_fornecedor,
                        valor_minimo_venda,
                        self.precos['preco 1'],
                        self.precos['preco 2'],
                        self.precos['preco 3'],
                        comissao,
                        lucro_reais,
                        lucro_porcentagem,
                        preco_fornecedor
                        ])
        # Adiciona o produto analisado ao dataframe
        self.produtos = pd.concat([self.produtos,
                                                pd.DataFrame(produto,columns=['Nome', 'Preço de compra', 'Valor minímo', 
                                                                                'Preço 1', 'Preço 2', 'Preço 3',
                                                                                'Comissão', 'Lucro R$', 
                                                                                'Lucro %', 'Preço desejável'])])
    
    def produtos_vertical(self):
         # Verifica o conteudo da pagina para ver se o produto existe
        html = BeautifulSoup(self.driver.page_source, 'html.parser') # conteudo da pagina

        produtos =  html.find_all('div', attrs={'class': VERTICAL})
        
        for indice in range(3): # Procurar nos cards do site 
            
            titulo = produtos[indice].find('a', attrs={'class': TITULO_CARD}).text.upper() # titulo do anuncio
            
            if titulo is not None: 
                porcentagem = fuzz.ratio(self.nome_produto, titulo)
                if porcentagem > 50: # Caso o texto seja 50% compatível
                    
                    self.precos[f'preco {indice+1}'] = produtos[indice].find('span', attrs={'class': 'a-offscreen'}).text # preco do produto anunciado
                    if self.precos[f'preco {indice+1}'] is not None: # se o preço existir
                        self.precos[f'preco {indice+1}'] = self.preco_formatado(self.precos[f'preco {indice+1}'])
                    else: # se o preço não existir igualar a 0
                        self.precos[f'preco {indice+1}'] = 0.1

                    # url do primeiro anuncio
                    self.url_anuncio = 'https://www.amazon.com.br/' + produtos[indice].find('a', attrs={'class': TITULO_CARD})['href'] if indice == 0 else self.url_anuncio
                    
    def produtos_horizontal(self):
        # Verifica o conteudo da pagina para ver se o produto existe
        html = BeautifulSoup(self.driver.page_source, 'html.parser') # conteudo da pagina

        produtos =  html.find_all('div', attrs={'class': HORIZONTAL})
        
        for indice in range(3): # Procurar nos cards do site 
            
            titulo = produtos[indice].find('a', attrs={'class': TITULO_CARD}).text.upper() # titulo do anuncio
            
            if titulo is not None: 
                porcentagem = fuzz.ratio(self.nome_produto, titulo)
                if porcentagem > 50: # Caso o texto seja 50% compatível
                    
                    self.precos[f'preco {indice+1}'] = produtos[indice].find('span', attrs={'class': 'a-offscreen'}).text # preco do produto anunciado
                    if self.precos[f'preco {indice+1}'] is not None: # se o preço existir
                        self.precos[f'preco {indice+1}'] = self.preco_formatado(self.precos[f'preco {indice+1}'])
                    else: # se o preço não existir igualar a 0
                        self.precos[f'preco {indice+1}'] = 0.1

                    # url do primeiro anuncio
                    self.url_anuncio = 'https://www.amazon.com.br/' + produtos[indice].find('a', attrs={'class': TITULO_CARD})['href'] if indice == 0 else self.url_anuncio

    def conteudo_pagina(self):
        # Buscar as informações no HTML da página
        html = BeautifulSoup(self.driver.page_source, 'html.parser') # conteudo da pagina
        
        try:
            if html.find_all('div', attrs={'class': VERTICAL}): # Verifica se os produtos estão na vertical
                self.produtos_vertical()
                
            if html.find_all('div', attrs={'class': HORIZONTAL}): # Verifica se os produtos estão na horizontal
                self.produtos_horizontal()
        except:
            pass

    def search(self):
        # Buscar o produto na amazon
        url = f'https://www.amazon.com.br/s?k={self.nome_produto}'
        self.driver.get(url)
        sleep(1)     
        
    def produto(self):
        # Caracteristicas do produto atual
        
        while self.indice_atual != self.tamanho_plan: # Enquanto não terminar a lista ele não procura
            self.nome_produto = self.planilha['Nome'][self.indice_atual].upper() # Nome do produto
            self.preco_fornecedor = self.tirar_virgula(str(self.planilha['Preço'][self.indice_atual])) # Preço do fornecedor
            self.precos = {'preco 1': 0,  # TOP 3 PREÇOS 
                           'preco 2': 0,
                           'preco 3': 0}
            
            self.search() # Procurar o produto
            self.stop_dogs() # Parar os cachorros
            self.conteudo_pagina() # pegar o conteudo da página
            self.analise_produto(self.precos['preco 1'])
            self.gerar_planilha() # gera a planilha a cada loop para se travar não perder todo o progresso
            self.indice_atual += 1 # passa para o próximo produto
                      
teste = Amazon('teste.xlsx')
teste.produto()