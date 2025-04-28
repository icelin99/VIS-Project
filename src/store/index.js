import { createStore } from 'vuex'

export default createStore({
    state: {
        originalNodes: [],
        originalLinks: [],
        filteredNodes: [],
        filteredLinks: [],
        countries: [],
        filterConditions: {
            nodeTypes: [],
            countries: [],
            relations: []
        },
        selectedNodeId: null
    },
    mutations: {
        setOriginalData(state, { nodes, links }) {
            state.originalNodes = nodes
            state.originalLinks = links
        },
        setFilteredData(state, { nodes, links }) {
            state.filteredNodes = nodes
            state.filteredLinks = links
        },
        setFilterConditions(state, conditions) {
            state.filterConditions = { ...state.filterConditions, ...conditions }
        },
        setCountries(state, countries) {
            state.countries = countries
        },
        setSelectedNodeId(state, nodeId) {
            state.selectedNodeId = nodeId
        }
    },
    actions: {
        async loadData({ commit, dispatch }) {
            try {
                console.log('开始加载数据...');
                const response = await fetch('/assets/mc1_clean.json');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                console.log('节点数据加载成功，节点数量:', data.nodes.length);
                console.log('连接数据加载成功，连接数量:', data.links.length);
                
                // 验证数据格式
                if (!Array.isArray(data.nodes) || !Array.isArray(data.links)) {
                    throw new Error('数据格式错误：nodes 和 links 必须是数组');
                }
                
                // 设置原始数据
                commit('setOriginalData', {
                    nodes: data.nodes,
                    links: data.links
                });

                // 设置默认筛选条件
                commit('setFilterConditions', {
                    nodeTypes: ['person', 'organization'],
                    countries: [] // 国家数据还未加载，先设为空
                });

                // 加载国家数据
                const countryResponse = await fetch('/assets/country_counts.csv');
                if (!countryResponse.ok) {
                    throw new Error(`HTTP error! status: ${countryResponse.status}`);
                }
                const countryText = await countryResponse.text();
                const countries = countryText.split('\n')
                    .slice(1) // 跳过标题行
                    .filter(line => line.trim()) // 过滤空行
                    .map(line => {
                        const [country, count] = line.split(',');
                        return {
                            value: country,
                            label: `${country} (${count})`
                        };
                    });
                
                console.log('国家数据加载成功，数量:', countries.length);
                commit('setCountries', countries);

                // 更新筛选条件中的国家（选择所有国家）
                commit('setFilterConditions', {
                    countries: countries.map(country => country.value)
                });
                
                // 应用筛选
                dispatch('applyFilters');
                
                console.log('所有数据已成功提交到 store');
            } catch (error) {
                console.error('加载数据失败:', error);
                console.error('错误详情:', error.message);
                if (error.stack) {
                    console.error('错误堆栈:', error.stack);
                }
            }
        },
        applyFilters({state, commit}) {
            const {nodeTypes, countries} = state.filterConditions;
            console.log('应用筛选条件:', { nodeTypes, countries });

            // 检查是否选择了所有国家
            const isAllCountriesSelected = countries.length === state.countries.length;
            console.log('是否选择所有国家:', isAllCountriesSelected);

            // 计算每个节点的连接数
            const nodeLinkCounts = {};
            state.originalLinks.forEach(link => {
                const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
                const targetId = typeof link.target === 'object' ? link.target.id : link.target;
                nodeLinkCounts[sourceId] = (nodeLinkCounts[sourceId] || 0) + 1;
                nodeLinkCounts[targetId] = (nodeLinkCounts[targetId] || 0) + 1;
            });

            // 首先过滤节点，并添加连接数属性
            const filteredNodes = state.originalNodes.filter(node => {
                // 连接数筛选
                const linkCount = nodeLinkCounts[node.id] || 0;
                const linkCountMatch = linkCount >= 5;
                
                // 节点类型筛选
                const typeMatch = nodeTypes.includes(node.type);
                
                // 国家筛选：   
                const countryMatch = 
                    isAllCountriesSelected || 
                    countries.length === 0 || 
                    countries.includes(node.country);
                
                if (linkCountMatch && typeMatch && countryMatch) {
                    // 添加连接数属性
                    node.linkCount = linkCount;
                    return true;
                }
                return false;
            });

            // 获取过滤后节点的ID集合
            const filteredNodeIds = new Set(filteredNodes.map(node => node.id));
            
            // 过滤连接：只保留两端都在过滤后节点集合中的连接
            const filteredLinks = state.originalLinks.filter(link => {
                const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
                const targetId = typeof link.target === 'object' ? link.target.id : link.target;
                return filteredNodeIds.has(sourceId) && filteredNodeIds.has(targetId);
            });

            console.log('筛选后的数据:', {
                nodes: filteredNodes.length,
                links: filteredLinks.length,
                removedNodes: state.originalNodes.length - filteredNodes.length,
                removedLinks: state.originalLinks.length - filteredLinks.length
            });

            // 更新过滤后的数据
            commit('setFilteredData', {
                nodes: filteredNodes,
                links: filteredLinks
            });
        }
    }
})