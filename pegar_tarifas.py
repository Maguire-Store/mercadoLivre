from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

tarifas = 'https://www.mercadolivre.com.br/landing/costos-venta-producto'

servico = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=servico)
driver.maximize_window()
driver.get(tarifas)

lista = list()

html = BeautifulSoup(driver.page_source, 'html.parser')

categorias = html.findAll('li', attrs={'class': 'andes-list__item category-selection-lisitem andes-list__item--size-medium'})
for categoria in categorias:
    texto_1 = categoria.text
    button = driver.find_element(By.CLASS_NAME, 'andes-list__item-action')
    button.click()
    
    sleep(2)
    html = BeautifulSoup(driver.page_source, 'html.parser')
    sub_categorias = html.findAll('li', attrs={'class': 'andes-list__item category-selection-lisitem andes-list__item--size-medium'})
    for sub_categoria in sub_categorias:
        texto_2 = texto_1 + '/' + sub_categoria.text
        button = driver.find_element(By.CLASS_NAME, 'andes-list__item-action')
        button.click()
        
        sleep(2)
        html = BeautifulSoup(driver.page_source, 'html.parser')
        sub_categorias = html.findAll('li', attrs={'class': 'andes-list__item category-selection-lisitem andes-list__item--size-medium'})
        for sub_categoria in sub_categorias:
            texto_3 = texto_1 + '/' + texto_2 + '/' + sub_categoria.text
            button = driver.find_element(By.CLASS_NAME, 'andes-list__item-action')
            button.click()
            sleep(2)

            html = BeautifulSoup(driver.page_source, 'html.parser')
            porcentagens = html.findAll('span', attrs={'class': 'andes-table__column--value'})
            if porcentagens:
                classico = porcentagens[1].text
                premium = porcentagens[2].text
                lista.append([texto_3, classico, premium])
                element = html.find_element_by_xpath(f'//a[contains(@title, "{sub_categoria.text}")]').text
                sleep(5)
            
            else:
                sleep(2)
                html = BeautifulSoup(driver.page_source, 'html.parser')
                sub_categorias = html.findAll('li', attrs={'class': 'andes-list__item category-selection-lisitem andes-list__item--size-medium'})
                for sub_categoria in sub_categorias:
                    texto_4 = texto_1 + '/' + texto_2 + '/' + texto_3 + '/' +  sub_categoria.text
                    button = driver.find_element(By.CLASS_NAME, 'andes-list__item-action')
                    button.click()

                    sleep(2)
                    html = BeautifulSoup(driver.page_source, 'html.parser')
                    porcentagens = html.findAll('span', attrs={'class': 'andes-table__column--value'})
                    if porcentagens:
                        classico = porcentagens[1].text
                        premium = porcentagens[2].text
                        lista.append([texto_4, classico, premium])
                        elements = driver.find_elements_by_css_selector('andes-breadcrumb__link')
                        element = element[-1]
                        xpath = driver.execute_script("return arguments[0].getPath()", element)
                        print(xpath)
                        xpath.click()
                        sleep(5)
                    
                    else:
                        sleep(2)
                        html = BeautifulSoup(driver.page_source, 'html.parser')
                        sub_categorias = html.findAll('li', attrs={'class': 'andes-list__item category-selection-lisitem andes-list__item--size-medium'})
                        for sub_categoria in sub_categorias:
                            texto_5 = texto_1 + '/' + texto_2 + '/' + texto_3 + '/' + texto_4 + '/' +  sub_categoria.text
                            button = driver.find_element(By.CLASS_NAME, 'andes-list__item-action')
                            button.click()
                            
                            sleep(2)
                            html = BeautifulSoup(driver.page_source, 'html.parser')
                            porcentagens = html.findAll('span', attrs={'class': 'andes-table__column--value'})
                            if porcentagens:
                                classico = porcentagens[1].text
                                premium = porcentagens[2].text
                                lista.append([texto_5, classico, premium])
                                element = html.find_all('a', attrs={'class': 'andes-breadcrumb__link'})
                                element = element[-1]
                                element.click()
                                sleep(5)
                            
                            else:
                                sleep(2)
                                html = BeautifulSoup(driver.page_source, 'html.parser')
                                sub_categorias = html.findAll('li', attrs={'class': 'andes-list__item category-selection-lisitem andes-list__item--size-medium'})
                                for sub_categoria in sub_categorias:
                                    texto_6 = texto_1 + '/' + texto_2 + '/' + texto_3 + '/' + texto_4 + '/' + texto_5 + '/' + sub_categoria.text
                                    button = driver.find_element(By.CLASS_NAME, 'andes-list__item-action')
                                    button.click()
                                    sleep(2)

                                    html = BeautifulSoup(driver.page_source, 'html.parser')
                                    porcentagens = html.findAll('span', attrs={'class': 'andes-table__column--value'})
                                    if porcentagens:
                                        classico = porcentagens[1].text
                                        premium = porcentagens[2].text
                                        lista.append([texto_6, classico, premium])
                                        element = html.find_all('a', attrs={'class': 'andes-breadcrumb__link'})
                                        element = element[-1]
                                        element.click()
                                        sleep(5)      
        
for item in lista:
    print(item)