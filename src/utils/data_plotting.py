import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Função para criar a matriz de confusão
def cria_matriz_confusao(matriz_confusao, modelo):
    """
    Cria (plota) matriz de confusão

    Args:
        matriz_confusao (numpy.ndarray): matriz de confusão criada a partir de confusion_matrix().
        modelo (sklearn.ensemble._forest.RandomForestClassifier): modelo RandomForestClassifier()
    """

    # Normaliza a matriz de confusão por linha
    matriz_confusao_normalizada = matriz_confusao.astype('float') / matriz_confusao.sum(axis=1)[:, np.newaxis]
    
    # Rótulos das litologias
    categorias = modelo.classes_

    # Cria strings com os valores absolutos e porcentagem de cada célula da matriz
    num_absoluto_porcentagem = np.empty_like(matriz_confusao, dtype=object)
    for i in range(matriz_confusao.shape[0]):
        for j in range(matriz_confusao.shape[1]):
            num_absoluto_porcentagem[i, j] = f'{matriz_confusao[i, j]}\n{matriz_confusao_normalizada[i, j]:.1%}'
    
    # Tamanho da figura
    plt.figure(figsize=(12,8))
    
    # Objeto dos eixos
    ax = plt.gca()
    
    # Remove traços dos eixos
    ax.tick_params(axis='x', which='both', bottom=False, top=False)  
    ax.tick_params(axis='y', which='both', left=False, right=False)
    
    # Cria o heatmap
    heatmap = sns.heatmap(matriz_confusao_normalizada, 
                annot=num_absoluto_porcentagem, 
                fmt='',
                cmap='BuGn', 
                xticklabels=categorias, 
                yticklabels=categorias,
                cbar_kws={'label': 'Proporção da Litologia'},
                annot_kws={"size": 12},
                linewidths=0.7,
                linecolor='gray')
    
    # Modifica a barra de cores para mostrar de 0% a 100%
    cbar = heatmap.collections[0].colorbar
    cbar.set_ticks([0, 0.25, 0.5, 0.75, 1])
    cbar.set_ticklabels(['0%', '25%', '50%', '75%', '100%'])
    
    # Rótulos dos eixos
    plt.xlabel('Predito', fontsize=12)
    plt.ylabel('Verdadeiro', fontsize=12)
    
    plt.show()