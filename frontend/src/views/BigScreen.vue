<template>
  <div class="kaspersky-screen">
    <div class="scan-line"></div>
    <div class="bg-grid"></div>
    <canvas ref="mapCanvas" class="world-map-canvas"></canvas>
    
    <div class="screen-header">
      <div class="header-deco"></div>
      <div class="header-content">
        <div class="header-left">
          <div class="logo">
            <span class="logo-icon glitch-text">⚡</span>
            <div class="logo-box">
              <span class="logo-text">RED TEAM OPS</span>
              <span class="logo-sub">攻防演练协同终端 // {{ currentTime }}</span>
            </div>
          </div>
        </div>
        <div class="header-right">
          <div class="status-indicator" :class="{ 'alert-state': attackCount > 0 }">
            <span class="status-dot"></span>
            <span class="status-text">{{ attackCount > 0 ? '检测到入侵活动' : '系统监控中' }}</span>
          </div>
          <el-button class="back-btn cyber-btn" type="text" @click="goBack">
            [ 退出终端 ]
          </el-button>
        </div>
      </div>
      <div class="header-deco flip"></div>
    </div>

    <div class="screen-body">
      <div class="side-panel left-panel">
        <div class="cyber-card">
          <div class="card-corner top-left"></div>
          <div class="card-corner top-right"></div>
          <div class="card-corner bottom-left"></div>
          <div class="card-corner bottom-right"></div>
          
          <div class="panel-header">
            <span class="panel-deco-box"></span>
            <span class="panel-title">战术资源概览</span>
          </div>
          <div class="stats-grid">
            <div class="stat-item" v-for="(item, index) in coreData" :key="index">
              <div class="stat-label">{{ item.label }}</div>
              <div class="stat-val-wrapper">
                <span class="stat-value">{{ item.value }}</span>
                <span class="unit">{{ item.unit }}</span>
              </div>
              <div class="stat-progress">
                <div class="stat-progress-bar" :style="{width: (Math.random() * 40 + 60) + '%'}"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="cyber-card flex-grow" @mouseenter="pauseRotation" @mouseleave="resumeRotation">
          <div class="card-corner top-left"></div>
          <div class="card-corner top-right"></div>
          <div class="card-corner bottom-left"></div>
          <div class="card-corner bottom-right"></div>
          
          <div class="panel-header tab-header">
            <div 
              class="tab-btn" 
              :class="{ active: activeTab === 'vuln' }"
              @click="switchTab('vuln')"
            >
              <span class="panel-deco-box warn"></span>
              <span class="panel-title">漏洞生命周期</span>
            </div>
            <div class="tab-divider">//</div>
            <div 
              class="tab-btn" 
              :class="{ active: activeTab === 'asset' }"
              @click="switchTab('asset')"
            >
              <span class="panel-deco-box"></span>
              <span class="panel-title">目标资产指纹</span>
            </div>
          </div>

          <div class="panel-content relative-container">
            <transition name="fade-slide">
              <div v-show="activeTab === 'vuln'" class="tab-content-wrapper">
                <div class="vuln-stats-grid">
                  <div class="vuln-stat-item">
                    <div class="vuln-stat-label">总漏洞</div>
                    <div class="vuln-stat-value total">{{ vulnData.total }}</div>
                  </div>
                  <div class="vuln-stat-item">
                    <div class="vuln-stat-label">已提交</div>
                    <div class="vuln-stat-value submitted">{{ vulnData.submitted }}</div>
                  </div>
                  <div class="vuln-stat-item">
                    <div class="vuln-stat-label">未提交</div>
                    <div class="vuln-stat-value not-submitted">{{ vulnData.notSubmitted }}</div>
                  </div>
                  <div class="vuln-stat-item">
                    <div class="vuln-stat-label">已修复</div>
                    <div class="vuln-stat-value fixed">{{ vulnData.fixed }}</div>
                  </div>
                  <div class="vuln-stat-item">
                    <div class="vuln-stat-label">未修复</div>
                    <div class="vuln-stat-value not-fixed">{{ vulnData.notFixed }}</div>
                  </div>
                  <div class="vuln-stat-item">
                    <div class="vuln-stat-label">无法访问</div>
                    <div class="vuln-stat-value no-access">{{ vulnData.noAccess }}</div>
                  </div>
                </div>
              </div>
            </transition>

            <transition name="fade-slide">
              <div v-show="activeTab === 'asset'" class="tab-content-wrapper">
                 <div ref="assetTypeChart" class="chart"></div>
              </div>
            </transition>
          </div>
        </div>
      </div>

      <div class="center-map">
        <div class="map-decoration-circle"></div>
        <div class="map-overlay">
          <div ref="worldMapChart" class="world-chart"></div>
        </div>
        
        <div class="attack-hud">
          <div class="hud-line"></div>
          <div class="counter-label">THREAT LEVEL // 威胁指数</div>
          <div class="counter-value glitch-text">
            {{ attackCount }}
          </div>
          <div class="hud-status">ACTIVE</div>
        </div>
      </div>

      <div class="side-panel right-panel">
        <div class="cyber-card chart-container-fixed">
          <div class="card-corner top-left"></div>
          <div class="card-corner top-right"></div>
          <div class="card-corner bottom-left"></div>
          <div class="card-corner bottom-right"></div>

          <div class="panel-header">
            <span class="panel-deco-box warn"></span>
            <span class="panel-title">漏洞危害评级</span>
          </div>
          <div class="panel-content">
            <div ref="riskChart" class="chart"></div>
          </div>
        </div>

        <div class="cyber-card flex-grow">
          <div class="card-corner top-left"></div>
          <div class="card-corner top-right"></div>
          <div class="card-corner bottom-left"></div>
          <div class="card-corner bottom-right"></div>

          <div class="panel-header">
            <span class="panel-deco-box active"></span>
            <span class="panel-title">作战日志流</span>
          </div>
          <div class="activity-stream terminal-font">
            <div class="activity-item" v-for="(item, index) in activities" :key="index">
              <span class="cmd-prompt">></span>
              <span class="activity-time">[{{ item.time ? (item.time.split(' ')[1] || item.time) : 'LOG' }}]</span>
              <span class="activity-text">{{ item.text }}</span>
            </div>
            <div class="typing-cursor">_</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import request from '../utils/request'
