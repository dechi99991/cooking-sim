<script setup lang="ts">
import { ref } from 'vue'
import { useGameStore } from '../stores/game'
import { storeToRefs } from 'pinia'
import ShopPanel from './ShopPanel.vue'
import CookingFlow from './CookingFlow.vue'

const emit = defineEmits<{
  done: []
}>()

const store = useGameStore()
const { loading } = storeToRefs(store)

type ActionChoice = 'none' | 'shop' | 'distant' | 'batch' | 'rest' | 'skip'
const currentChoice = ref<ActionChoice>('none')

const actions = [
  { id: 'shop', name: '近所のスーパー', description: '近くのスーパーで買い物', icon: '🛒' },
  { id: 'distant', name: '遠出して買い物', description: '遠くの店で特別な食材を探す', icon: '🚃' },
  { id: 'batch', name: '料理の作り置き', description: '作り置き料理を作る', icon: '🍲' },
  { id: 'rest', name: 'のんびり休養', description: '気力と体力を回復', icon: '😴' },
  { id: 'skip', name: '何もしない', description: 'そのまま次へ進む', icon: '⏭️' },
]

async function selectAction(id: string) {
  if (id === 'rest') {
    await store.doHolidayAction('rest')
    emit('done')
  } else if (id === 'skip') {
    emit('done')
  } else {
    currentChoice.value = id as ActionChoice
  }
}

function backToMenu() {
  currentChoice.value = 'none'
}

async function onShopDone() {
  emit('done')
}

function onBatchCookDone() {
  emit('done')
}
</script>

<template>
  <div class="holiday-panel">
    <!-- 選択画面 -->
    <template v-if="currentChoice === 'none'">
      <h3>休日の行動</h3>
      <p class="description">今日は休日です。何をして過ごしますか？</p>

      <div class="actions">
        <button
          v-for="action in actions"
          :key="action.id"
          class="action-btn"
          :disabled="loading"
          @click="selectAction(action.id)"
        >
          <span class="icon">{{ action.icon }}</span>
          <span class="name">{{ action.name }}</span>
          <span class="desc">{{ action.description }}</span>
        </button>
      </div>
    </template>

    <!-- 近所のスーパー -->
    <template v-else-if="currentChoice === 'shop'">
      <div class="back-link back-link-dark">
        <button class="back-btn" @click="backToMenu">← 戻る</button>
      </div>
      <ShopPanel @done="onShopDone" />
    </template>

    <!-- 遠出して買い物 -->
    <template v-else-if="currentChoice === 'distant'">
      <div class="back-link back-link-dark">
        <button class="back-btn" @click="backToMenu">← 戻る</button>
      </div>
      <ShopPanel :is-distant="true" @done="onShopDone" />
    </template>

    <!-- 作り置き -->
    <template v-else-if="currentChoice === 'batch'">
      <div class="back-link">
        <button class="back-btn" @click="backToMenu">← 戻る</button>
      </div>
      <div class="batch-section">
        <h4>作り置き料理</h4>
        <p>保存用の料理を作ります。作った料理は後日食べることができます。</p>
        <CookingFlow @done="onBatchCookDone" />
      </div>
    </template>
  </div>
</template>

<style scoped>
.holiday-panel {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  padding: 20px;
  color: white;
}

h3 {
  margin: 0 0 10px 0;
  font-size: 1.5em;
  text-align: center;
}

h4 {
  margin: 0 0 10px 0;
  color: white;
}

.description {
  margin: 0 0 20px 0;
  opacity: 0.9;
  text-align: center;
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.action-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.icon {
  font-size: 2em;
}

.name {
  font-weight: bold;
  font-size: 1.1em;
}

.desc {
  margin-left: auto;
  opacity: 0.8;
  font-size: 0.9em;
}

.back-link {
  margin-bottom: 15px;
}

.back-btn {
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  cursor: pointer;
  color: white;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* 買い物フェーズ用（白背景対応） */
.back-link-dark .back-btn {
  background: #f8f9fa;
  border: 1px solid #ddd;
  color: #2c3e50;
}

.back-link-dark .back-btn:hover {
  background: #e9ecef;
}

.batch-section {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 15px;
}

.batch-section p {
  margin: 0 0 15px 0;
  opacity: 0.9;
}
</style>
