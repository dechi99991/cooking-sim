<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useGameStore } from '../stores/game'
import { storeToRefs } from 'pinia'

const store = useGameStore()
const { state, loading } = storeToRefs(store)

// 選択状態: { type: 'provision' | 'prepared', value: string | number }
const selected = ref<{ type: 'provision' | 'prepared', value: string | number } | null>(null)

const provisions = computed(() => state.value?.provisions ?? [])
const prepared = computed(() => state.value?.prepared ?? [])

// デバッグ: state変更を監視
watch(() => state.value, (newState) => {
  console.log('[ProvisionPanel] state changed:', {
    provisions: newState?.provisions,
    prepared: newState?.prepared
  })
}, { immediate: true, deep: true })

const hasAnyFood = computed(() => provisions.value.length > 0 || prepared.value.length > 0)

function selectProvision(name: string) {
  if (selected.value?.type === 'provision' && selected.value.value === name) {
    selected.value = null
  } else {
    selected.value = { type: 'provision', value: name }
  }
}

function selectPrepared(index: number) {
  if (selected.value?.type === 'prepared' && selected.value.value === index) {
    selected.value = null
  } else {
    selected.value = { type: 'prepared', value: index }
  }
}

async function consume() {
  if (!selected.value) return

  if (selected.value.type === 'provision') {
    await store.eatProvision([selected.value.value as string])
  } else {
    await store.eatPrepared(selected.value.value as number)
  }
  selected.value = null
}

function getSelectedLabel(): string {
  if (!selected.value) return ''
  if (selected.value.type === 'provision') {
    return selected.value.value as string
  } else {
    const idx = selected.value.value as number
    const dish = prepared.value[idx]
    return dish ? `${dish.dish_type}: ${dish.name}` : ''
  }
}
</script>

<template>
  <div class="provision-panel">
    <h3>食糧・作り置き</h3>

    <div v-if="!hasAnyFood" class="empty">
      食糧がありません
    </div>

    <template v-else>
      <!-- 作り置き料理 -->
      <div v-if="prepared.length > 0" class="section">
        <h4>作り置き料理</h4>
        <div class="items">
          <div
            v-for="(item, index) in prepared"
            :key="`prepared-${index}`"
            class="item prepared"
            :class="{ selected: selected?.type === 'prepared' && selected.value === index }"
            @click="selectPrepared(index)"
          >
            <div class="item-header">
              <span class="dish-type">{{ item.dish_type }}</span>
              <span class="expiry">{{ item.expiry_day }}日まで</span>
            </div>
            <div class="name">{{ item.name }}</div>
            <div class="item-stats">
              <span>満腹: +{{ item.fullness }}</span>
            </div>
            <div class="item-nutrition">
              <span>活{{ item.nutrition.vitality }}</span>
              <span>精{{ item.nutrition.mental }}</span>
              <span>覚{{ item.nutrition.awakening }}</span>
              <span>持{{ item.nutrition.sustain }}</span>
              <span>防{{ item.nutrition.defense }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 通販食糧 -->
      <div v-if="provisions.length > 0" class="section">
        <h4>通販食糧</h4>
        <div class="items">
          <div
            v-for="item in provisions"
            :key="item.name"
            class="item"
            :class="{
              selected: selected?.type === 'provision' && selected.value === item.name,
              caffeine: item.caffeine > 0
            }"
            @click="selectProvision(item.name)"
          >
            <div class="item-header">
              <span class="name">{{ item.name }}</span>
              <span class="qty">x{{ item.quantity }}</span>
            </div>
            <div class="item-stats">
              <span>満腹: +{{ item.fullness }}</span>
              <span v-if="item.caffeine > 0" class="caffeine-value">
                ☕ {{ item.caffeine }}
              </span>
            </div>
            <div class="item-nutrition">
              <span>活{{ item.nutrition.vitality }}</span>
              <span>精{{ item.nutrition.mental }}</span>
              <span>覚{{ item.nutrition.awakening }}</span>
              <span>持{{ item.nutrition.sustain }}</span>
              <span>防{{ item.nutrition.defense }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="selected" class="selection">
        <span>選択中: {{ getSelectedLabel() }}</span>
        <button
          class="consume-btn"
          :disabled="loading"
          @click="consume"
        >
          食べる
        </button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.provision-panel {
  background: #fff;
  border-radius: 8px;
  padding: 15px;
  border: 1px solid #ddd;
}

h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
}

h4 {
  margin: 0 0 10px 0;
  color: #7f8c8d;
  font-size: 0.9em;
}

.section {
  margin-bottom: 20px;
}

.empty {
  color: #95a5a6;
  text-align: center;
  padding: 20px;
}

.items {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 10px;
}

.item {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.item:hover {
  border-color: #3498db;
}

.item.selected {
  border-color: #3498db;
  background: #ebf5fb;
}

.item.caffeine {
  border-color: #9b59b6;
}

.item.prepared {
  border-color: #27ae60;
  background: #f0fff4;
}

.item.prepared.selected {
  background: #d5f5e3;
}

.item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.dish-type {
  font-size: 0.8em;
  color: #27ae60;
  font-weight: bold;
}

.expiry {
  font-size: 0.8em;
  color: #e67e22;
}

.name {
  font-weight: bold;
  margin-bottom: 5px;
}

.qty {
  color: #3498db;
}

.item-stats {
  font-size: 0.85em;
  color: #7f8c8d;
  margin-bottom: 5px;
}

.caffeine-value {
  color: #9b59b6;
  margin-left: 10px;
}

.item-nutrition {
  display: flex;
  gap: 5px;
  font-size: 0.75em;
  color: #95a5a6;
}

.selection {
  margin-top: 15px;
  padding: 15px;
  background: #ebf5fb;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.consume-btn {
  padding: 10px 20px;
  background: #27ae60;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.consume-btn:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}
</style>
