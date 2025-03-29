<template>
    <div class="visualization-panel">
        <div class="vis-container">
            <div id="force-directed-graph"></div>
        </div>
    </div>
</template>

<script>
import * as d3 from 'd3'
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
        this.initGraph()
        this.loadData()
        window.addEventListener('resize', this.handleResize)
    },
    beforeUnmount() {
        window.removeEventListener('resize', this.handleResize)
    },
    methods: {
        handleResize() {
            const container = document.getElementById('force-directed-graph')
            this.width = container.clientWidth
            this.height = container.clientHeight

            // 更新SVG大小
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
                    d3.select('.graph-container')
                        .attr('transform', event.transform)
                }
                ))
        },
        async loadData() {
            try {
                const response = await fetch('assets/MC1.json')
                const data = await response.json()
                this.createGraph(data)
            } catch (error) {
                console.error('Error loading data:', error)
            }
        },
        createGraph(data) {
            this.simulation = d3.forceSimulation(data.nodes)
                .force('link', d3.forceLink(data.links).id(d => d.id).distance(10))
                .force('charge', d3.forceManyBody().strength(-300))
                .force('center', d3.forceCenter(this.width / 2, this.height / 2))
                .force('collision', d3.forceCollide().radius(30))
            const container = this.svg.select('.graph-container')

            // add links
            const links = container.selectAll('.link')
                .data(data.links)
                .enter()
                .append('line')
                .attr('class', 'link')
                .style('stroke', '#999')
                .style('stroke-width', 1)

            // nodes group
            const nodes = container.selectAll('.node')
                .data(data.nodes)
                .enter()
                .append('g')
                .attr('class', 'node')
                .call(d3.drag()
                    .on('start', this.dragStarted)
                    .on('drag', this.dragged)
                    .on('end', this.dragEnded))

            nodes.append('circle')
                .attr('r', 10)
                .style('fill', '#69b3a2')
            // add labels
            nodes.append('text')
                .text(d => d.id)
                .attr('dx', 12)
                .attr('dy', 4)
                .style('font-family', 'Arial, sans-serif')
                .style('font-size', 12)

            this.simulation.on('tick', () => {
                links.attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y)
                nodes.attr('transform', d => `translate(${d.x}, ${d.y})`)
            })
        },
        dragstarted(event, d) {
            if (!event.active) this.simulation.alphaTarget(0.3).restart()
            d.fx = d.x
            d.fy = d.y
        },
        dragged(event, d) {
            d.fx = event.x
            d.fy = event.y
        },
        dragended(event, d) {
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
}

.vis-container {
    margin-top: 20px;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 20px;
    min-height: 500px;
}

#force-directed-graph {
    width: 100%;
    height: calc(100vh - 100px);
    border: 1px solid #ddd;
    border-radius: 4px;
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
</style>