# Aplicação para fazer mineração de reviews de determinada página(restaurante ou atração) do Trip Advisor
# Aplicação utiliza da biblioteca BeautifulSoup para fazer mineração do HTML, salvando os HTMLs para uso posterior.
# A aplicação também é capaz de salvar os textos de review em um arquivo CSV para processamento usando algoritmos de NLP´.
# Aplicação criada por Matheus Farinaro Vesco, em outubro de 2022
#
# workflow sugerido:
# 1. use_web_html = False | save_html_option = True | save_csv = True | number_of_pages = 'last max'(ou número de páginas de páginas definido)
#   Esta etapa salvará os HTMLs para serem usados em uma execução futura, gerando menos problemas de timeout antes de gerar o CSV. Lembre-se de continuar
#   a tentar executar a aplicação até todos os HTMLs serem gerados.
#
# 2. use_web_html = False | save_html_option = False | save_csv = True | number_of_pages = 'last max'(ou número de páginas de páginas definido)
#   Esta etapa lerá os HTMLs salvos na etapa anterior, gerando o CSV através dos HTMLs locais, sem fazer nenhuma requisição ao site
#   
# Utilizar este workflow elimina diversos problemas que podem ocorrer ao utilizar o modo de HTML web(use_web_html = True), tornando o processo de scrape
# mais fácil e prático.

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import os
from time import sleep

use_web_html = False # deseja usar html direto da web? Se falso, salva HTML em uma pasta para uso em futura execução
# para números maiores de páginas, é recomendável utilizar HTML local a fim de diminuir riscos de bloqueio por parte do site
save_html_option = False # deseja salvar HTML localmente?
save_csv = True # deseja exportar CSV das reviews?

number_of_pages = 'last max' # numero de páginas de reviews a serem carregadas, ou 'max' para número máximo de páginas de reviews.
# ou 'last N' para checar HTMLs locais e continuar processo de salvamento de HTML desde a ultima execução. 'last max' também é aceito
html_parser = 'html.parser' # tipo de html parser a ser usado 'lxml', 'html5lib', and 'html.parser'
request_timeout = 15 # número de segundos antes de desistir de carregar a página

vero_bistro_moderne = 'https://www.tripadvisor.com/Restaurant_Review-g154913-d1119735-Reviews-Vero_Bistro_Moderne-Calgary_Alberta.html'
caesar_steak_house = 'https://www.tripadvisor.com/Restaurant_Review-g154913-d683068-Reviews-Caesar_s_Steak_House_Lounge-Calgary_Alberta.html'
product_url = caesar_steak_house # url a ser minerada por reviews

business_name = product_url.split('Reviews-')[1].replace('.html','').split('-')[0].lower() # limpa URL para achar apenas nome do restaurante
# no futuro, será usado para gerar diretórios específicos para cada website

html_file_folder = 'tripadvisor-html/' #Pasta onde os arquivos de HTML serão salvos
html_file_path = 'test_html.html' #arquivo teste de HTML
csv_file_path = f'data/{business_name}.csv' #Local de armazenamento do CSV

# Checa se diretório existe
# retorna True em caso de existência do diretório, ou False em caso negativo
def dir_check(path):
    pass

# Cria diretório
def create_dir(path):
    pass

# Faz requisição do HTML da página
# retorna conteúdo HTML
def request_html(url):
    try: # tenta acessar url
        start_time = datetime.now()
        print(f'Tentando carregar página: {url}\nStart: {start_time}')
        request = requests.get(url,timeout=request_timeout)
        end_time = datetime.now()
        print(f'Finish: {end_time} | delta = {end_time - start_time}')
        print(f'')
        return request 
    except: # se falha, inicia outra tentativa
        new_request = request_html(url)
        return new_request

