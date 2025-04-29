<template>
  <div class="parallel-coordinates-container">
    <div ref="chartContainer" class="parallel-coordinates-chart"></div>
  </div>
</template>

<script>
import * as d3 from 'd3'

export default {
  name: 'ParallelCoordinates',
  props: {
    nodes: {
      type: Array,
      required: true
    }
  },
  computed: {
    ...mapState(['selectedNodeId']),
  },
  mounted() {
    this.renderChart()
    window.addEventListener('resize', this.handleResize)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize)
    d3.select(".tooltip").remove()
  },
  methods: {
    handleResize() {
      this.renderChart()
    },
    renderChart() {
      console.log("Rendering chart with nodes:", this.nodes)
      // 清除之前的图表
      d3.select(this.$refs.chartContainer).selectAll("*").remove()
      
      // 准备数据
      const nodesArray = Array.isArray(this.nodes) ? this.nodes : (this.nodes?.nodes || [])
      const { data, minAvgNode, maxAvgNode } = this.transformData(nodesArray)
      if (!data || data.length === 0) return

      // 获取容器尺寸
      const container = this.$refs.chartContainer
      const width = container.clientWidth
      const height = container.clientHeight
      const margin = { top: 30, right: 100, bottom: 50, left: 60 }
      console.log("width", width)
      console.log("height", height)

      // 创建SVG
      const svg = d3.select(container)
        .append("svg")
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("viewBox", `0 0 ${width} ${height}`)
        .attr("preserveAspectRatio", "xMidYMid meet")

      // 提取所有维度(节点)
      const dimensions = [...new Set(data.flatMap(d => Object.keys(d.values)))].filter(d => d !== 'name')
      
      // 创建比例尺
      const x = d3.scalePoint()
        .domain(dimensions)
        .range([margin.left, width - margin.right])
        .padding(0.5)

      const y = d3.scaleLinear()
        .domain([0, 1]) // 假设value范围是0-1
        .range([height - margin.bottom, margin.top])

      // 添加坐标轴
      svg.append("g")
        .attr("transform", `translate(0,${height - margin.bottom})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
          .style("text-anchor", "end")
          .attr("dx", "-.8em")
          .attr("dy", ".15em")
          .attr("transform", "rotate(-45)")

      svg.append("g")
        .attr("transform", `translate(${margin.left},0)`)
        .call(d3.axisLeft(y))

      // 添加标题
      svg.append("text")
        .attr("x", width / 2)
        .attr("y", margin.top / 2)
        .attr("text-anchor", "middle")
        .text("Node Relationships Parallel Coordinates")
        .style("font-size", "16px")
        .style("font-weight", "bold")

      // 创建折线生成器
      const line = d3.line()
        .defined(d => !isNaN(d.value))
        .x(d => x(d.dimension))
        .y(d => y(d.value))

      // 绘制折线
      svg.selectAll(".line")
        .data(data)
        .enter()
        .append("path")
        .attr("class", "line")
        .attr("d", d => line(dimensions.map(dim => ({
          dimension: dim,
          value: d.values[dim] || 0
        }))))
        .attr("stroke", d => {
          if (d.name === maxAvgNode.name) return "#ff0000" // 最高平均值标红
          if (d.name === minAvgNode.name) return "#00aa00" // 最低平均值标绿
          return "#999999" // 其余灰色
        })
        .attr("stroke-width", d => {
          if (d.name === maxAvgNode.name || d.name === minAvgNode.name) return 2
          return 1
        })
        .attr("fill", "none")
        .attr("opacity", d => {
          if (d.name === maxAvgNode.name || d.name === minAvgNode.name) return 0.9
          return 0.4
        })
        .on("mouseover", (event, d) => {  // 改为箭头函数以保持this上下文
            d3.select(event.currentTarget)
                .attr("stroke-width", 3)
                .attr("opacity", 1)
          
          // 显示详细相关性列表
          const tooltipContent = this.generateTooltipContent(d, dimensions)
          tooltip.style("visibility", "visible")
            .html(tooltipContent)
        })
        .on("mouseout", function() {
          d3.select(this)
            .attr("stroke-width", d => {
              if (d.name === maxAvgNode.name || d.name === minAvgNode.name) return 2
              return 1
            })
            .attr("opacity", d => {
              if (d.name === maxAvgNode.name || d.name === minAvgNode.name) return 0.9
              return 0.4
            })
          
          tooltip.style("visibility", "hidden")
        })
        .on("mousemove", function(event) {
          tooltip
            .style("top", (event.pageY - 10) + "px")
            .style("left", (event.pageX + 10) + "px")
        })

      // 添加图例
      const legend = svg.append("g")
        .attr("transform", `translate(${width - margin.right + 10}, ${margin.top})`)

      // 最高平均值图例
      legend.append("rect")
        .attr("x", -60)
        .attr("y", 0)
        .attr("width", 15)
        .attr("height", 15)
        .attr("fill", "#ff0000")

      legend.append("text")
        .attr("x", -40)
        .attr("y", 12)
        .text(`Highest Avg: ${maxAvgNode.name} (${maxAvgNode.avg.toFixed(2)})`)
        .style("font-size", "12px")

      // 最低平均值图例
      legend.append("rect")
        .attr("x", -60)
        .attr("y", 20)
        .attr("width", 15)
        .attr("height", 15)
        .attr("fill", "#00aa00")

      legend.append("text")
        .attr("x", -40)
        .attr("y", 32)
        .text(`Lowest Avg: ${minAvgNode.name} (${minAvgNode.avg.toFixed(2)})`)
        .style("font-size", "12px")

      // 添加tooltip
      const tooltip = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("position", "absolute")
        .style("visibility", "hidden")
        .style("background", "white")
        .style("border", "1px solid #ddd")
        .style("padding", "10px")
        .style("border-radius", "5px")
        .style("pointer-events", "none")
        .style("box-shadow", "0 0 10px rgba(0,0,0,0.2)")
        .style("max-width", "300px")
    },
    transformData(nodes) {
      // 将原始数据转换为平行坐标格式
      const nodeMap = {}
      
      // 首先收集所有节点
      nodes.forEach(node => {
        if (!nodeMap[node.name]) {
          nodeMap[node.name] = {
            name: node.name,
            values: {},
            sum: 0,
            count: 0
          }
        }
        if (node.target) {
          nodeMap[node.name].values[node.target] = node.value
          nodeMap[node.name].sum += node.value
          nodeMap[node.name].count++
        }
      })

      // 确保每个节点都有所有其他节点的值(默认为0)
      const allNodes = Object.keys(nodeMap)
      allNodes.forEach(nodeName => {
        allNodes.forEach(otherNode => {
          if (nodeName !== otherNode && !nodeMap[nodeName].values[otherNode]) {
            nodeMap[nodeName].values[otherNode] = 0
          }
        })
        // 计算平均值
        nodeMap[nodeName].avg = nodeMap[nodeName].count > 0 ? 
          nodeMap[nodeName].sum / nodeMap[nodeName].count : 0
      })

      // 找出平均值最高和最低的节点
      const nodeList = Object.values(nodeMap)
      let maxAvgNode = nodeList[0]
      let minAvgNode = nodeList[0]
      
      nodeList.forEach(node => {
        if (node.avg > maxAvgNode.avg) maxAvgNode = node
        if (node.avg < minAvgNode.avg) minAvgNode = node
      })

      return {
        data: nodeList,
        minAvgNode,
        maxAvgNode
      }
    },
    generateTooltipContent(node, dimensions) {
      // 生成详细的tooltip内容
      let content = `<div class="tooltip-header">
        <strong>${node.name}</strong> (Avg: ${node.avg.toFixed(2)})
      </div>
      <div class="tooltip-body">
        <table>
          <tr>
            <th>Target Node</th>
            <th>Value</th>
          </tr>`
      
      dimensions.sort((a, b) => node.values[b] - node.values[a])
        .forEach(dim => {
          content += `<tr>
            <td>${dim}</td>
            <td>${node.values[dim].toFixed(2)}</td>
          </tr>`
        })
      
      content += `</table></div>`
      
      return content
    }
  },
  watch: {
    nodes: {
      handler() {
        console.log("get parallel nodes")
        this.renderChart()
      },
      deep: true
    },
    selectedNodeId: {
      handler() {
        // todo: 选择了view a的点后要干嘛
      },
      immediate: true
    }
  
  }
}
</script>

<style scoped>
.parallel-coordinates-container {
  width: 100%;
  height: 100%;
}

.parallel-coordinates-chart {
  width: 100%;
  height: 100%;
  min-height: 200px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
}
</style>

<style>
/* 全局tooltip样式 */
.tooltip {
  font-family: Arial, sans-serif;
  font-size: 12px;
  z-index: 100;
}

.tooltip-header {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
}

.tooltip-body table {
  width: 100%;
  border-collapse: collapse;
}

.tooltip-body th {
  text-align: left;
  background-color: #f5f5f5;
  padding: 3px 8px;
}

.tooltip-body td {
  padding: 3px 8px;
  border-bottom: 1px solid #eee;
}

.tooltip-body tr:hover td {
  background-color: #f9f9f9;
}
</style>