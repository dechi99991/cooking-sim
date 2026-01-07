<script setup lang="ts">
interface TemperamentInfo {
  id: string
  name: string
  description: string
  icon: string
}

defineProps<{
  show: boolean
  temperament: TemperamentInfo | null
}>()

const emit = defineEmits<{
  close: []
}>()
</script>

<template>
  <Teleport to="body">
    <div v-if="show && temperament" class="modal-overlay" @click.self="emit('close')">
      <div class="modal-content">
        <div class="modal-header">
          <h2>気質が判明しました！</h2>
        </div>

        <div class="modal-body">
          <div class="temperament-icon">{{ temperament.icon }}</div>
          <h3 class="temperament-name">{{ temperament.name }}</h3>
          <p class="temperament-description">{{ temperament.description }}</p>

          <div class="explanation">
            <p>あなたの3日間の行動傾向から、この気質が判定されました。</p>
            <p>この気質は今後のゲームプレイに影響します。</p>
          </div>
        </div>

        <div class="modal-footer">
          <button class="confirm-btn" @click="emit('close')">
            OK
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 30px;
  max-width: 400px;
  width: 90%;
  color: white;
  text-align: center;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header h2 {
  margin: 0 0 20px 0;
  font-size: 1.3em;
}

.modal-body {
  margin-bottom: 20px;
}

.temperament-icon {
  font-size: 4em;
  margin-bottom: 15px;
}

.temperament-name {
  margin: 0 0 10px 0;
  font-size: 1.8em;
}

.temperament-description {
  margin: 0 0 20px 0;
  font-size: 1.2em;
  background: rgba(255, 255, 255, 0.2);
  padding: 10px 15px;
  border-radius: 8px;
}

.explanation {
  font-size: 0.9em;
  opacity: 0.9;
  line-height: 1.6;
}

.explanation p {
  margin: 5px 0;
}

.modal-footer {
  margin-top: 20px;
}

.confirm-btn {
  padding: 12px 40px;
  background: white;
  color: #667eea;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.1em;
  font-weight: bold;
  transition: all 0.2s;
}

.confirm-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}
</style>
