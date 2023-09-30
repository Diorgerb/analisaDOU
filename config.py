from dou_extractor import DOUExtractor
import pandas as pd

douext = DOUExtractor('email', 'senha') # do usuário criado em https://inlabs.in.gov.br/acessar.php

atos = douext.extract('2023-09-14', '2023-09-14')

# Crie um DataFrame a partir da lista de dicionários
df = pd.DataFrame(atos)

# Especifique o nome do arquivo Excel de destino
nome_arquivo_excel = 'atos_do_dou.xlsx'

# Salve o DataFrame no arquivo Excel
df.to_excel(nome_arquivo_excel, index=False)  # O argumento 'index=False' evita a inclusão da coluna de índice no arquivo Excel

print(f'Dados salvos em {nome_arquivo_excel}')




