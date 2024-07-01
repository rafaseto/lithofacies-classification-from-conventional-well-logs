import pandas as pd

# Aplicação dos filtros

nomes_pocos = ['merged_1-BRSA-459-SE', 'merged_1-BRSA-551-SE', 'merged_1-BRSA-574-SE', 'merged_1-BRSA-595-SE',
               'merged_1-BRSA-605-SE', 'merged_1-BRSA-643-SE', 'merged_1-BRSA-645-SE', 'merged_1-BRSA-659-SE',
               'merged_1-BRSA-689-SE', 'merged_1-BRSA-696-SE', 'merged_1-BRSA-698-SE']

# Criação de um dicionário para armazenar os DataFrames associados aos nomes dos poços
dfs_por_poco = {}

for poco in nomes_pocos:
    # Leitura do poço e armazenamento no dicionário
    df = pd.read_csv(f'{poco}.csv')
    parts = poco.split("-")
    dfs_por_poco[f"P_{parts[len(parts)-2]}"] = df

# Simplifica os nomes dos poços
for idx, poco in enumerate(nomes_pocos):
  parts = poco.split("-")
  nomes_pocos[idx] = f"P_{parts[len(parts)-2]}"

def filtra_coluna(df, coluna, min=None, max=None):
    indices_para_remover = []
    for index, row in df.iterrows():
        if (min is not None and row[coluna] <= min) or (max is not None and row[coluna] >= max):
            indices_para_remover.append(index)

    df.drop(index=indices_para_remover, inplace=True)
    return df

colunas = ['GR', 'NPHI', 'RHOB', 'DRHO', 'RESD', 'DCAL', 'PE', 'Litologia']
for poco in nomes_pocos:
    #print(f"{poco}:")
    #print(f"Número de amostra antes do filtro de nulos: {len(dfs_por_poco[poco])}")

    # Excluir as linhas que não possuem alguma curva de perfil
    dfs_por_poco[poco].dropna(subset=colunas, inplace=True)
    #print(f"Número de amostras depois do filtro de nulos: {len(dfs_por_poco[poco])}")

    # Aplica os filtros de perfis definidos pelos geólogos
    dfs_por_poco[poco] = filtra_coluna(dfs_por_poco[poco], 'DCAL', max=1.5, min=-1)
    dfs_por_poco[poco] = filtra_coluna(dfs_por_poco[poco], 'DRHO', min=-0.15, max=0.15)
    #print(f"Número de amostras depois do filtro de valores máximos e mínimos: {len(dfs_por_poco[poco])}")