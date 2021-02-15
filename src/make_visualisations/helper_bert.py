import numpy as np
from sklearn import manifold

from sklearn.metrics.pairwise import cosine_distances
import plotly.graph_objects as go


def plot_distances(word_vectors: np.ndarray,
                   labels: list,
                   dims: int = 2,
                   words_of_interest: list = [],
                   title: str = ''):
    """
    Plot the distances using MDS in 2D or 3D.
    References:
        - Takes in labels from eval_distances in `src.make_features.helper_bert.py`

    :param word_vectors: Array of distance matrix.
    :param labels: List of labels for objects on plot.
    :param dims: Integer of whether you want a 2D or 3D plot. Defaults to 2.
    :param words_of_interest: List of words to highlight with a different colour.
    :param title: String of the title for the plot.
    :return: Plot
    """
    colour = list()
    distances = cosine_distances(word_vectors)

    # separate colours for words that are in `words_of_interest` vs other,
    # where each word will have a _SentenceNumber at the end to differentiate the words coming
    # from difference sentences.
    for lab in labels:
        found = False
        for wrd_int in words_of_interest:
            if wrd_int in lab:
                found = True
                break
        if found:
            colour.append(1)
        else:
            colour.append(0)

    colourscale = [[0, 'darkcyan'], [1, 'white']]

    # distances are precomputed using cosine-similarity and passed to calculate multi-dimensional-scaling
    # with number of dims passed
    mds = manifold.MDS(n_components=dims, dissimilarity='precomputed', random_state=42, max_iter=90000)
    results = mds.fit(distances)

    # get coordinates for each point
    coords = results.embedding_

    # plot
    if dims == 3:
        fig = go.Figure(data=[go.Scatter3d(x=coords[:, 0],
                                           y=coords[:, 1],
                                           z=coords[:, 2],
                                           mode='markers+text',
                                           textposition='top center',
                                           text=labels,
                                           marker=dict(size=10,
                                                       color=colour,
                                                       colorscale=colourscale,
                                                       opacity=0.8))])
    elif dims == 2:
        fig = go.Figure(data=[go.Scatter(x=coords[:, 0],
                                         y=coords[:, 1],
                                         mode='markers+text',
                                         text=labels,
                                         textposition='top center',
                                         marker=dict(size=12,
                                                     color=colour,
                                                     colorscale=colourscale,
                                                     opacity=0.8))])
    else:
        print(f"{dims} dimensions chosen. Please select 2 or 3.")

    fig.update_layout(template='plotly_dark')
    if title != '':
        fig.update_layout(title_text=title)
    fig.show()
