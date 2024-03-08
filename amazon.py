import re
import pandas as pd
from time import sleep
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup
from selenium import webdriver
from amazoncaptcha import AmazonCaptcha
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class BaseAmazon:
    def __init__(self):
        self.servico = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.servico)
        self.driver.maximize_window()
        self.validar_captcha()
        
    def validar_captcha(self):
        self.driver.get('https://www.amazon.com.br/errors/validateCaptcha')
        link = self.driver.find_element(By.XPATH, "//div[@class = 'a-row a-text-center']//img").get_attribute('src')
        captcha = AmazonCaptcha.fromlink(link)
        captcha_value = AmazonCaptcha.solve(captcha)
        input_field = self.driver.find_element(By.ID, "captchacharacters").send_keys(captcha_value)
        button = self.driver.find_element(By.CLASS_NAME, "a-button-text").click()

class Amazon(BaseAmazon):
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
        sleep(3)
        self.indice_atual = indice_atual
        self.nome_produto = self.planilha['Nome'][indice_atual].upper()
        nome_formatado = self.nome_produto.replace(' ', '+')
        url = f'https://www.amazon.com.br/s?k={nome_formatado}'
        self.driver.get(url)
        
    def conteudo_pagina(self):
        html = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        try:
            produtos = html.findAll('div', attrs={'class': 'a-section a-spacing-small puis-padding-left-small puis-padding-right-small'})

            if produtos is not None:
                    for produto in produtos:
                        texto_anuncio = produto.find('div', attrs={'class': 'a-section a-spacing-none a-spacing-top-small s-title-instructions-style'}).text.upper()
                        compatibilidade_do_texto = fuzz.ratio(texto_anuncio, self.nome_produto)
                        
                        if compatibilidade_do_texto >= 60:
                            preco_anuncio = produto.find('span', attrs={'class': 'a-offscreen'}).text
                            if preco_anuncio is not None:
                                self.preco_venda = self.preco_formatado(preco_anuncio)
                                self.link_produto = produto.find('a', attrs={'class': 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})['href']
                                self.link_produto = 'https://www.amazon.com.br/' + self.link_produto
                                
                                self.calculadora_lucro()
                            
        except:
            pass
                    
                    
    def preco_formatado(self, preco_desformatado):
        preco_desformatado = preco_desformatado.replace('R$\xa0','')
        
        if '.' in preco_desformatado:
            preco_desformatado = preco_desformatado.replace('.', '')
            
        if ',' in preco_desformatado:
            preco = preco_desformatado.replace(',', '.')
            
        return float(preco) 
    
    def calculadora_lucro(self):
        preco_planilha = self.planilha['Preço'][self.indice_atual]
        
        custo_fixo = 5
        porcentagem_amazon = 0.1
        custo_amazon = preco_planilha * porcentagem_amazon + custo_fixo
        custo_final = preco_planilha + custo_amazon 

        
        lucro_desejado = 1
        preco_minimo_venda = lucro_desejado * custo_final
        
        if self.preco_venda >= preco_minimo_venda:
            self.produtos_encontrados.append([self.nome_produto, preco_planilha, custo_amazon, self.preco_venda, self.link_produto])
            
    def gerar_planilha(self):
        df = pd.DataFrame(self.produtos_encontrados, columns=(['Nome', 'Preço de custo', 'Porcentagem Amazon', 'Preço de venda', 'Link anúncio']))
        df.to_excel(f'analises/analise_amazon_{self.nome_planilha}', index=False)


# teste = Amazon('teste.xlsx')
# for c in range(2):
#     teste.procurar_produto(c)
#     teste.conteudo_pagina()
# teste.conteudo_pagina()
