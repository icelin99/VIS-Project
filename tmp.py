import json


with open('./src/assets/nodes_coef.json','r') as f:
    data = json.load(f)

for i in range(len(data)):
    data[i]['id'] = str(data[i]['id'])

with open('./src/assets/nodes_coef.json','w') as f:
    json.dump(data, f, indent=4)