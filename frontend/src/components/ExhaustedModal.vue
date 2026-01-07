<script setup lang="ts">
defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  close: []
}>()
</script>

<template>
  <div v-if="show" class="exhausted-overlay">
    <div class="exhausted-modal">
      <div class="exhausted-icon">😵</div>
      <h3>あなたは力尽きた…</h3>
      <p class="message">体力も気力も底を尽きてしまった</p>
      <button class="close-btn" @click="emit('close')">結果を見る</button>
    </div>
  </div>
</template>

<style scoped>
.exhausted-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.exhausted-modal {
  background: linear-gradient(135deg, #2c3e50 0%, #1a252f 100%);
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  max-width: 320px;
  width: 90%;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
  color: white;
}

.exhausted-icon {
  font-size: 4em;
  margin-bottom: 15px;
}

.exhausted-modal h3 {
  margin: 0 0 15px 0;
  font-size: 1.5em;
  color: #e74c3c;
}

.message {
  font-size: 1em;
  margin: 0 0 25px 0;
  opacity: 0.8;
  line-height: 1.5;
}

.close-btn {
  padding: 12px 40px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.1em;
  font-weight: bold;
}

.close-btn:hover {
  background: #c0392b;
}
</style>
