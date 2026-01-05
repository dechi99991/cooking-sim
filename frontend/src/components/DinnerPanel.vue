<script setup lang="ts">
import { ref } from 'vue'
import { useGameStore } from '../stores/game'
import { storeToRefs } from 'pinia'
import CookingFlow from './CookingFlow.vue'
import ProvisionPanel from './ProvisionPanel.vue'

const emit = defineEmits<{
  done: []
}>()

const store = useGameStore()
const { loading } = storeToRefs(store)

type MenuChoice = 'none' | 'cook' | 'provision' | 'skip'
const currentChoice = ref<MenuChoice>('none')

const menu = [
  { id: 'cook', label: '自炊する', icon: '🍳', description: '食材を使って料理を作る' },
  { id: 'provision', label: '食糧を食べる', icon: '🥫', description: 'ストックの食糧を消費' },
  { id: 'skip', label: '食べない', icon: '❌', description: '何も食べずに次へ' },
]

function selectChoice(id: string) {
  if (id === 'skip') {
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
  <div class="dinner-panel">
    <!-- メニュー選択 -->
    <template v-if="currentChoice === 'none'">
      <div class="menu-header">
        <h3>夕食</h3>
        <p>何をしますか？</p>
      </div>

      <div class="menu-options">
        <button
          v-for="item in menu"
          :key="item.id"
          class="menu-btn"
          :disabled="loading"
          @click="selectChoice(item.id)"
        >
          <span class="icon">{{ item.icon }}</span>
          <span class="label">{{ item.label }}</span>
          <span class="desc">{{ item.description }}</span>
        </button>
      </div>
    </template>

    <!-- 自炊 -->
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
.dinner-panel {
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
