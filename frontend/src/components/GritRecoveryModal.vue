<script setup lang="ts">
defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  close: []
}>()
</script>

<template>
  <div v-if="show" class="grit-overlay" @click="emit('close')">
    <div class="grit-modal" @click.stop>
      <div class="grit-icon">💪</div>
      <h3>体力が無くなった…</h3>
      <p class="message">根性で動くしかない！</p>
      <div class="effect-box">
        <span class="negative">気力 -2</span>
        <span class="positive">体力 +1</span>
      </div>
      <button class="close-btn" @click="emit('close')">OK</button>
    </div>
  </div>
</template>

<style scoped>
.grit-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.grit-modal {
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  border-radius: 12px;
  padding: 30px;
  text-align: center;
  max-width: 300px;
  width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
  color: white;
}

.grit-icon {
  font-size: 3.5em;
  margin-bottom: 10px;
}

.grit-modal h3 {
  margin: 0 0 10px 0;
  font-size: 1.4em;
}

.message {
  font-size: 1.1em;
  margin: 0 0 20px 0;
  opacity: 0.9;
}

.effect-box {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 20px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 8px;
}

.negative {
  font-size: 1.2em;
  font-weight: bold;
  color: #ffcccc;
}

.positive {
  font-size: 1.2em;
  font-weight: bold;
  color: #aaffaa;
}

.close-btn {
  padding: 12px 50px;
  background: white;
  color: #c0392b;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.1em;
  font-weight: bold;
}

.close-btn:hover {
  background: #f8f9fa;
}
</style>
