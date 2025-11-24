<template>
  <div class="cyber-decoration" :class="type">
    <svg v-if="type === 'header-border'" width="100%" height="100%" viewBox="0 0 1000 50" preserveAspectRatio="none">
      <path d="M0,50 L20,20 L300,20 L320,50 L680,50 L700,20 L980,20 L1000,50" fill="none" stroke="#00d4ff" stroke-width="2" vector-effect="non-scaling-stroke"/>
      <path d="M35,25 L290,25" stroke="#00d4ff" stroke-width="2" stroke-dasharray="5,5" class="blink"/>
      <path d="M710,25 L965,25" stroke="#00d4ff" stroke-width="2" stroke-dasharray="5,5" class="blink"/>
    </svg>

    <svg v-if="type === 'panel-corner'" width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none">
      <path d="M0,0 L20,0 L0,20 Z" fill="#00d4ff"/>
      <path d="M100,0 L80,0 L100,20 Z" fill="#00d4ff"/>
      <path d="M0,100 L0,80 L20,100 Z" fill="#00d4ff"/>
      <path d="M100,100 L80,100 L100,80 Z" fill="#00d4ff"/>
    </svg>

    <div v-if="type === 'scan-line'" class="scan-line-inner"></div>
  </div>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    default: 'header-border'
  }
})
</script>

<style scoped>
.cyber-decoration {
  position: absolute;
  pointer-events: none;
}

.blink {
  animation: blink 2s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.scan-line-inner {
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00d4ff, transparent);
  position: absolute;
  top: 0;
  left: 0;
  animation: scan 3s linear infinite;
}

@keyframes scan {
  0% { top: 0%; opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { top: 100%; opacity: 0; }
}
</style>
