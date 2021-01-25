# build graph
# https://stackoverflow.com/questions/25108472/generating-a-feature-vector-for-nodes-and-edges-in-networkx
# for each node, add a feature vector which is the USE embeddings
# felisia's previous code:
# https://github.com/alphagov/govuk-network-embedding/blob/master/notebooks/graphsage/train_graphsage_v2.ipynb
# look at this link
# https://crowintelligence.org/2020/06/22/graph-theory-and-network-science-for-natural-language-processing-part-1/
# https://medium.com/stellargraph/do-i-know-you-flexible-unsupervised-and-semi-supervised-graph-models-with-deep-graph-infomax-96fbfd63ec31
# note that Stellargraph is ideally used with Python v3.6 at the moment, so this is running in Conda stellar_graph

import networkx as nx
import numpy as np
import pandas as pd
import os
import pickle
from tqdm import tqdm
from stellargraph import StellarGraph
from stellargraph.mapper import CorruptedGenerator, FullBatchNodeGenerator
from stellargraph.layer import GCN, DeepGraphInfomax
from tensorflow.keras.callbacks import EarlyStopping
import tensorflow as tf
from tensorflow.keras import Model
from tensorflow.keras.optimizers import Adam
from stellargraph.utils import plot_history
from sklearn import model_selection
from sklearn.linear_model import LogisticRegression
import random
from matplotlib import pyplot as plt
from tensorflow.keras.utils import plot_model
from sklearn.manifold import TSNE

PROCESSED_DIR = os.getenv('DIR_DATA_PROCESSED')

# declaring the graph
G = nx.DiGraph()

# adding nodes to the graph
# data from `notebooks/recommend-content-dgi/01_data_pull_use.py`
use_embeddings = pd.read_csv(filepath_or_buffer=PROCESSED_DIR + '/embeddings_use_large_2000_df.csv')
use_embeddings.shape

# populate nodes of graph
node_content_id_map = {}
for i in tqdm(range(0, use_embeddings.shape[0], 1)):
    feature_vector = np.array(use_embeddings.iloc[i, 0:512])
    node_content_id = use_embeddings.iloc[i, 512]
    # this is where the node is added
    G.add_node(i, v=feature_vector)
    # also to keep track of the node mapping, from the content_id to the node id
    node_content_id_map[node_content_id] = i

# check the contents of one of the new nodes
G.nodes[0]['v']

del feature_vector, node_content_id
# adding edges to the graph
# https://networkx.org/documentation/networkx-2.0/reference/classes/generated/networkx.Graph.add_weighted_edges_from.html
pickle_file = open('data/relationship_weights.bin', 'rb')
relationship_weights = pickle.load(pickle_file)

found_dict = {}
not_found_dict = {}
# populate edges of graph
for i in tqdm(range(0, len(relationship_weights), 1)):
    edge_dict = relationship_weights[i]
    try:
        node_id_m = node_content_id_map[edge_dict['m.contentID']]
        found_dict[edge_dict['m.contentID']] = found_dict.get(edge_dict['m.contentID'], 0) + 1
    except KeyError:
        node_id_m = None
        not_found_dict[edge_dict['m.contentID']] = not_found_dict.get(edge_dict['m.contentID'], 0) + 1
    try:
        node_id_n = node_content_id_map[edge_dict['n.contentID']]
        found_dict[edge_dict['n.contentID']] = found_dict.get(edge_dict['n.contentID'], 0) + 1
    except KeyError:
        node_id_n = None
        not_found_dict[edge_dict['n.contentID']] = not_found_dict.get(edge_dict['n.contentID'], 0) + 1
    if (node_id_m is not None) and (node_id_n is not None):
        # edge_tuple = (node_id_m, node_id_n, edge_dict['r.weight'])
        G.add_edge(node_id_m, node_id_n, weight=edge_dict['r.weight'])

del node_id_m, node_id_n, edge_dict
# check the graph exists: this looks suspicious in that the in and out degree are the same to within 4dp
nx.info(G)

# the fact "not_found_dict" is not zero means that the two datasets have different data
# the next steps here are to create a more complete dataset by downloading everything at once from neo4j
len(found_dict)
len(not_found_dict)


# now the build of the Deep Graph Infomax embeddings model
# https://stellargraph.readthedocs.io/en/v1.2.1/demos/embeddings/deep-graph-infomax-embeddings.html
# note that there is an alternative graph called the StellarDiGraph, but no difference in performance was seen
# the lack in difference in performance suggests that the networkx graph is not really taking account of direction
stellar_G = StellarGraph.from_networkx(graph=G, node_features="v")
print(stellar_G.info())

# https://stellargraph.readthedocs.io/en/stable/api.html#stellargraph.mapper.FullBatchNodeGenerator
fullbatch_generator = FullBatchNodeGenerator(G=stellar_G, sparse=False, weighted=True, method='gcn')

