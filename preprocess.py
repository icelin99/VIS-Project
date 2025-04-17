import json

with open('public/assets/MC1.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

nodes = data.get('nodes', [])
edges = data.get('links', data.get('edges', []))

# Filter nodes by type: keep company, organization, person, political_organization and location
allowed_node_types = {'company', 'organization', 'person', 'political_organization', 'location'}
filtered_nodes = [
    n for n in nodes
    if n.get('type') in allowed_node_types
]

# Filter edges by relationship type and weight threshold: keep ownership, partnership, family_relationship, membership and weight ≥ 0.9
allowed_edge_types = {'ownership', 'partnership', 'family_relationship', 'membership'}
weight_threshold = 0.9
filtered_edges = [
    e for e in edges
    if e.get('type') in allowed_edge_types and e.get('weight', 0) >= weight_threshold
]

# 3. Build the filtered graph and save
filtered_graph = {
    "directed": data.get("directed", True),
    "multigraph": data.get("multigraph", True),
    "graph": data.get("graph", {}),
    "nodes": filtered_nodes,
    "links": filtered_edges
}

with open('MC1_filtered.json', 'w', encoding='utf-8') as f:
    json.dump(filtered_graph, f, ensure_ascii=False, indent=2)

# Summary output
print(f"Original nodes: {len(nodes)}, filtered nodes: {len(filtered_nodes)}")
print(f"Original edges: {len(edges)}, filtered edges: {len(filtered_edges)}")
