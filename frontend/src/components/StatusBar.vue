<script setup lang="ts">
import { useGameStore } from '../stores/game'
import { storeToRefs } from 'pinia'

const store = useGameStore()
const { state } = storeToRefs(store)
</script>

<template>
  <div v-if="state" class="status-bar">
    <div class="date-info">
      <span class="date">{{ state.month }}月{{ state.day }}日({{ state.weekday_name }})</span>
      <span class="weather">{{ state.weather }}</span>
      <span class="phase">{{ state.phase_display }}</span>
      <span v-if="state.is_holiday" class="holiday">休日</span>
    </div>
    <div class="stats">
      <div class="stat">
        <span class="label">所持金</span>
        <span class="value money">¥{{ state.player.money.toLocaleString() }}</span>
        <span v-if="state.player.card_debt > 0" class="debt">(カード: -{{ state.player.card_debt.toLocaleString() }})</span>
      </div>
      <div class="stat">
        <span class="label">気力</span>
        <span class="value" :class="{ low: state.player.energy <= 3 }">{{ state.player.energy }}/10</span>
      </div>
      <div class="stat">
        <span class="label">体力</span>
        <span class="value" :class="{ low: state.player.stamina <= 3 }">{{ state.player.stamina }}/10</span>
      </div>
      <div class="stat">
        <span class="label">満腹</span>
        <span class="value">{{ state.player.fullness }}/10</span>
      </div>
      <div v-if="state.caffeine > 0" class="stat">
        <span class="label">カフェイン</span>
        <span class="value" :class="{ warning: state.caffeine >= 3 }">{{ state.caffeine }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.status-bar {
  background: #2c3e50;
  color: white;
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.date-info {
  display: flex;
  gap: 15px;
  align-items: center;
}

.date {
  font-size: 1.2em;
  font-weight: bold;
}

.weather {
  font-size: 1.1em;
}

.phase {
  background: #3498db;
  padding: 4px 12px;
  border-radius: 4px;
}

.holiday {
  background: #e74c3c;
  padding: 4px 12px;
  border-radius: 4px;
}

.stats {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.stat {
  display: flex;
  gap: 5px;
  align-items: center;
}

.label {
  color: #bdc3c7;
  font-size: 0.9em;
}

.value {
  font-weight: bold;
}

.value.low {
  color: #e74c3c;
}

.value.warning {
  color: #f39c12;
}

.money {
  color: #2ecc71;
}

.debt {
  color: #e74c3c;
  font-size: 0.9em;
}
</style>
