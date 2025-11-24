<template>
  <div class="tech-decoration" :class="type">
    <!-- Minimal Header Line: Just a thin line with a glowing center -->
    <div v-if="type === 'header-line'" class="header-line">
      <div class="line-left"></div>
      <div class="line-center"></div>
      <div class="line-right"></div>
    </div>

    <!-- Minimal Corner: Just thin L-shapes -->
    <svg v-if="type === 'panel-border'" width="100%" height="100%" class="panel-border">
      <path d="M0,0 L10,0 L0,10 Z" fill="#00f2fe" opacity="0.8"/>
      <path d="M100%,0 Lcalc(100% - 10px),0 L100%,10 Z" fill="#00f2fe" opacity="0.8" transform="translate(0,0) scale(-1,1)" transform-origin="center"/>
      <rect x="0" y="0" width="100%" height="1" fill="url(#grad1)" opacity="0.3"/>
      <rect x="0" y="100%" width="100%" height="1" fill="url(#grad1)" opacity="0.3"/>
      
      <defs>
        <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" style="stop-color:transparent;stop-opacity:0" />
          <stop offset="50%" style="stop-color:#00f2fe;stop-opacity:1" />
          <stop offset="100%" style="stop-color:transparent;stop-opacity:0" />
        </linearGradient>
      </defs>
    </svg>

    <!-- Pulsing Dot for Titles -->
    <div v-if="type === 'title-pulse'" class="title-pulse"></div>
  </div>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    default: 'header-line'
  }
})
</script>

<style scoped>
.tech-decoration {
  position: absolute;
  pointer-events: none;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
}

.header-line {
  width: 100%;
  height: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: absolute;
  bottom: 0;
}

.line-left, .line-right {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(0, 242, 254, 0.3));
}

.line-right {
  background: linear-gradient(90deg, rgba(0, 242, 254, 0.3), transparent);
}

.line-center {
  width: 100px;
  height: 2px;
  background: #00f2fe;
  box-shadow: 0 0 10px #00f2fe;
}

.panel-border {
  pointer-events: none;
}

.title-pulse {
  width: 6px;
  height: 6px;
  background: #00f2fe;
  border-radius: 50%;
  box-shadow: 0 0 0 0 rgba(0, 242, 254, 0.7);
  animation: pulse-blue 2s infinite;
  display: inline-block;
  margin-right: 8px;
  vertical-align: middle;
  position: relative;
}

@keyframes pulse-blue {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(0, 242, 254, 0.7);
  }
  70% {
    transform: scale(1);
    box-shadow: 0 0 0 6px rgba(0, 242, 254, 0);
  }
  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(0, 242, 254, 0);
  }
}
</style>
