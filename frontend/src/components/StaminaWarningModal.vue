<script setup lang="ts">
defineProps<{
  show: boolean
  actionType: 'commute' | 'shopping'
  currentStamina: number
}>()

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()

const actionText = {
  commute: '出勤',
  shopping: '買い出し',
}

const costText = {
  commute: 3,
  shopping: 1,
}
</script>

<template>
  <div v-if="show" class="stamina-warning-overlay" @click="emit('cancel')">
    <div class="stamina-warning-modal" @click.stop>
      <div class="warning-icon">⚠</div>
      <h3>体力警告</h3>
      <p class="message">
        {{ actionText[actionType] }}すると体力が0になり、<br>
        <strong>ゲームオーバー</strong>になります。
      </p>
      <div class="stamina-info">
        <div class="stamina-row">
          <span class="label">現在の体力:</span>
          <span class="value danger">{{ currentStamina }}</span>
        </div>
        <div class="stamina-row">
          <span class="label">消費体力:</span>
          <span class="value">-{{ costText[actionType] }}</span>
        </div>
        <div class="stamina-row result">
          <span class="label">残り体力:</span>
          <span class="value danger">{{ currentStamina - costText[actionType] }}</span>
        </div>
      </div>
      <p class="confirm-text">本当に{{ actionText[actionType] }}しますか？</p>
      <div class="actions">
        <button class="cancel-btn" @click="emit('cancel')">
          キャンセル
        </button>
        <button class="confirm-btn" @click="emit('confirm')">
          {{ actionText[actionType] }}する
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stamina-warning-overlay {
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

.stamina-warning-modal {
  background: white;
  border-radius: 12px;
  padding: 30px;
  text-align: center;
  max-width: 350px;
  width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  border: 2px solid #e74c3c;
}

.warning-icon {
  font-size: 3em;
  color: #e74c3c;
  margin-bottom: 10px;
}

.stamina-warning-modal h3 {
  margin: 0 0 15px 0;
  color: #e74c3c;
}

.message {
  font-size: 1em;
  color: #2c3e50;
  margin: 0 0 20px 0;
  line-height: 1.6;
}

.message strong {
  color: #e74c3c;
}

.stamina-info {
  background: #fef5f5;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
}

.stamina-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 0;
}

.stamina-row.result {
  border-top: 1px solid #eee;
  padding-top: 10px;
  margin-top: 5px;
  font-weight: bold;
}

.stamina-row .label {
  color: #7f8c8d;
}

.stamina-row .value {
  font-size: 1.1em;
  color: #2c3e50;
}

.stamina-row .value.danger {
  color: #e74c3c;
  font-weight: bold;
}

.confirm-text {
  font-size: 1em;
  color: #7f8c8d;
  margin: 0 0 20px 0;
}

.actions {
  display: flex;
  gap: 10px;
}

.cancel-btn {
  flex: 1;
  padding: 12px;
  background: #95a5a6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
}

.cancel-btn:hover {
  background: #7f8c8d;
}

.confirm-btn {
  flex: 1;
  padding: 12px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
}

.confirm-btn:hover {
  background: #c0392b;
}
</style>
