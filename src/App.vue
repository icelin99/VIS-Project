<template>
  <div id="app">
    <div class="header-container">
      <h1 class="title">Vast Challenge 2023 MC1</h1>
    </div>

    <div class="main-container">
      <div class="left-panel">
        <div class="left-top-container">
          <div class="filter-panel">
            <FilterPanel />
          </div>
          <div class="fdg-container">
            <FDG />
          </div>
        </div>
        <div class="left-bottom-container">
          <div class="subgraphs-container">
            <SubGraphs />
          </div>
        </div>
      </div>
      <div class="right-panel">
        <div class="network-wrapper">
          <NetworkGraph />
        </div>
        <div class="parallel-wrapper">
          <ParallelCoordinates :nodes="coefData" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import FilterPanel from './components/FilterPanel.vue'
import FDG from './components/FDG.vue'
import SubGraphs from './components/SubGraphs.vue'
import NetworkGraph from './components/NetworkGraph.vue'
import ParallelCoordinates from './components/ParallelCoordinates.vue'
import { useStore } from 'vuex'

export default {
  name: 'App',
  components: {
      FilterPanel,
      FDG,
      SubGraphs,
      NetworkGraph,
      ParallelCoordinates
    },
  setup() {
    const store = useStore()
    return { 
      store
    }
  },
  async mounted() {
    console.log('App 组件挂载，开始加载数据...')
    try {
      await this.store.dispatch('loadData')
      const coefData = await fetch('/assets/nodes_coef.json');
      this.coefData = await coefData.json();
      console.log('数据加载完成')
    } catch (error) {
      console.error('数据加载失败:', error)
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

.main-container {
  display: flex;
  gap: 10px;
  background-color: #e6effe;
  height: calc(100vh - 60px); /* 减去header高度 */
  padding: 10px;
  box-sizing: border-box;
  width: 100%;
}

.left-panel {
  display: flex;
  flex-direction: column;
  gap: 7px;
  width: 68%;
  height: 100%;
}

.left-top-container {
  display: flex;
  flex-direction: row; /* 横向排列 */
  gap: 10px;
  height: 70%; /* 占83%高度 */
}

.left-bottom-container {
  height: 30%; /* 占17%高度 */
}

.filter-panel {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: calc(30% - 20px); /* filter panel占left-top的30% */
  height: calc(100% - 30px);
}

.fdg-container {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: calc(70% - 20px); /* filter panel占left-top的30% */
  height: calc(100% - 30px);
}

.subgraphs-container {
  background: white;
  border-radius: 4px;
  width: calc(100% - 5px); /* filter panel占left-top的30% */
  height: calc(100% - 5px);
  display: flex;
  flex-direction: row;
  gap: 10px;

}

.right-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 32%;
  height: 100%;
}

.network-wrapper {
  flex: 1;
  background: white;
  border-radius: 4px;
  padding: 10px;
  width: calc(100% - 20px); /* filter panel占left-top的30% */
  height: calc(100% - 30px);
}

.parallel-wrapper {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  flex: 1;
  width: calc(100% - 30px); /* filter panel占left-top的30% */
  height: calc(100% - 30px);
}

/* 确保所有容器内的组件能填充整个空间 */
.filter-panel > *,
.fdg-container > *,
.subgraphs-container > *,
.network-container > *,
.parallel-container > * {
  width: 100%;
  height: 100%;
}

/* 确保subgraphs中的每个子图都能正确显示 */
.subgraph {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.content-wrapper h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
  text-align: left;
}

.content-placeholder {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 16px;
  background: #f8f9fa;
  border-radius: 4px;
  padding: 20px;
}
</style>