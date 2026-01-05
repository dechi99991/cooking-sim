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
const { loading } = storeToRefs(store)

type MenuChoice = 'none' | 'cook' | 'cook-bento' | 'provision' | 'skip'
const currentChoice = ref<MenuChoice>('none')
const cookingDone = ref(false)
const bentoDone = ref(false)

// 平日メニュー
const weekdayMenu = [
  { id: 'cook', label: '自炊する', icon: '🍳', description: '食材を使って料理を作る' },
  { id: 'cook-bento', label: '自炊して弁当も作る', icon: '🍱', description: '料理を作り、さらに弁当も用意' },
  { id: 'provision', label: '食糧を食べる', icon: '🥫', description: 'ストックの食糧を消費' },
  { id: 'skip', label: '食べない', icon: '❌', description: '何も食べずに次へ' },
]

// 休日メニュー（弁当オプションなし）
const holidayMenu = [
  { id: 'cook', label: '自炊する', icon: '🍳', description: '食材を使って料理を作る' },
  { id: 'provision', label: '食糧を食べる', icon: '🥫', description: 'ストックの食糧を消費' },
  { id: 'skip', label: '食べない', icon: '❌', description: '何も食べずに次へ' },
]

const menu = computed(() => props.isHoliday ? holidayMenu : weekdayMenu)

function selectChoice(id: string) {
  currentChoice.value = id as MenuChoice
  if (id === 'skip') {
    emit('done')
  }
}

function onCookingDone() {
  if (currentChoice.value === 'cook-bento') {
    // 弁当作成フェーズへ
    cookingDone.value = true
  } else {
    emit('done')
  }
}

function onBentoDone() {
  bentoDone.value = true
  emit('done')
}

function backToMenu() {
  currentChoice.value = 'none'
  cookingDone.value = false
  bentoDone.value = false
}
</script>

<template>
  <div class="breakfast-panel">
    <!-- メニュー選択 -->
    <template v-if="currentChoice === 'none'">
      <div class="menu-header">
        <h3>{{ isHoliday ? '休日の朝食' : '朝食' }}</h3>
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
    <template v-else-if="currentChoice === 'cook' || (currentChoice === 'cook-bento' && !cookingDone)">
      <div class="back-link">
        <button class="back-btn" @click="backToMenu">← メニューに戻る</button>
      </div>
      <CookingFlow @done="onCookingDone" />
    </template>

    <!-- 弁当作成（自炊+弁当の場合） -->
    <template v-else-if="currentChoice === 'cook-bento' && cookingDone && !bentoDone">
      <div class="bento-section">
        <h3>弁当を作る</h3>
        <p>お昼用の弁当を作りましょう。</p>
        <CookingFlow :is-bento="true" @done="onBentoDone" />
      </div>
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
.breakfast-panel {
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

.bento-section h3 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.bento-section p {
  margin: 0 0 20px 0;
  color: #7f8c8d;
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
