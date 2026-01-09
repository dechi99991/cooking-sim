<script setup lang="ts">
import type { WeeklyEvaluation } from '../types'

defineProps<{
  show: boolean
  evaluation: WeeklyEvaluation | null
}>()

const emit = defineEmits<{
  close: []
}>()

// ランクに応じた色
function getRankColor(rank: string): string {
  switch (rank) {
    case 'SS': return '#f1c40f'  // ゴールド
    case 'S': return '#9b59b6'   // パープル
    case 'A': return '#3498db'   // ブルー
    case 'B': return '#27ae60'   // グリーン
    case 'C': return '#95a5a6'   // グレー
    case 'F': return '#e74c3c'   // レッド
    default: return '#7f8c8d'
  }
}

// ランクに応じたアイコン
function getRankIcon(rank: string): string {
  switch (rank) {
    case 'SS': return '👑'
    case 'S': return '🌟'
    case 'A': return '⭐'
    case 'B': return '✨'
    case 'C': return '💫'
    case 'F': return '💀'
    default: return '❓'
  }
}
</script>

<template>
  <div v-if="show && evaluation" class="modal-overlay" @click.self="emit('close')">
    <div class="modal">
      <h3>週の総決算</h3>

      <!-- ランク表示 -->
      <div class="rank-display" :style="{ borderColor: getRankColor(evaluation.rank) }">
        <div class="rank-icon">{{ getRankIcon(evaluation.rank) }}</div>
        <div class="rank-label">総合評価</div>
        <div class="rank-value" :style="{ color: getRankColor(evaluation.rank) }">
          {{ evaluation.rank }}
        </div>
      </div>

      <!-- 評価詳細 -->
      <div class="evaluation-details">
        <!-- 栄養評価 -->
        <div class="detail-section">
          <h4>栄養バランス</h4>
          <div class="detail-row">
            <span class="label">栄養グレード</span>
            <span class="value grade" :class="'grade-' + evaluation.nutrition_grade.toLowerCase()">
              {{ evaluation.nutrition_grade }}
            </span>
          </div>
          <div class="detail-row">
            <span class="label">閾値達成</span>
            <span class="value">{{ evaluation.nutrients_ok }}/5 栄養素</span>
          </div>
        </div>

        <!-- 食費評価 -->
        <div class="detail-section">
          <h4>食費管理</h4>
          <div class="detail-row">
            <span class="label">今週の食費</span>
            <span class="value">¥{{ evaluation.food_spending.toLocaleString() }}</span>
          </div>
          <div class="detail-row">
            <span class="label">自炊回数</span>
            <span class="value">{{ evaluation.meals_cooked }}回</span>
          </div>
          <div class="detail-row">
            <span class="label">節約</span>
            <span class="value" :class="{ success: evaluation.saving_success, fail: !evaluation.saving_success }">
              {{ evaluation.saving_success ? '達成!' : '未達成' }}
            </span>
          </div>
          <div v-if="evaluation.overspending" class="warning-badge">
            使いすぎ警告!
          </div>
        </div>
      </div>

      <!-- 効果 -->
      <div class="effects">
        <h4>結果</h4>
        <div class="effect-grid">
          <div v-if="evaluation.energy_change !== 0" class="effect-item" :class="{ positive: evaluation.energy_change > 0, negative: evaluation.energy_change < 0 }">
            <span class="effect-label">気力</span>
            <span class="effect-value">{{ evaluation.energy_change > 0 ? '+' : '' }}{{ evaluation.energy_change }}</span>
          </div>
          <div v-if="evaluation.stamina_change !== 0" class="effect-item" :class="{ positive: evaluation.stamina_change > 0, negative: evaluation.stamina_change < 0 }">
            <span class="effect-label">体力</span>
            <span class="effect-value">{{ evaluation.stamina_change > 0 ? '+' : '' }}{{ evaluation.stamina_change }}</span>
          </div>
          <div v-if="evaluation.money_change !== 0" class="effect-item" :class="{ positive: evaluation.money_change > 0, negative: evaluation.money_change < 0 }">
            <span class="effect-label">お金</span>
            <span class="effect-value">{{ evaluation.money_change > 0 ? '+¥' : '-¥' }}{{ Math.abs(evaluation.money_change).toLocaleString() }}</span>
          </div>
        </div>
        <p v-if="evaluation.energy_change === 0 && evaluation.stamina_change === 0 && evaluation.money_change === 0" class="no-effect">
          特に変化なし
        </p>
      </div>

      <!-- メッセージ -->
      <div class="message-box">
        <p>{{ evaluation.message }}</p>
      </div>

      <button class="close-btn" @click="emit('close')">
        閉じる
      </button>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
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

.modal {
  background: white;
  border-radius: 12px;
  padding: 24px;
  max-width: 420px;
  width: 90%;
  max-height: 85vh;
  overflow-y: auto;
}

h3 {
  margin: 0 0 20px 0;
  text-align: center;
  color: #2c3e50;
  font-size: 1.4em;
}

h4 {
  margin: 0 0 10px 0;
  color: #7f8c8d;
  font-size: 0.9em;
}

/* ランク表示 */
.rank-display {
  text-align: center;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  border: 3px solid;
  margin-bottom: 20px;
}

.rank-icon {
  font-size: 2.5em;
  margin-bottom: 5px;
}

.rank-label {
  font-size: 0.85em;
  color: #7f8c8d;
  margin-bottom: 5px;
}

.rank-value {
  font-size: 3em;
  font-weight: bold;
}

/* 評価詳細 */
.evaluation-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 20px;
}

.detail-section {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.detail-row:last-child {
  margin-bottom: 0;
}

.detail-row .label {
  font-size: 0.85em;
  color: #7f8c8d;
}

.detail-row .value {
  font-weight: bold;
  color: #2c3e50;
}

.detail-row .value.success {
  color: #27ae60;
}

.detail-row .value.fail {
  color: #e74c3c;
}

/* グレード色 */
.grade {
  padding: 2px 8px;
  border-radius: 4px;
  color: white;
}

.grade-s { background: #9b59b6; }
.grade-a { background: #3498db; }
.grade-b { background: #27ae60; }
.grade-c { background: #f39c12; }
.grade-d { background: #e67e22; }
.grade-e { background: #e74c3c; }

.warning-badge {
  margin-top: 8px;
  padding: 4px 8px;
  background: #e74c3c;
  color: white;
  border-radius: 4px;
  font-size: 0.8em;
  text-align: center;
}

/* 効果 */
.effects {
  background: #ebf5fb;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.effect-grid {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

.effect-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 20px;
  background: white;
  border-radius: 8px;
  min-width: 80px;
}

.effect-item.positive {
  border: 2px solid #27ae60;
}

.effect-item.negative {
  border: 2px solid #e74c3c;
}

.effect-label {
  font-size: 0.8em;
  color: #7f8c8d;
}

.effect-value {
  font-size: 1.3em;
  font-weight: bold;
}

.effect-item.positive .effect-value {
  color: #27ae60;
}

.effect-item.negative .effect-value {
  color: #e74c3c;
}

.no-effect {
  text-align: center;
  color: #95a5a6;
  margin: 0;
  font-style: italic;
}

/* メッセージ */
.message-box {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.message-box p {
  margin: 0;
  line-height: 1.5;
  text-align: center;
}

/* ボタン */
.close-btn {
  width: 100%;
  padding: 12px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1em;
  transition: background 0.2s;
}

.close-btn:hover {
  background: #2980b9;
}
</style>
