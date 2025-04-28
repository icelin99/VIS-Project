<template>
    <div class="subgraphs-container">
        <div class="subgraph">
            <div id="subgraph-membership" class="subgraph-vis"></div>
        </div>
        <div class="subgraph">
            <div id="subgraph-partnership" class="subgraph-vis"></div>
        </div>
        <div class="subgraph">
            <div id="subgraph-ownership" class="subgraph-vis"></div>
        </div>
        <div class="subgraph">
            <div id="subgraph-family-relationship" class="subgraph-vis"></div>
        </div>
        <div id="subgraph-tooltip"></div>
    </div>
</template>

<script>
import * as d3 from 'd3'
import { mapState } from 'vuex'

export default {
    name: 'SubGraphs',
    data() {
        return {
            simulations: {},
            svgs: {},
            width: 0,
            height: 0,
            linkTypes: ['membership', 'partnership', 'ownership', 'family_relationship'],
            linkColors: {
                'membership': '#B0C4DE',     
                'partnership': '#A8D4B2',    
                'ownership': '#C7B8E0',       
                'family_relationship': '#C2B8A3'
            },
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
            }
        }
    },
    computed: {
        ...mapState(['filteredNodes', 'filteredLinks', 'links', 'nodes', 'selectedNodeId'])
    },
    methods: {
        formatType(type) {
            return type.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
        },
        handleResize() {
            const membershipContainer = document.getElementById('subgraph-membership')
            const partnershipContainer = document.getElementById('subgraph-partnership')
            const ownershipContainer = document.getElementById('subgraph-ownership')
            const familyContainer = document.getElementById('subgraph-family-relationship')

            const containers = {
                'membership': membershipContainer,
                'partnership': partnershipContainer,
                'ownership': ownershipContainer,
                'family_relationship': familyContainer
            }

            Object.entries(containers).forEach(([type, container]) => {
                if (container) {
                    const width = container.clientWidth
                    const height = container.clientHeight

                    // 更新SVG大小
                    if (this.svgs[type]) {
                        this.svgs[type]
                            .attr('width', width)
                            .attr('height', height)

                        // 更新力导向图中心点
                        if (this.simulations[type]) {
                            this.simulations[type]
                                .force('center', d3.forceCenter(width / 2, height / 2))
                                .alpha(0.3)
                                .restart()
                        }
                    }
                }
            })
        },
        async initSubgraphs() {
            await this.$nextTick();
            
            const graphConfigs = [
                { type: 'membership', id: 'subgraph-membership' },
                { type: 'partnership', id: 'subgraph-partnership' },
                { type: 'ownership', id: 'subgraph-ownership' },
                { type: 'family_relationship', id: 'subgraph-family-relationship' }
            ];

            // 停止所有现有的模拟器
            Object.values(this.simulations).forEach(sim => {
                if (sim) sim.stop();
            });
            this.simulations = {};

            graphConfigs.forEach(({ type, id }) => {
                const container = d3.select(`#${id}`)
                const element = container.node()
                
                if (!element) {
                    console.warn(`Container for ${type} not found`)
                    return
                }

                // 清除现有的SVG
                container.selectAll("svg").remove()

                const width = element.clientWidth || 300
                const height = element.clientHeight || 200

                // 创建SVG
                const svg = container.append('svg')
                    .attr('width', '100%')
                    .attr('height', '100%')
                    .attr('viewBox', `0 0 ${width} ${height}`)
                    .attr('preserveAspectRatio', 'xMidYMid meet')
                    .style('display', 'block') // 确保SVG是块级元素

                // 添加标题
                svg.append('text')
                    .attr('x', width / 2)
                    .attr('y', 15)
                    .attr('text-anchor', 'middle')
                    .attr('dominant-baseline', 'middle')
                    .style('font-size', '10px')
                    .style('font-weight', 'bold')
                    .text(this.formatType(type))

                // 添加图形容器，并为标题留出空间
                const graphContainer = svg.append('g')
                    .attr('class', 'graph-container')
                    .attr('transform', `translate(0, 25)`)

                // 设置缩放行为
                svg.call(d3.zoom()
                    .scaleExtent([0.5, 4])
                    .on('zoom', (event) => {
                        graphContainer.attr('transform', event.transform)
                    }))

                this.svgs[type] = svg
            })
        },
        updateSubgraphs() {
            if (!this.filteredNodes || !this.filteredLinks) {
                console.warn('No data available for updating subgraphs');
                return;
            }

            // 停止所有现有的模拟器
            Object.values(this.simulations).forEach(sim => {
                if (sim) {
                    sim.stop();
                    sim.nodes().forEach(node => {
                        node.fx = null;
                        node.fy = null;
                    });
                }
            });

            this.linkTypes.forEach(type => {
                // 过滤出当前类型的连接
                const links = this.filteredLinks.filter(link => link.type === type)
                console.log(type, 'links', links)
                
                const nodeIds = new Set()
                links.forEach(link => {
                    // 从 Proxy 对象中获取 id
                    nodeIds.add(typeof link.source === 'object' ? link.source.id : link.source)
                    nodeIds.add(typeof link.target === 'object' ? link.target.id : link.target)
                })
                console.log(type, 'nodeIds', nodeIds)
                
                const nodes = this.filteredNodes.filter(node => nodeIds.has(node.id))
                console.log(type, 'nodes', nodes)

                // 找出最大和最小连接数
                const linkCounts = nodes.map(node => node.linkCount);
                const maxLinks = Math.max(...linkCounts);
                const minLinks = Math.min(...linkCounts);

                // 创建半径的比例尺
                const radiusScale = d3.scaleLinear()
                    .domain([minLinks, maxLinks])
                    .range([3, 10]); // 子图中节点范围小一些：3-10

                const svg = this.svgs[type]
                if (!svg) {
                    console.warn(`SVG for ${type} not found`)
                    return
                }

                const container = svg.select('.graph-container')
                const width = svg.node().clientWidth
                const height = svg.node().clientHeight - 20 // 减去标题的高度

                // 清除之前的图形
                container.selectAll("*").remove()

                // 计算布局参数
                const radius = Math.min(width, height) * 0.35
                const centerX = width / 2
                const centerY = height / 2

                // 计算节点位置
                const connectedNodes = nodes.filter(d => d.isConnected)
                const angleStep = (2 * Math.PI) / connectedNodes.length
                connectedNodes.forEach((node, i) => {
                    const angle = i * angleStep
                    node.x = centerX + radius * Math.cos(angle)
                    node.y = centerY + radius * Math.sin(angle)
                })

                // 将未连接的节点放在外圈
                const unconnectedNodes = nodes.filter(d => !d.isConnected)
                const outerRadius = radius * 1.5
                unconnectedNodes.forEach((node, i) => {
                    const angle = (i * 2 * Math.PI) / unconnectedNodes.length
                    node.x = centerX + outerRadius * Math.cos(angle)
                    node.y = centerY + outerRadius * Math.sin(angle)
                })

                // 绘制连接线
                container.selectAll('.link')
                    .data(links)
                    .enter()
                    .append('path')
                    .attr('class', 'link')
                    .attr('d', d => {
                        const sourceX = d.source.x || centerX
                        const sourceY = d.source.y || centerY
                        const targetX = d.target.x || centerX
                        const targetY = d.target.y || centerY
                        const dx = targetX - sourceX
                        const dy = targetY - sourceY
                        const dr = Math.sqrt(dx * dx + dy * dy) * 1.5
                        return `M${sourceX},${sourceY}A${dr},${dr} 0 0,1 ${targetX},${targetY}`
                    })
                    .style('fill', 'none')
                    .style('stroke', d => d.weight > 0.99 ? '#FF0000' : this.linkColors[type])
                    .style('stroke-opacity', d => d.weight > 0.99 ? 0.8 : 0.6)
                    .style('stroke-width', d => d.weight > 0.99 ? d.weight * 3 : d.weight * 1.5)

                // 创建节点组
                const nodeGroups = container.selectAll('.node')
                    .data(nodes)
                    .enter()
                    .append('g')
                    .attr('class', 'node')
                    .attr('transform', d => `translate(${d.x}, ${d.y})`)

                // 添加节点圆圈
                nodeGroups.append('circle')
                    .attr('r', d => radiusScale(d.linkCount))
                    .style('fill', d => this.typeColors[d.type])
                    .style('stroke', '#fff')
                    .style('stroke-width', '1.5px')

                // 添加节点标签
                // nodeGroups.append('text')
                //     .text(d => d.id)
                //     .attr('dx', 8)
                //     .attr('dy', '.35em')
                //     .style('font-size', '8px')
                //     .style('pointer-events', 'none')

                // 不需要保存模拟器引用，因为我们不使用力导向
                this.simulations[type] = null

                // 添加交互效果
                nodeGroups
                    .on('mouseover', function() {
                        d3.select(this).select('circle')
                            .transition()
                            .duration(200)
                            .attr('r', d => radiusScale(d.linkCount) * 1.5)
                    })
                    .on('mouseout', function() {
                        d3.select(this).select('circle')
                            .transition()
                            .duration(200)
                            .attr('r', d => radiusScale(d.linkCount))
                    })
            })
        }
    },
    mounted() {
        this.initSubgraphs()
        window.addEventListener('resize', this.handleResize)
    },
    beforeUnmount() {
        window.removeEventListener('resize', this.handleResize)
        // 清理所有模拟器
        Object.values(this.simulations).forEach(simulation => {
            if (simulation) simulation.stop()
        })
    },
    watch: {
        filteredNodes: {
            handler(newNodes, oldNodes) {
                // 只有当节点数据真正改变时才更新
                if (JSON.stringify(newNodes) !== JSON.stringify(oldNodes)) {
                    this.updateSubgraphs()
                }
            },
            deep: true
        },
        selectedNodeId: {
            handler(newId) {
                // 更新所有子图中的节点样式
                Object.values(this.svgs).forEach(svg => {
                    svg.selectAll('.node circle')
                        .transition()
                        .duration(200)
                        .style('stroke', d => d.id === newId ? '#FF0000' : '#fff')
                        .style('stroke-width', d => d.id === newId ? 4 : 1.5);
                });
            }
        }
    }
}
</script>

<style scoped>
.subgraphs-container {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    grid-template-rows: 1fr;
    gap: 8px;
    height: calc(100% - 5px);
    width: calc(100% - 10px);
    padding: 5px;
    background: white;
    box-sizing: border-box;
}

.subgraph {
    background: white;
    border-radius: 4px;
    padding: 2px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    height: 100%;
    width: 100%;
    position: relative;
    min-width: 0;
    box-sizing: border-box;
}

.subgraph-vis {
    width: 100%;
    height: 100%;
    border-radius: 3px;
    position: relative;
    overflow: hidden;
    box-sizing: border-box;
}

/* 调整标题文字大小和位置 */
.graph-container text {
    font-size: 10px !important;
}

.node text {
    pointer-events: none;
    font-size: 7px !important;
}

.node circle {
    stroke: #fff;
    stroke-width: 1px;
}

.link {
    stroke-opacity: 0.6;
    fill: none;
    stroke-width: 1px;
}

/* 确保SVG填充整个容器 */
svg {
    width: 100% !important;
    height: 100% !important;
    display: block;
}

#subgraph-tooltip {
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
</style> 