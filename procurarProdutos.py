import pandas as pd
from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


servico = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=servico)
driver.maximize_window()

planilha = pd.read_excel('maguire_produtos.xlsx')

tamanho =  len(planilha['Nome'])
indice_atual = 0 

lista_final = pd.DataFrame(columns=['Nome'])

while indice_atual != (tamanho+1):

    produto_nome = planilha['Nome'][indice_atual]
    url_base = f'https://lista.mercadolivre.com.br/{produto_nome}'
    driver.get(url_base )
    sleep(3)
    conteudo_pagina = BeautifulSoup(driver.page_source, 'html.parser')

    produtos = conteudo_pagina.findAll('div', attrs={'class': 'andes-card ui-search-result shops__cardStyles ui-search-result--core andes-card--flat andes-card--padding-16'})

    for produto in produtos:
        nome = produto.find('h2', attrs={'class': 'ui-search-item__title shops__item-title'}).text
        
        if str(produto_nome).lower() in nome.lower():
            lista_temporaria = pd.DataFrame([produto_nome], columns=['Nome'])
            lista_final = pd.concat([lista_final, lista_temporaria], ignore_index=True)
            break

    indice_atual += 1
    lista_final.to_excel('produtos_encontrados.xlsx', index=False)


