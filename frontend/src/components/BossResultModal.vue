<script setup lang="ts">
import type { BossResult } from '../types'

defineProps<{
  show: boolean
  result: BossResult | null
}>()

const emit = defineEmits<{
  close: []
}>()

// カテゴリ別の表示情報
const categoryInfo: Record<string, { icon: string; name: string }> = {
  event: { icon: '🎉', name: 'イベント' },
  work: { icon: '💼', name: '仕事' },
  life: { icon: '🏠', name: '生活' },
  nutrition: { icon: '🥗', name: '栄養' },
}

function getCategoryInfo(category: string) {
  return categoryInfo[category] || { icon: '❓', name: '不明' }
}

function formatChange(value: number, suffix: string = ''): string {
  if (value > 0) return `+${value}${suffix}`
  if (value < 0) return `${value}${suffix}`
  return ''
}
</script>

<template>
  <Teleport to="body">
    <div v-if="show && result" class="modal-overlay" @click.self="emit('close')">
      <div class="modal-content" :class="{ success: result.success, failure: !result.success }">
        <div class="modal-header">
          <div class="result-icon">{{ result.success ? '🎊' : '😢' }}</div>
          <h2>{{ result.success ? '生存成功！' : '生存失敗...' }}</h2>
        </div>

        <div class="modal-body">
          <div class="boss-info">
            <span class="category-icon">{{ getCategoryInfo(result.category).icon }}</span>
            <span class="boss-name">{{ result.boss_name }}</span>
          </div>

          <div class="result-message" :class="{ success: result.success, failure: !result.success }">
            {{ result.message }}
          </div>

          <div class="changes-section">
            <h3>結果</h3>
            <div class="changes">
              <div v-if="result.energy_change !== 0" class="change-item" :class="{ positive: result.energy_change > 0, negative: result.energy_change < 0 }">
                <span class="change-icon">⚡</span>
                <span class="change-label">気力</span>
                <span class="change-value">{{ formatChange(result.energy_change) }}</span>
              </div>
              <div v-if="result.stamina_change !== 0" class="change-item" :class="{ positive: result.stamina_change > 0, negative: result.stamina_change < 0 }">
                <span class="change-icon">💪</span>
                <span class="change-label">体力</span>
                <span class="change-value">{{ formatChange(result.stamina_change) }}</span>
              </div>
              <div v-if="result.money_change !== 0" class="change-item" :class="{ positive: result.money_change > 0, negative: result.money_change < 0 }">
                <span class="change-icon">💰</span>
                <span class="change-label">資金</span>
                <span class="change-value">{{ formatChange(result.money_change, '円') }}</span>
              </div>
            </div>
          </div>

          <div class="nutrition-section">
            <h3>今週の栄養（累計）</h3>
            <div class="nutrition-grid">
              <div class="nutrition-item">
                <span class="nutr-label">活力</span>
                <span class="nutr-value">{{ result.weekly_nutrition.vitality }}</span>
              </div>
              <div class="nutrition-item">
                <span class="nutr-label">精神</span>
                <span class="nutr-value">{{ result.weekly_nutrition.mental }}</span>
              </div>
              <div class="nutrition-item">
                <span class="nutr-label">覚醒</span>
                <span class="nutr-value">{{ result.weekly_nutrition.awakening }}</span>
              </div>
              <div class="nutrition-item">
                <span class="nutr-label">持続</span>
                <span class="nutr-value">{{ result.weekly_nutrition.sustain }}</span>
              </div>
              <div class="nutrition-item">
                <span class="nutr-label">防衛</span>
                <span class="nutr-value">{{ result.weekly_nutrition.defense }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="confirm-btn" :class="{ success: result.success }" @click="emit('close')">
            {{ result.success ? '次へ' : '来週こそ...' }}
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
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: #fff;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  animation: slideIn 0.3s ease;
}

.modal-content.success {
  border: 3px solid #27ae60;
}

.modal-content.failure {
  border: 3px solid #e74c3c;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.modal-header {
  padding: 20px;
  text-align: center;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
}

.result-icon {
  font-size: 4em;
  margin-bottom: 10px;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.8em;
  color: #2c3e50;
}

.modal-body {
  padding: 20px;
}

.boss-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 15px;
}

.category-icon {
  font-size: 1.5em;
}

.boss-name {
  font-size: 1.5em;
  font-weight: bold;
  color: #2c3e50;
}

.result-message {
  text-align: center;
  font-size: 1.1em;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  line-height: 1.6;
}

.result-message.success {
  background: #e8f8f0;
  color: #27ae60;
}

.result-message.failure {
  background: #fef5f5;
  color: #e74c3c;
}

.changes-section, .nutrition-section {
  margin-bottom: 15px;
}

.changes-section h3, .nutrition-section h3 {
  margin: 0 0 10px 0;
  font-size: 0.9em;
  color: #7f8c8d;
}

.changes {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.change-item {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 8px 12px;
  border-radius: 8px;
  background: #f8f9fa;
}

.change-item.positive {
  background: #e8f8f0;
  color: #27ae60;
}

.change-item.negative {
  background: #fef5f5;
  color: #e74c3c;
}

.change-icon {
  font-size: 1.2em;
}

.change-label {
  color: #666;
}

.change-value {
  font-weight: bold;
}

.nutrition-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
}

.nutrition-item {
  text-align: center;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
}

.nutr-label {
  display: block;
  font-size: 0.8em;
  color: #666;
  margin-bottom: 4px;
}

.nutr-value {
  display: block;
  font-weight: bold;
  color: #2c3e50;
}

.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: center;
}

.confirm-btn {
  padding: 12px 40px;
  background: #95a5a6;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1em;
  cursor: pointer;
  transition: background 0.2s;
}

.confirm-btn.success {
  background: #27ae60;
}

.confirm-btn:hover {
  filter: brightness(0.9);
}
</style>
