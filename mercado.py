import re
import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

CLASS_PRECOS = 'andes-money-amount ui-search-price__part ui-search-price__part--medium andes-money-amount--cents-superscript'
CLASS_URL_PRODUTO = 'ui-search-item__group__element ui-search-link__title-card ui-search-link'

class BaseMercadoLivre:
    def __init__(self):
        servico = Service(ChromeDriverManager().install())
        chrome_option = Options()
        # chrome_option.add_extension('arquivos/extensoes/avantpro.crx')
        self.driver = webdriver.Chrome(service=servico, options=chrome_option)
        self.driver.maximize_window()
        # self.login_avant()

    def login_avant(self):
        self.driver.get('https://www.mercadolivre.com.br/o-mar-de-monstros-serie-percy-jackson-e-os-olimpianos-de-rick-riordan-serie-percy-jackson-e-os-olimpianos-vol-2-editora-intrinseca-ltda-capa-mole-edico-1-em-portugus-2023/p/MLB29915187?pdp_filters=category:MLB437616#searchVariation=MLB29915187&position=3&search_layout=grid&type=product&tracking_id=de296ab6-d29b-45b4-8ff0-cb60689c27d8')

        self.esperar_botao('openLogin')

        email = self.driver.find_element(By.ID, 'userEmail')
        email.send_keys('lucascintra97@gmail.com')
        botao_entrar = self.driver.find_element(By.ID, 'btnSubmitLogin').click()
        sleep(3)

    def esperar_botao(self, nome_botao):
        while True:
            try:
                botao = self.driver.find_element(By.ID, f'{nome_botao}').click()
                sleep(1)
                break
            except:
                sleep(1)

