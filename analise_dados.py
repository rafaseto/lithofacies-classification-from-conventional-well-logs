# ----------------------------------------------------------------------------- #
# Nome do Programa: analise_dados.py
# Versão: 1.0
# Autor: Rafael Takeguma Goto
# Data: 08/03/2024
#
# Descrição: Este script realiza o carregamento e armazenamento dos dados dos arquivos dlis, 
#               e operações de pré-processamento.
#
# Funcionalidades:
#   - Carrega os dados
#   - Cria dataframes (tabelas) para cada poço
#   - Transforma os valores -999.25 em nulos
#   - Adiciona a coluna DCALI
#   - Limita os valores da curva DCALI no intervalo [-2, 2]
#   - Limita os valores da curva DCALI no intervalo [-0.15, 0.15]
# ----------------------------------------------------------------------------- #

# %% [markdown]
# ## Importa funções para o pré-processamento

# %%
from aux_datapreprocess import *

from dlisio import dlis
import pandas as pd

# A função 'glob' do módulo 'glob' é usada para procurar todos os arquivos em um diretório com determinada extensão
import glob

# %% [markdown]
# ## Carrega os dados

# %%
dli_dict = {}        # Conterá os arquivos lógicos
filenames = []  # Conterá os caminhos dos arquivos dlis
nomes_anp = []      # Conterá os nomes ANP dos poços
charId_inicio, charId_fim = 7, 10   # Índices de início e fim da substring identificadora do poço

# Utilizando a função 'glob' do módulo 'glob' para procurar todos os arquivos com extensão DLIS em 'Data'
for file in glob.glob(r'**/Data' + "/*.dlis", recursive=True):
    
    # Carregando os arquivos dlis com 'load' e armazenando-os em 'leitura'
    # 'tail' recebe valores restantes, caso a função retorne mais de uma peça de informação
    leitura, *tail = dlis.load(f'{file}')
    
    nome = leitura.origins[0].well_name

    nomes_anp.append(nome)    # armazenando o nome do poço
    
    filenames.append(file)      # armazenando o caminho dos arquivos dlis
    
    nome_abreviado = nome[charId_inicio : charId_fim]   # identificador do poço, e.g. '900'
    
    # Armazenando o arquivo lógico como valor em um dicionário onde a chave é o identificador do poço
    dli_dict[nome_abreviado] = leitura   

# %% [markdown]
# ## Cria dataframes para os poços

# %%
dlis_df_dict = {}   # Conterá os dataframes respectivos aos poços

# Curvas de perfis que não serão utilizadas
curvas_nao_utilizadas = ['WF11', 'AHV', 'AHVT', 'BHV', 'BHVT', 'CS', 'FCPS', 'HDCN', 'HMCN', 'ITT', 'ITTT', 'LSPD', 'MMK', 'NCPS', 'SP', 'TENS']

# Iterando sobre os arquivos lógicos de todos os poços (que estão armazenados em 'dli_dict'),
# '.values()' se refere aos valores do dicionário (não às chaves)
for chave, poco in dli_dict.items():
    try:
        # Armazenando as curvas que serão utilizadas em uma lista
        curvas_utilizadas = [
            channel.name                                    # Os elementos da lista serão os nomes das curvas
            for channel in poco.channels                    # As curvas são acessadas por meio de 'poco.channels'
            if channel.name not in curvas_nao_utilizadas    # As curvas que não utilizaremos não serão armazenadas na lista
        ]


        curvas = poco.frames[0].curves()

        # Criando um pandas dataframe do poço respectivo à atual iteração e armazenando o mesmo em dlis_df
        dlis_df_dict[chave] = pd.DataFrame(curvas[curvas_utilizadas])
    except:
        pass

# %%
# Transformados os valores -999.25 em nulos
for poco in dlis_df_dict.values():
    poco.replace([-999.25], [None], inplace = True)

# %% [markdown]
# ## Adiciona coluna DCALI

# %%
add_DCALI(dlis_df_dict)

limita_curva(dlis_df_dict, "DCALI", -2, 2)

# %% [markdown]
# ## Remove valores DRHO indesejados

# %%
limita_curva(dlis_df_dict, "DRHO", -0.15, 0.15)


print(dlis_df_dict['900'])