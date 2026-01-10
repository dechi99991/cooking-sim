<script setup lang="ts">
import type { WeeklyBossInfo } from '../types'

defineProps<{
  show: boolean
  boss: WeeklyBossInfo | null
}>()

const emit = defineEmits<{
  close: []
}>()

// カテゴリ別の表示情報
const categoryInfo: Record<string, { icon: string; name: string; color: string }> = {
  event: { icon: '🎉', name: 'イベント', color: '#9b59b6' },
  work: { icon: '💼', name: '仕事', color: '#3498db' },
  life: { icon: '🏠', name: '生活', color: '#2ecc71' },
  nutrition: { icon: '🥗', name: '栄養', color: '#f39c12' },
}

function getCategoryInfo(category: string) {
  return categoryInfo[category] || { icon: '❓', name: '不明', color: '#95a5a6' }
}
</script>

<template>
  <Teleport to="body">
    <div v-if="show && boss" class="modal-overlay" @click.self="emit('close')">
      <div class="modal-content">
        <div class="modal-header" :style="{ backgroundColor: getCategoryInfo(boss.category).color }">
          <span class="category-icon">{{ getCategoryInfo(boss.category).icon }}</span>
          <h2>今週のボス</h2>
        </div>

        <div class="modal-body">
          <div class="boss-name">{{ boss.name }}</div>

          <p class="boss-description">{{ boss.description }}</p>

          <div class="requirements-section">
            <h3>生存条件</h3>
            <div class="requirements-text">{{ boss.requirements_text }}</div>

            <div class="requirements-detail">
              <div v-if="boss.required_money > 0" class="requirement-item">
                <span class="req-icon">💰</span>
                <span class="req-label">必要資金:</span>
                <span class="req-value">¥{{ boss.required_money.toLocaleString() }}</span>
              </div>
              <div v-if="boss.required_energy > 0" class="requirement-item">
                <span class="req-icon">⚡</span>
                <span class="req-label">必要気力:</span>
                <span class="req-value">{{ boss.required_energy }}</span>
              </div>
              <div v-if="boss.required_stamina > 0" class="requirement-item">
                <span class="req-icon">💪</span>
                <span class="req-label">必要体力:</span>
                <span class="req-value">{{ boss.required_stamina }}</span>
              </div>
              <div v-if="Object.keys(boss.required_nutrition).length > 0" class="requirement-item nutrition-req">
                <span class="req-icon">🥗</span>
                <span class="req-label">栄養条件:</span>
                <span v-for="(value, key) in boss.required_nutrition" :key="key" class="req-value nutrition-value">
                  {{ key === 'vitality' ? '活力' : key === 'mental' ? '精神' : key === 'awakening' ? '覚醒' : key === 'sustain' ? '持続' : key === 'defense' ? '防衛' : key }}
                  {{ value }}+
                </span>
              </div>
              <div v-if="boss.required_all_nutrients > 0" class="requirement-item">
                <span class="req-icon">⭐</span>
                <span class="req-label">全栄養素:</span>
                <span class="req-value">{{ boss.required_all_nutrients }}以上</span>
              </div>
            </div>
          </div>

          <div class="warning-text">
            金曜日までに条件を満たさないとペナルティが発生します！
          </div>
        </div>

        <div class="modal-footer">
          <button class="confirm-btn" @click="emit('close')">
            了解！
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

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  padding: 20px;
  text-align: center;
  color: white;
}

.category-icon {
  font-size: 3em;
  display: block;
  margin-bottom: 10px;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5em;
}

.modal-body {
  padding: 20px;
}

.boss-name {
  font-size: 2em;
  font-weight: bold;
  text-align: center;
  color: #2c3e50;
  margin-bottom: 15px;
}

.boss-description {
  font-size: 1.1em;
  color: #555;
  text-align: center;
  margin-bottom: 20px;
  line-height: 1.6;
}

.requirements-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
}

.requirements-section h3 {
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 1em;
}

.requirements-text {
  font-weight: bold;
  color: #e74c3c;
  margin-bottom: 10px;
  padding: 10px;
  background: #fef5f5;
  border-radius: 4px;
}

.requirements-detail {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.requirement-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.req-icon {
  font-size: 1.2em;
}

.req-label {
  color: #666;
}

.req-value {
  font-weight: bold;
  color: #2c3e50;
}

.nutrition-req {
  flex-wrap: wrap;
}

.nutrition-value {
  background: #eef7ff;
  padding: 2px 8px;
  border-radius: 4px;
  margin-right: 5px;
}

.warning-text {
  text-align: center;
  color: #e74c3c;
  font-weight: bold;
  padding: 10px;
  background: #fef5f5;
  border-radius: 4px;
}

.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: center;
}

.confirm-btn {
  padding: 12px 40px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1em;
  cursor: pointer;
  transition: background 0.2s;
}

.confirm-btn:hover {
  background: #2980b9;
}
</style>
