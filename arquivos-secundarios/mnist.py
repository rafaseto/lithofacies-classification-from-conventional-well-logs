import torch
from torch.utils.data import TensorDataset, DataLoader, random_split
import argparse
import numpy as np
from DCN import DCN
from sklearn.metrics import silhouette_score
from sklearn.metrics import davies_bouldin_score
import pandas as pd
from dlisio import dlis
import glob
import matplotlib.pyplot as plt
import datapreprocess as dpp


# Função para Plotar o gráfico

def plot_latent_points(latent_points, cluster_labels):

    if (len(latent_points) != len(cluster_labels)):
        raise ValueError(
            "Número de Pontos Latentes diferente do número de Labels")

    labels_unicos = np.unique(cluster_labels)
    cores = plt.cm.viridis(np.linspace(0, 1, len(labels_unicos)))

    plt.figure(figsize=(10, 7))

    for i, label in enumerate(labels_unicos):
        cluster_points = latent_points[cluster_labels == label]
        plt.scatter(cluster_points[:, 0], cluster_points[:, 1], c=[
                    cores[i]], s=10, label=f'Agrupamento {label}')

    # plt.scatter(latent_points[:, 0],
    #             latent_points[:, 1], c='blue', s=10)
    plt.xlabel('Latent Dimension x')
    plt.ylabel('Latent Dimension y')
    plt.title('Regiões do Cluster')
    plt.legend()
    plt.show()


def avaliar_latentes(model, dataloader):
    all_points = []
    y_pred = []
    model.eval()
    for data in dataloader:
        batch_size = data.size()[0]
        data = data.view(batch_size, -1).to(model.device)
        with torch.no_grad():
            latent_X = model.autoencoder(data, latent=True)
            latent_X = latent_X.cpu().numpy()
        all_points.append(latent_X)

        y_pred_batch = model.kmeans.update_assign(
            latent_X).reshape(-1, 1)
        y_pred.append(y_pred_batch)

    all_points = np.vstack(all_points)
    y_pred = np.vstack(y_pred).reshape(-1)
    return all_points, y_pred


def evaluate(model, test_loader):
    # y_test = []
    # for data, target in test_loader:
    #     batch_size = data.size()[0]
    #     data = data.view(batch_size, -1).to(model.device)
    #     latent_X = model.autoencoder(data, latent=True)
    #     latent_X = latent_X.detach().cpu().numpy()

    #     y_test.append(target.view(-1, 1).numpy())
    #     y_pred.append(model.kmeans.update_assign(latent_X).reshape(-1, 1))

    y_pred = []
    latent_X = []

    for data in test_loader:
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

    return silhouette_score(latent_X, y_pred), davies_bouldin_score(latent_X, y_pred)

# Função que gerencia o modelo e faz o pré-treino e o treino dele


