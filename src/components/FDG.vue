<template>
    <div class="visualization-panel">
        <div class="vis-container">
            <div id="force-directed-graph"></div>
            <div id="graph-tooltip"></div>
        </div>
    </div>
</template>

<script>
import * as d3 from 'd3'
import { mapState } from 'vuex'
export default {
    name: 'FDG',
    computed: {
        ...mapState(['filteredNodes', 'filteredLinks', 'selectedNodeId'])
    },
    data() {
        return {
            simulation: null,
            svg: null,
            width: 0,
            height: 0,
            currentNodes: [],
            typeColors: {
                'person': '#FFB6C1',
                'organization': '#4ECDC4',
                'company': '#45B7D1',
                'political_organization': '#96CEB4',
                'location': '#FFEEAD',
                'vessel': '#D4A5A5',
                'event': '#9B59B6',
                'movement': '#3498DB',
                'unknown': '#95A5A6'
            },
            linkColors: {
                'membership': '#B0C4DE',     
                'partnership': '#A8D4B2',    
                'ownership': '#C7B8E0',       
                'family_relationship': '#C2B8A3'  
            }
        }
    },
    mounted() {
        const container = document.getElementById('force-directed-graph')
        this.width = container.clientWidth
        this.height = container.clientHeight
        this.initGraph()
        this.handleResize() // 初始化时调用一次 handleResize 获取容器尺寸
        window.addEventListener('resize', this.handleResize)
    },
    beforeUnmount() {
        window.removeEventListener('resize', this.handleResize)
    },
    watch: {
        filteredNodes: {
            handler(newNodes) {
                if (newNodes && newNodes.length > 0) {
                    this.updateVisualization()
                }
            },
            immediate: true
        },
        selectedNodeId: {
            handler(newId) {
                // 更新节点样式
                this.svg.selectAll('.node circle')
                    .transition()
                    .duration(200)
                    .style('stroke', d => d.id === newId ? '#FF0000' : '#fff')
                    .style('stroke-width', d => d.id === newId ? 3 : 1.5);
            }
        }
    },
    methods: {
        handleResize() {
            const container = document.getElementById('force-directed-graph')
            this.width = container.clientWidth
            this.height = container.clientHeight

            this.svg
                .attr('width', this.width)
                .attr('height', this.height)

             // 更新力导向图中心点
            if (this.simulation) {
                this.simulation.force('center', d3.forceCenter(this.width / 2, this.height / 2))
                this.simulation.alpha(0.3).restart()
            }
        },
        initGraph() {
            const container = document.getElementById('force-directed-graph')
            this.width = container.clientWidth
            this.height = container.clientHeight

            this.svg = d3.select('#force-directed-graph')
                .append('svg')
                .attr('width', this.width)
                .attr('height', this.height)

            // add zoom behavior
            this.svg.append('g')
                .attr('class', 'graph-container')

            this.svg.call(d3.zoom()
                .scaleExtent([0.1, 4])
                .on('zoom', (event) => {
                    this.svg.select('.graph-container')
                        .attr('transform', event.transform)
                }))
        },
        createGraph() {
            const data_nodes = this.filteredNodes
            const data_links = this.filteredLinks
            
            // 找出最大和最小连接数
            const linkCounts = this.filteredNodes.map(node => node.linkCount);
            const maxLinks = Math.max(...linkCounts);
            const minLinks = Math.min(...linkCounts);

            // 创建半径和中心力的比例尺
            const radiusScale = d3.scaleLinear()
                .domain([minLinks, maxLinks])
                .range([5, 20]); // 节点半径范围：5-20

            console.log('节点连接数统计：', {
                maxLinks,
                minLinks,
                nodeCounts: this.filteredNodes
                    .sort((a, b) => b.linkCount - a.linkCount)
                    .slice(0, 10)
                    .map(node => ({id: node.id, count: node.linkCount}))
            });
            
            // 首先找出所有边的权重范围
            const weights = data_links.map(d => d.weight);
            const maxWeight = Math.max(...weights);
            const minWeight = Math.min(...weights);
            console.log('边的权重范围：', { minWeight, maxWeight });

            // 创建权重到距离的线性映射
            const distanceScale = d3.scaleLinear()
                .domain([minWeight, maxWeight])
                .range([150, 50]); // 增加整体距离范围

            this.simulation = d3.forceSimulation(data_nodes)
                .force('link', d3.forceLink(data_links)
                    .id(d => d.id)
                    .distance(d => distanceScale(d.weight))
                    .strength(0.5))
                .force('charge', d3.forceManyBody()
                    .strength(d => d.linkCount < 15 ? -30 : -100)
                    .distanceMin(10)
                    .distanceMax(200))
                .force('center', d3.forceCenter(this.width / 2, this.height / 2))
                .force('collision', d3.forceCollide()
                    .radius(d => radiusScale(d.linkCount) + 5)
                    .strength(0.5))
                .force('x', d3.forceX(this.width / 2).strength(0.02))
                .force('y', d3.forceY(this.height / 2).strength(0.02))
                .alpha(1)
                .alphaDecay(0.01)
                .velocityDecay(0.3)
                .restart();

            // 确保节点没有固定位置
            data_nodes.forEach(node => {
                node.fx = null;
                node.fy = null;
            });

            const container = this.svg.select('.graph-container')
            
            // 保存 this 的引用
            const self = this;

            // 创建连线
            const links = container.selectAll('.link')
                .data(data_links)
                .enter()
                .append('line')
                .attr('class', 'link')
                .style('stroke', (d) => {
                    if (d.weight > 0.99) {
                        return '#FF0000'; // 高权重用红色
                    }
                    return self.linkColors[d.type];
                })
                .style('stroke-opacity', d => d.weight > 0.99 ? 0.8 : 0.3)
                .style('stroke-width', d => {
                    if (d.weight > 0.99) {
                        return d.weight * 4; // 高权重的连接加粗
                    }
                    return d.weight * 2;
                })
                .on('mouseover', (event, d) => {
                    // 高亮当前边
                    d3.select(event.target)
                        .style('stroke-opacity', 1)
                        .style('stroke', (d) => {
                            if (d.weight > 0.99) {
                                return '#FF0000';
                            }
                            return self.linkColors[d.type];
                        });

                    // 高亮相连节点
                    const nodes = container.selectAll('.node')
                        .filter(node => node.id === d.source.id || node.id === d.target.id);
                    nodes.each((node, i, elements) => {
                        const el = d3.select(elements[i]);
                        el.select('circle')
                            .transition()
                            .duration(200)
                            .attr('r', node => radiusScale(node.linkCount) * 1.5);
                        el.select('text')
                            .transition()
                            .duration(200)
                            .style('font-weight', 'bold');
                    });

                    // 显示tooltip
                    const tooltip = d3.select('#graph-tooltip');
                    tooltip.style('display', 'block')
                        .html(`
                            <div class="tooltip-content">
                                <div>Source: ${d.source.id}</div>
                                <div>Target: ${d.target.id}</div>
                                <div>Type: ${d.type || 'Unknown'}</div>
                                <div>Weight: ${d.weight?.toFixed(4) || 'N/A'}</div>
                                <div>Distance: ${distanceScale(d.weight)?.toFixed(4) || 'N/A'}</div>
                                <div>Color: ${self.linkColors[d.type] || '#999'}</div>
                            </div>
                        `)
                        .style('left', (event.pageX + 10) + 'px')
                        .style('top', (event.pageY - 10) + 'px');
                })
                .on('mouseout', (event, d) => {
                    // 恢复边的样式
                    d3.select(event.target)
                        .style('stroke-opacity', 0.3);

                    // 恢复节点样式
                    const nodes = container.selectAll('.node')
                        .filter(node => node.id === d.source.id || node.id === d.target.id);
                    nodes.each((node, i, elements) => {
                        const el = d3.select(elements[i]);
                        el.select('circle')
                            .transition()
                            .duration(200)
                            .attr('r', node => radiusScale(node.linkCount));
                        el.select('text')
                            .transition()
                            .duration(200)
                            .style('font-size', node => {
                                const size = (node.linkCount - minLinks) / (maxLinks - minLinks) * 4 + 8;
                                return `${size}px`;
                            })
                            .style('font-weight', 'normal');
                    });

                    // 隐藏tooltip
                    d3.select('#graph-tooltip').style('display', 'none');
                });

            // 创建节点组
            const nodes = container.selectAll('.node')
                .data(data_nodes)
                .enter()
                .append('g')
                .attr('class', 'node')
                .call(d3.drag()
                    .on('start', this.dragStarted)
                    .on('drag', this.dragged)
                    .on('end', this.dragEnded))
                .on('click', this.handleNodeClick);  // 添加点击事件

            // 添加节点圆圈
            nodes.append('circle')
                .attr('r', d => radiusScale(d.linkCount))
                .style('fill', d => this.typeColors[d.type] || '#95A5A6')
                .style('stroke', d => d.id === this.selectedNodeId ? '#FF0000' : '#fff')  // 选中节点红色边框
                .style('stroke-width', d => d.id === this.selectedNodeId ? 3 : 1.5);  // 选中节点边框加粗

            // 添加节点标签
            nodes.append('text')
                .text(d => d.id)
                .attr('dx', d => radiusScale(d.linkCount) + 2)
                .attr('dy', 4)
                .style('font-family', 'Arial, sans-serif')
                .style('font-size', d => {
                    // 连接数越多，文字越大
                    const size = (d.linkCount - minLinks) / (maxLinks - minLinks) * 4 + 8;
                    return `${size}px`;
                });

            // 添加节点的hover事件
            nodes.on('mouseover', (event, d) => {
                // 高亮当前节点
                const currentNode = d3.select(event.currentTarget);
                currentNode.select('circle')
                    .transition()
                    .duration(200)
                    .attr('r', node => radiusScale(node.linkCount) * 1.5);
                currentNode.select('text')
                    .transition()
                    .duration(200)
                    .style('font-weight', 'bold');

                // 高亮相关连接
                const links = container.selectAll('.link')
                    .filter(link => link.source.id === d.id || link.target.id === d.id);
                links.style('stroke-opacity', 1)
                    .style('stroke', link => {
                        if (link.weight > 0.99) {
                            return '#FF0000';
                        }
                        return self.linkColors[link.type];
                    });

                // 显示tooltip
                const tooltip = d3.select('#graph-tooltip');
                tooltip.style('display', 'block')
                    .html(`
                        <div class="tooltip-content">
                            <div>ID: ${d.id}</div>
                            <div>Type: ${d.type || 'Unknown'}</div>
                            <div>Country: ${d.country || 'N/A'}</div>
                            <div>Connections: ${d.linkCount}</div>
                        </div>
                    `)
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 10) + 'px');
            })
            .on('mouseout', (event, d) => {
                // 恢复节点样式
                const currentNode = d3.select(event.currentTarget);
                currentNode.select('circle')
                    .transition()
                    .duration(200)
                    .attr('r', node => radiusScale(node.linkCount));
                currentNode.select('text')
                    .transition()
                    .duration(200)
                    .style('font-size', node => {
                        const size = (node.linkCount - minLinks) / (maxLinks - minLinks) * 4 + 8;
                        return `${size}px`;
                    })
                    .style('font-weight', 'normal');

                // 恢复连接样式
                const links = container.selectAll('.link')
                    .filter(link => link.source.id === d.id || link.target.id === d.id);
                links.style('stroke-opacity', d => d.weight > 0.99 ? 0.8 : 0.3)
                    .style('stroke', link => {
                        if (link.weight > 0.99) {
                            return '#FF0000';
                        }
                        return self.linkColors[link.type];
                    });

                // 隐藏tooltip
                d3.select('#graph-tooltip').style('display', 'none');
            });

            this.simulation.on('tick', () => {
                links
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y)
                nodes
                    .attr('transform', d => `translate(${d.x}, ${d.y})`)
            })
        },
        dragStarted(event, d) {
            if (!event.active) this.simulation.alphaTarget(0.3).restart()
            d.fx = d.x
            d.fy = d.y
        },
        dragged(event, d) {
            d.fx = event.x
            d.fy = event.y
        },
        dragEnded(event, d) {
            if (!event.active) this.simulation.alphaTarget(0)
            d.fx = null
            d.fy = null
        },
        updateVisualization() {
            if (this.simulation) {
                this.simulation.stop()
            }

            // 清除svg
            d3.select('.graph-container').selectAll('*').remove()

            // 只在有数据时创建图
            if (this.filteredNodes.length > 0) {
                console.log("更新FDG")
                this.createGraph()
            }
        },
        handleNodeClick(event, d) {
            // 提交选中的节点ID
            this.$store.commit('setSelectedNodeId', d.id);
        }
    }
}
</script>

<style scoped>
.visualization-panel {
    height: 100%;
}

.vis-container {
    height: 100%;
}

#force-directed-graph {
    width: 100%;
    height: calc(100% - 10px);
    border-radius: 4px;
    background: #f9f9f9;
}

.node:hover {
    cursor: pointer;
}

.node circle {
    stroke: #fff;
    stroke-width: 2px;
}

.node text {
    pointer-events: none;
}

#graph-tooltip {
    position: absolute;
    display: none;
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 10px;
    font-size: 12px;
    pointer-events: none;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    z-index: 1000;
}

.tooltip-content {
    line-height: 1.5;
}

.tooltip-content div {
    margin: 2px 0;
}

.link {
    transition: all 0.2s;
}

.node circle {
    transition: all 0.2s;
}

.node text {
    transition: all 0.2s;
}
</style>