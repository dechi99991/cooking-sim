import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  GameState,
  CharacterInfo,
  ShopResponse,
  OnlineShopResponse,
  NamedRecipeInfo,
  DishInfo,
  EventInfo,
  PendingDeliveryItem,
  CookPreviewResponse,
  NutritionState,
} from '../types'
import * as api from '../api/game'

export const useGameStore = defineStore('game', () => {
  // 状態
  const sessionId = ref<string | null>(null)
  const state = ref<GameState | null>(null)
  const characters = ref<CharacterInfo[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 一時的な表示用データ
  const lastCookedDish = ref<DishInfo | null>(null)
  const lastEvaluationComment = ref<string>('')
  const lastCookPreview = ref<CookPreviewResponse | null>(null)
  const lastBentoName = ref<string | null>(null)
  const lastEvents = ref<EventInfo[]>([])
  const lastDeliveries = ref<PendingDeliveryItem[]>([])
  const lastSalaryInfo = ref<{ gross: number; rent: number; net: number } | null>(null)
  const lastBonusInfo = ref<{ amount: number } | null>(null)
  const lastEncouragementMessage = ref<string | null>(null)

  // ショップデータ
  const shopData = ref<ShopResponse | null>(null)
  const onlineShopData = ref<OnlineShopResponse | null>(null)
  const recipesData = ref<NamedRecipeInfo[]>([])

  // 計算プロパティ
  const isPlaying = computed(() => sessionId.value !== null && state.value !== null)
  const isGameOver = computed(() => state.value?.is_game_over ?? false)
  const isGameClear = computed(() => state.value?.is_game_clear ?? false)
  const currentPhase = computed(() => state.value?.phase ?? '')
  const isHoliday = computed(() => state.value?.is_holiday ?? false)

  // カテゴリ別在庫
  const stockByCategory = computed(() => {
    if (!state.value) return {}
    const result: Record<string, typeof state.value.stock> = {}
    for (const item of state.value.stock) {
      if (!result[item.category]) {
        result[item.category] = []
      }
      result[item.category]!.push(item)
    }
    return result
  })

  // アクション
  async function fetchCharacters() {
    loading.value = true
    error.value = null
    try {
      characters.value = await api.getCharacters()
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function startGame(characterId?: string) {
    loading.value = true
    error.value = null
    try {
      const result = await api.startGame(characterId)
      sessionId.value = result.session_id
      state.value = result.state
      // リセット
      lastCookedDish.value = null
      lastEvaluationComment.value = ''
      lastEvents.value = []
      lastDeliveries.value = []
      lastSalaryInfo.value = null
      lastBonusInfo.value = null
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function refreshState() {
    if (!sessionId.value) return
    loading.value = true
    try {
      state.value = await api.getState(sessionId.value)
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function goShopping() {
    if (!sessionId.value) return
    loading.value = true
    error.value = null
    try {
      state.value = await api.goShopping(sessionId.value)
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function fetchShop() {
    if (!sessionId.value) return
    loading.value = true
    try {
      shopData.value = await api.getShop(sessionId.value)
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function buyFromShop(items: { ingredient_name: string; quantity: number }[]) {
    if (!sessionId.value) return
    loading.value = true
    try {
      state.value = await api.buyFromShop(sessionId.value, items)
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function fetchOnlineShop() {
    if (!sessionId.value) return
    loading.value = true
    try {
      onlineShopData.value = await api.getOnlineShop(sessionId.value)
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function buyFromOnlineShop(itemType: 'provision' | 'relic', itemName: string, quantity: number = 1) {
    if (!sessionId.value) return
    loading.value = true
    try {
      state.value = await api.buyFromOnlineShop(sessionId.value, itemType, itemName, quantity)
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function fetchRecipes() {
    if (!sessionId.value) return
    loading.value = true
    try {
      const result = await api.getRecipes(sessionId.value)
      recipesData.value = result.available
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function cook(ingredientNames: string[]) {
    if (!sessionId.value) return
    loading.value = true
    try {
      const result = await api.cook(sessionId.value, ingredientNames)
      state.value = result.state
      lastCookedDish.value = result.dish
      lastEvaluationComment.value = result.evaluation_comment
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function cookPreview(
    ingredientNames: string[],
    mealNutrition?: NutritionState,
    mealFullness: number = 0,
    dishNumber: number = 1
  ) {
    if (!sessionId.value) return null
    loading.value = true
    error.value = null
    try {
      const result = await api.cookPreview(
        sessionId.value,
        ingredientNames,
        mealNutrition,
        mealFullness,
        dishNumber
      )
      lastCookPreview.value = result
      return result
    } catch (e: any) {
      error.value = e.message
      return null
    } finally {
      loading.value = false
    }
  }

  async function cookConfirm(ingredientNames: string[]) {
    if (!sessionId.value) return
    loading.value = true
    error.value = null
    try {
      const result = await api.cookConfirm(sessionId.value, ingredientNames)
      state.value = result.state
      lastCookedDish.value = result.dish
      lastEvaluationComment.value = result.evaluation_comment
      lastCookPreview.value = null
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function eatCafeteria() {
    if (!sessionId.value) return
    loading.value = true
    error.value = null
    try {
      state.value = await api.eatCafeteria(sessionId.value)
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function makeBento(ingredientNames: string[]) {
    if (!sessionId.value) return
    loading.value = true
    error.value = null
    try {
      console.log('[makeBento] Calling API with:', ingredientNames)
      const result = await api.makeBento(sessionId.value, ingredientNames)
      console.log('[makeBento] API response:', result)
      console.log('[makeBento] prepared in response:', result.state?.prepared)
      state.value = result.state
      lastBentoName.value = result.bento_name
      console.log('[makeBento] state.prepared after update:', state.value?.prepared)
    } catch (e: any) {
      console.error('[makeBento] Error:', e)
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function eatProvision(provisionNames: string[]) {
    if (!sessionId.value) return
    loading.value = true
    try {
      state.value = await api.eatProvision(sessionId.value, provisionNames)
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function eatPrepared(preparedIndex: number) {
    if (!sessionId.value) return
    loading.value = true
    error.value = null
    try {
      state.value = await api.eatPrepared(sessionId.value, preparedIndex)
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function advancePhase() {
    if (!sessionId.value) return
    loading.value = true
    try {
      const result = await api.advancePhase(sessionId.value)
      state.value = result.state
      lastEvents.value = result.events
      lastDeliveries.value = result.deliveries
      lastSalaryInfo.value = result.salary_info
      lastBonusInfo.value = result.bonus_info
      lastEncouragementMessage.value = result.encouragement_message ?? null
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function doHolidayAction(action: string) {
    if (!sessionId.value) return
    loading.value = true
    try {
      state.value = await api.holidayAction(sessionId.value, action)
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  function resetGame() {
    sessionId.value = null
    state.value = null
    lastCookedDish.value = null
    lastEvaluationComment.value = ''
    lastCookPreview.value = null
    lastBentoName.value = null
    lastEvents.value = []
    lastDeliveries.value = []
    lastSalaryInfo.value = null
    lastBonusInfo.value = null
    shopData.value = null
    onlineShopData.value = null
    recipesData.value = []
  }

  return {
    // 状態
    sessionId,
    state,
    characters,
    loading,
    error,
    lastCookedDish,
    lastEvaluationComment,
    lastCookPreview,
    lastBentoName,
    lastEvents,
    lastDeliveries,
    lastSalaryInfo,
    lastBonusInfo,
    lastEncouragementMessage,
    shopData,
    onlineShopData,
    recipesData,
    // 計算プロパティ
    isPlaying,
    isGameOver,
    isGameClear,
    currentPhase,
    isHoliday,
    stockByCategory,
    // アクション
    fetchCharacters,
    startGame,
    refreshState,
    goShopping,
    fetchShop,
    buyFromShop,
    fetchOnlineShop,
    buyFromOnlineShop,
    fetchRecipes,
    cook,
    cookPreview,
    cookConfirm,
    eatCafeteria,
    makeBento,
    eatProvision,
    eatPrepared,
    advancePhase,
    doHolidayAction,
    resetGame,
  }
})
