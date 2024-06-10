"""
Nome do Arquivo: processamento_dados.py
Versão: 1.2
Autor: Rafael Takeguma Goto
Data de Criação: 18/03/2024
Data de Modificação: 16/05/2024

Descrição:
Este arquivo contém funções para o pré-processamento de dados, que foram extraídos dos arquivos com a extensão dlis, de poços de petróleo.

Funcionalidades:
- remove_colunas: Remove colunas especificadas de um DataFrame.
- renomeiaColuna: Renomeia uma coluna em um DataFrame.
- aplica_mnemonico: Renomeia curvas com nomes diferentes consideradas equivalentes para um nome unificado.
- nphi_transform: Transforma os valores da curva NPHI de um dicionário de DataFrames.
- remove_pontos_com_falha: Remove linhas de DataFrames com valores de TDEP fora do intervalo desejado.
- add_DCALI: Adiciona uma coluna DCALI ao DataFrame com a diferença entre as colunas CALI e BSZ.
- limita_curva: Remove linhas de DataFrames com valores da curva fora do intervalo desejado.
- cria_frames_dict: Cria um dicionário para armazenar os frames de um poço
- cria_dataframes_dict: Cria um dicionário para armazenar os dataframes respectivos aos frames de um poço.
- unifica_dataframes: Unifica múltiplos dataframes em um dataframe ('dataframe_unificado')
"""

import pandas as pd

def remove_colunas(df, colunas):
    """
    Remove colunas especificadas de um DataFrame.

    Args:
        df (DataFrame): O DataFrame do qual as colunas serão removidas.
        colunas (list): Lista de nomes de colunas a serem removidas.

    Returns:
        df_filtrado (DataFrame): O DataFrame resultante após a remoção das colunas.
    """
    df_filtrado = df.drop(columns=colunas, errors='ignore')
    return df_filtrado


def renomeia_coluna(df, coluna_antes, coluna_depois):
    """
    Renomeia uma coluna em um DataFrame.

    Args:
        df (DataFrame): O DataFrame no qual a coluna será renomeada.
        coluna_antes (str): O nome da coluna a ser renomeada.
        coluna_depois (str): O novo nome da coluna.
    """
    df.rename(columns={coluna_antes: coluna_depois}, inplace=True)

def aplica_mnemonico(dlis_df_dict, mnemonicos, nome_unificado):
    """
    Renomeia curvas com nomes diferentes consideradas equivalentes para um nome unificado.

    Args:
        dlis_df_dict (dict): Dicionário contendo DataFrames com dados de poços.
        mnemonicos (str): Lista com mnemônicos
        nome_unificado (str): O novo nome unificado da coluna.
    """
    for poco in dlis_df_dict.values():
        for nome in mnemonicos:
            if nome in poco.columns:
                poco.rename(columns={nome: nome_unificado}, inplace=True)


def nphi_transform(dlis_df_dict, pocos):
    """
    Transforma os valores da curva NPHI de um dicionário de DataFrames.

    Args:
        dlis_df_dict (dict): Dicionário contendo DataFrames com dados de poços.
        pocos (list): Lista de nomes de poços para os quais a transformação será aplicada.
    """
    # Multiplica os valores da curva NPHI por 100
    for poco in pocos:
        dlis_df_dict[poco]["NPHI"] *= 100


def remove_pontos_com_falha(dlis_df_dict, pontos_com_falha):
    """
    Remove linhas de DataFrames com valores de TDEP fora do intervalo desejado.

    Args:
        dlis_df_dict (dict): Dicionário contendo DataFrames com dados de poços.
        pontos_com_falha (dict): Dicionário contendo intervalos desejados de TDEP para cada poço.
    """
    # Remove linhas com TDEP maior que o máximo desejado
    for key, value in dlis_df_dict.items():
        dlis_df_dict[key] = value.drop(value[value['TDEP'] > pontos_com_falha[key][1]].index)

    # Remove linhas com TDEP menor que o mínimo desejado
    for key, value in dlis_df_dict.items():
        dlis_df_dict[key] = value.drop(value[value['TDEP'] < pontos_com_falha[key][0]].index)


def add_DCAL(dlis_df_dict):
    """
    Adiciona uma coluna DCAL ao DataFrame com a diferença entre as colunas CAL e BS.

    Args:
        dlis_df_dict (dict): Dicionário contendo DataFrames com dados de poços.
    """
    for poco in dlis_df_dict.values():
        if 'CAL' in poco.columns and 'BS' in poco.columns:
            # Faz o cálculo de DCAL apenas para as linhas que possuem CAL e BS diff de None
            poco['DCAL'] = poco['CAL'][poco['CAL']!=None] - poco['BS'][poco['BS']!=None]
        else:
            # Caso CAL ou BS estejam ausentes, preenche a coluna DCAL com None
            poco['DCAL'] = None


def limita_curva(dlis_df_dict, curva, limite_inferior, limite_superior):
    """
    Transforma em None as linhas dos DataFrames com valores da curva fora do intervalo desejado

    Args:
        dlis_df_dict (dict): Dicionário contendo DataFrames com dados de poços.
        curva (str): Nome da curva para a qual os valores serão limitados.
        limite_inferior (float): Limite inferior desejado para os valores da curva.
        limite_superior (float): Limite superior desejado para os valores da curva.
    """
    # Transforma em None linhas com valores da curva abaixo do limite inferior
    for poco in dlis_df_dict.values():
        poco[curva][poco[curva] < limite_inferior] = None 

    # Transforma em None linhas com valores da curva acima do limite superior
    for poco in dlis_df_dict.values():
        poco[curva][poco[curva] > limite_superior] = None


def cria_frames_dict(poco):
    """
    Cria um dicionário para armazenar os frames de um poço

    Args:
        poco (LogicalFile): Arquivo do poço que contém os frames que serão armazenados no dicionário. 

    Returns:
        frames_dict (dict): Dicionário contendo ndarrays com dados de frames de poços.
    """
    frames_dict = {}

    for frame in poco.frames:
        indice = poco.frames.index(frame)

        curvas = frame.curves()

        frames_dict[indice] = curvas

    return frames_dict


def cria_dataframes_dict(frames_dict, curvas_escolhidas):
    """
    Cria um dicionário para armazenar os dataframes respectivos aos frames de um poço.

    Args:
        frames_dict (dict): Dicionário contendo ndarrays com dados de frames do poço.
        curvas_escolhidas (list): Lista contendo os nomes das curvas escolhidas.
    """
    indice_frame = 0
    # Dicionário contendo dataframes com dados de frames do poço
    dataframes_dict = {}

    for frame in frames_dict.values():
        i = 0
        nomes_curvas = frame.dtype.names
        frame_dict = {}

        for nome in nomes_curvas:
            if nome in curvas_escolhidas:
                dados_curva = [tupla[i] for tupla in frame]
                
                frame_dict[nome] = dados_curva
            i += 1

        dataframes_dict[indice_frame] = pd.DataFrame(frame_dict)
        indice_frame += 1


def unifica_dataframes(dataframes_dict):
    """
    Unifica múltiplos dataframes em um dataframe ('dataframe_unificado')

    Args:
        dataframes_dict (dict): Dicionário contendo dataframes com dados de frames do poço
    """
    dataframe_unificado = dataframes_dict[0]

    for i in range(1, len(dataframes_dict)):
        dataframe_unificado = pd.merge(dataframe_unificado, dataframes_dict[i], on='TDEP', how='outer', suffixes=(None, "_new"))

    return dataframe_unificado