import re
import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

class BaseMercadoLivre:
    def __init__(self):
        self.servico = Service(ChromeDriverManager().install())
        # self.chrome_option = Options()
        # self.chrome_option.add_extension('arquivos/avantpro.crx')
        self.driver = webdriver.Chrome(service=self.servico)#, options=self.chrome_option)
        self.driver.maximize_window()
        #self.login_avant()

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
        self.nome_planilha = nome_planilha
        self.planilha = pd.read_excel(f'arquivos/{nome_planilha}')
        self.produtos_relevance= {
            'Nome': [],
            'Preço de compra': [],
            'Valor minímo': [],
            'Preço anunciado': [],
            'Imposto': [],
            'Comissão': [],
            'Lucro R$': [],
            'Lucro %': [],
            'Preço desejável': [],
            # 'Vendas': [],
            # 'Estimativa': [],
            # 'Visitas': [],
            # 'Visitas pro venda': [],
        }
        
        self.produtos_cheap = {
            'Nome': [],
            'Preço de compra': [],
            'Valor minímo': [],
            'Preço 0': [],
            'Preço 1': [],
            'Preço 2': [],
            'Imposto': [],
            'Comissão': [],
            'Lucro R$': [],
            'Lucro %': [],
            'Preço desejável': [],
            # 'Vendas': [],
            # 'Estimativa': [],
            # 'Visitas': [],
            # 'Visitas pro venda': [],
        }

    @property
    def quantidade_produtos(self):
        tamanho_planilha = len(self.planilha['Nome'])
        return tamanho_planilha
    
    def produto(self, indice_atual):
        self.indice_atual = indice_atual
        self.nome_produto = self.planilha['Nome'][indice_atual].upper()
        
        self.produtos_cheap['Nome'].append(self.nome_produto)
        self.produtos_cheap['Preço de compra'].append(self.planilha['Preço'][indice_atual])
        
        self.produtos_relevance['Nome'].append(self.nome_produto)
        self.produtos_relevance['Preço de compra'].append(self.planilha['Preço'][indice_atual])
        
    def pesquisar(self, categoria):
        nome_formatado = self.nome_produto.replace(' ', '-')
        
        url = f'https://lista.mercadolivre.com.br/{nome_formatado}_OrderId_PRICE_NoIndex_True'
        if categoria == 'mais relevante':
            url = f'https://lista.mercadolivre.com.br/{nome_formatado}'
        self.driver.get(url)
        sleep(3)
        
        self.conteudo_pesquisa(categoria)
        # self.pagina_produto('Mais relevante')
        self.calculadora_lucro(categoria)
        
    
    def conteudo_pesquisa(self, categoria):
        html = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        try:
            precos = html.findAll('span', attrs={'class': 'andes-money-amount ui-search-price__part ui-search-price__part--medium andes-money-amount--cents-superscript'})
            if categoria == 'mais relevante':
                self.link = html.find('a', attrs={'class': 'ui-search-item__group__element ui-search-link__title-card ui-search-link'})
        except:
            pass
        
        for indice in range(3):
            if precos is not None:
                if categoria == 'mais relevante':
                    preco_formatado = self.preco_formatado(precos[indice].text)
                    self.produtos_relevance['Preço anunciado'].append(preco_formatado)
                    break
                preco_formatado = self.preco_formatado(precos[indice].text)
                self.produtos_cheap[f'Preço {indice}'].append(preco_formatado)
                
    
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
    
    def preco_sem_virgula(self, preco):
        if ',' in preco:
            preco = preco.replace(',', '.')
        return float(preco)
    
    def calculadora_lucro(self, categoria):
        preco_planilha = self.preco_sem_virgula(self.planilha['Preço'][self.indice_atual])
        
        if categoria == 'mais relevante':
            preco_categoria = self.produtos_relevance['Preço anunciado'][self.indice_atual]
        else:
            preco_categoria = self.produtos_cheap['Preço 0'][self.indice_atual]
        
        despesas_fixas = 0
        if preco_categoria < 80:
            despesas_fixas += 6
            
        frete = 0 # Calcular dependendo do peso
        despesas_fixas += frete

        imposto = 0.07
        comissao_ml = 0.15  # mudar dependendo da categoria
        despesas_variaveis = imposto + comissao_ml # mudar dependendo da categoria
        lucro_desejado = 0.05
        
        if categoria == 'mais relevante':
            # preço minímo para obter o lucro desejado
            valor_minimo_venda = (preco_planilha + despesas_fixas) / (1 - despesas_variaveis - lucro_desejado)
            self.produtos_relevance['Valor minímo'].append(round(valor_minimo_venda, 2))
            
            # Lucro com as condições atuais
            lucro_reais  = preco_categoria - (despesas_variaveis * preco_categoria) - despesas_fixas - preco_planilha
            self.produtos_relevance[f'Lucro R$'].append(round(lucro_reais, 2))
            
            lucro_porcentagem  = lucro_reais / preco_categoria * 100
            self.produtos_relevance[f'Lucro %'].append(round(lucro_porcentagem, 2))
            
            # preço que precisa conseguir do fornecedor para obter lucro vendendo com o menor preço anunciado
            preco_fornecedor = preco_categoria - despesas_fixas - (preco_categoria * despesas_variaveis) - (lucro_desejado * preco_categoria)
            self.produtos_relevance[f'Preço desejável'].append(round(preco_fornecedor, 2))
            
            imposto_real = imposto * preco_categoria
            self.produtos_relevance[f'Imposto'].append(round(imposto_real, 2))
            
            comissao_real = comissao_ml * preco_categoria 
            self.produtos_relevance[f'Comissão'].append(round(comissao_real, 2))
            
        else:
            # preço minímo para obter o lucro desejado
            valor_minimo_venda = (preco_planilha + despesas_fixas) / (1 - despesas_variaveis - lucro_desejado)
            self.produtos_cheap['Valor minímo'].append(round(valor_minimo_venda, 2))
            
            # Lucro com as condições atuais
            lucro_reais  = preco_categoria - (despesas_variaveis * preco_categoria) - despesas_fixas - preco_planilha
            self.produtos_cheap[f'Lucro R$'].append(round(lucro_reais, 2))
            
            lucro_porcentagem  = lucro_reais / preco_categoria * 100
            self.produtos_cheap[f'Lucro %'].append(round(lucro_porcentagem, 2))
            
            # preço que precisa conseguir do fornecedor para obter lucro vendendo com o menor preço anunciado
            preco_fornecedor = preco_categoria - despesas_fixas - (preco_categoria * despesas_variaveis) - (lucro_desejado * preco_categoria)
            self.produtos_cheap[f'Preço desejável'].append(round(preco_fornecedor, 2))
            
            imposto_real = imposto * preco_categoria
            self.produtos_cheap[f'Imposto'].append(round(imposto_real, 2))
            
            comissao_real = comissao_ml * preco_categoria 
            self.produtos_cheap[f'Comissão'].append(round(comissao_real, 2))
            
    
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
        df1 = pd.DataFrame(self.produtos_cheap)
        df2 = pd.DataFrame(self.produtos_relevance)
        # Escrever o DataFrame em um arquivo Excel
        with pd.ExcelWriter(f'analise_{self.nome_planilha}') as writer:
            df1.to_excel(writer, sheet_name='TOP3', index=False)
            df2.to_excel(writer, sheet_name='RELEVANTE', index=False)
    

# teste = MercadoLivre('teste.xlsx')
# for c in range(3):
#     teste.produto(c)
#     teste.pesquisar('mais relevante')
#     teste.pesquisar('nada')
# teste.gerar_planilha()