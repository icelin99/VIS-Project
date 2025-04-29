<template>
  <div class="network-container">
    <div ref="graphContainer" class="network-graph"></div>
  </div>
</template>

<script>
import * as d3 from 'd3'
import hierarchyData from '@/assets/tree_hierarchy.json'
import { mapState } from 'vuex'  // 添加 mapState

export default {
  name: 'TreeNetworkGraph',
  computed: {
    ...mapState(['selectedNodeId', 'originalNodes', 'originalLinks']),
  },
  data() {
    return {
      hierarchyData: hierarchyData,
      levelNodeCounts: {}, // 用于记录每个层级的节点计数
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
    this.renderTreeGraph()
  },
  methods: {
    convertToD3Hierarchy(rootNodeData) {
      if (!rootNodeData || rootNodeData.length === 0) {
        return { name: this.selectedNodeId || 'Root', children: [] }
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
      // 按深度排序节点，并只保留深度不超过3的节点
      const sortedNodes = [...rootNodeData]
        // .filter(node => node.depth <= 3)  // 限制最大深度为3
        .sort((a, b) => a.depth - b.depth)

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

    // 获取节点类型的辅助方法
    getNodeType(nodeName) {
      const node = this.originalNodes.find(n => (n.id).toString() === nodeName.toString())
      const type = node ? node.type : 'unknown'
      return type
    },
    // 获取连接类型的辅助方法
    getLinkType(source, target) {
      const link = this.originalLinks.find(l => 
        ((l.source).toString() === source.toString() && (l.target).toString() === target.toString()) || 
        ((l.source).toString() === target.toString() && (l.target).toString() === source.toString())
      )
      return link ? link.type : 'unknown'
    },

    renderTreeGraph() {
      // 清除之前的图形
      const container = this.$refs.graphContainer
      d3.select(container).selectAll("*").remove()
      
      // 检查是否有选中的节点和层级数据
      if (!this.selectedNodeId || !this.hierarchyData) return

      const rootNodeData = this.hierarchyData[this.selectedNodeId]
      if (!rootNodeData) {
        // 添加提示文本
        const svg = d3.select(container)
          .append("svg")
          .attr("width", "100%")
          .attr("height", "100%")
          .style("background", "#f9f9f9")

        // 添加提示文本
        svg.append("text")
          .attr("x", "50%")
          .attr("y", "50%")
          .attr("text-anchor", "middle")
          .attr("dominant-baseline", "middle")
          .style("font-size", "16px")
          .style("fill", "#666")
          .text("There is no hierarchy data for this node")
          
        return
      }

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
        .attr("class", "graph-container")

      // 创建树状布局
      const treeLayout = d3.tree()
        .size([height * 0.8, width * 0.8])  // 使用更大的空间
        .separation((a, b) => {
          // 增加节点间的水平间距
          return a.parent === b.parent ? 2 : 3;
        })

      // 创建层次数据
      const hierarchy = d3.hierarchy(root)
      
      // 对每一层的子节点进行排序和限制
      hierarchy.each(d => {
        if (d.children) {
          // 按照某种规则排序子节点（这里用名称排序）
          d.children.sort((a, b) => a.data.name.localeCompare(b.data.name))
          // 限制每层最多显示15个节点
          if (d.children.length > 15) {
            d.children = d.children.slice(0, 15)
          }
        }
      })
      
      const treeData = treeLayout(hierarchy)

      // 颜色比例尺
      // const colorScale = d3.scaleOrdinal(d3.schemeTableau10)

      // 绘制连接线
      g.selectAll(".link")
        .data(treeData.links())
        .enter().append("path")
        .attr("class", "link")
        .attr("fill", "none")
        .attr("stroke", d => {
          const linkType = this.getLinkType(d.source.data.name, d.target.data.name)
          return this.linkColors[linkType] || '#aaa'
        })
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
        .attr("r", d => 8 - d.depth)  // 根据深度调整大小
        .attr("fill", (d) => {
          const type = this.getNodeType(d.data.name)
          // 确保即使是unknown类型也返回一个有效的颜色
          return this.typeColors[type] || this.typeColors['unknown']
        })
        .attr("stroke", "#fff")
        .attr("stroke-width", 1.5)
        .style("cursor", "pointer")
        .on("mouseover", function(event, d) {
          d3.select(this)
            .transition()
            .duration(200)
            .attr("r", (8 - d.depth) * 1.5)
            .attr("stroke-width", 2)

          // 显示文本
          d3.select(this.parentNode).select("text")
            .transition()
            .duration(200)
            .style("opacity", 1)
            .style("font-weight", "bold")
        })
        .on("mouseout", function(event, d) {
          d3.select(this)
            .transition()
            .duration(200)
            .attr("r", 8 - d.depth)
            .attr("stroke-width", 1.5)

          // 如果不是叶子节点，恢复文本透明度
          if (d.children) {
            d3.select(this.parentNode).select("text")
              .transition()
              .duration(200)
              .style("opacity", 0.7)
              .style("font-weight", "normal")
          }
        })

      // 添加节点文本
      node.append("text")
        .attr("dy", "0.31em")
        .attr("x", d => d.children ? -12 : 12)
        .attr("text-anchor", d => d.children ? "end" : "start")
        .text(d => d.data.name)
        .attr("font-size", d => Math.max(12 - d.depth * 1.5, 8))  // 根据深度调整字体大小，但不小于8px
        .style("opacity", d => d.children ? 0.7 : 1)  // 非叶子节点文本透明度降低
        .style("pointer-events", "none")
        .style("text-shadow", "0 0 2px white")
        .style("font-family", "Arial, sans-serif")
       

      // 添加缩放和平移功能
      const zoom = d3.zoom()
        .scaleExtent([0.3, 2])
        .on("zoom", (event) => {
          g.attr("transform", event.transform)
        })

      svg.call(zoom)

      // 计算初始缩放和平移以适应视图
      const bounds = g.node().getBBox()
      const fullWidth = bounds.width
      const fullHeight = bounds.height
      const scale = Math.min(
        width / fullWidth * 0.9,
        height / fullHeight * 0.9
      )
      const x = (width - fullWidth * scale) / 2
      const y = (height - fullHeight * scale) / 2

      // 应用初始变换
      svg.call(
        zoom.transform,
        d3.zoomIdentity
          .translate(x, y)
          .scale(scale)
      )
    }
    
  },
  watch: {
    selectedNodeId: {
      handler() {
        this.renderTreeGraph()
      },
      immediate: true
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
  padding: 5px;
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