"""
Nome do Arquivo: processamento_dados.py
Versão: 1.0
Autor: Rafael Takeguma Goto
Data de Criação: 18/03/2024

Descrição:
Este arquivo contém funções para processamento de dados de poços, incluindo remoção de colunas, renomeação de colunas,
transformações de dados, remoção de pontos com falha e adição de colunas calculadas.

Funcionalidades:
- remove_colunas: Remove colunas especificadas de um DataFrame.
- renomeiaColuna: Renomeia uma coluna em um DataFrame.
- nphi_transform: Transforma os valores da curva NPHI de um dicionário de DataFrames.
- remove_pontos_com_falha: Remove linhas de DataFrames com valores de TDEP fora do intervalo desejado.
- add_DCALI: Adiciona uma coluna DCALI ao DataFrame com a diferença entre as colunas CALI e BSZ.
- limita_curva: Remove linhas de DataFrames com valores da curva fora do intervalo desejado.
"""

import pandas as pd

def remove_colunas(df, colunas):
    """
    Remove colunas especificadas de um DataFrame.

    Args:
        df (DataFrame): O DataFrame do qual as colunas serão removidas.
        colunas (list): Lista de nomes de colunas a serem removidas.

    Returns:
        DataFrame: O DataFrame resultante após a remoção das colunas.
    """
    df = df.drop(columns=colunas, errors='ignore')
    return df


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
    Renomeia os mnemônicos com um nome unificado

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


def add_DCALI(dlis_df_dict):
    """
    Adiciona uma coluna DCALI ao DataFrame com a diferença entre as colunas CALI e BSZ.

    Args:
        dlis_df_dict (dict): Dicionário contendo DataFrames com dados de poços.
    """
    for poco in dlis_df_dict.values():
        if 'CALI' in poco.columns and 'BSZ' in poco.columns:
            poco['DCALI'] = poco['CALI'] - poco['BSZ']
        else:
            # Caso CALI ou BSZ estejam ausentes, preenche a coluna DCALI com None
            poco['DCALI'] = None


def limita_curva(dlis_df_dict, curva, limite_inferior, limite_superior):
    """
    Remove linhas de DataFrames com valores da curva fora do intervalo desejado.

    Args:
        dlis_df_dict (dict): Dicionário contendo DataFrames com dados de poços.
        curva (str): Nome da curva para a qual os valores serão limitados.
        limite_inferior (float): Limite inferior desejado para os valores da curva.
        limite_superior (float): Limite superior desejado para os valores da curva.
    """
    # Remove linhas com valores da curva abaixo do limite inferior
    for key, value in dlis_df_dict.items():
        dlis_df_dict[key] = value.drop(value[value[curva] < limite_inferior].index)

    # Remove linhas com valores da curva acima do limite superior
    for key, value in dlis_df_dict.items():
        dlis_df_dict[key] = value.drop(value[value[curva] > limite_superior].index)