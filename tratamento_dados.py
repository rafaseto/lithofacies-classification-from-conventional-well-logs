# %% [markdown]
# ## Importa funções para o pré-processamento

# %%
from pre_processamento import *

from dlisio import dlis
import pandas as pd
import numpy as np

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

# %%
print(nomes_arquivos)
print(nomes_anp)

# %% [markdown]
# ## Cria dicionário para armazenar os dados e respectivos nomes

# %%
# Casa itens da lista 'nome_anp_abreviados' com os itens da lista 'leituras_dlis'
pares = zip(nomes_anp, leituras_dlis)

# Cria dicionário 'dli_dict'
dli_dict = dict(pares)
dli_dict

# %% [markdown]
# ## Separa TODAS as curvas presentes nos .dlis de cada poço

# %%
channels_dict = {}

for key, poco in dli_dict.items():
    channels_list = []
    for frame in poco.frames:
        channels = frame.channels
        channels_list.append([channel.name for channel in channels])
    channels_dict[key] = sum(channels_list, [])

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
# ## Processa os 'frames' do poço 1-BRSA-551-SE

# %% [markdown]
# #### Quantidade de 'frames' do poço 1-BRSA-551-SE

# %%
dli_dict['1-FSG-1-SE'].frames

# %% [markdown]
# #### Cria um 'dataframe' para cada 'frame'

# %% [markdown]
# ## Processa os 'frames' do poço 1-BRSA-605-SE

# %% [markdown]
# #### Quantidade de 'frames' no poço 1-BRSA-605-SE

# %%
dli_dict['1-BRSA-605-SE'].frames

# %% [markdown]
# #### Cria um 'dataframe' para cada 'frame'

# %%
dataframes_605 = {}
poco = dli_dict['1-BRSA-605-SE']

for frame in poco.frames:
    indice = poco.frames.index(frame)

    curves = pd.DataFrame(frame.curves())

    dataframes_605[indice] = curves

# %% [markdown]
# #### Move a vírgula uma casa para a esquerda em todos os valores das colunas TDEP

# %%
for value in dataframes_605.values():
    value["TDEP"] = value["TDEP"] / 10

# %% [markdown]
# #### Converte de polegada para metro

# %%
for value in dataframes_605.values():
    value["TDEP"] = value["TDEP"] * 0.0254

# %% [markdown]
# #### Salva os dataframes como arquivos CSV

# %%
for key, value in dataframes_605.items():
    file_name = f"Frames_605/frame_{key}.csv"
    value.to_csv(file_name, index=False)
    print(f"Arquivo {file_name} criado com sucesso.")

# %% [markdown]
# #### Remove valores de profundidade que não estão presentes no primeiro frame

# %%
for key, value in dataframes_605.items():
    dataframes_605[key] = value[value["TDEP"].isin(dataframes_605[0]["TDEP"])]

# %% [markdown]
# #### Junta os 4 dataframes 

# %%
dataframes_605_merged = dataframes_605[0]

for i in range(1, len(dataframes_605)):
    dataframes_605_merged = pd.merge(dataframes_605_merged, dataframes_605[i], on='TDEP', how='outer', suffixes=(None, "_new"))

# %% [markdown]
# #### Mantém apenas as curvas escolhidas

# %%
curvas_escolhidas = ['TDEP', 'GR', 'NPHI', 'RHOB', 'RHOZ', 'DRHO', 'BSZ', 'BS', 'HCAL', 'CAL', 'CALI', 'DCALI', 'DCAL', 'PE', 'DT', 'DTC', 'ILD', 'RILD', 'IEL', 'AIT90', 'AHT90', 'RT90', 'AT90', 'AO90', 'RT', 'AF90', 'AHF90', 'AFH90', 'LLD', 'RLLD', 'HDRS', 'HLLD', 'LL7', 'RLL7']

# Remove colunas duplicadas 
dataframes_605_merged = dataframes_605_merged.loc[:, ~dataframes_605_merged.columns.duplicated()]

# Filtra de modo a manter apenas as curvas escolhidas
dataframes_605_merged_filtered = dataframes_605_merged.filter(items=curvas_escolhidas)

# %%
dataframes_605_merged_filtered

# %%
dlis_df_dict = {}   # Conterá os dataframes respectivos aos poços

