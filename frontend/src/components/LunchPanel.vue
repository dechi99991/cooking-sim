<script setup lang="ts">
import { ref, computed } from 'vue'
import { useGameStore } from '../stores/game'
import { storeToRefs } from 'pinia'
import CookingFlow from './CookingFlow.vue'
import ProvisionPanel from './ProvisionPanel.vue'

const props = defineProps<{
  isHoliday: boolean
}>()

const emit = defineEmits<{
  done: []
}>()

const store = useGameStore()
const { state, loading } = storeToRefs(store)

type MenuChoice = 'none' | 'cafeteria' | 'cook' | 'provision' | 'skip'
const currentChoice = ref<MenuChoice>('none')

// 平日メニュー（社食あり）
const weekdayMenu = [
  { id: 'cafeteria', label: '社食（500円）', icon: '🍽️', description: '社員食堂で食べる' },
  { id: 'provision', label: '食糧を食べる', icon: '🥫', description: 'ストックの食糧を消費' },
  { id: 'skip', label: '食べない', icon: '❌', description: '何も食べずに次へ' },
]

// 休日メニュー（自炊可能）
const holidayMenu = [
  { id: 'cook', label: '自炊する', icon: '🍳', description: '食材を使って料理を作る' },
  { id: 'provision', label: '食糧を食べる', icon: '🥫', description: 'ストックの食糧を消費' },
  { id: 'skip', label: '食べない', icon: '❌', description: '何も食べずに次へ' },
]

const menu = computed(() => props.isHoliday ? holidayMenu : weekdayMenu)

const canAffordCafeteria = computed(() => {
  return (state.value?.player.money ?? 0) >= 500
})

async function selectChoice(id: string) {
  if (id === 'cafeteria') {
    if (!canAffordCafeteria.value) return
    await store.eatCafeteria()
    emit('done')
  } else if (id === 'skip') {
    emit('done')
  } else {
    currentChoice.value = id as MenuChoice
  }
}

function onCookingDone() {
  emit('done')
}

function backToMenu() {
  currentChoice.value = 'none'
}
</script>

<template>
  <div class="lunch-panel">
    <!-- メニュー選択 -->
    <template v-if="currentChoice === 'none'">
      <div class="menu-header">
        <h3>{{ isHoliday ? '休日の昼食' : '昼食' }}</h3>
        <p>何をしますか？</p>
      </div>

      <div class="menu-options">
        <button
          v-for="item in menu"
          :key="item.id"
          class="menu-btn"
          :disabled="loading || (item.id === 'cafeteria' && !canAffordCafeteria)"
          :class="{ disabled: item.id === 'cafeteria' && !canAffordCafeteria }"
          @click="selectChoice(item.id)"
        >
          <span class="icon">{{ item.icon }}</span>
          <span class="label">{{ item.label }}</span>
          <span class="desc">
            {{ item.description }}
            <template v-if="item.id === 'cafeteria' && !canAffordCafeteria">
              （お金が足りません）
            </template>
          </span>
        </button>
      </div>

      <div v-if="!isHoliday && state" class="money-info">
        所持金: {{ state.player.money.toLocaleString() }}円
      </div>
    </template>

    <!-- 自炊（休日のみ） -->
    <template v-else-if="currentChoice === 'cook'">
      <div class="back-link">
        <button class="back-btn" @click="backToMenu">← メニューに戻る</button>
      </div>
      <CookingFlow @done="onCookingDone" />
    </template>

    <!-- 食糧消費 -->
    <template v-else-if="currentChoice === 'provision'">
      <div class="back-link">
        <button class="back-btn" @click="backToMenu">← メニューに戻る</button>
      </div>
      <ProvisionPanel />
      <button class="done-btn" @click="emit('done')">完了</button>
    </template>
  </div>
</template>

<style scoped>
.lunch-panel {
  padding: 10px;
}

.menu-header {
  text-align: center;
  margin-bottom: 20px;
}

.menu-header h3 {
  margin: 0 0 5px 0;
  color: #2c3e50;
}

.menu-header p {
  margin: 0;
  color: #7f8c8d;
}

.menu-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.menu-btn {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px 20px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.menu-btn:hover:not(:disabled) {
  border-color: #3498db;
  background: #ebf5fb;
}

.menu-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.menu-btn.disabled {
  background: #f8f9fa;
}

.menu-btn .icon {
  font-size: 2em;
}

.menu-btn .label {
  font-weight: bold;
  font-size: 1.1em;
  color: #2c3e50;
}

.menu-btn .desc {
  margin-left: auto;
  color: #7f8c8d;
  font-size: 0.9em;
}

.money-info {
  margin-top: 15px;
  text-align: center;
  color: #7f8c8d;
  font-size: 0.9em;
}

.back-link {
  margin-bottom: 15px;
}

.back-btn {
  padding: 8px 12px;
  background: transparent;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  color: #7f8c8d;
}

.back-btn:hover {
  background: #f8f9fa;
}

.done-btn {
  display: block;
  width: 100%;
  margin-top: 20px;
  padding: 12px;
  background: #27ae60;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
}

.done-btn:hover {
  background: #219a52;
}
</style>
