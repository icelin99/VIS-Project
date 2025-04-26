import json


filename = './src/assets/tree_relation.json'

with open(filename, 'r') as f:
    data = json.load(f)
    
links = data['links']
# links = links[-2:]
nodes = {}
for link in links:    
    source = str(link['source'])
    if source not in nodes:
        nodes[source] = 1
    else:
        nodes[source] += 1

json_data = {'name': nodes}
json_data_sorted = sorted(json_data['name'].items(), key=lambda x: x[1], reverse=True)

json_data_sorted = json_data_sorted[:10]
for i in range(len(json_data_sorted)):
    json_data_sorted[i] = {'name':json_data_sorted[i][0]}

final_data = {'nodes': json_data_sorted}

with open('./src/assets/tree_nodes.json', 'w') as f:
    json.dump(final_data, f, ensure_ascii=False, indent=4)