# intuition for GNN:
# https://medium.com/analytics-vidhya/getting-the-intuition-of-graph-neural-networks-a30a2c34280d
# understanding GCN:
# https://towardsdatascience.com/understanding-graph-convolutional-networks-for-node-classification-a2bfdb7aba7b
# stellargraph implementation
# https://medium.com/stellargraph/do-i-know-you-flexible-unsupervised-and-semi-supervised-graph-models-with-deep-graph-infomax-96fbfd63ec31  # noqa: E501
# 2-layer GCN model
# https://stellargraph.readthedocs.io/en/stable/api.html?highlight=gcn#stellargraph.layer.GCN
gcn_model = GCN(layer_sizes=[128, 128], activations=["relu", "relu"], generator=fullbatch_generator)

# data generator to shuffle node features for corrupted graph
corrupted_generator = CorruptedGenerator(fullbatch_generator)
# produce object for training model
gen = corrupted_generator.flow(stellar_G.nodes())

# create Deep Graph Infomax model
infomax = DeepGraphInfomax(gcn_model, corrupted_generator)
x_in, x_out = infomax.in_out_tensors()

# train model
model = Model(inputs=x_in, outputs=x_out)
model.compile(loss=tf.nn.sigmoid_cross_entropy_with_logits, optimizer=Adam(lr=1e-3))
model.summary()
# create a model image, print to file
plot_model(model, show_shapes=True, to_file="model.png")

epochs = 1000
es = EarlyStopping(monitor="loss", min_delta=0, patience=20)
# next line triggers the model to train, run time 10 mins with a GTX 1070
# 90 minutes on CPU
history = model.fit(gen, epochs=epochs, verbose=0, callbacks=[es])
plot_history(history)

# playing with the embedding vectors, obtain trained node embedding model
x_emb_in, x_emb_out = gcn_model.in_out_tensors()

# for full batch models, squeeze out the batch dim (which is 1)
x_out = tf.squeeze(x_emb_out, axis=0)
emb_model = Model(inputs=x_emb_in, outputs=x_out)

# get the target, document type is the best I can think of at short notice
text_df = pd.read_csv('data/processed/text_use_large_2000_df.csv')
text_df.head()
text_df['document_type'].value_counts()

# build a list of labels corresponding to the order of the nodes
label_dict = dict(zip(text_df.content_id, text_df.document_type))

node_series = []
label_series = []
for key in node_content_id_map.keys():
    node_series.append(node_content_id_map[key])
    label_series.append(label_dict[key])

node_label_df = (pd.DataFrame({'node': node_series,
                              'label': label_series})
                 .sort_values(['node']))

train_subjects, test_subjects = model_selection.train_test_split(
    node_label_df, train_size=0.7, test_size=None, stratify=None
)


test_gen = fullbatch_generator.flow(test_subjects.index)
train_gen = fullbatch_generator.flow(train_subjects.index)

test_embeddings = emb_model.predict(test_gen)
train_embeddings = emb_model.predict(train_gen)

lr = LogisticRegression(multi_class="auto", solver="lbfgs", max_iter=2000)
lr.fit(train_embeddings, train_subjects['label'])

y_pred = lr.predict(test_embeddings)
test_acc = (y_pred == test_subjects['label']).mean()
test_acc

# random prediction
random_preds = list(train_subjects['label'].values)
random_test_preds = random.choices(random_preds, k=len(test_subjects))
random_acc = (random_test_preds == test_subjects['label']).mean()
random_acc

# visualisation with TSNE
all_embeddings = emb_model.predict(fullbatch_generator.flow(stellar_G.nodes()))

y = node_label_df['label'].astype("category")
trans = TSNE(n_components=2)
emb_transformed = pd.DataFrame(trans.fit_transform(all_embeddings), index=stellar_G.nodes())
emb_transformed["label"] = y

alpha = 0.7

fig, ax = plt.subplots(figsize=(7, 7))
ax.scatter(
    emb_transformed[0],
    emb_transformed[1],
    c=emb_transformed["label"].cat.codes,
    cmap="jet",
    alpha=alpha,
)
ax.set(aspect="equal", xlabel="$X_1$", ylabel="$X_2$")
plt.title("TSNE visualization of GCN embeddings for Gov Graph dataset")
plt.show()

# output all embeddings to look in Annoy at some similar content
# need to double check there was no shuffling of the data: this is reliant on all use_embeddings being
# in the local graph
dgi_embeddings_df = pd.DataFrame(all_embeddings)
assert dgi_embeddings_df.shape[0] == use_embeddings.shape[0]
dgi_embeddings_df['content_id'] = use_embeddings.iloc[:, 512]

dgi_embeddings_df.to_csv(PROCESSED_DIR + '/dgi_embeddings_df.csv', index=False, header=True, mode='w')
