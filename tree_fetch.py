import json
from collections import defaultdict

def load_data(nodes_file, links_file):
    """加载节点和链接数据"""
    with open(nodes_file, 'r') as f:
        nodes_data = json.load(f)
    
    with open(links_file, 'r') as f:
        links_data = json.load(f)
    
    return nodes_data['nodes'], links_data['links']

def build_hierarchy(links, max_depth=6):
    """构建节点的层级关系"""
    # 创建邻接表
    adjacency = defaultdict(list)
    for link in links:
        source = str(link['source'])
        target = str(link['target'])
        adjacency[source].append((target, link.get('weight', 1.0)))
        # 确保所有节点都在邻接表中
        if target not in adjacency:
            adjacency[target] = []
    
    return adjacency

def find_descendants(adjacency, root_node, max_depth):
    """递归查找所有子节点，并进行去重处理"""
    descendants = []
    visited = set()  # 用于记录已访问的节点
    
    def dfs(node, current_depth, path):
        if current_depth > max_depth:
            return
        
        # 节点去重：如果节点已在更浅的层级出现过，则不再重复添加
        node_key = f"{node}-{current_depth}"  # 考虑节点名和深度作为唯一标识
        
        if node_key in visited:
            return
        visited.add(node_key)
        
        # 记录当前节点信息
        node_info = {
            'name': node,
            'depth': current_depth,
            'path': path + [node]
        }
        descendants.append(node_info)
        
        # 遍历所有子节点
        for child, weight in adjacency.get(node, []):
            dfs(child, current_depth + 1, path + [node])
    
    dfs(root_node, 1, [])
    return descendants

def process_all_nodes(nodes, adjacency, max_depth=6):
    """处理所有根节点"""
    results = {}
    
    for node in nodes:
        root_name = node['name']
        descendants = find_descendants(adjacency, root_name, max_depth)
        
        # 对结果进行层级去重
        unique_descendants = []
        seen = set()
        
        for item in descendants:
            # 使用节点名和深度作为唯一标识
            identifier = (item['name'], item['depth'])
            if identifier not in seen:
                seen.add(identifier)
                unique_descendants.append(item)
        
        results[root_name] = unique_descendants
    
    return results

def save_results(results, output_file):
    """保存结果到JSON文件"""
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

def main():
    # 文件路径
    nodes_file = './src/assets/tree_nodes.json'
    links_file = './src/assets/tree_relation.json'
    output_file = './src/assets/tree_hierarchy.json'
    
    # 最大深度
    max_depth = 3
    
    # 加载数据
    nodes, links = load_data(nodes_file, links_file)
    
    # 构建邻接表
    adjacency = build_hierarchy(links)
    
    # 处理所有根节点
    results = process_all_nodes(nodes, adjacency, max_depth)
    
    # 保存结果
    save_results(results, output_file)
    
    print(f"处理完成，结果已保存到 {output_file}")

if __name__ == '__main__':
    main()