# Curvas de perfis escolhidas
curvas_escolhidas = ['TDEP', 'GR', 'NPHI', 'RHOB', 'RHOZ', 'DRHO', 'BSZ', 'BS', 'HCAL', 'CAL', 'CALI', 'DCALI', 'DCAL', 'PE', 'DT', 'DTC', 'ILD', 'RILD', 'IEL', 'AIT90', 'AHT90', 'RT90', 'AT90', 'AO90', 'RT', 'AF90', 'AHF90', 'AFH90', 'LLD', 'RLLD', 'HDRS', 'HLLD', 'LL7', 'RLL7']


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
    
    #frames = [np.atleast_1d(frame) for frame in poco.frames]
    #curvas = np.concatenate(frames, axis=0)
    try:
        dataframe = pd.DataFrame()
        
        for frame in poco.frames:

            curvas = frame.curves()

            dataframe = pd.concat([dataframe, pd.DataFrame(curvas[curvas_utilizadas_sem_duplicados])])

        # Criando um pandas dataframe do poço respectivo à atual iteração e armazenando o mesmo em dlis_df
        dlis_df_dict[chave] = dataframe
    except:
        pass


# %%
dlis_df_dict['1-BRSA-605-SE'] = dataframes_605_merged_filtered
dlis_df_dict.keys()

# %% [markdown]
# ## Transforma os valores -999.25 em nulos

# %%
for poco in dlis_df_dict.values():
    poco.replace([-999.25], [None], inplace = True)

# %% [markdown]
# ## Aplicando os mnemônicos

# %%
aplica_mnemonico(dlis_df_dict, ['BS', 'BSZ'], 'BS')
aplica_mnemonico(dlis_df_dict, ['LLD',	'LL7',	'RLLD',	 'RLL7', 'HDRS', 'HLLD', 'ILD',	'RILD',	'IEL',	'AIT90', 'AHT90', 'RT90', 'AT90', 'AO90', 'RT', 'AF90',	'AHF90', 'AFH90'], 'RESD')
aplica_mnemonico(dlis_df_dict, ['RHOB', 'RHOZ'], 'RHOB')
aplica_mnemonico(dlis_df_dict, ['DTC', 'DT'], 'DT')
aplica_mnemonico(dlis_df_dict, ['HCAL', 'CAL', 'CALI'], 'CAL')
aplica_mnemonico(dlis_df_dict, ['DCAL', 'DCALI'], 'DCAL')
aplica_mnemonico(dlis_df_dict, ['DRHO', 'HDRA'], 'DRHO')

# %% [markdown]
# ## Adiciona coluna DCAL

# %%
add_DCAL(dlis_df_dict)

# %% [markdown]
# ## Preenche os poços com curvas faltando

# %%
dlis_df_dict['1-BRSA-595-SE']

# %%
# Se um dos poços não tiver uma dessas curvas, adicionamos a coluna da curva e mantemos os valores como None
curvas_obrigatorias = ['TDEP', 'BS', 'CAL', 'DCAL', 'GR', 'RESD', 'DT', 'RHOB', 'DRHO', 'NPHI', 'PE']

# Percorre todos os poços
for poco in dlis_df_dict.values():
    # Percorre todas as curvas obrigatórias
    for curva in curvas_obrigatorias:
        # Se o poço não tiver a curva
        if curva not in poco.columns:
            # Adiciona a coluna e os valores dela = None
            poco[curva] = None

# %%
dlis_df_dict['1-BRSA-605-SE']

# %% [markdown]
# ## Temos as seguintes curvas 

# %%
for key, poco in dlis_df_dict.items():
    curvas = sorted(poco.keys())
    print(f"{key}: {curvas}")

# %% [markdown]
# ## Remove valores DRHO e DCAL indesejados (Só depois)

# %%
#limita_curva(dlis_df_dict, "DRHO", -0.15, 0.15)
#limita_curva(dlis_df_dict, "DCAL", -2, 2)

# %% [markdown]
# ## Inverte a ordem das linhas dos dataframes

# %%
for key in dlis_df_dict.keys():
    dlis_df_dict[key] = dlis_df_dict[key].iloc[::-1]

# %% [markdown]
# ## Ordena as colunas dos dataframes

# %%
# Simon e Vandelli vao definir a ordem de preferencia
ordem_desejada = ['TDEP', 'BS', 'CAL', 'DCAL', 'GR', 'RESD', 'DT', 'RHOB', 'DRHO', 'NPHI', 'PE']

for key in dlis_df_dict.keys():
    dlis_df_dict[key] = dlis_df_dict[key].reindex(columns=ordem_desejada)

# %% [markdown]
# ## Salva os dados dos dataframes em arquivos CSV

# %%
for key, value in dlis_df_dict.items():
    file_name = f"Pocos_CSV/poco_{key}.csv"
    value.to_csv(file_name, index=False)
    print(f"Arquivo {file_name} criado com sucesso.")