import worldJson from '@/assets/world.json'

export default {
  name: 'BigScreen',
  setup() {
    const router = useRouter()
    const mapCanvas = ref(null)
    const worldMapChart = ref(null)
    const assetTypeChart = ref(null)
    const riskChart = ref(null)
    const currentTime = ref('')
    
    // === 新增：轮播控制 ===
    const activeTab = ref('vuln') // 'vuln' or 'asset'
    let rotateTimer = null

    // 核心数据
    const coreData = ref([
      { label: '总资产数', value: 0, unit: '个' },
      { label: '项目数量', value: 0, unit: '个' },
      { label: '用户数量', value: 0, unit: '人' },
      { label: '今日新增', value: 0, unit: '个' }
    ])
    
    const activities = ref([])
    const attackCount = computed(() => (coreData.value[0].value || 0) + (coreData.value[3].value || 0))

    const vulnData = ref({
      total: 0, submitted: 0, notSubmitted: 0, fixed: 0, notFixed: 0, noAccess: 0
    })

    let assetTypeChartInstance = null
    let riskChartInstance = null
    let worldMapChartInstance = null
    let timeInterval = null
    let dataInterval = null

    const updateTime = () => {
      const now = new Date()
      const timeStr = now.toTimeString().split(' ')[0]
      const dateStr = now.toISOString().split('T')[0]
      currentTime.value = `${dateStr} ${timeStr}`
    }

    // === 新增：轮播逻辑 ===
    const switchTab = (tab) => {
      activeTab.value = tab
      // 如果切换到图表Tab，必须重新调整图表大小，否则可能因为display:none导致宽度为0
      if (tab === 'asset') {
        nextTick(() => {
          assetTypeChartInstance?.resize()
        })
      }
    }

    const startRotation = () => {
      stopRotation()
      rotateTimer = setInterval(() => {
        const next = activeTab.value === 'vuln' ? 'asset' : 'vuln'
        switchTab(next)
      }, 5000) // 5秒切换一次
    }

    const stopRotation = () => {
      if (rotateTimer) clearInterval(rotateTimer)
    }

    const pauseRotation = () => stopRotation()
    const resumeRotation = () => startRotation()


    const loadData = async () => {
      try {
        const res = await request.get('/dashboard/bigscreen')
        if (res.success) {
          const data = res.data
          
          coreData.value[0].value = data.totalAssets || 0
          coreData.value[1].value = data.totalProjects || 0
          coreData.value[2].value = data.totalUsers || 0
          coreData.value[3].value = data.todayAssets || 0
          
          activities.value = data.recentActivities || []
          
          vulnData.value.total = data.totalVulnerabilities || 0
          vulnData.value.submitted = data.vulnSubmitted || 0
          vulnData.value.notSubmitted = data.vulnNotSubmitted || 0
          vulnData.value.fixed = data.vulnFixed || 0
          vulnData.value.notFixed = data.vulnNotFixed || 0
          vulnData.value.noAccess = data.vulnNoAccess || 0

          nextTick(() => {
            renderAssetTypeChart(data.assetTypeDistribution || [])
            renderRiskChart(data.riskLevelDistribution || [])
            renderWorldMap()
          })
        }
      } catch (error) {
        console.error('数据加载失败，尝试使用默认数据渲染图表', error)
        renderAssetTypeChart([])
        renderRiskChart([])
      }
    }

    const chartConfig = {
      backgroundColor: 'transparent',
      textStyle: { fontFamily: 'Consolas, monospace', color: '#00f2ff' }
    }

    const renderAssetTypeChart = (data) => {
      if (!assetTypeChart.value) return
      // 注意：这里不能重复init，如果已存在则复用，否则会导致内存泄漏或警告
      if (!assetTypeChartInstance) {
         assetTypeChartInstance = echarts.init(assetTypeChart.value)
      }
      
      const finalData = data.length ? data : [{name: '无数据', value: 0}]
      
      const option = {
        ...chartConfig,
        color: ['#ff003c', '#00f2ff', '#ebff00', '#bd00ff', '#00ff9d'],
        tooltip: { trigger: 'item', backgroundColor: 'rgba(0,0,0,0.9)', borderColor: '#00f2ff', textStyle: { color: '#00f2ff' } },
        legend: { 
          orient: 'vertical', 
          right: 0, 
          top: 'middle', 
          textStyle: { color: 'rgba(255,255,255,0.8)', fontSize: 10 } 
        },
        series: [{
          type: 'pie', 
          radius: ['40%', '70%'], // 稍微调小一点半径以适应自适应容器
          center: ['35%', '50%'],
          itemStyle: { borderRadius: 2, borderColor: '#000', borderWidth: 2 },
          label: { show: false },
          data: finalData.map(item => ({ name: item.type || item.name, value: item.count || item.value }))
        }]
      }
      assetTypeChartInstance.setOption(option)
    }

    const renderRiskChart = (data) => {
      if (!riskChart.value) return
      if (!riskChartInstance) riskChartInstance = echarts.init(riskChart.value)
      
      const colorMap = { '高危': '#ff003c', '中危': '#ebff00', '低危': '#00f2ff' }
      const option = {
        ...chartConfig,
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, backgroundColor: 'rgba(0,0,0,0.9)', borderColor: '#ff003c', textStyle: { color: '#fff' } },
        grid: { top: '10%', bottom: '5%', left: '20%', right: '5%', containLabel: false },
        xAxis: { show: false },
        yAxis: { type: 'category', data: data.map(i => i.level), axisLine: {show:false}, axisTick: {show:false}, axisLabel: { color: '#00f2ff' } },
        series: [{
          type: 'bar', barWidth: 10,
          label: { show: true, position: 'right', color: '#fff' },
          itemStyle: { color: p => colorMap[p.name] || '#00f2ff', barBorderRadius: [0,4,4,0] },
          data: data.map(i => ({ value: i.count, name: i.level }))
        }]
      }
      riskChartInstance.setOption(option)
    }

    const renderWorldMap = () => {
      if (!worldMapChart.value) return
      if (!worldMapChartInstance) worldMapChartInstance = echarts.init(worldMapChart.value)
      
      const attackPoints = Array.from({length: 30}, () => {
        const isAttack = Math.random() > 0.7
        return {
          value: [Math.random() * 360 - 180, Math.random() * 160 - 80, Math.random() * 100],
          itemStyle: { color: isAttack ? '#ff003c' : '#00f2ff' },
          symbol: isAttack ? 'diamond' : 'circle'
        }
      })
      
      const option = {
        backgroundColor: 'transparent',
        geo: {
          map: 'world',
          roam: true,
          zoom: 1.2,
          label: { show: false },
          itemStyle: { areaColor: 'rgba(20, 30, 40, 0.8)', borderColor: '#1c4e5e', borderWidth: 1, shadowBlur: 10, shadowColor: 'rgba(0, 242, 255, 0.2)' },
          emphasis: { itemStyle: { areaColor: '#2a4b5b' } }
        },
        series: [
          { type: 'scatter', coordinateSystem: 'geo', data: attackPoints, symbolSize: v => v[2]/12 + 2, zlevel: 1 },
          { 
            type: 'effectScatter', coordinateSystem: 'geo', 
            data: attackPoints.filter(p => p.itemStyle.color === '#ff003c').slice(0, 5),
            symbolSize: 15, rippleEffect: { scale: 4, brushType: 'stroke' }, itemStyle: { color: '#ff003c' }, zlevel: 2 
          }
        ]
      }
      worldMapChartInstance.setOption(option)
    }

    const initCanvas = () => {
      if (!mapCanvas.value) return
      const canvas = mapCanvas.value
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
      const ctx = canvas.getContext('2d')
      const drops = Array(Math.floor(canvas.width / 20)).fill(1)
      
      const animate = () => {
        ctx.fillStyle = 'rgba(0, 10, 18, 0.1)'
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        ctx.fillStyle = '#0f0'
        ctx.font = '12px monospace'
        drops.forEach((y, i) => {
          const text = String.fromCharCode(0x30A0 + Math.random() * 96)
          ctx.fillStyle = Math.random() > 0.95 ? '#00f2ff' : 'rgba(0, 242, 255, 0.1)'
          ctx.fillText(text, i * 20, y * 20)
          if (y * 20 > canvas.height && Math.random() > 0.975) drops[i] = 0
          drops[i]++
        })
        requestAnimationFrame(animate)
      }
      animate()
    }

    const goBack = () => router.push('/dashboard')

    const handleResize = () => {
      assetTypeChartInstance?.resize()
      riskChartInstance?.resize()
      worldMapChartInstance?.resize()
      if (mapCanvas.value) {
        mapCanvas.value.width = window.innerWidth
        mapCanvas.value.height = window.innerHeight
      }
    }

    onMounted(() => {
      echarts.registerMap('world', worldJson)
      updateTime()
      timeInterval = setInterval(updateTime, 1000)
      initCanvas()
      loadData()
      dataInterval = setInterval(loadData, 30000)
      window.addEventListener('resize', handleResize)
      startRotation() // 启动轮播
    })

    onUnmounted(() => {
      clearInterval(timeInterval)
      clearInterval(dataInterval)
      stopRotation() // 停止轮播
      window.removeEventListener('resize', handleResize)
      assetTypeChartInstance?.dispose()
      riskChartInstance?.dispose()
      worldMapChartInstance?.dispose()
    })

    return {
      mapCanvas, worldMapChart, assetTypeChart, riskChart,
      currentTime, coreData, activities, attackCount, vulnData,
      activeTab, switchTab, pauseRotation, resumeRotation, // 新增导出
      goBack
    }
  }
}
</script>

