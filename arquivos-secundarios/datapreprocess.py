import torch
from torch.utils.data import TensorDataset, DataLoader, random_split
import numpy as np
import pandas as pd
from dlisio import dlis
import matplotlib.pyplot as plt

# Funções de suporte para Limpeza e Pré-processamento de dados
# Renomeando a Coluna BS


def BStoBSZ(dlis_df):
    dlis_df[0].rename(columns={'BS': 'BSZ'}, inplace=True)
    return dlis_df


def NPHItransform(dlis_df):
    dlis_df[0]["NPHI"] = (dlis_df[0]["NPHI"] * 100)
    dlis_df[1]["NPHI"] = (dlis_df[1]["NPHI"] * 100)
    dlis_df[3]["NPHI"] = (dlis_df[3]["NPHI"] * 100)
    return dlis_df

# Acrescentando o DCALI e Excluindo as Linhas com DCALI X, onde X>2 ou X<-2


def addDCALIfilter(dlis_df):
    for i in range(len(dlis_df)):
        dlis_df[i]['DCALI'] = dlis_df[i]['CALI'] - dlis_df[i]['BSZ']
    for i in range(len(dlis_df)):
        dlis_df[i] = dlis_df[i].drop(
            dlis_df[i][(dlis_df[i].DCALI > 2) | (dlis_df[i].DCALI < -2)].index)
        dlis_df[i] = dlis_df[i].drop(
            dlis_df[i][(dlis_df[i].DRHO > 0.15) | (dlis_df[i].DRHO < -0.15)].index)
    return dlis_df

# Renomeando Curvas HDRS e LLD para RESD - Curvas HMRS e LLS para RESM


def renomearCurvas(dlis_df):
    dlis_df[0].rename(
        columns={'HDRS': 'RESD', 'HMRS': 'RESM'}, inplace=True)
    dlis_df[1].rename(
        columns={'HDRS': 'RESD', 'HMRS': 'RESM'}, inplace=True)
    dlis_df[2].rename(
        columns={'LLD': 'RESD', 'LLS': 'RESM'}, inplace=True)
    dlis_df[3].rename(
        columns={'HDRS': 'RESD', 'HMRS': 'RESM'}, inplace=True)
    dlis_df[4].rename(
        columns={'HDRS': 'RESD', 'HMRS': 'RESM'}, inplace=True)
    dlis_df[5].rename(
        columns={'HDRS': 'RESD', 'HMRS': 'RESM'}, inplace=True)
    return dlis_df

# Removendo as leituras que possui curvas com falhas em sua leitura


def removeFalha(dlis_df):
    dlis_df[0] = dlis_df[0].drop(
        dlis_df[0][(dlis_df[0].TDEP < 248) | (dlis_df[0].TDEP >= 360)].index)
    dlis_df[1] = dlis_df[1].drop(
        dlis_df[1][(dlis_df[1].TDEP <= 73.8) | (dlis_df[1].TDEP >= 209.9)].index)
    dlis_df[2] = dlis_df[2].drop(
        dlis_df[2][(dlis_df[2].TDEP <= 60.8) | (dlis_df[2].TDEP >= 257.7)].index)
    dlis_df[3] = dlis_df[3].drop(
        dlis_df[3][(dlis_df[3].TDEP <= 88.1) | (dlis_df[3].TDEP >= 303.1)].index)
    dlis_df[4] = dlis_df[4].drop(
        dlis_df[4][(dlis_df[4].TDEP <= 63.4) | (dlis_df[4].TDEP >= 216.1)].index)
    dlis_df[5] = dlis_df[5].drop(
        dlis_df[5][(dlis_df[5].TDEP <= 89.8) | (dlis_df[5].TDEP >= 318.2)].index)
    return dlis_df

# Concatenando todos os dataframes em 1