# salva HTML localmente
def save_html(content,filepath):
    soup = BeautifulSoup(content,html_parser)

    try: #Tenta criar arquivo se não existe
        print(f'Criando arquivo html | {filepath}')
        html = open(filepath,'x', encoding = 'utf-8')
        print('Escrevendo soup')
        html.write(soup.prettify())
        print('Fechando')
        html.close()
    except: #se existe, abre em modo escrita
        print(f'Criando arquivo html | {filepath}')
        html = open(filepath,'w', encoding = 'utf-8')
        print('Escrevendo soup')
        html.write(soup.prettify())
        print('Fechando')
        html.close()

# Limpa string da review
# retorna string limpa
def string_format(string_list):
    for i in range(len(string_list)):
        string_list[i] = string_list[i].split() #faz split para limpar whitespaces
        string_list[i] = ' '.join(string_list[i]) #junta novamente em formato limpo
        if string_list[i].endswith(' More'): #Se string possuia post snippet, limpa texto da caixa de "More"
            string_list[i] = string_list[i][:-5]
            pass
    return string_list

# Testa se elemento de texto é uma review de cliente
# ou se é uma resposta do dono a uma review
def is_customer_review(content):
    # content --> Um elemento que possui classe "partial_entry"
    #
    # .findParent('div',{'data-prwidget-init':"handlers"}) --> acha parent que possui atributo data-prwidget-init="handlers"
    # Tanto a review de um cliente, quanto a resposta do dono, terão esse parent. Por isso, devemos olhar os siblings deste elemento
    #
    # .find_previous_sibling('div',{'class':"quote"}) --> tenta achar sibling que tem classe "quote". Caso ache, estamos lidando com
    # uma review de cliente. Isto pois o elemento com classe "quote" é parent do elemento de header, que também é armazenado do CSV final.
    # As respostas de donos não possui elemento de classe header.
    if type(content.findParent('div',{'data-prwidget-init':"handlers"}).find_previous_sibling('div',{'class':"quote"})) != type(None):
        return True
    else:
        return False

# extrai header da review
# retorna lista de headers da página
def extract_review_header(soup):
    review_header_list = []
    for review_header in soup.body.find_all('span',{'class':"noQuotes"}):
        review_header_list.append(review_header.text.replace('\n',''))
    return review_header_list

# extrai partial entry(texto) da review
# retorna lista de partial entries da página
def extract_partial_entry(soup):
    partial_entry_list = []
    for partial_entry in soup.body.find_all('p',{'class':"partial_entry"}):
        if is_customer_review(partial_entry): # se o texto é de uma review de cliente, e não uma resposta do dono a uma review...
            partial_entry_list.append(partial_entry.text)
    return partial_entry_list

# extrai post snippet(segunda metade do texto) da review
# o post snippet é o texto após o botão de "More", que também já é mostrado na partial entry
# desta forma, o post snippet é opcional e o algoritmo para minerá-lo foi feito para expansões futuras
# retorna lista de post snippets
def extract_post_snippet(soup):
    post_snippet_list = []
    for post_snippet in soup.body.find_all('span',{'class':"postSnippet"}):
        post_snippet_list.append(post_snippet.text)
    return post_snippet_list


# Extrai header e corpo da review
# retorna lista de headers da página, seguido da lista de partial entries
def extract_from_html(filepath):
    html_file = open(filepath,encoding='utf-8')
    soup = BeautifulSoup(html_file,html_parser)
    
    review_header_list = extract_review_header(soup)

    partial_entry_list = extract_partial_entry(soup)

    # post snippet não é necessário pois a partial entry já nos dá a review completa
    # para fins de demonstração e para expansão no futuro, extrai todos os post_snippets
    #post_snippet_list = extract_post_snippet(soup)

    html_file.close()

    # formata as listas de strings
    review_header_list = string_format(review_header_list)
    partial_entry_list = string_format(partial_entry_list)
    #post_snippet_list = string_format(post_snippet_list)

    return review_header_list,partial_entry_list

