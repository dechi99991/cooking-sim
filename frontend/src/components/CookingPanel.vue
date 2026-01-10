<script setup lang="ts">
import { ref, computed } from 'vue'
import { useGameStore } from '../stores/game'
import { storeToRefs } from 'pinia'

defineProps<{
  allowBento?: boolean
}>()

const store = useGameStore()
const { state, recipesData, lastCookedDish, lastEvaluationComment, loading } = storeToRefs(store)

const selectedIngredients = ref<string[]>([])

const availableIngredients = computed(() => {
  if (!state.value) return []
  // 重複を除いた食材リスト
  const seen = new Set<string>()
  return state.value.stock.filter(item => {
    if (seen.has(item.name) || item.is_expired) return false
    seen.add(item.name)
    return true
  })
})

const canCook = computed(() => {
  return state.value?.can_cook && selectedIngredients.value.length > 0
})

function toggleIngredient(name: string) {
  const idx = selectedIngredients.value.indexOf(name)
  if (idx >= 0) {
    selectedIngredients.value.splice(idx, 1)
  } else {
    selectedIngredients.value.push(name)
  }
}

async function doCook() {
  if (!canCook.value) return
  await store.cook(selectedIngredients.value)
  selectedIngredients.value = []
}

function clearSelection() {
  selectedIngredients.value = []
}

// レシピ取得
async function loadRecipes() {
  await store.fetchRecipes()
}
</script>

<template>
  <div class="cooking-panel">
    <h3>調理</h3>

    <div v-if="!state?.can_cook" class="warning">
      調理には気力が必要です（現在不足）
    </div>

    <div class="section">
      <h4>食材を選択</h4>
      <div class="ingredients">
        <button
          v-for="item in availableIngredients"
          :key="item.name"
          class="ingredient-btn"
          :class="{ selected: selectedIngredients.includes(item.name) }"
          @click="toggleIngredient(item.name)"
        >
          {{ item.name }}
        </button>
      </div>
      <div v-if="availableIngredients.length === 0" class="empty">
        使える食材がありません
      </div>
    </div>

    <div v-if="selectedIngredients.length > 0" class="selection">
      <span>選択中: {{ selectedIngredients.join(', ') }}</span>
      <button class="clear-btn" @click="clearSelection">クリア</button>
    </div>

    <div class="actions">
      <button
        class="cook-btn"
        :disabled="!canCook || loading"
        @click="doCook"
      >
        調理する
      </button>
      <button class="recipe-btn" @click="loadRecipes">レシピ確認</button>
    </div>

    <!-- レシピ一覧 -->
    <div v-if="recipesData.length > 0" class="recipes">
      <h4>レシピ一覧</h4>
      <div class="recipe-list">
        <div
          v-for="recipe in recipesData"
          :key="recipe.name"
          class="recipe"
          :class="{ canMake: recipe.can_make }"
        >
          <span class="recipe-name">{{ recipe.name }}</span>
          <span class="recipe-ingredients">{{ recipe.required_ingredients.join(' + ') }}</span>
          <span v-if="recipe.can_make" class="makeable">作れる</span>
        </div>
      </div>
    </div>

    <!-- 調理結果 -->
    <div v-if="lastCookedDish" class="result">
      <h4>調理結果</h4>
      <div class="dish">
        <div class="dish-name">
          {{ lastCookedDish.name }}
          <span v-if="lastCookedDish.is_named" class="named-badge">レシピ料理</span>
        </div>
        <div class="dish-stats">
          <span>満腹度: +{{ lastCookedDish.fullness }}</span>
        </div>
        <div class="nutrition">
          <span>活力: {{ lastCookedDish.nutrition.vitality }}</span>
          <span>精神: {{ lastCookedDish.nutrition.mental }}</span>
          <span>覚醒: {{ lastCookedDish.nutrition.awakening }}</span>
          <span>持続: {{ lastCookedDish.nutrition.sustain }}</span>
          <span>防御: {{ lastCookedDish.nutrition.defense }}</span>
        </div>
        <div v-if="lastEvaluationComment" class="comment">
          「{{ lastEvaluationComment }}」
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cooking-panel {
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

.warning {
  background: #fef9e7;
  color: #f39c12;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.section {
  margin-bottom: 15px;
}

.ingredients {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.ingredient-btn {
  padding: 8px 12px;
  border: 1px solid #3498db;
  background: white;
  color: #3498db;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.ingredient-btn:hover {
  background: #ebf5fb;
}

.ingredient-btn.selected {
  background: #3498db;
  color: white;
}

.empty {
  color: #95a5a6;
  padding: 10px;
}

.selection {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ebf5fb;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.clear-btn {
  padding: 4px 8px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.actions {
  display: flex;
  gap: 10px;
}

.cook-btn {
  flex: 1;
  padding: 12px;
  background: #27ae60;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
}

.cook-btn:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.recipe-btn {
  padding: 12px;
  background: #9b59b6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.recipes {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.recipe-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.recipe {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
}

.recipe.canMake {
  background: #eafaf1;
}

.recipe-name {
  font-weight: bold;
  min-width: 100px;
}

.recipe-ingredients {
  color: #7f8c8d;
  font-size: 0.9em;
}

.makeable {
  margin-left: auto;
  background: #27ae60;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8em;
}

.result {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.dish {
  background: #fef9e7;
  padding: 15px;
  border-radius: 8px;
}

.dish-name {
  font-size: 1.2em;
  font-weight: bold;
  margin-bottom: 10px;
}

.named-badge {
  background: #f39c12;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.7em;
  margin-left: 10px;
}

.dish-stats {
  margin-bottom: 10px;
  color: #27ae60;
}

.nutrition {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 0.9em;
  color: #7f8c8d;
}

.comment {
  margin-top: 10px;
  font-style: italic;
  color: #8e44ad;
}
</style>
