import numpy as np
np.float = float
import json
import networkx as nx
from node2vec import Node2Vec
from sklearn.manifold import TSNE


with open("mc1_clean.json", "r", encoding="utf-8") as f:
    data = json.load(f)
G = nx.node_link_graph(data, directed=True, multigraph=True)

node2vec = Node2Vec(G,
                    dimensions=128,
                    walk_length=30,
                    num_walks=200,
                    workers=4)
model = node2vec.fit(window=10, min_count=1, batch_words=4)

nodes = list(G.nodes())
embeddings = np.vstack([model.wv[str(n)] for n in nodes])  # shape (N,128)

tsne = TSNE(n_components=2,
            perplexity=30,
            n_iter=1000,
            metric="euclidean",
            random_state=42)
coords = tsne.fit_transform(embeddings)  # shape (N,2)

tsne_dict = {str(nodes[i]): coords[i].tolist() for i in range(len(nodes))}
with open("tsne_embeddings.json", "w", encoding="utf-8") as f:
    json.dump(tsne_dict, f, ensure_ascii=False, indent=2)

print("已生成 tsne_embeddings.json，共含", len(tsne_dict), "个节点的 2D 坐标。")