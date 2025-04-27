<template>
    <div class="visualization-panel">
        <div class="vis-container">
            <div id="force-directed-graph"></div>
        </div>
    </div>
</template>

<script>
import * as d3 from 'd3'
import MC1Data from '@/assets/MC1.json' // 直接导入

export default {
    name: 'FDG',
    data() {
        return {
            simulation: null,
            svg: null,
            width: 0,
            height: 0
        }
    },
    mounted() {
        const container = document.getElementById('force-directed-graph')
        this.width = container.clientWidth
        this.height = container.clientHeight
        this.initGraph()
        this.loadData()
        window.addEventListener('resize', this.handleResize)
    },
    beforeUnmount() {
        window.removeEventListener('resize', this.handleResize)
        if (this.simulation) this.simulation.stop()
    },
    methods: {
        handleResize() {
            const container = document.getElementById('force-directed-graph')
            this.width = container.clientWidth
            this.height = container.clientHeight

            this.svg
                .attr('width', this.width)
                .attr('height', this.height)

            if (this.simulation) {
                this.simulation.force('center', d3.forceCenter(this.width / 2, this.height / 2))
                this.simulation.alpha(0.3).restart()
            }
        },
        initGraph() {
            this.svg = d3.select('#force-directed-graph')
                .append('svg')
                .attr('width', this.width)
                .attr('height', this.height)
                .style('background', '#f9f9f9')

            this.svg.append('g')
                .attr('class', 'graph-container')

            this.svg.call(d3.zoom()
                .scaleExtent([0.1, 4])
                .on('zoom', (event) => {
                    d3.select('.graph-container')
                        .attr('transform', event.transform)
                }))
        },
        async loadData() {
            try {
                console.log('Loading data...', MC1Data) // 调试
                if (!MC1Data.nodes || !MC1Data.links) {
                    throw new Error('Invalid data format')
                }
                this.createGraph(MC1Data)
            } catch (error) {
                console.error('Error loading data:', error)
            }
        },
        createGraph(data) {
            const container = d3.select('.graph-container')
            
            // 清除现有元素
            container.selectAll('*').remove()

            // 创建连线
            const links = container.selectAll('.link')
                .data(data.links)
                .enter()
                .append('line')
                .attr('class', 'link')
                .attr('stroke', '#999')
                .attr('stroke-width', 1)

            // 创建节点组
            const nodes = container.selectAll('.node')
                .data(data.nodes)
                .enter()
                .append('g')
                .attr('class', 'node')
                .call(d3.drag()
                    .on('start', this.dragStarted)
                    .on('drag', this.dragged)
                    .on('end', this.dragEnded))

            // 添加节点圆圈
            nodes.append('circle')
                .attr('r', 10)
                .attr('fill', '#69b3a2')
                .attr('stroke', '#fff')
                .attr('stroke-width', 2)

            // 添加节点标签
            nodes.append('text')
                .text(d => d.id)
                .attr('dx', 12)
                .attr('dy', 4)
                .attr('font-family', 'Arial, sans-serif')
                .attr('font-size', 12)
                .attr('fill', '#333')

            // 创建力导向模拟
            this.simulation = d3.forceSimulation(data.nodes)
                .force('link', d3.forceLink(data.links).id(d => d.id).distance(100))
                .force('charge', d3.forceManyBody().strength(-300))
                .force('center', d3.forceCenter(this.width / 2, this.height / 2))
                .force('collision', d3.forceCollide().radius(20))
                .on('tick', () => {
                    links.attr('x1', d => d.source.x)
                        .attr('y1', d => d.source.y)
                        .attr('x2', d => d.target.x)
                        .attr('y2', d => d.target.y)
                    nodes.attr('transform', d => `translate(${d.x}, ${d.y})`)
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
        }
    }
}
</script>

<style scoped>
.visualization-panel {
    height: 100%;
    width: 100%;
}

.vis-container {
    height: 100%;
    width: 100%;
    padding: 10px;
}

#force-directed-graph {
    width: 100%;
    height: 100%;
    min-height: 500px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: #f9f9f9;
}

.node:hover {
    cursor: pointer;
}

.node text {
    pointer-events: none;
    user-select: none;
}
</style>