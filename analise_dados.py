# %% [markdown]
# ## Importa funções para o pré-processamento

# %%
from pre_processamento import *

from dlisio import dlis
import pandas as pd

# A função 'glob' do módulo 'glob' é usada para procurar todos os arquivos em um diretório com determinada extensão
import glob

# %% [markdown]
# ## Carrega os dados

# %%
nomes_arquivos = []     # Armazena os nomes dos arquivos .dlis
leituras_dlis = []      # Armazena as leituras dos arquivos .dlis
nomes_anp = []          # Armazena os nomes obtidos das leituras

for file in glob.glob(r'**/Data' + "/*.dlis", recursive=True):
    # Salva o nome do arquivo
    nomes_arquivos.append(file)

    # Salva os dados da leitura
    leitura, *tail = dlis.load(f'{file}')
    leituras_dlis.append(leitura)

    # Salva o nome do poço
    nome = leitura.origins[0].well_name
    nomes_anp.append(nome)

# %% [markdown]
# ## Padroniza nomes fora do padão 'X-BRSA-XXX-SE'

# %%
nomes_anp[0] = '1-BRSA-551-SE'
nomes_anp[1] = '1-BRSA-574-SE'

# %% [markdown]
# ## Salva os identificadores em 'nomes_anp_abreviados'

# %%
nomes_anp_abreviados = []   # Armazena os nomes abreviados (identificadores)

for nome in nomes_anp:
    nome_abreviado = nome[7:10]
    nomes_anp_abreviados.append(nome_abreviado)

# %% [markdown]
# ## Cria dicionário para armazenar os dados e respectivos nomes

# %%
# Casa itens da lista 'nome_anp_abreviados' com os itens da lista 'leituras_dlis'
pares = zip(nomes_anp_abreviados, leituras_dlis)

# Cria dicionário 'dli_dict'
dli_dict = dict(pares)

# %% [markdown]
# ## Separa TODAS as curvas presentes nos .dlis de cada poço

# %%
channels_dict = {}

for key, poco in dli_dict.items():
    channels = poco.frames[0].channels
    channels_list = [channel.name for channel in channels]
    channels_dict[key] = channels_list

# %% [markdown]
# ## Salva as curvas presentes nos .dlis em arquivos CSV

# %%
import csv

for key, value in channels_dict.items():
    file_name = f"Curvas_CSV/curvas_{key}.csv"
    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Curva", "Poco"])
        for item in value:
            writer.writerow([item, f'P_{key}'])

    print(f"Arquivo {file_name} criado com sucesso")

# %% [markdown]
# ## Concatena os arquivos CSV das curvas em um único arquivo

# %%
import os

pasta = "Curvas_CSV"

# Lista para armazenar os dataframes repectivos aos .csv
df_list = []

# Itera sobre a pasta Curvas_CSV
for arquivo in os.listdir(pasta):
    file_path = os.path.join(pasta, arquivo)

    # Lê o arquivo CSV como um DF
    df = pd.read_csv(file_path)
    df_list.append(df)

# Concatena os DFs ao longo do eixo das colunas
df_concat = pd.concat(df_list, axis=0, ignore_index=True)

# Salva o DF concatenado em um .csv
df_concat.to_csv("curvas_pocos.csv", index=False)

print("Arquivo curvas_pocos.csv criado com sucesso")

# %% [markdown]
# ## Cria dataframes para os poços

# %%
dlis_df_dict = {}   # Conterá os dataframes respectivos aos poços

# Curvas de perfis escolhidas
curvas_escolhidas = ['TDEP', 'GR', 'NPHI', 'RHOB', 'DRHO', 'HDRS', 'LLD', 'BSZ', 'BS', 'CALI', 'DCALI', 'PE', 'DTC']

# Iterando sobre os arquivos lógicos de todos os poços (que estão armazenados em 'dli_dict'),
# '.values()' se refere aos valores do dicionário (não às chaves)
for chave, poco in dli_dict.items():

    # Armazenando as curvas que serão utilizadas em uma lista
    curvas_utilizadas = [
        channel.name                                    # Os elementos da lista serão os nomes das curvas
        for channel in poco.channels                    # As curvas são acessadas por meio de 'poco.channels'
        if channel.name in curvas_escolhidas            # As curvas que não utilizaremos não serão armazenadas na lista
    ]
    conjunto_aux = set(curvas_utilizadas)
    curvas_utilizadas_sem_duplicados = list(conjunto_aux)

    curvas = poco.frames[0].curves()

    # Criando um pandas dataframe do poço respectivo à atual iteração e armazenando o mesmo em dlis_df
    dlis_df_dict[chave] = pd.DataFrame(curvas[curvas_utilizadas_sem_duplicados])


# %% [markdown]
# ## Transforma os valores -999.25 em nulos

# %%
for poco in dlis_df_dict.values():
    poco.replace([-999.25], [None], inplace = True)

# %% [markdown]
# ## Aplicando os mnemônicos

# %%
aplica_mnemonico(dlis_df_dict, ['BS', 'BSZ'], 'BS')
aplica_mnemonico(dlis_df_dict, ['LLD', 'HDRS'], 'RESD')
aplica_mnemonico(dlis_df_dict, ['RHOB', 'RHOZ'], 'RHOB')

# %% [markdown]
# ## Renomeia CALI para CAL

# %%
for poco in dlis_df_dict.values():
    renomeia_coluna(poco, 'CALI', 'CAL')

# %% [markdown]
# ## Adiciona coluna DCAL

# %%
add_DCAL(dlis_df_dict)

# %% [markdown]
# ## Preenche os poços com curvas faltando

# %%
# Se um dos poços não tiver uma dessas curvas, adicionamos a coluna da curva e mantemos os valores como None
curvas_obrigatorias = ['BS', 'CAL', 'DCAL', 'DRHO', 'DTC', 'GR', 'NPHI', 'PE', 'RESD', 'RHOB', 'TDEP']

# Percorre todos os poços
for poco in dlis_df_dict.values():
    # Percorre todas as curvas obrigatórias
    for curva in curvas_obrigatorias:
        # Se o poço não tiver a curva
        if curva not in poco.columns:
            # Adiciona a coluna e os valores dela = None
            poco[curva] = None

# %% [markdown]
# ## Temos as seguintes curvas 

# %%
for key, poco in dlis_df_dict.items():
    curvas = sorted(poco.keys())
    print(f"{key}: {curvas}")

# %% [markdown]
# ## Inverte a ordem das linhas dos dataframes

# %%
for key in dlis_df_dict.keys():
    dlis_df_dict[key] = dlis_df_dict[key].iloc[::-1]

# %% [markdown]
# ## Ordena os dataframes

# %%
ordem_desejada = ['TDEP', 'GR', 'RESD', 'BS', 'CAL', 'DCAL', 'NPHI', 'PE', 'DRHO', 'RHOB', 'DTC']

for key in dlis_df_dict.keys():
    dlis_df_dict[key] = dlis_df_dict[key].reindex(columns=ordem_desejada)

# %% [markdown]
# ## Salva os dados dos dataframes em arquivos CSV

# %%
for key, value in dlis_df_dict.items():
    file_name = f"Pocos_CSV/poco_{key}.csv"
    value.to_csv(file_name, index=False)
    print(f"Arquivo {file_name} criado com sucesso.")