class MercadoLivre(BaseMercadoLivre):
    def __init__(self, nome_planilha):
        super().__init__()
        self.planilha = self.dados_planilha(nome_planilha)
        self.tamanho_plan = len(self.planilha['Nome']) # tamanho da planilha
        self.indice_atual = 0 # O ponto de partida onde vai começar a busca
        self.data_frames()

    def dados_planilha(self, nome):
        # ler dados da planilha em excel
        self.nome_excel = nome.split('/')[-1].split('.')[0]
        return pd.read_excel('arquivos/' + nome)
        
    def data_frames(self):
        # Criar DF de produtos relevantes
        self.relevantes = pd.DataFrame(columns=['Nome', 'Preço de compra', 'Valor minímo', 'Preço anunciado',
                                                'Imposto', 'Comissão', 'Lucro R$', 'Lucro %', 'Preço desejável'])
        # 'Vendas': [],
        # 'Estimativa': [],
        # 'Visitas': [],
        # 'Visitas pro venda': [],
        
        # Criar DF de produtos mais baratos
        self.mais_baratos = pd.DataFrame(columns=['Nome', 'Preço de compra', 'Valor minímo',
                                                  'Preço 1', 'Preço 2', 'Preço 3',
                                                  'Imposto', 'Comissão', 'Lucro R$',
                                                  'Lucro %', 'Preço desejável'])
        # 'Vendas': [],
        # 'Estimativa': [],
        # 'Visitas': [],
        # 'Visitas pro venda': [], 
         
    def gerar_planilha(self):
        df1 = pd.DataFrame(self.mais_baratos)
        df2 = pd.DataFrame(self.relevantes)
        # Escrever o DataFrame em um arquivo Excel
        with pd.ExcelWriter(f'analises/analise-{self.nome_excel}-mercado.xlsx') as writer:
            df1.to_excel(writer, sheet_name='TOP3', index=False)
            df2.to_excel(writer, sheet_name='RELEVANTEs', index=False)
        
    def tirar_virgula(self, preco):
        # tirar a virgula e colocar um ponto para transformar em float
        preco = preco.replace(',', '.') if ',' in preco else preco
        return float(preco)
    
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
    
    def calculadora_lucro(self, preco):        
        # calculadora de lucro do produto
        produto = list() # cria lista para adicionar as caracteristicas do produto
        
        despesas_fixas = 0
        if preco < 80: # se o preço de venda for menor que R$80 eles possuem uma taxa de R$6
            despesas_fixas += 6
            
        frete = 0 # Calcular dependendo do peso
        despesas_fixas += frete

        imposto = 0.07 # Imposto sobre a venda
        comissao_ml = 0.15  # mudar dependendo da categoria
        despesas_variaveis = imposto + comissao_ml 
        lucro_desejado = 0.05 # Lucro que desejo obter no mínimo
        
        # preço minímo para obter o lucro desejado
        valor_minimo_venda = (self.preco_fornecedor + despesas_fixas) / (1 - despesas_variaveis - lucro_desejado)
        
        # Lucro com as condições atuais
        lucro_reais  = preco - (despesas_variaveis * preco) - despesas_fixas - self.preco_fornecedor
        
        # Lucro em porcentagem
        lucro_porcentagem  = lucro_reais / preco * 100
        
        # preço que precisa conseguir do fornecedor para obter lucro vendendo com o menor preço anunciado
        preco_fornecedor = preco - despesas_fixas - (preco * despesas_variaveis) - (lucro_desejado * preco)
        
        # Imposto em reais
        imposto = imposto * preco
        
        # Comissao em reais
        comissao = comissao_ml * preco 
                
        if self.categoria['categoria'] == 'mais relevantes':
            produto.append([self.nome_produto,
                            self.preco_fornecedor,
                            valor_minimo_venda,
                            self.preco,
                            imposto,
                            comissao,
                            lucro_reais,
                            lucro_porcentagem,
                            preco_fornecedor])
            
            self.relevantes = pd.concat([self.relevantes,
                                         pd.DataFrame(produto, columns=['Nome', 'Preço de compra', 'Valor minímo',
                                                                        'Preço anunciado', 'Imposto', 'Comissão',
                                                                        'Lucro R$', 'Lucro %', 'Preço desejável'])])
        
        if self.categoria['categoria'] == 'menores precos':
            produto.append([self.nome_produto,
                            self.preco_fornecedor,
                            valor_minimo_venda,
                            self.precos['preco 1'],
                            self.precos['preco 2'],
                            self.precos['preco 3'],
                            imposto,
                            comissao,
                            lucro_reais,
                            lucro_porcentagem,
                            preco_fornecedor])
            
            self.mais_baratos = pd.concat([self.mais_baratos,
                                         pd.DataFrame(produto, columns=['Nome', 'Preço de compra', 'Valor minímo',
                                                                        'Preço 1', 'Preço 2', 'Preço 3', 
                                                                        'Imposto', 'Comissão', 'Lucro R$',
                                                                        'Lucro %', 'Preço desejável'])])
        
    def conteudo_pesquisa(self):
        # Pega os preços e o link dos produtos 
        html = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        try:
            if self.categoria['categoria'] == 'mais relevantes':
                preco_desformatado = html.find('span', attrs={'class': CLASS_PRECOS})  # primeiro preço que aparece
                self.link = html.find('a', attrs={'class': CLASS_URL_PRODUTO}) # link para analise do avantpro
                self.preco = self.preco_formatado(preco_desformatado.text) # preço mais relevante

            if self.categoria['categoria'] == 'menores precos':
                precos = html.findAll('span', attrs={'class': CLASS_PRECOS}) # todos os preços dos anuncios
                self.link = html.find('a', attrs={'class': CLASS_URL_PRODUTO}) # link para analise do avantpro
                
                for indice in range(3): # Pega os 3 primeiros preços e os formata
                    preco_desformatado = precos[indice]
                    self.precos[f'preco {indice+1}'] = self.preco_formatado(preco_desformatado.text)
        except:
            pass
                
    def search(self):
        # Pesquisa o produto no mercado livre
        nome_formatado = self.nome_produto.replace(' ', '-')
        
        url = f'https://lista.mercadolivre.com.br/{nome_formatado}' + self.categoria['parametro']
        self.driver.get(url)
        sleep(3)   
        
    def executar_mais_baratos(self):
        # Faz os passos para analisar os produtos mais baratos
        self.categoria = {'categoria': 'menores precos',  
                          'parametro' :'_OrderId_PRICE_NoIndex_True'} # parametro para os produtos com menor preço
        
        self.precos = {'preco 1': 0,  # TOP 3 PREÇOS 
                       'preco 2': 0,
                       'preco 3': 0}
        
        self.search() # Pesquisa o produto
        self.conteudo_pesquisa() # Conteudo da página
        self.calculadora_lucro(self.precos['preco 1']) # Calcular margens

    def executar_relevantes(self):
        # Faz os passos para analisar os produtos mais baratos
        self.categoria = {'categoria': 'mais relevantes', 
                          'parametro' :'_NoIndex_True'}# parametro para os produtos mais relevantes
        
        self.preco = 0 
        self.search() # Pesquisa o produto 
        self.conteudo_pesquisa() # Conteudo da página
        self.calculadora_lucro(self.preco) # Calcular margens
        
    def produto(self):
        # Caracteristicas do produto atual
        self.nome_produto = self.planilha['Nome'][self.indice_atual].upper() # Nome do produto
        self.preco_fornecedor = self.tirar_virgula(str(self.planilha['Preço'][self.indice_atual])) # Preço do fornecedor
        
        while self.indice_atual != self.tamanho_plan: # Enquanto não terminar a lista ele não procura
            self.executar_mais_baratos()
            self.executar_relevantes()
            self.gerar_planilha() # gera a planilha a cada loop para se travar não perder todo o progresso
            self.indice_atual += 1 # passa para o próximo produto
    
    
    # def pagina_produto(self, categoria):
    #     self.driver.get(self.link)
    #     self.esperar_botao('btnMostrarInfos')
        
    #     response = BeautifulSoup(self.driver.page_source, 'html.parser')
        
    #     vendas = self.vendas_mes(response)
    #     self.produtos_analisados['Vendas'].append(vendas)
    
    # def vendas_mes(self, html):
    #     atributos = html.findAll('div', attrs={'class', 'details-card'})
    #     for atributo in atributos:
    #         atributo = atributo.text
    #         atributo = atributo.replace(' ', '').replace('\t', '').replace('\n', '')  
    #         try:
    #             padrao_mes = r'\d+\/Mês'
    #             correspondencia = re.search(padrao_mes, atributo)
    #             mes = correspondencia.group().replace('/Mês', '')
    #             return int(mes)
    #         except:
    #             pass
            
    # def visitas(self, html):
    #     pass
            
    # def frete(self, html):
    #     # preço do frete
    #     frete = html.find('div', attrs={'class', 'linha-3'}).text
    #     frete = frete.replace(' ', '').replace('\n', '').replace('\t', '').replace('\xa0', '')
        
    #     padrao_frete = r'(R\$+\d+\,\d+)'
    #     correspondencia = re.search(padrao_frete, frete)
    #     frete = correspondencia.group().replace('R$', '').replace(',', '.')
    #     self.produtos_analisados['Frete'] = float(frete)
    