def concatenaDF(dlis_df):
    dlis_df[1].dropna(inplace=True)
    dlis_concat = pd.concat([dlis_df[0], dlis_df[1], dlis_df[2],
                            dlis_df[3], dlis_df[4], dlis_df[5]]).reset_index().drop('index', axis=1)
    dlis_concat.dropna(axis=0, inplace=True)
    return dlis_concat

# Removendo as colunas que não contribuem para as eletrofácies


def dropColumns(df: pd.DataFrame):
    df = df.drop(["TDEP"], axis=1)
    df = df.drop(["BSZ"], axis=1)
    df = df.drop(["CALI"], axis=1)
    df = df.drop(["TENS"], axis=1)
    df = df.drop(["DRHO"], axis=1)
    df = df.drop(["DCALI"], axis=1)
    return df


def dropColumnsMenosDept(df: pd.DataFrame):
    df = df.drop(["BSZ"], axis=1)
    df = df.drop(["CALI"], axis=1)
    df = df.drop(["TENS"], axis=1)
    df = df.drop(["DRHO"], axis=1)
    df = df.drop(["DCALI"], axis=1)
    return df


def addPocoLabel(df: pd.DataFrame, nPoco):
    match nPoco:
        case 0:
            df["Poco"] = "P-47"
        case 1:
            df["Poco"] = "P-48"
        case 2:
            df["Poco"] = "P-51"
        case 3:
            df["Poco"] = "P-53"
        case 4:
            df["Poco"] = "P-55"
        case 5:
            df["Poco"] = "P-57"

    return df


def addLatentVariables(df: pd.DataFrame, latent_X, latent_dim):
    df = df.reset_index(drop=True)
    match latent_dim:
        case 2:
            tempDf = pd.DataFrame(latent_X, columns=['X', 'Y'])
            # df_concat = df
            # df_concat['X'] = tempDf['X']
            df_concat = pd.concat([df, tempDf], axis=1)
            return df_concat
        case 3:
            tempDf = pd.DataFrame(latent_X, columns=['X', 'Y', 'Z'])
            df_concat = pd.concat([df, tempDf], axis=1)
            return df_concat
        case 5:
            tempDf = pd.DataFrame(latent_X, columns=['X', 'Y', 'Z', 'V', 'W'])
            df_concat = pd.concat([df, tempDf], axis=1)
            return df_concat


def dataTOfloat(df):
    for col in df.columns:
        df[col] = df[col].astype(float)
    return df


def dataToTensorToNormal(df: pd.DataFrame):

    # Transformando os dados em Tensores
    numpyDf = df.to_numpy()
    dataTensor = torch.tensor(numpyDf, dtype=torch.float32)

    # Normalizando os dados
    media = dataTensor.mean(dim=0)
    desviop = dataTensor.std(dim=0)

    dataArray = dataTensor.numpy()
    normalData = (dataArray - media.numpy()) / desviop.numpy()

    normalizedTensor = torch.tensor(normalData, dtype=torch.float32)
    return normalizedTensor


def dataToNormal(df: pd.DataFrame):

    # Transformando os dados em Tensores
    numpyDf = df.to_numpy()
    dataTensor = torch.tensor(numpyDf, dtype=torch.float32)

    # Normalizando os dados
    media = dataTensor.mean(dim=0)
    desviop = dataTensor.std(dim=0)

    dataArray = dataTensor.numpy()
    normalData = (dataArray - media.numpy()) / desviop.numpy()

    return normalData


# Função que cria um dataloader a partir de uma Tensor e de um batch_size


def loadDataloader(dataset: TensorDataset, batchSize):
    trainloader = DataLoader(
        dataset, batch_size=batchSize, shuffle=True)

    return trainloader


def loadDataloaderWithoutShuffle(dataset: TensorDataset, batchSize):
    trainloader = DataLoader(
        dataset, batch_size=batchSize, shuffle=False)

    return trainloader


