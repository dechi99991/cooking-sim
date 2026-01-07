<script setup lang="ts">
import type { CookPreviewResponse } from '../types'

const props = defineProps<{
  preview: CookPreviewResponse
  ingredients: string[]
  loading?: boolean
}>()

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()
</script>

<template>
  <div class="cooking-preview">
    <h4>調理確認</h4>

    <!-- 何品目かの表示 -->
    <div v-if="preview.dish_number > 1" class="dish-number">
      【{{ preview.dish_number }}品目】
    </div>

    <div class="dish-preview">
      <div class="dish-name">
        <span v-if="preview.is_named" class="star">★</span>
        {{ preview.dish_name }}
        <span v-if="preview.named_recipe_name" class="recipe-name">
          ({{ preview.named_recipe_name }})
        </span>
      </div>

      <div class="ingredients-used">
        使用食材: {{ ingredients.join(' + ') }}
      </div>

      <!-- この料理の情報 -->
      <div class="section-label" v-if="preview.dish_number > 1">この料理:</div>

      <div class="stats">
        <div class="stat">
          <span class="label">満腹度</span>
          <span class="value">+{{ preview.fullness }}</span>
        </div>
      </div>

      <div class="nutrition">
        <div class="nutrition-item">
          <span class="label">活力</span>
          <span class="value">{{ preview.nutrition.vitality }}</span>
        </div>
        <div class="nutrition-item">
          <span class="label">精神</span>
          <span class="value">{{ preview.nutrition.mental }}</span>
        </div>
        <div class="nutrition-item">
          <span class="label">覚醒</span>
          <span class="value">{{ preview.nutrition.awakening }}</span>
        </div>
        <div class="nutrition-item">
          <span class="label">持続</span>
          <span class="value">{{ preview.nutrition.sustain }}</span>
        </div>
        <div class="nutrition-item">
          <span class="label">防御</span>
          <span class="value">{{ preview.nutrition.defense }}</span>
        </div>
      </div>

      <!-- 食事トータル（2品目以降） -->
      <div v-if="preview.dish_number > 1" class="meal-total">
        <div class="section-label">食事計:</div>
        <div class="stats">
          <div class="stat">
            <span class="label">満腹度</span>
            <span class="value total-value">={{ preview.meal_fullness }}</span>
          </div>
        </div>
        <div class="nutrition total-nutrition">
          <div class="nutrition-item">
            <span class="label">活力</span>
            <span class="value">{{ preview.meal_nutrition.vitality }}</span>
          </div>
          <div class="nutrition-item">
            <span class="label">精神</span>
            <span class="value">{{ preview.meal_nutrition.mental }}</span>
          </div>
          <div class="nutrition-item">
            <span class="label">覚醒</span>
            <span class="value">{{ preview.meal_nutrition.awakening }}</span>
          </div>
          <div class="nutrition-item">
            <span class="label">持続</span>
            <span class="value">{{ preview.meal_nutrition.sustain }}</span>
          </div>
          <div class="nutrition-item">
            <span class="label">防御</span>
            <span class="value">{{ preview.meal_nutrition.defense }}</span>
          </div>
        </div>
      </div>

      <div v-if="preview.evaluation_comment" class="comment">
        「{{ preview.evaluation_comment }}」
      </div>
    </div>

    <div v-if="!preview.can_make" class="warning">
      気力が足りないため調理できません
    </div>

    <div class="actions">
      <button
        class="confirm-btn"
        :disabled="!preview.can_make || loading"
        @click="emit('confirm')"
      >
        作る
      </button>
      <button
        class="cancel-btn"
        :disabled="loading"
        @click="emit('cancel')"
      >
        やり直す
      </button>
    </div>
  </div>
</template>

<style scoped>
.cooking-preview {
  background: #fef9e7;
  border-radius: 8px;
  padding: 20px;
  border: 2px solid #f39c12;
}

h4 {
  margin: 0 0 15px 0;
  color: #d68910;
}

.dish-preview {
  margin-bottom: 20px;
}

.dish-name {
  font-size: 1.3em;
  font-weight: bold;
  margin-bottom: 10px;
  color: #2c3e50;
}

.star {
  color: #f39c12;
}

.recipe-name {
  font-size: 0.8em;
  color: #8e44ad;
  margin-left: 5px;
}

.ingredients-used {
  color: #7f8c8d;
  font-size: 0.9em;
  margin-bottom: 15px;
}

.stats {
  margin-bottom: 15px;
}

.stat {
  display: flex;
  gap: 10px;
}

.stat .label {
  color: #7f8c8d;
}

.stat .value {
  color: #27ae60;
  font-weight: bold;
}

.nutrition {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 15px;
}

.nutrition-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 12px;
  background: white;
  border-radius: 4px;
}

.nutrition-item .label {
  font-size: 0.8em;
  color: #7f8c8d;
}

.nutrition-item .value {
  font-size: 1.2em;
  font-weight: bold;
  color: #2c3e50;
}

.dish-number {
  font-size: 1.1em;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 2px dashed #f39c12;
}

.section-label {
  font-size: 0.9em;
  font-weight: bold;
  color: #7f8c8d;
  margin-bottom: 8px;
  margin-top: 10px;
}

.meal-total {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #f39c12;
  background: rgba(255, 255, 255, 0.5);
  padding: 15px;
  border-radius: 4px;
}

.total-nutrition {
  background: #eafaf1;
}

.total-nutrition .nutrition-item {
  background: #d5f5e3;
}

.total-value {
  color: #2980b9 !important;
}

.comment {
  font-style: italic;
  color: #8e44ad;
  padding: 10px;
  background: rgba(142, 68, 173, 0.1);
  border-radius: 4px;
  margin-top: 15px;
}

.warning {
  background: #e74c3c;
  color: white;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  text-align: center;
}

.actions {
  display: flex;
  gap: 10px;
}

.confirm-btn {
  flex: 1;
  padding: 12px;
  background: #27ae60;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
  font-weight: bold;
}

.confirm-btn:hover:not(:disabled) {
  background: #219a52;
}

.confirm-btn:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.cancel-btn {
  padding: 12px 20px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
}

.cancel-btn:hover:not(:disabled) {
  background: #c0392b;
}

.cancel-btn:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}
</style>
