<template>
  <div id="app">
    <div class="header-container">
      <h1 class="title">Vast Challenge 2023 MC1</h1>
      
      <!-- 修改后的选项卡导航 -->
      <div class="tab-navigation">
        <button 
          @click="currentTab = 'forceDirected'"
          :class="{ active: currentTab === 'forceDirected' }"
        >
          Force Directed Graph
        </button>
        <button 
          @click="currentTab = 'treeGraph'"
          :class="{ active: currentTab === 'treeGraph' }"
        >
          Tree Graph
        </button>
        <button 
          @click="currentTab = 'parallelCoordinates'"
          :class="{ active: currentTab === 'parallelCoordinates' }"
        >
          Parallel Coordinates
        </button>
      </div>
    </div>

    <div class="container">
      <!-- 根据当前选项卡显示不同内容 -->
      <template v-if="currentTab === 'forceDirected'">
        <div class="left-panel">
          <FilterPanel />
        </div>
        <div class="right-panel">
          <ForceDirectedGraph />
        </div>
      </template>

      <template v-else-if="currentTab === 'treeGraph'">
        <div class="full-panel">
          <NetworkGraph
           :links="linksData"
           :nodes="nodesData" />
        </div>
      </template>

      <template v-else-if="currentTab === 'parallelCoordinates'">
        <div class="full-panel">
          <ParallelCoordinates :nodes="coefData" />
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import FilterPanel from './components/FilterPanel.vue'
import ForceDirectedGraph from './components/FDG.vue'
import NetworkGraph from './components/NetworkGraph.vue'
import ParallelCoordinates from './components/ParallelCoordinates.vue'
import linksData from './assets/tree_relation.json'
import nodesData from './assets/tree_nodes.json'
import coefData from './assets/nodes_coef.json'

export default {
  name: 'App',
  components: {
    FilterPanel,
    ForceDirectedGraph,
    NetworkGraph,
    ParallelCoordinates
  },
  data() {
    return {
      linksData: linksData.links || [],
      nodesData: nodesData.nodes || [],
      coefData: coefData.nodes || [],
      currentTab: 'forceDirected' // 默认显示Force Directed Graph
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  background-color: #2c3e50;
  padding: 0 20px;
}

.title {
  margin: 0;
  color: white;
  font-size: 24px;
  line-height: 60px;
}

/* 修改后的选项卡导航样式 */
.tab-navigation {
  display: flex;
  gap: 10px;
}

.tab-navigation button {
  padding: 8px 16px;
  border: none;
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 4px;
}

.tab-navigation button:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

.tab-navigation button.active {
  background-color: white;
  color: #2c3e50;
  font-weight: bold;
}

.container {
  display: flex;
  min-height: calc(100vh - 60px); /* 只减去标题高度 */
}

.left-panel {
  flex: 1;
  background-color: #f8fafd;
  padding: 20px 10px;
  border-right: 1px solid #ddd;
}

.right-panel {
  flex: 4;
  background-color: rgb(230, 237, 248);
}

.full-panel {
  width: 100%;
  background-color: rgb(230, 237, 248);
  padding: 20px;
  box-sizing: border-box;
}
</style>