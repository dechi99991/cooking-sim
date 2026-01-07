<script setup lang="ts">
import type { AutoConsumeInfo } from '../types'

defineProps<{
  show: boolean
  info: AutoConsumeInfo | null
}>()

const emit = defineEmits<{
  close: []
}>()
</script>

<template>
  <div v-if="show && info" class="auto-consume-overlay" @click="emit('close')">
    <div class="auto-consume-modal" @click.stop>
      <div class="auto-consume-icon">☕</div>
      <h3>カフェイン摂取</h3>
      <p class="message">気力が足りなかったので</p>
      <p class="consumed-item">{{ info.consumed_name }}を飲みました！</p>
      <p class="energy-info">気力 +{{ info.energy_restored }}</p>
      <p v-if="info.will_cause_insomnia" class="warning">
        ⚠ カフェイン過多！今夜は眠れなくなりそう...
      </p>
      <button class="close-btn" @click="emit('close')">OK</button>
    </div>
  </div>
</template>

<style scoped>
.auto-consume-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.auto-consume-modal {
  background: white;
  border-radius: 12px;
  padding: 30px;
  text-align: center;
  max-width: 300px;
  width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.auto-consume-icon {
  font-size: 3em;
  margin-bottom: 10px;
}

.auto-consume-modal h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
}

.message {
  font-size: 0.9em;
  color: #7f8c8d;
  margin: 0 0 5px 0;
}

.consumed-item {
  font-size: 1.2em;
  color: #2c3e50;
  margin: 0 0 10px 0;
  font-weight: bold;
}

.energy-info {
  font-size: 1.1em;
  color: #27ae60;
  margin: 0 0 10px 0;
  font-weight: bold;
}

.warning {
  font-size: 0.9em;
  color: #e74c3c;
  margin: 0 0 15px 0;
  padding: 8px;
  background: #fef5f5;
  border-radius: 4px;
}

.close-btn {
  padding: 10px 40px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
}

.close-btn:hover {
  background: #2980b9;
}
</style>
