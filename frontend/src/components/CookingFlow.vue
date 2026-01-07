<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useGameStore } from '../stores/game'
import { storeToRefs } from 'pinia'
import CookingPreview from './CookingPreview.vue'
import AutoConsumeModal from './AutoConsumeModal.vue'
import type { CookPreviewResponse, NutritionState, NamedRecipeInfo } from '../types'

const props = defineProps<{
  allowBento?: boolean
  isBento?: boolean  // 弁当作成モード
}>()

const emit = defineEmits<{
  done: []
}>()

const store = useGameStore()
const { state, recipesData, lastCookedDish, lastEvaluationComment, lastBentoName, lastAutoConsume, loading } = storeToRefs(store)

// カフェイン自動消費モーダル
const showAutoConsumeModal = ref(false)

// フロー状態: 'select' | 'preview' | 'result' | 'continue'
type FlowState = 'select' | 'preview' | 'result' | 'continue'
const flowState = ref<FlowState>('select')

const selectedIngredients = ref<string[]>([])
const currentPreview = ref<CookPreviewResponse | null>(null)

// 食事トータル追跡（複数料理時用）
const mealNutrition = ref<NutritionState | null>(null)
const mealFullness = ref(0)
const dishNumber = ref(1)

const availableIngredients = computed(() => {
  if (!state.value) return []
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

const canCookMore = computed(() => {
  if (!state.value) return false
  // 気力・食材・満腹度をチェック
  const hasEnergy = state.value.can_cook
  const hasIngredients = availableIngredients.value.length > 0
  const hasRoom = state.value.player.fullness < 100
  return hasEnergy && hasIngredients && hasRoom
})

// 作れるレシピのみフィルタ
const makeableRecipes = computed(() =>
  recipesData.value.filter(r => r.can_make)
)

function toggleIngredient(name: string) {
  const idx = selectedIngredients.value.indexOf(name)
  if (idx >= 0) {
    selectedIngredients.value.splice(idx, 1)
  } else {
    selectedIngredients.value.push(name)
  }
}

function clearSelection() {
  selectedIngredients.value = []
}

async function showPreview() {
  if (!canCook.value) return
  const preview = await store.cookPreview(
    selectedIngredients.value,
    mealNutrition.value ?? undefined,
    mealFullness.value,
    dishNumber.value
  )
  if (preview) {
    currentPreview.value = preview
    flowState.value = 'preview'
  }
}

async function confirmCook() {
  if (props.isBento) {
    console.log('[CookingFlow] Making bento with:', selectedIngredients.value)
    await store.makeBento(selectedIngredients.value)
    console.log('[CookingFlow] Bento made, lastBentoName:', lastBentoName.value)
  } else {
    await store.cookConfirm(selectedIngredients.value)
    // 食事トータルを更新
    if (lastCookedDish.value) {
      const dish = lastCookedDish.value
      if (mealNutrition.value) {
        // 既存の累計に追加
        mealNutrition.value = {
          vitality: mealNutrition.value.vitality + dish.nutrition.vitality,
          mental: mealNutrition.value.mental + dish.nutrition.mental,
          awakening: mealNutrition.value.awakening + dish.nutrition.awakening,
          sustain: mealNutrition.value.sustain + dish.nutrition.sustain,
          defense: mealNutrition.value.defense + dish.nutrition.defense,
        }
      } else {
        // 最初の料理
        mealNutrition.value = { ...dish.nutrition }
      }
      mealFullness.value += dish.fullness
      dishNumber.value++
    }
  }
  // カフェイン自動消費があった場合はモーダルを表示
  if (lastAutoConsume.value) {
    showAutoConsumeModal.value = true
  } else {
    flowState.value = 'result'
  }
}

function closeAutoConsumeModal() {
  showAutoConsumeModal.value = false
  flowState.value = 'result'
}

function cancelPreview() {
  currentPreview.value = null
  flowState.value = 'select'
}

function cookMore() {
  selectedIngredients.value = []
  currentPreview.value = null
  flowState.value = 'select'
}

function finishCooking() {
  selectedIngredients.value = []
  currentPreview.value = null
  // 食事トータルをリセット
  mealNutrition.value = null
  mealFullness.value = 0
  dishNumber.value = 1
  flowState.value = 'select'
  emit('done')
}

async function loadRecipes() {
  await store.fetchRecipes()
}

// レシピ選択で食材を自動セット
function selectRecipeIngredients(recipe: NamedRecipeInfo) {
  selectedIngredients.value = [...recipe.required_ingredients]
}

// マウント時にレシピを自動取得
onMounted(async () => {
  await store.fetchRecipes()
})
</script>

<template>
  <div class="cooking-flow">
    <!-- カフェイン自動消費モーダル -->
    <AutoConsumeModal
      :show="showAutoConsumeModal"
      :info="lastAutoConsume"
      @close="closeAutoConsumeModal"
    />

    <!-- 食材選択 -->
    <template v-if="flowState === 'select'">
      <h3>調理</h3>

      <div v-if="!state?.can_cook" class="warning">
        気力が足りません（必要: {{ state?.cooking_energy_cost }}）
      </div>

      <!-- 作れるレシピの表示 -->
      <div v-if="makeableRecipes.length > 0" class="makeable-recipes">
        <h4>作れるレシピ</h4>
        <div class="recipe-buttons">
          <button
            v-for="recipe in makeableRecipes"
            :key="recipe.name"
            class="recipe-select-btn"
            @click="selectRecipeIngredients(recipe)"
          >
            <span class="recipe-btn-name">{{ recipe.name }}</span>
            <span class="recipe-btn-ingredients">{{ recipe.required_ingredients.join(' + ') }}</span>
          </button>
        </div>
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
          @click="showPreview"
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
    </template>

    <!-- プレビュー（確認画面） -->
    <template v-else-if="flowState === 'preview' && currentPreview">
      <CookingPreview
        :preview="currentPreview"
        :ingredients="selectedIngredients"
        :loading="loading"
        @confirm="confirmCook"
        @cancel="cancelPreview"
      />
    </template>

    <!-- 調理結果 -->
    <template v-else-if="flowState === 'result' && (lastCookedDish || lastBentoName)">
      <div class="result">
        <!-- 弁当モードの結果 -->
        <template v-if="isBento && lastBentoName">
          <h3>弁当完成！</h3>
          <div class="dish bento">
            <div class="dish-name">
              🍱 {{ lastBentoName }}
            </div>
            <p class="bento-message">お昼に食べられるように保存しました。</p>
          </div>
          <div class="actions">
            <button
              class="finish-btn"
              :disabled="loading"
              @click="finishCooking"
            >
              完了
            </button>
          </div>
        </template>

        <!-- 通常の調理結果 -->
        <template v-else-if="lastCookedDish">
          <h3>調理完了！</h3>
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

          <div class="continue-prompt">
            <p v-if="canCookMore">もう1品作りますか？</p>
            <p v-else class="cannot-cook-reason">
              <template v-if="!state?.can_cook">気力が足りません</template>
              <template v-else-if="availableIngredients.length === 0">食材がありません</template>
              <template v-else>お腹がいっぱいです</template>
            </p>

            <div class="actions">
              <button
                v-if="canCookMore"
                class="more-btn"
                :disabled="loading"
                @click="cookMore"
              >
                もう1品作る
              </button>
              <button
                class="finish-btn"
                :disabled="loading"
                @click="finishCooking"
              >
                終了する
              </button>
            </div>
          </div>
        </template>
      </div>
    </template>
  </div>
</template>

<style scoped>
.cooking-flow {
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

.makeable-recipes {
  background: #eafaf1;
  border: 1px solid #27ae60;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
}

.makeable-recipes h4 {
  color: #27ae60;
  margin: 0 0 10px 0;
}

.recipe-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.recipe-select-btn {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 10px 15px;
  background: white;
  border: 2px solid #27ae60;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.recipe-select-btn:hover {
  background: #27ae60;
  color: white;
}

.recipe-select-btn:hover .recipe-btn-ingredients {
  color: rgba(255, 255, 255, 0.8);
}

.recipe-btn-name {
  font-weight: bold;
  color: #27ae60;
}

.recipe-select-btn:hover .recipe-btn-name {
  color: white;
}

.recipe-btn-ingredients {
  font-size: 0.8em;
  color: #7f8c8d;
  margin-top: 2px;
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
  text-align: center;
}

.result h3 {
  color: #27ae60;
}

.dish {
  background: #eafaf1;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.dish.bento {
  background: #fff9e6;
  border: 2px solid #f39c12;
}

.bento-message {
  color: #7f8c8d;
  margin-top: 10px;
}

.dish-name {
  font-size: 1.3em;
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
  justify-content: center;
  flex-wrap: wrap;
  gap: 15px;
  font-size: 0.9em;
  color: #7f8c8d;
}

.comment {
  margin-top: 15px;
  font-style: italic;
  color: #8e44ad;
}

.continue-prompt {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.continue-prompt p {
  margin: 0 0 15px 0;
}

.cannot-cook-reason {
  color: #e74c3c;
}

.more-btn {
  flex: 1;
  padding: 12px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
}

.more-btn:hover:not(:disabled) {
  background: #2980b9;
}

.finish-btn {
  flex: 1;
  padding: 12px;
  background: #27ae60;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
}

.finish-btn:hover:not(:disabled) {
  background: #219a52;
}
</style>