# Extrai header e corpo da review, mas pelo request da url
# retorna lista de headers da página, seguido da lista de partial entries
def extract_from_web(url):
    request = request_html(url)
    soup = BeautifulSoup(request.content,html_parser)
    
    review_header_list = extract_review_header(soup)

    partial_entry_list = extract_partial_entry(soup)

    # post snippet não é necessário pois a partial entry já nos dá a review completa
    # para fins de demonstração e para expansão no futuro, extrai todos os post_snippets
    #post_snippet_list = extract_post_snippe

    # formata as listas de strings
    review_header_list = string_format(review_header_list)
    partial_entry_list = string_format(partial_entry_list)
    #post_snippet_list = string_format(post_snippet_list)

    return review_header_list,partial_entry_list

# Gera lista de URLs a serem minerados
# Retorna esta lista
def scrape_worklist(url,pages_list):
    worklist = []
    for i in pages_list:
        if i != 0:
            page_num = i*15
            review_quarry = f'Reviews-or{page_num}'
        else:
            review_quarry = f'Reviews'
        page_url = url.replace('Reviews',review_quarry)
        worklist.append(page_url)
    return worklist

# Testa se diretório não possui arquivos HTML
# Retorna True se vazio, e False se há pelo menos um arquivo .HTML
def is_dir_empty(path):
    file_list = []
    for file in os.listdir(path):
        if len(file_list) == 0:
            if '.html' in file:
                file_list.append(file)
        else:
            return False
    return True

# Decide se HTML local já existe, neste caso retornando-o. Caso não existe arquivo HTML no diretório, busca HTML da web e retorna-o
# Retorna conteúdo de arquivo HTML
def decide_html_source(url,path):
    if is_dir_empty(path): # checa se diretório de HTMLs está vazio
        request = request_html(url) # se vazio, tenta acessar HTML online para fazer scrape da informação
        html_content = request.content
    else:
        for file in os.listdir(path): # se diretório não está vazio, pega o primeiro arquivo HTML encontrado na pasta
            if '.html' in file:
                filepath = f'{path}{file}'
                html_file = open(filepath,encoding='utf-8')
                html_content = html_file
                break
    return html_content
# Minera valor de reviews da página do local desejado
# Retorna inteiro deste valor
def get_max_reviews(url,path):

    html_content = decide_html_source(url,path) # decide se fonte do HTML é um arquivo local(se existente) ou se é online, retornando o HTML independente da fonte

    soup = BeautifulSoup(html_content,html_parser)

    number_of_reviews_element = soup.body.find('a',{'href':"#REVIEWS"}) 

    max_num = number_of_reviews_element.text.split() # em formato 'X Reviews', pega apenas o valor de 'X'
    print(f'Existem {max_num[0]} reviews associadas a este estabelecimento')
    return int(max_num[0])


# Gera lista de indexes para serem usados como range()
# Retorna a lista
def gen_pages_list(num):
    pages_list = []
    if type(num) == type(1): # se número de páginas foi especificado...
        for i in range(num):
            pages_list.append(num)
        return pages_list
    elif type(num) == type(''): # se número de páginas é uma string...
        num = num.lower()
        if num == 'max': # se número de páginas indica que o usuário deseja o máximo de páginas...
            max_pages = get_max_reviews(product_url,html_file_folder) # retorna o número máximo de páginas baseado no número de reviews
            num_max = round(max_pages/15)
            for i in range(num_max):
                pages_list.append(i)
            return pages_list
        elif 'last' in num: # se número de páginas indica que usuário quer continuar desde a última execução...
            try:
                num_max = int(num.split()[1]) # retorna apenas segunda parte da string(número ou max)
                num_min = last_html_file(html_file_folder)
                for i in range(num_min,(num_max+1)):
                    pages_list.append(i)
                return pages_list
            except: # se segunda parte da string não pode ser convertida para string(em caso de ser 'max')...
                print('erro ao converter para int!')
                if num.split()[1] == 'max': # se segunda parte é de fato string "max", implementa o algoritmo para achar número máximo de páginas
                    try:
                        print('tentando achar o valor total de reviews...')
                        pages_list = []
                        max_pages = get_max_reviews(product_url,html_file_folder) # retorna o número máximo de páginas baseado no número de reviews
                        num_max = round(max_pages/15)
                        print(f'Separadas em {num_max} páginas')
                        num_min = last_html_file(html_file_folder)
                        for i in range(num_min,(num_max+1)):
                            pages_list.append(i)
                        print()
                        return pages_list
                    except:
                        print('Número de páginas inválido!')
                else:
                    print('Número de páginas inválido!')
    else:
        print('Número de páginas inválido!')

