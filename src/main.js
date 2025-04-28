import { createApp } from 'vue'
import App from './App.vue'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as echarts from 'echarts'


const app = createApp(App)
app.use(store)
app.use(ElementPlus)
app.config.globalProperties.$echarts = echarts
app.mount('#app')
