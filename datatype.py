import json
import pandas as pd
import re
import networkx as nx

with open('public/assets/MC1.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

raw_nodes = data.get('nodes', [])
raw_edges = data.get('links', [])

def clean_node(node):
    node = node.copy()
    node_id = str(node.get('id', ''))
    node['id'] = re.sub(r"[^\w\s\-\.\&]", "", node_id).strip()
    if 'type' not in node:
        lower = node['id'].lower()
        if any(k in lower for k in ['gmbh','co','company','ltd']):
            node['type'] = 'company'
        elif re.match(r"[A-Z]{2,3}$", node['id']):
            node['type'] = 'location'
        elif re.search(r"[a-z]+\s[a-z]+", lower):
            node['type'] = 'person'
        else:
            node['type'] = 'unknown'
    return node

cleaned_nodes = [clean_node(n) for n in raw_nodes]
df_nodes = pd.DataFrame(cleaned_nodes)

df_edges = pd.DataFrame(raw_edges)
df_edges['source'] = df_edges['source'].astype(str)
df_edges['target'] = df_edges['target'].astype(str)
df_edges['type']   = df_edges['type'].fillna('unknown')

type_counts = df_nodes['type'].value_counts().rename_axis('Entity Type').reset_index(name='Count')
country_counts = df_nodes['country'].fillna('Unknown').value_counts().rename_axis('Country').reset_index(name='Count')
edge_type_counts = df_edges['type'].value_counts().rename_axis('Edge Type').reset_index(name='Count')

# 构图并算度 & PageRank
G = nx.MultiDiGraph()
for _, r in df_nodes.iterrows():
    G.add_node(r['id'], type=r['type'])
for _, r in df_edges.iterrows():
    G.add_edge(r['source'], r['target'], type=r['type'], weight=r.get('weight', 1))

df_in  = pd.DataFrame(G.in_degree(),  columns=['id','in_degree'])
df_out = pd.DataFrame(G.out_degree(), columns=['id','out_degree'])
df_deg = df_in.merge(df_out, on='id')
top_in  = df_deg.nlargest(10, 'in_degree')
top_out = df_deg.nlargest(10, 'out_degree')

G_simple = nx.DiGraph()
for u, v, data_e in G.edges(data=True):
    w = data_e.get('weight', 1)
    if G_simple.has_edge(u, v):
        G_simple[u][v]['weight'] += w
    else:
        G_simple.add_edge(u, v, weight=w)

pr = nx.pagerank(G_simple, weight='weight')
df_pr = (
    pd.DataFrame({
        'id': list(pr.keys()),
        'pagerank': list(pr.values())
    })
    .astype({'pagerank': float})
    .nlargest(10, 'pagerank')
    .reset_index(drop=True)
)

# 国家与类型交叉分布：每个实体的 country 字段和 type 字段放到一起，统计出每个国家中有多少家 company、多少个 organization、多少个 person、多少个 location 等
cross = df_nodes.groupby(['country', 'type']).size().reset_index(name='Count')

results = {
    '节点类型分布': type_counts,
    '国家分布': country_counts,
    '边类型分布': edge_type_counts,
    'Top 10 入度节点': top_in,
    'Top 10 出度节点': top_out,
    'Top 10 PageRank 节点': df_pr,
    '国家与类型交叉分布': cross
}

type_counts.to_csv('data_analysis/type_counts.csv', index=False)
country_counts.to_csv('data_analysis/country_counts.csv', index=False)
edge_type_counts.to_csv('data_analysis/edge_type_counts.csv', index=False)
top_in.to_csv('data_analysis/top_in.csv', index=False)
top_out.to_csv('data_analysis/top_out.csv', index=False)
df_pr.to_csv('data_analysis/top_pagerank.csv', index=False)
cross.to_csv('data_analysis/country_type_cross.csv', index=False)
