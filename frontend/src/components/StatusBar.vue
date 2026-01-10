<script setup lang="ts">
import { useGameStore } from '../stores/game'
import { storeToRefs } from 'pinia'

const store = useGameStore()
const { state } = storeToRefs(store)

// カテゴリ別アイコン
function getCategoryIcon(category: string): string {
  const icons: Record<string, string> = {
    event: '🎉',
    work: '💼',
    life: '🏠',
    nutrition: '🥗',
  }
  return icons[category] || '❓'
}
</script>

<template>
  <div v-if="state" class="status-bar">
    <div class="date-info">
      <span class="date">{{ state.month }}月{{ state.day }}日({{ state.weekday_name }})</span>
      <span class="weather">{{ state.weather }}</span>
      <span class="phase">{{ state.phase_display }}</span>
      <span v-if="state.is_holiday" class="holiday">休日</span>
      <!-- ボス情報 -->
      <span v-if="state.current_boss" class="boss-indicator" :class="state.current_boss.category">
        <span class="boss-icon">{{ getCategoryIcon(state.current_boss.category) }}</span>
        <span class="boss-name">{{ state.current_boss.name }}</span>
      </span>
    </div>
    <div class="stats">
      <div class="stat">
        <span class="label">所持金</span>
        <span class="value money">¥{{ state.player.money.toLocaleString() }}</span>
        <span v-if="state.player.card_debt > 0" class="debt">(カード: -{{ state.player.card_debt.toLocaleString() }})</span>
      </div>
      <div class="stat">
        <span class="label">気力</span>
        <span class="value" :class="{ low: state.player.energy <= 3 }">{{ state.player.energy }}/{{ state.player.max_energy }}</span>
      </div>
      <div class="stat">
        <span class="label">体力</span>
        <span class="value" :class="{ low: state.player.stamina <= 3 }">{{ state.player.stamina }}/{{ state.player.max_stamina }}</span>
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

.boss-indicator {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 4px 12px;
  border-radius: 4px;
  font-weight: bold;
  animation: pulse 2s infinite;
}

.boss-indicator.event {
  background: #9b59b6;
}

.boss-indicator.work {
  background: #2980b9;
}

.boss-indicator.life {
  background: #27ae60;
}

.boss-indicator.nutrition {
  background: #f39c12;
}

.boss-icon {
  font-size: 1em;
}

.boss-name {
  font-size: 0.9em;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}
</style>