<style scoped>
/* ========== 全局布局 ========== */
.kaspersky-screen {
  width: 100vw;
  height: 100vh;
  background-color: #02060b;
  color: #00f2ff;
  font-family: 'Share Tech Mono', 'Consolas', 'Courier New', monospace;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column; /* 确保整体纵向布局 */
}

/* 动效保持不变... */
.scan-line {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 4px;
  background: rgba(0, 242, 255, 0.3);
  box-shadow: 0 0 10px rgba(0, 242, 255, 0.5);
  animation: scan 6s linear infinite;
  z-index: 5;
  opacity: 0.3;
  pointer-events: none;
}
@keyframes scan { 0% { top: -5%; } 100% { top: 105%; } }

.bg-grid {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  background-image: linear-gradient(rgba(0, 242, 255, 0.03) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(0, 242, 255, 0.03) 1px, transparent 1px);
  background-size: 40px 40px;
  z-index: 0;
  pointer-events: none;
}

.world-map-canvas {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  z-index: 1;
  opacity: 0.3;
  pointer-events: none;
}

/* Header */
.screen-header {
  height: 80px;
  flex-shrink: 0; /* 防止头部被压缩 */
  display: flex;
  justify-content: space-between;
  position: relative;
  z-index: 10;
  background: linear-gradient(180deg, rgba(0,15,25,0.9) 0%, rgba(0,0,0,0) 100%);
  border-bottom: 1px solid rgba(0, 242, 255, 0.2);
}
.header-deco { width: 50px; height: 100%; background: repeating-linear-gradient(45deg, rgba(0, 242, 255, 0.2) 0, rgba(0, 242, 255, 0.2) 2px, transparent 2px, transparent 8px); }
.header-deco.flip { transform: scaleX(-1); }
.header-content { flex: 1; display: flex; justify-content: space-between; align-items: center; padding: 0 20px; }
.logo { display: flex; align-items: center; gap: 15px; }
.logo-icon { font-size: 32px; color: #ff003c; text-shadow: 0 0 15px #ff003c; }
.logo-text { font-size: 24px; font-weight: bold; letter-spacing: 4px; color: #fff; text-shadow: 0 0 10px rgba(0, 242, 255, 0.5); }
.logo-sub { font-size: 12px; color: #00f2ff; opacity: 0.7; }
.header-right { display: flex; align-items: center; gap: 20px; }
.status-indicator { display: flex; align-items: center; gap: 8px; padding: 6px 16px; border: 1px solid #00f2ff; background: rgba(0, 242, 255, 0.05); }
.status-dot { width: 8px; height: 8px; background: #00f2ff; border-radius: 50%; box-shadow: 0 0 10px #00f2ff; }
.alert-state { border-color: #ff003c; background: rgba(255, 0, 60, 0.1); animation: pulse-border 1s infinite alternate; }
.alert-state .status-dot { background: #ff003c; animation: blink-dot 0.5s infinite; }
.alert-state .status-text { color: #ff003c; font-weight: bold; }
.cyber-btn { font-family: 'Consolas', monospace; color: rgba(255,255,255,0.6) !important; letter-spacing: 1px; }
.cyber-btn:hover { color: #fff !important; text-shadow: 0 0 8px #fff; }

/* Body Layout */
.screen-body {
  display: flex;
  flex: 1; /* 占据剩余空间 */
  overflow: hidden; /* 确保body内部不会溢出 */
  padding: 20px;
  gap: 20px;
  position: relative;
  z-index: 2;
}

/* 面板通用逻辑：纵向Flex，高度自适应 */
.side-panel { 
  flex: 0 0 380px; 
  display: flex; 
  flex-direction: column; 
  gap: 20px; 
  height: 100%; /* 占满body的高度 */
}

/* flex-grow 让元素自动填充 Flex 容器的剩余空间 */
.flex-grow { 
  flex: 1; 
  min-height: 0; /* 关键：允许flex子项缩小到0，防止内容撑开容器 */
  display: flex;
  flex-direction: column;
}

/* 右侧上方图表固定高度，或根据需要调整 */
.chart-container-fixed {
  height: 35%; /* 占据大约35%的高度 */
  min-height: 200px;
}

.center-map {
  flex: 1;
  position: relative;
  border: 1px solid rgba(0, 242, 255, 0.1);
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  clip-path: polygon(0 0, 100% 0, 100% calc(100% - 30px), calc(100% - 30px) 100%, 0 100%);
}

/* 卡片样式 */
.cyber-card {
  position: relative;
  background: rgba(4, 12, 20, 0.85);
  border: 1px solid rgba(0, 242, 255, 0.15);
  padding: 20px;
  backdrop-filter: blur(4px);
  box-shadow: inset 0 0 30px rgba(0, 242, 255, 0.02);
  display: flex;
  flex-direction: column;
}

.card-corner { position: absolute; width: 8px; height: 8px; border: 2px solid #00f2ff; transition: all 0.3s; }
.top-left { top: -1px; left: -1px; border-right: 0; border-bottom: 0; }
.top-right { top: -1px; right: -1px; border-left: 0; border-bottom: 0; }
.bottom-left { bottom: -1px; left: -1px; border-right: 0; border-top: 0; }
.bottom-right { bottom: -1px; right: -1px; border-left: 0; border-top: 0; }
.cyber-card:hover { border-color: rgba(0, 242, 255, 0.3); }
.cyber-card:hover .card-corner { width: 15px; height: 15px; box-shadow: 0 0 5px #00f2ff; }

.panel-header { display: flex; align-items: center; gap: 12px; margin-bottom: 15px; border-bottom: 1px solid rgba(0, 242, 255, 0.1); padding-bottom: 10px; flex-shrink: 0; }
.panel-deco-box { width: 12px; height: 12px; background: #00f2ff; box-shadow: 0 0 8px #00f2ff; }
.panel-deco-box.warn { background: #ff003c; box-shadow: 0 0 8px #ff003c; }
.panel-deco-box.active { background: #ebff00; box-shadow: 0 0 8px #ebff00; }
.panel-title { font-size: 16px; font-weight: bold; color: #fff; letter-spacing: 1px; text-transform: uppercase; }

/* Tab Header Customization */
.tab-header {
  cursor: pointer;
  justify-content: flex-start;
}
.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  opacity: 0.5;
  transition: all 0.3s;
}
.tab-btn:hover, .tab-btn.active {
  opacity: 1;
}
.tab-btn.active .panel-title {
  text-shadow: 0 0 10px rgba(0,242,255,0.5);
}
.tab-divider {
  color: #00f2ff;
  opacity: 0.3;
  margin: 0 5px;
}

.panel-content { flex: 1; min-height: 0; position: relative; }
/* 相对定位容器，用于 Tab 切换的内容堆叠 */
.relative-container { position: relative; overflow: hidden; }
.tab-content-wrapper {
  width: 100%;
  height: 100%;
  position: absolute; /* 绝对定位以支持过渡动画 */
  top: 0; left: 0;
  display: flex;
  flex-direction: column;
}

.chart { width: 100%; height: 100%; }

/* 过渡动画 */
.fade-slide-enter-active, .fade-slide-leave-active {
  transition: all 0.5s ease;
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* 统计数字 */
.stats-grid { display: flex; flex-direction: column; gap: 10px; overflow-y: auto; }
.stat-item { padding: 10px; background: linear-gradient(90deg, rgba(0, 242, 255, 0.05) 0%, transparent 100%); border-left: 2px solid #00f2ff; }
.stat-label { font-size: 12px; color: #00f2ff; margin-bottom: 5px; text-transform: uppercase; }
.stat-val-wrapper { display: flex; align-items: baseline; gap: 5px; }
.stat-value { font-size: 24px; color: #fff; font-weight: bold; text-shadow: 0 0 10px rgba(0, 242, 255, 0.5); }
.unit { font-size: 14px; color: rgba(255, 255, 255, 0.6); }
.stat-progress { width: 100%; height: 2px; background: #111; margin-top: 5px; }
.stat-progress-bar { height: 100%; background: #00f2ff; box-shadow: 0 0 5px #00f2ff; }

/* 漏洞网格 - 使用Flex wrap或Grid自适应 */
.vuln-stats-grid { 
  display: grid; 
  grid-template-columns: repeat(2, 1fr); 
  gap: 10px; 
  align-content: start; /* 向上对齐 */
  overflow-y: auto;
  padding-right: 5px;
}
.vuln-stat-item { padding: 10px; background: rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 4px; text-align: center; }
.vuln-stat-label { font-size: 11px; color: rgba(255, 255, 255, 0.7); margin-bottom: 5px; }
.vuln-stat-value { font-size: 22px; font-weight: bold; color: #fff; }
.vuln-stat-value.total { color: #00f2ff; text-shadow: 0 0 15px #00f2ff; }
.vuln-stat-value.submitted { color: #00ff9d; }
.vuln-stat-value.not-submitted { color: #ebff00; }
.vuln-stat-value.fixed { color: #00ff9d; }
.vuln-stat-value.not-fixed { color: #ff003c; }
.vuln-stat-value.no-access { color: #999; }

/* 地图装饰 */
.map-overlay { width: 100%; height: 100%; }
.world-chart { width: 100%; height: 100%; }
.map-decoration-circle { position: absolute; width: 500px; height: 500px; border: 1px dashed rgba(0, 242, 255, 0.1); border-radius: 50%; pointer-events: none; animation: rotate 30s linear infinite; }
.attack-hud { position: absolute; bottom: 40px; left: 50%; transform: translateX(-50%); text-align: center; background: rgba(0, 0, 0, 0.7); padding: 20px 60px; border: 1px solid #ff003c; box-shadow: 0 0 30px rgba(255, 0, 60, 0.2); clip-path: polygon(15% 0, 100% 0, 100% 100%, 0 100%, 0 30%); z-index: 5; }
.hud-line { position: absolute; top: 0; left: 0; width: 100%; height: 2px; background: #ff003c; }
.counter-label { font-size: 12px; color: #ff003c; margin-bottom: 5px; letter-spacing: 2px; }
.counter-value { font-size: 56px; color: #fff; font-weight: bold; text-shadow: 0 0 20px #ff003c; line-height: 1; }
.hud-status { font-size: 12px; color: #fff; background: #ff003c; display: inline-block; padding: 2px 8px; margin-top: 10px; }

/* 日志流 */
.activity-stream { flex: 1; overflow-y: auto; font-size: 12px; display: flex; flex-direction: column; justify-content: flex-end; padding-right: 5px; min-height: 0; }
.activity-item { margin-bottom: 6px; display: flex; gap: 8px; opacity: 0.8; border-bottom: 1px dashed rgba(255,255,255,0.05); padding-bottom: 2px; }
.cmd-prompt { color: #00f2ff; }
.activity-time { color: #666; }
.activity-text { color: #ddd; }
.typing-cursor { color: #00f2ff; animation: blink 1s step-end infinite; }

/* 动画 */
@keyframes rotate { to { transform: rotate(360deg); } }
@keyframes pulse-border { from { box-shadow: 0 0 5px #ff003c; } to { box-shadow: 0 0 20px #ff003c; } }
@keyframes blink-dot { 0%,100% { opacity: 1; } 50% { opacity: 0; } }
@keyframes blink { 50% { opacity: 0; } }
.glitch-text { animation: glitch 3s infinite; }
@keyframes glitch {
  0%, 90% { text-shadow: 0 0 0 #ff003c; }
  92% { text-shadow: -2px 0 #00f2ff, 2px 0 #ff003c; transform: translateX(1px); }
  94% { text-shadow: 2px 0 #00f2ff, -2px 0 #ff003c; transform: translateX(-1px); }
  96% { text-shadow: 0 0 0 #ff003c; transform: translateX(0); }
}

/* ==================== 响应式 ==================== */

@media (max-width: 1366px) {
  .side-panel { flex: 0 0 300px; }
  .attack-hud { padding: 15px 30px; }
  .counter-value { font-size: 40px; }
  .logo-text { font-size: 20px; }
}

@media (max-width: 1024px) {
  .kaspersky-screen {
    height: auto;
    min-height: 100vh;
    overflow-y: auto;
    overflow-x: hidden;
  }
  .screen-body {
    flex-direction: column;
    height: auto;
    gap: 15px;
    padding-bottom: 40px;
  }
  .side-panel {
    flex: none;
    width: 100%;
    height: auto; /* 移动端取消高度继承，由内容撑开 */
  }
  /* 移动端需要固定高度，因为不再是Flex自适应 */
  .flex-grow {
    height: 400px;
    flex: none;
  }
  .chart-container-fixed {
    height: 300px;
  }
  .center-map {
    order: -1;
    min-height: 350px;
    width: 100%;
    margin-bottom: 10px;
    clip-path: none;
  }
  .map-decoration-circle {
    width: 280px; height: 280px;
    top: 50%; left: 50%; margin-top: -140px; margin-left: -140px;
  }
}

@media (max-width: 600px) {
  .screen-header { padding: 10px; height: 60px; }
  .header-content { padding: 0 5px; }
  .logo-icon { font-size: 24px; }
  .logo-text { font-size: 16px; letter-spacing: 1px; }
  .logo-sub { display: none; }
  .status-text { display: none; }
  .vuln-stats-grid { grid-template-columns: repeat(3, 1fr); gap: 5px; }
  .vuln-stat-value { font-size: 16px; }
  .attack-hud { bottom: 10px; width: 90%; padding: 10px; }
  .counter-value { font-size: 32px; }
  .counter-label { font-size: 10px; }
}
</style>