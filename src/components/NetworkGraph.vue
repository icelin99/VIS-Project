<template>
  <div class="network-container">
    <div class="controls">
      <span class="select-label">Please choose the root node:</span>
      <select 
        v-model="selectedRootNode" 
        @change="updateTreeGraph" 
        class="node-select"
      >
        <option 
          v-for="node in uniqueNodes" 
          :key="node" 
          :value="node"
        >
          {{ node }}
        </option>
      </select>
    </div>
    <div ref="graphContainer" class="network-graph"></div>
  </div>
</template>

<script>
import * as d3 from 'd3'
import hierarchyData from '@/assets/tree_hierarchy.json'

export default {
  name: 'TreeNetworkGraph',
  props: {
    nodes: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      selectedRootNode: null,
      uniqueNodes: [],
      hierarchyData: hierarchyData,
      levelNodeCounts: {} // 用于记录每个层级的节点计数
    }
  },
  mounted() {
    this.extractUniqueNodes()
    this.renderTreeGraph()
  },
  methods: {
    extractUniqueNodes() {
      this.uniqueNodes = this.nodes.map(node => node.name)
      this.selectedRootNode = this.uniqueNodes.length > 0 ? this.uniqueNodes[0] : null
    },

    convertToD3Hierarchy(rootNodeData) {
      if (!rootNodeData || rootNodeData.length === 0) {
        return { name: this.selectedRootNode || 'Root', children: [] }
      }

      // 重置层级节点计数
      this.levelNodeCounts = {}

      const root = {
        name: rootNodeData[0].name,
        depth: 1,
        children: [],
        showLabel: true // 默认显示标签
      }

      const nodeMap = { [root.name]: root }
      const sortedNodes = [...rootNodeData].sort((a, b) => a.depth - b.depth)

      sortedNodes.forEach(node => {
        if (node.depth === 1) return

        const parentPath = node.path.slice(0, -1)
        const parentName = parentPath[parentPath.length - 1]
        const parent = nodeMap[parentName]

        if (parent) {
          // 更新层级节点计数
          if (!this.levelNodeCounts[node.depth]) {
            this.levelNodeCounts[node.depth] = 0
          }
          this.levelNodeCounts[node.depth] += 1

          const childNode = {
            name: node.name,
            depth: node.depth,
            children: [],
            showLabel: this.levelNodeCounts[node.depth] <= 10 // 前10个节点显示标签
          }
          parent.children.push(childNode)
          nodeMap[node.name] = childNode
        }
      })

      return root
    },

    renderTreeGraph() {
      if (!this.selectedRootNode || !this.hierarchyData) return

      const rootNodeData = this.hierarchyData[this.selectedRootNode]
      if (!rootNodeData) return

      // 清除之前的图形
      const container = this.$refs.graphContainer
      d3.select(container).selectAll("*").remove()

      // 转换为d3需要的层级结构
      const root = this.convertToD3Hierarchy(rootNodeData)

      // 获取容器尺寸
      const width = container.clientWidth || 1200
      const height = container.clientHeight || 800

      // 创建SVG
      const svg = d3.select(container)
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .style("background", "#f9f9f9")

      // 创建内部分组
      const g = svg.append("g")
        .attr("transform", `translate(80, ${height / 2})`)

      // 创建树状布局
      const treeLayout = d3.tree()
        .size([height - 150, width - 200])

      // 创建层次数据
      const hierarchy = d3.hierarchy(root)
      const treeData = treeLayout(hierarchy)

      // 颜色比例尺
      const colorScale = d3.scaleOrdinal(d3.schemeTableau10)

      // 绘制连接线
      g.selectAll(".link")
        .data(treeData.links())
        .enter().append("path")
        .attr("class", "link")
        .attr("fill", "none")
        .attr("stroke", "#aaa")
        .attr("stroke-width", 1.5)
        .attr("stroke-dasharray", function(d) {
          return d.target.depth % 2 === 0 ? "3,3" : "none"
        })
        .attr("d", d3.linkHorizontal()
          .x(d => d.y)
          .y(d => d.x)
        )

      // 创建节点组
      const node = g.selectAll(".node")
        .data(treeData.descendants())
        .enter().append("g")
        .attr("class", "node")
        .attr("transform", d => `translate(${d.y},${d.x})`)

      // 添加节点圆圈
      node.append("circle")
        .attr("r", d => 6 + (1 - d.depth / 6) * 6)
        .attr("fill", d => colorScale(d.depth))
        .attr("stroke", "#fff")
        .attr("stroke-width", 1.5)
        .style("cursor", "pointer")
        .on("mouseover", function() {
          d3.select(this)
            .transition()
            .duration(200)
            .attr("r", 12)
            .attr("stroke-width", 2)

          // 显示对应文本（如果原本不显示）
          d3.select(this.parentNode).select("text")
            .transition()
            .duration(200)
            .style("opacity", 1)
        })
        .on("mouseout", function() {
          const radius = 6 + (1 - d3.select(this).datum().depth / 6) * 6
          d3.select(this)
            .transition()
            .duration(200)
            .attr("r", radius)
            .attr("stroke-width", 1.5)

          // 如果不是前10个节点，则隐藏文本
          const nodeData = d3.select(this).datum()
          if (!nodeData.data.showLabel) {
            d3.select(this.parentNode).select("text")
              .transition()
              .duration(200)
              .style("opacity", 0)
          }
        })

      // 添加节点文本
      node.append("text")
        .attr("dy", 4)
        .attr("dx", d => d.children ? -15 : 15)
        .attr("text-anchor", d => d.children ? "end" : "start")
        .text(d => d.data.name)
        .attr("font-size", 11)
        .attr("font-weight", "500")
        .attr("fill", "#333")
        .style("opacity", d => d.data.showLabel ? 1 : 0) // 前10个节点默认显示
        .style("pointer-events", "none")
        .style("text-shadow", "0 0 2px white")
        .style("font-family", "Arial, sans-serif")

      // 添加缩放和平移功能
      const zoom = d3.zoom()
        .scaleExtent([0.5, 3])
        .on("zoom", (event) => {
          g.attr("transform", event.transform)
        })

      svg.call(zoom)
    },

    updateTreeGraph() {
      this.renderTreeGraph()
    }
  },
  watch: {
    nodes: {
      handler() {
        this.extractUniqueNodes()
      },
      deep: true
    }
  }
}
</script>

<style scoped>
.network-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  font-family: 'Arial', sans-serif;
}

.controls {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 15px;
  background: linear-gradient(to right, #f5f7fa, #e4e8eb);
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  margin-bottom: 10px;
  gap: 10px;
}

.select-label {
  font-size: 14px;
  color: #555;
  font-weight: 500;
}

.node-select {
  padding: 8px 15px;
  font-size: 14px;
  border-radius: 20px;
  border: 1px solid #d1d5db;
  background: white;
  min-width: 250px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
}

.node-select:focus {
  outline: none;
  border-color: #4f46e5;
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.2);
}

.network-graph {
  flex-grow: 1;
  width: 100%;
  height: calc(100% - 60px);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  background: white;
}
</style>