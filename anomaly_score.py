import json
import networkx as nx
import numpy as np
from tqdm import tqdm

with open("mc1_clean.json","r",encoding="utf-8") as f:
    data = json.load(f)
G = nx.node_link_graph(data, directed=True, multigraph=True)

with open("tsne_embeddings.json","r",encoding="utf-8") as f:
    raw = json.load(f)
tsne_emb = {k: np.array(v) for k,v in raw.items()}

def dist(u,v):
    return np.linalg.norm(tsne_emb[str(u)] - tsne_emb[str(v)])

wcc = list(nx.weakly_connected_components(G))
rv_dict = {}
for comp in wcc:
    vessels = sum(1 for n in comp if G.nodes[n].get("type")=="vessel")
    ratio = vessels / len(comp)
    for n in comp:
        rv_dict[n] = ratio
rv_hat = np.mean(list(rv_dict.values()))

nbr1 = {}
nbr2 = {}
for u in G.nodes():
    # 一阶
    s = set(G.successors(u)) | set(G.predecessors(u))
    nbr1[u] = s
    # 二阶
    s2 = set()
    for v in s:
        s2 |= set(G.successors(v)) | set(G.predecessors(v))
    nbr2[u] = s2 - {u}

illegal = {979893388, "Oceanfront Oasis Inc Carriers"}
def compute_C(u, L=4):
    count = 0
    path = [u]
    visited = {u}

    def dfs(curr, depth):
        nonlocal count
        if depth >= L:
            return
        for nxt in G.successors(curr):
            if nxt == u:
                if any(node in illegal for node in path):
                    count += 1
            elif nxt not in visited:
                visited.add(nxt)
                path.append(nxt)
                dfs(nxt, depth+1)
                path.pop()
                visited.remove(nxt)

    dfs(u, 0)
    return count

def compute_F12_P12(u):
    nbrs = nbr1[u] | nbr2[u]
    F12 = sum(1 for x,y,d in G.edges(nbrs, data=True)
              if d.get("type")=="family_relationship")
    P12 = sum(1 for v in nbrs
              if G.nodes[v].get("type")=="political_organization")
    return F12, P12

raw_scores = {}
for u in tqdm(G.nodes(), desc="Anomaly scoring"):
    Rv = rv_dict[u]
    F12, P12 = compute_F12_P12(u)
    C = compute_C(u, L=4)
    d1 = dist(u, 979893388)
    d2 = dist(u, "Oceanfront Oasis Inc Carriers")
    S = (Rv - rv_hat + 0.1*F12 + P12 - 0.5*d1 + d2 + C)
    raw_scores[u] = S

# 归一化
vals = np.array(list(raw_scores.values()))
mn, mx = vals.min(), vals.max()
norm = {u:(raw_scores[u]-mn)/(mx-mn)*100 for u in raw_scores}

# 写文件
out = [{"id":u, "raw_score":raw_scores[u], "norm_score":norm[u]} for u in G.nodes()]
with open("nodes_coef.json","w",encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print("Done: mc1_scores_tsne_fast.json generated.")
