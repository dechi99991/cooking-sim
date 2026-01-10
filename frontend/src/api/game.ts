import axios from 'axios'
import type {
  GameState,
  CharacterInfo,
  ShopResponse,
  OnlineShopResponse,
  NamedRecipeInfo,
  CookResponse,
  CookPreviewResponse,
  MakeBentoResponse,
  GoShoppingResponse,
  AdvancePhaseResponse,
  NutritionState,
} from '../types'

// 本番環境では同一オリジンからAPI配信、開発時はlocalhost:8000
const API_BASE = import.meta.env.VITE_API_URL || ''

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

// キャラクター一覧
export async function getCharacters(): Promise<CharacterInfo[]> {
  const res = await api.get('/api/characters')
  return res.data
}

// ゲーム開始
export async function startGame(characterId?: string): Promise<{ session_id: string; state: GameState }> {
  const res = await api.post('/api/game/start', { character_id: characterId })
  return res.data
}

// 状態取得
export async function getState(sessionId: string): Promise<GameState> {
  const res = await api.get(`/api/game/${sessionId}/state`)
  return res.data
}

// 買い出しに行く（気力・体力消費）
export async function goShopping(sessionId: string): Promise<GoShoppingResponse> {
  const res = await api.post(`/api/game/${sessionId}/go-shopping`)
  return res.data
}

// ショップ情報
export async function getShop(sessionId: string, isDistant: boolean = false): Promise<ShopResponse> {
  const res = await api.get(`/api/game/${sessionId}/shop`, {
    params: { is_distant: isDistant }
  })
  return res.data
}

// 買い物
export async function buyFromShop(
  sessionId: string,
  items: { ingredient_name: string; quantity: number }[],
  isDistant: boolean = false
): Promise<GameState> {
  const res = await api.post(`/api/game/${sessionId}/shop/buy`, { items, is_distant: isDistant })
  return res.data
}

// 通販情報
export async function getOnlineShop(sessionId: string): Promise<OnlineShopResponse> {
  const res = await api.get(`/api/game/${sessionId}/online-shop`)
  return res.data
}

// 通販購入
export async function buyFromOnlineShop(
  sessionId: string,
  itemType: 'provision' | 'relic',
  itemName: string,
  quantity: number = 1
): Promise<GameState> {
  const res = await api.post(`/api/game/${sessionId}/online-shop/buy`, {
    item_type: itemType,
    item_name: itemName,
    quantity,
  })
  return res.data
}

// レシピ一覧
export async function getRecipes(sessionId: string): Promise<{ available: NamedRecipeInfo[] }> {
  const res = await api.get(`/api/game/${sessionId}/recipes`)
  return res.data
}

// 調理プレビュー
export async function cookPreview(
  sessionId: string,
  ingredientNames: string[],
  mealNutrition?: NutritionState,
  mealFullness: number = 0,
  dishNumber: number = 1
): Promise<CookPreviewResponse> {
  const res = await api.post(`/api/game/${sessionId}/cook/preview`, {
    ingredient_names: ingredientNames,
    meal_nutrition: mealNutrition ?? null,
    meal_fullness: mealFullness,
    dish_number: dishNumber,
  })
  return res.data
}

// 調理確定
export async function cookConfirm(sessionId: string, ingredientNames: string[]): Promise<CookResponse> {
  const res = await api.post(`/api/game/${sessionId}/cook/confirm`, { ingredient_names: ingredientNames })
  return res.data
}

// 調理（後方互換性のためエイリアス）
export async function cook(sessionId: string, ingredientNames: string[]): Promise<CookResponse> {
  return cookConfirm(sessionId, ingredientNames)
}

// 社食
export async function eatCafeteria(sessionId: string): Promise<GameState> {
  const res = await api.post(`/api/game/${sessionId}/eat-cafeteria`)
  return res.data
}

// デリバリー（うぼあデリバリ）
export async function eatDelivery(sessionId: string): Promise<GameState> {
  const res = await api.post(`/api/game/${sessionId}/eat-delivery`)
  return res.data
}

// 弁当作成
export async function makeBento(sessionId: string, ingredientNames: string[]): Promise<MakeBentoResponse> {
  const res = await api.post(`/api/game/${sessionId}/make-bento`, { ingredient_names: ingredientNames })
  return res.data
}

// 食糧消費
export async function eatProvision(sessionId: string, provisionNames: string[]): Promise<GameState> {
  const res = await api.post(`/api/game/${sessionId}/eat-provision`, { provision_names: provisionNames })
  return res.data
}

// 作り置き消費
export async function eatPrepared(sessionId: string, preparedIndex: number): Promise<GameState> {
  const res = await api.post(`/api/game/${sessionId}/eat-prepared?prepared_index=${preparedIndex}`)
  return res.data
}

// フェーズ進行
export async function advancePhase(sessionId: string): Promise<AdvancePhaseResponse> {
  const res = await api.post(`/api/game/${sessionId}/advance-phase`)
  return res.data
}

// 休日アクション
export async function holidayAction(sessionId: string, action: string): Promise<GameState> {
  const res = await api.post(`/api/game/${sessionId}/holiday-action`, { action })
  return res.data
}

// ボス予告を表示済みにする
export async function markBossPreviewShown(sessionId: string): Promise<GameState> {
  const res = await api.post(`/api/game/${sessionId}/boss-preview-shown`)
  return res.data
}
