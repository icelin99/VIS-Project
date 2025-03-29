<template>
  <div id="app">
    <h1 class="title">Vast Challenge 2023 MC1</h1>
    <div class="container">
      <div class="left-panel">
        <FilterPanel />
      </div>
      <div class="right-panel">
        <ForceDirectedGraph />
      </div>
    </div>
  </div>
</template>

<script>
import FilterPanel from './components/FilterPanel.vue'
import ForceDirectedGraph from './components/FDG.vue'

export default {
  name: 'App',
  components: {
    FilterPanel,
    ForceDirectedGraph
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

.title {
  height: 60px;
  line-height: 60px;
  margin: 0;
  background-color: #2c3e50;
  color: white;
  font-size: 24px;
}

.container {
  display: flex;
  min-height: 100vh;
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
</style>