def solver(args, model, train_loader, originalDfList):

    rec_loss_list = model.pretrain(train_loader, args.pre_epoch)
    siscore_list = []
    davies_list = []

    for e in range(args.epoch):
        model.train()
        model.fit(e, train_loader)

        model.eval()

        Siscore, Daviescore = evaluate(model, train_loader)
        siscore_list.append(Siscore)
        davies_list.append(Daviescore)

        print('\nEpoch: {:02d} | Silhouette Score: {:.3f} | Davies Bouldin Score: {:.3f}'.format(
            e, Siscore, Daviescore))

    # Plot dos dados do autoencoder, só pode plotar duas dimensões
    # latent_points, pred_labels = avaliar_latentes(model, train_loader)
    # plot_latent_points(latent_points, pred_labels)

    # Local onde é chamado a função para o exportar os dados após o término do treino
    # dpp.exportDatasetTrained(model, originalDfList, args)

    return rec_loss_list, siscore_list, davies_list


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Deep Clustering Network')

    # Dataset parameters
    # parser.add_argument('--dir', default='../Dataset/mnist',
    #                     help='dataset directory')
    parser.add_argument('--dir', default='Data/*',
                        help='dataset directory')
    # parser.add_argument('--input-dim', type=int, default=28*28,
    #                     help='input dimension')
    parser.add_argument('--input-dim', type=int, default=7,
                        help='input dimension')
    parser.add_argument('--n-classes', type=int, default=2,
                        help='output dimension')

    # Training parameters
    # parser.add_argument('--lr', type=float, default=1e-4,
    #                     help='learning rate (default: 1e-4)')
    parser.add_argument('--lr', type=float, default=1e-5,
                        help='learning rate (default: 1e-4)')
    parser.add_argument('--wd', type=float, default=5e-4,
                        help='weight decay (default: 5e-4)')
    parser.add_argument('--batch-size', type=int, default=256,
                        help='input batch size for training')
    parser.add_argument('--epoch', type=int, default=100,
                        help='number of epochs to train')
    parser.add_argument('--pre-epoch', type=int, default=50,
                        help='number of pre-train epochs')
    parser.add_argument('--pretrain', type=bool, default=True,
                        help='whether use pre-training')

    # Model parameters
    parser.add_argument('--lamda', type=float, default=1,
                        help='coefficient of the reconstruction loss')
    parser.add_argument('--beta', type=float, default=1,
                        help=('coefficient of the regularization term on '
                              'clustering'))

    # [7, 5, 5, 21, 2, 21, 5, 5, 7]
    parser.add_argument('--hidden-dims', default=[5, 5, 21],
                        help='learning rate (default: 1e-4)')
    parser.add_argument('--latent_dim', type=int, default=2,
                        help='latent space dimension')
    parser.add_argument('--n-clusters', type=int, default=7,
                        help='number of clusters in the latent space')

    # Utility parameters
    parser.add_argument('--n-jobs', type=int, default=1,
                        help='number of jobs to run in parallel')
    parser.add_argument('--cuda', type=bool, default=True,
                        help='whether to use GPU')
    parser.add_argument('--log-interval', type=int, default=10,
                        help=('how many batches to wait before logging the '
                              'training status'))

    args = parser.parse_args()

    # Entry-point da aplicação

    # Carregando todos os arquivos Dlis da pasta Data
    dli = []
    filenames = []
    pocos = []
    for file in glob.glob(r'**/Data' + "/*.dlis", recursive=True):
        leitura, *tail = dlis.load(f'{file}')
        pocos.append(file[5:14])
        filenames.append(file)
        dli.append(leitura)

    frames = []
    for file in dli:
        frames.append(file.object('FRAME', '50'))

    # Armazenando as Curvas dos poços em um lista de DataFrames Pandas

    dlis_df = []

    # lista das curvas utilizadas
    lista_curvas = ['TDEP', 'GR', 'TENS', 'BSZ', 'NPHI', 'CALI',
                    'RHOB', 'DRHO', 'PE', 'HDRS', 'HMRS', 'DTC', 'LLD', 'LLS', 'BS']

    for data in frames:
        try:
            channel_dict = [
                x.name for x in data.channels if x.name in lista_curvas]
            curves = data.curves()
            # Cria um DF com as curvas especificadas no dict
            dlis_df.append(pd.DataFrame(curves[channel_dict]))
            # ordena em função da profundidade e transforma os valores -999.25 em nulos
            dlis_df[-1].sort_values('TDEP', inplace=True)
            dlis_df[-1].reset_index(drop=True, inplace=True)
            dlis_df[-1].replace([-999.25], [None], inplace=True)
            dlis_df[-1] = dlis_df[-1].round(4)
        except:
            pass

    # Chamada da Função caso deseje exportar os dados das curvas para um csv
    # exportData(dlis_df)

    # Aplicação das transformações do conjunto de dados original
    dlis_df = dpp.BStoBSZ(dlis_df)
    dlis_df = dpp.NPHItransform(dlis_df)
    dlis_df = dpp.addDCALIfilter(dlis_df)
    dlis_df = dpp.renomearCurvas(dlis_df)
    dlis_df = dpp.removeFalha(dlis_df)

    dlis_concat = dpp.concatenaDF(dlis_df)
    dlis_concat = dpp.dropColumns(dlis_concat)

    # Transformação dos dados do Dataframe em Float
    dlis_concat = dpp.dataTOfloat(dlis_concat)

    dataset = dpp.dataToTensorToNormal(dlis_concat)

    print(dataset)

    train_loader = dpp.loadDataloader(dataset, args.batch_size)

    # Execução do Modelo
    model = DCN(args)
    rec_loss_list, siscore_list, davies_list = solver(
        args, model, train_loader, dlis_df)
