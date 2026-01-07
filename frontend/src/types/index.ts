// API型定義

export interface NutritionState {
  vitality: number
  mental: number
  awakening: number
  sustain: number
  defense: number
}

export interface PlayerState {
  money: number
  energy: number
  stamina: number
  fullness: number
  card_debt: number
}

export interface StockItem {
  name: string
  category: string
  quantity: number
  purchase_day: number
  expiry_day: number
  days_remaining: number
  is_expired: boolean
  nutrition: NutritionState
  fullness: number
}

export interface ProvisionItem {
  name: string
  quantity: number
  nutrition: NutritionState
  fullness: number
  caffeine: number
}

export interface PreparedItem {
  name: string
  dish_type: string
  nutrition: NutritionState
  fullness: number
  expiry_day: number
}

export interface PendingDeliveryItem {
  item_type: string
  name: string
  quantity: number
  delivery_day: number
}

export interface GameState {
  session_id: string
  day: number
  month: number
  phase: string
  phase_display: string
  weather: string
  is_holiday: boolean
  weekday_name: string
  player: PlayerState
  stock: StockItem[]
  provisions: ProvisionItem[]
  prepared: PreparedItem[]
  pending_deliveries: PendingDeliveryItem[]
  relics: string[]
  daily_nutrition: NutritionState
  caffeine: number
  is_game_over: boolean
  is_game_clear: boolean
  game_over_reason: string | null
  bag_capacity: number
  cooking_energy_cost: number
  can_cook: boolean
  can_go_shopping: boolean
}

export interface CharacterInfo {
  id: string
  name: string
  description: string
  initial_money: number
  initial_energy: number
  initial_stamina: number
  salary_amount: number
  bonus_amount: number
  has_bonus: boolean
  rent_amount: number
}

export interface ShopItemInfo {
  name: string
  category: string
  price: number
  quantity: number
  is_sale: boolean
  nutrition: NutritionState
  fullness: number
  expiry_days: number
}

export interface ShopResponse {
  items: ShopItemInfo[]
  bag_capacity: number
  player_money: number
}

export interface OnlineProvisionInfo {
  name: string
  price: number
  is_sale: boolean
  nutrition: NutritionState
  fullness: number
  caffeine: number
}

export interface OnlineRelicInfo {
  name: string
  description: string
  price: number
  is_sale: boolean
  effect_type: string
  effect_value: number
  is_owned: boolean
  is_pending: boolean
}

export interface OnlineShopResponse {
  provisions: OnlineProvisionInfo[]
  relics: OnlineRelicInfo[]
  player_money: number
  card_debt: number
}

export interface NamedRecipeInfo {
  name: string
  required_ingredients: string[]
  nutrition_multiplier: number
  fullness_bonus: number
  can_make: boolean
}

export interface DishInfo {
  name: string
  nutrition: NutritionState
  fullness: number
  ingredients: string[]
  is_named: boolean
  named_recipe_name: string | null
}

export interface EventInfo {
  id: string
  name: string
  description: string
  timing: string
}

export interface CookResponse {
  dish: DishInfo
  state: GameState
  evaluation_comment: string
}

export interface AdvancePhaseResponse {
  events: EventInfo[]
  state: GameState
  deliveries: PendingDeliveryItem[]
  salary_info: { gross: number; rent: number; net: number } | null
  bonus_info: { amount: number } | null
  encouragement_message: string | null
}

export interface CookPreviewResponse {
  dish_name: string
  nutrition: NutritionState  // この料理の栄養
  fullness: number           // この料理の満腹度
  is_named: boolean
  named_recipe_name: string | null
  evaluation_comment: string
  can_make: boolean
  // 食事トータル（複数料理時）
  meal_nutrition: NutritionState  // 食事トータル栄養
  meal_fullness: number           // 食事トータル満腹度
  dish_number: number             // 何品目か
}

export interface MakeBentoResponse {
  bento_name: string
  state: GameState
}