# Ordena lista de file_list
# Retorna lista em ordem ascendente
def filelist_sort(file_list):
    for file in file_list:
        index = file_list.index(file)
        number = file.replace('.html','')
        file_list[index] = int(number)
    file_list.sort()
    for file in file_list:
        index = file_list.index(file)
        number_string = f'{file}.html'
        file_list[index] = number_string
    
    return file_list

# Acha o index do último item HTML salvo
# Retorna int deste index
def last_html_file(filepath):
    file_list = []

    for file in os.listdir(filepath):
        if '.html' in file:
            file_list.append(file)
    if file_list == []:
        return 0
    file_list = filelist_sort(file_list) # ordena lista em ordem crescente
    last_index = len(file_list)-1
    last_item = file_list[last_index]
    return int(last_item.replace('.html',''))

print()
print(f'Iniciando programa com configurações:')
print('---------------------------------------------------')
print(f'use_web_html = {use_web_html}')
print(f'save_html_option = {save_html_option}')
print(f'save_csv = {save_csv}')
print('---------------------------------------------------')
print()

# Se serão requisitadas páginas da web...
if save_html_option or use_web_html:
    pages_list = gen_pages_list(number_of_pages) # gera lista de número de páginas a ser usado em outras funções

# se programa configurado para salvar HTML e não usar HTML local, 
# salva os HTMLs desejados para serem usados em futura execução
if save_html_option and not use_web_html:
    worklist = scrape_worklist(product_url,pages_list) #gera lista de urls a serem mineradas

    i = last_html_file(html_file_folder)

    for url in worklist:
        product_page = request_html(url) 

        i += 1

        save_html(product_page.content,f'{html_file_folder}{i}.html')
        if len(pages_list) > 5:
            sleep(2)

# se programa configurado para utilizar HTML da web,
# Salva arquivo CSV com todas as reviews
if use_web_html:
    data = {
            'Title':[],
            'Corpus':[],
        }
    csv_file = pd.DataFrame(data)
    worklist = scrape_worklist(product_url,pages_list) #gera lista de urls a serem mineradas
    for url in worklist:
        review_header_list , partial_entry_list = extract_from_web(url)

        data = {
            'Title':review_header_list,
            'Corpus':partial_entry_list,
        }

        temp_df = pd.DataFrame(data)
        csv_file = pd.concat([csv_file,temp_df],ignore_index=True)
        
    csv_file.to_csv(csv_file_path)
    print('CSV armazenado com sucesso!')

# se programa configurado para utilizar HTML local,
# Salva arquivo CSV com todas as reviews
if not use_web_html:
    data = {
            'Title':[],
            'Corpus':[],
        }
    csv_file = pd.DataFrame(data)
    for file in os.listdir(html_file_folder):
        if '.html' in file:
            html_file_path = f'{html_file_folder}{file}'
            review_header_list , partial_entry_list = extract_from_html(html_file_path)
            data = {
                'Title':review_header_list,
                'Corpus':partial_entry_list,
            }

            temp_df = pd.DataFrame(data)
            csv_file = pd.concat([csv_file,temp_df],ignore_index=True)
        
    csv_file.to_csv(csv_file_path)
    print('CSV armazenado com sucesso!')
