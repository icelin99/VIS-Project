<template>
<div class="parallel-coordinates-container">
  <div ref="chartContainer" class="scatter-plot"></div>
</div>
</template>

<script>
import * as d3 from 'd3'
import { mapState } from 'vuex'
import coefData from '@/assets/nodes_coef.json'

export default {
name: 'ParallelCoordinates',
data() {
  return {
    coefData: coefData
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
},
methods: {
  createTopTenScale(data, topItems, range) {
    const maxNormalValue = d3.max(
      data.filter(d => !topItems.some(top => top === d))
    )
    
    return d3.scaleLinear()
      .domain([0, maxNormalValue, d3.max(data)])
      .range([
        range[0], 
        range[0] + (range[1] - range[0]) * 0.8, 
        range[1]
      ])
      .clamp(true)
  },

  renderChart() {
    const data = this.coefData
    if (!data || data.length === 0) return

    d3.select(this.$refs.chartContainer).selectAll("*").remove()

    // 找出top 10数据
    // 使用原始 ID 而不是索引
    const topRaw = data
      .map((d, index) => ({ ...d, originalIndex: index }))
      .sort((a, b) => b.raw_score - a.raw_score)
      .slice(0, 10)
      .map(d => d.id)  // 使用原始 ID
    
    const topNorm = data
      .map((d, index) => ({ ...d, originalIndex: index }))
      .sort((a, b) => b.norm_score - a.norm_score)
      .slice(0, 10)
      .map(d => d.id)  // 使用原始 ID

    const container = this.$refs.chartContainer
    const width = container.clientWidth || 800
    const height = container.clientHeight || 600
    const margin = { top: 60, right: 60, bottom: 10, left: 60 }

    const svg = d3.select(container)
      .append("svg")
      .attr("width", width)
      .attr("height", height)
      .style("background", "#f9f9f9")

    const rawScores = data.map(d => d.raw_score)
    const normScores = data.map(d => d.norm_score)

    // 创建特殊的比例尺
    const yRaw = this.createTopTenScale(
      rawScores, 
      topRaw.map(id => data.find(d => d.id === id).raw_score), 
      [height - margin.bottom, margin.top]
    )

    const yNorm = this.createTopTenScale(
      normScores, 
      topNorm.map(id => data.find(d => d.id === id).norm_score), 
      [height - margin.bottom, margin.top]
    )

    const x = d3.scalePoint()
      .domain(data.map(d => d.id))  // 使用原始 ID 作为域
      .range([margin.left, width - margin.right])

    // 颜色比例尺
    const color = d3.scaleOrdinal()
      .domain(["normal", "top-raw", "top-norm"])
      .range(["#999", "#ff4d4d", "#4daf4d"])

    // 绘制连接线
    svg.selectAll(".connection-line")
      .data(data)
      .enter()
      .append("line")
      .attr("data-id", d => String(d.id))  // 使用原始 ID 
      .attr("x1", d => x(d.id))
      .attr("y1", d => yRaw(d.raw_score))
      .attr("x2", d => x(d.id))
      .attr("y2", d => yNorm(d.norm_score))
      .attr("stroke", d => {
        if (topRaw.includes(d.id) || topNorm.includes(d.id)) return color("top-raw")
        return "#ddd"
      })
      .attr("stroke-width", 1)
      .attr("opacity", 0.5)

    

    // 绘制Norm Score点
    svg.selectAll(".dot-norm")
      .data(data)
      .enter()
      .append("circle")
      .attr("class", "dot-norm")
      .attr("data-id", d => String(d.id))  // 使用原始 ID 
      .attr("cx", d => x(d.id))
      .attr("cy", d => yNorm(d.norm_score))
      .attr("r", 1)
      .attr("fill", d => {
        if (topNorm.includes(d.id)) return color("top-norm")
        return color("normal")
      })
      .attr("opacity", 0.7)

    // 绘制Raw Score点
    svg.selectAll(".dot-raw")
      .data(data)
      .enter()
      .append("circle")
      .attr("class", "dot-raw")
      .attr("data-id", d => String(d.id))  // 使用原始 ID 
      .attr("cx", d => x(d.id))
      .attr("cy", d => yRaw(d.raw_score))
      .attr("r", d => {
        return topRaw.includes(d.id) ? 2 : 1
      })
      .attr("fill", d => {
        if (topRaw.includes(d.id)) return color("top-raw")
        return color("normal")
      })
      .attr("opacity", 0.7)  


    // 坐标轴
    const axisColor = "#666"
    svg.append("g")
      .attr("transform", `translate(${margin.left},0)`)
      .call(d3.axisLeft(yRaw).ticks(5))
      .call(g => g.select(".domain").attr("stroke", axisColor))
      .call(g => g.selectAll(".tick line").attr("stroke", axisColor))
      .call(g => g.selectAll(".tick text").attr("fill", axisColor))
      .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", -40)
        .attr("x", -height/2)
        .attr("text-anchor", "middle")
        .text("Raw Score")
        .style("fill", axisColor)

    svg.append("g")
      .attr("transform", `translate(${width - margin.right},0)`)
      .call(d3.axisRight(yNorm).ticks(5))
      .call(g => g.select(".domain").attr("stroke", axisColor))
      .call(g => g.selectAll(".tick line").attr("stroke", axisColor))
      .call(g => g.selectAll(".tick text").attr("fill", axisColor))
      .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 40)
        .attr("x", -height/2)
        .attr("text-anchor", "middle")
        .text("Normalized Score")
        .style("fill", axisColor)

    // 图例
    const legend = svg.append("g")
      .attr("transform", `translate(${width - margin.right + 10}, ${margin.top})`)

    // Top Raw Score图例
    legend.append("circle")
      .attr("cx", -width*2/3+30)
      .attr("cy", -height/10)
      .attr("r", 3)
      .attr("fill", color("top-raw"))

    legend.append("text")
      .attr("x", -width*2/3+10+30)
      .attr("y", -height/10+4)
      .text("Top 10 Points")
      .style("font-size", "10px")

    // Top Norm Score图例
    legend.append("circle")
      .attr("cx", -width*1/3+30)
      .attr("cy", -height/10)
      .attr("r", 3)
      .attr("fill", color("normal"))

    legend.append("text")
      .attr("x", -width*1/3+10+30)
      .attr("y", -height/10+4)
      .text("Other points")
      .style("font-size", "10px")
  },

  highlightNode(newId) {
    const data = this.coefData
    if (!data || data.length === 0) return
    
    const svg = d3.select(this.$refs.chartContainer).select("svg")
    
    // 移除之前的文本框
    svg.selectAll(".node-info-box").remove()

    const nodeData = this.coefData.find(d => String(d.id) === String(newId))
    
    if (!nodeData) return

    // 找出top 10数据
    // 使用原始 ID 而不是索引
    const topRaw = data
      .map((d, index) => ({ ...d, originalIndex: index }))
      .sort((a, b) => b.raw_score - a.raw_score)
      .slice(0, 10)
      .map(d => d.id)  // 使用原始 ID

    // 颜色比例尺
    const color = d3.scaleOrdinal()
      .domain(["normal", "top-raw", "top-norm"])
      .range(["#999", "#ff4d4d", "#4daf4d"])

    // 重置所有元素样式
    svg.selectAll("[data-id]")
      .each(function() {
        const el = d3.select(this)
        
        if (el.classed('dot-raw') || el.classed('dot-norm')) {
          el.attr("r", 1)
            .attr("fill", "#999")
            .attr("opacity", 0.5)
            .attr("r", d => {
              return topRaw.includes(d.id) ? 2 : 1
            })
            .attr("fill", d => {
              if (topRaw.includes(d.id)) return color("top-raw")
              return color("normal")
            })
        }

        if (el.classed('connection-line')) {
          el.attr("stroke", "#ddd")
            .attr("stroke-width", 1)
            .attr("opacity", 0.3)
        }
      })

    // 只选择第一个匹配的点
    const matchedElement = svg.selectAll(`[data-id="${newId}"].dot-raw, [data-id="${newId}"].dot-norm`)
      .filter(function(d, i) {
        return i === 0;  // 只选择第一个元素
      })

    if (matchedElement.empty()) return

    // 高亮选中元素
    matchedElement
      .attr("r", 4)
      .attr("fill", "#40E0D0")
      .attr("opacity", 1)

    // 找到对应的连接线
    const connectedLine = svg.select(`[data-id="${newId}"].connection-line`)
    if (!connectedLine.empty()) {
      connectedLine
        .attr("stroke", "#40E0D0")
        .attr("stroke-width", 2)
        .attr("opacity", 1)
    }

    // 创建文本框
    const bx = parseFloat(matchedElement.attr('cx'))
    const by = parseFloat(matchedElement.attr('cy'))

    const infoBox = svg.append('g')
      .attr('class', 'node-info-box')
      .attr('transform', `translate(${bx + 10}, ${by - 40})`)

    // 背景矩形
    infoBox.append('rect')
      .attr('width', 130)
      .attr('height', 70)
      .attr('fill', 'white')
      .attr('stroke', '#333')
      .attr('stroke-width', 1)
      .attr('rx', 5)
      .attr('ry', 5)
      .attr('opacity', 0.6)

    // 文本内容
    const textData = [
      `ID: ${nodeData.id}`,
      `Raw Score: ${nodeData.raw_score.toFixed(2)}`,
      `Norm Score: ${nodeData.norm_score.toFixed(2)}`
    ]

    infoBox.selectAll('text')
      .data(textData)
      .enter()
      .append('text')
      .attr('x', 10)
      .attr('y', (d, i) => 20 + i * 18)
      .attr('font-size', '10px')
      .text(d => d)
  }
},

// 监听 Vuex store 中的选中节点变化
watch: {
  selectedNodeId: {
    handler(newId) {
      const stringId = String(newId)
      this.highlightNode(stringId)
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

.scatter-plot {
width: 100%;
height: 100%;
border: 1px solid #ddd;
border-radius: 1px;
background: white;
}
</style>