# Função para Exportar os dados básicos que compõem as cruvas de perfis
def exportData(dlis_df):
    dlis_df = BStoBSZ(dlis_df)
    dlis_df = NPHItransform(dlis_df)
    dlis_df = addDCALIfilter(dlis_df)
    dlis_df = renomearCurvas(dlis_df)
    dlis_df = removeFalha(dlis_df)
    cont = 0

    print("Exportando Dados do Dlis")

    for dlis in dlis_df:
        print("...")
        NovoDlis = dropColumnsMenosDept(dlis)
        match cont:
            case 0:
                NovoDlis.to_csv('Export\\3-CP-1847-SE.csv')
            case 1:
                NovoDlis.to_csv('Export\\3-CP-1848-SE.csv')
            case 2:
                NovoDlis.to_csv('Export\\3-CP-1851-SE.csv')
            case 3:
                NovoDlis.to_csv('Export\\3-CP-1853-SE.csv')
            case 4:
                NovoDlis.to_csv('Export\\3-CP-1855-SE.csv')
            case 5:
                NovoDlis.to_csv('Export\\3-CP-1857-SE.csv')
        cont += 1
    print("Dados Exportados")

# Função para exportar os dados após o final do treinamento


def exportDatasetTrained(model, originalDfList, args):

    dfListModificada = []
    clusterLabelList = []
    contPoco = 0

    for dlis_df in originalDfList:
        # Primeiro, computamos os labels do poço
        dataset = dropColumns(dlis_df)
        dataset = dataToTensorToNormal(dataTOfloat(dataset))
        datasetLoader = loadDataloaderWithoutShuffle(dataset, args.batch_size)
        y_pred = []
        latent_X = []

        for data in datasetLoader:
            batch_size = data.size()[0]
            data = data.view(batch_size, -1).to(model.device)
            latent_X_batch = model.autoencoder(data, latent=True)
            latent_X_batch = latent_X_batch.detach().cpu().numpy()
            latent_X.append(latent_X_batch)

            y_pred_batch = model.kmeans.update_assign(
                latent_X_batch).reshape(-1, 1)
            y_pred.append(y_pred_batch)

        latent_X = np.vstack(latent_X)
        y_pred = np.vstack(y_pred).reshape(-1)
        clusterLabelList.append(y_pred)

        # Segundo, nós criamos um dataframe com os dados necessários do Poço

        newDf = dropColumnsMenosDept(dlis_df)
        newDf = addPocoLabel(newDf, contPoco)
        newDf = addLatentVariables(newDf, latent_X, args.latent_dim)
        newDf[f"{args.latent_dim}D_{args.n_clusters}G"] = y_pred

        dfListModificada.append(newDf)

        contPoco += 1

    dlisConcat = concatenaDF(dfListModificada)
    # Caminho interno do PC onde deseja salvar os dados
    dlisConcat.to_csv(
        f'C:\\Users\\marco\\Desktop\\My Things\\Ufs\\TCC\\Modelo\My_model-04-09-2023\\Deep-Clustering-Network\\Export\\pocos_latent_dim{args.latent_dim}_nclusters{args.n_clusters}.csv')

    return

# Função para exportar as informações do K-means Controle


def exportDatasetBaseKmeans(originalDataList, labels):

    modifiedLis = []
    contPoco = 0

    for dlis_df in originalDataList:

        newDf = dropColumnsMenosDept(dlis_df)
        newDf = addPocoLabel(newDf, contPoco)
        modifiedLis.append(newDf)

        contPoco += 1

    datasetConcat = concatenaDF(modifiedLis)
    datasetConcat["7D_G7"] = labels

    # Caminho interno do PC onde deseja salvar os dados
    datasetConcat.to_csv(
        f'C:\\Users\\marco\\Desktop\\My Things\\Ufs\\TCC\\Modelo\My_model-04-09-2023\\Deep-Clustering-Network\\Export\\pocos_dim7_nclusters7.csv')
