"""Pydanticスキーマ定義"""
from __future__ import annotations
from pydantic import BaseModel


# === リクエストスキーマ ===

class StartGameRequest(BaseModel):
    character_id: str | None = None


class CookRequest(BaseModel):
    ingredient_names: list[str]
    # 複数料理時の累計（オプション）
    meal_nutrition: NutritionState | None = None
    meal_fullness: int = 0
    dish_number: int = 1


class ShopBuyRequest(BaseModel):
    items: list[dict]  # [{ingredient_name: str, quantity: int}]
    is_distant: bool = False  # 遠くのスーパーからの購入かどうか


class OnlineShopBuyRequest(BaseModel):
    item_type: str  # "provision" or "relic"
    item_name: str
    quantity: int = 1


class EatProvisionRequest(BaseModel):
    provision_names: list[str]


class HolidayActionRequest(BaseModel):
    action: str  # "shop", "distant", "batch", "rest", "skip"


class MakeBentoRequest(BaseModel):
    ingredient_names: list[str]


# === レスポンススキーマ ===

class NutritionState(BaseModel):
    vitality: int
    mental: int
    awakening: int
    sustain: int
    defense: int


class PlayerState(BaseModel):
    money: int
    energy: int
    stamina: int
    fullness: int
    card_debt: int
    max_energy: int
    max_stamina: int
    grit_used: bool = False  # 根性回復を使用したか


class StockItem(BaseModel):
    name: str
    category: str
    quantity: int
    purchase_day: int
    expiry_day: int
    days_remaining: int
    is_expired: bool
    nutrition: NutritionState
    fullness: int


class ProvisionItem(BaseModel):
    name: str
    quantity: int
    nutrition: NutritionState
    fullness: int
    caffeine: int


class PreparedItem(BaseModel):
    name: str
    dish_type: str
    nutrition: NutritionState
    fullness: int
    expiry_day: int


class PendingDeliveryItem(BaseModel):
    item_type: str
    name: str
    quantity: int
    delivery_day: int


class EventInfo(BaseModel):
    id: str
    name: str
    description: str
    timing: str
    reason: str = ""  # イベント発生の根拠


class AutoConsumeInfo(BaseModel):
    """カフェイン自動消費の結果"""
    consumed_name: str
    caffeine_amount: int
    energy_restored: int
    will_cause_insomnia: bool


class DishInfo(BaseModel):
    name: str
    nutrition: NutritionState
    fullness: int
    ingredients: list[str]
    is_named: bool
    named_recipe_name: str | None = None


class TemperamentInfo(BaseModel):
    """気質情報"""
    id: str
    name: str
    description: str
    icon: str


class WeeklyBossInfo(BaseModel):
    """週間ボス情報（月曜予告用）"""
    id: str
    name: str
    description: str  # 予告文
    category: str  # event, work, life, nutrition
    requirements_text: str  # 条件の人間可読形式
    required_money: int = 0
    required_energy: int = 0
    required_stamina: int = 0
    required_item: str | None = None
    required_nutrition: dict = {}  # {"mental": 20} など
    required_all_nutrients: int = 0


class BossResult(BaseModel):
    """金曜ボスイベント結果"""
    boss_id: str
    boss_name: str
    category: str
    success: bool
    requirements_text: str
    energy_change: int
    stamina_change: int
    money_change: int  # 報酬 - 借金
    message: str
    weekly_nutrition: NutritionState  # 週間累計栄養


class WeeklyEvaluation(BaseModel):
    """週間評価結果（金曜ボスイベント）- 旧互換用"""
    rank: str  # SS, S, A, B, C, F
    nutrition_grade: str  # S, A, B, C, D, E
    nutrients_ok: int  # 閾値達成数 (0-5)
    saving_success: bool
    overspending: bool
    food_spending: int
    meals_cooked: int
    energy_change: int
    stamina_change: int
    money_change: int
    message: str


class GameState(BaseModel):
    session_id: str

    # 日付状態
    day: int
    month: int
    phase: str
    phase_display: str
    weather: str
    is_holiday: bool
    is_friday: bool  # 金曜日かどうか
    is_weekend: bool  # 週末かどうか
    weekday_name: str

    # プレイヤー状態
    player: PlayerState

    # 在庫
    stock: list[StockItem]
    provisions: list[ProvisionItem]
    prepared: list[PreparedItem]
    pending_deliveries: list[PendingDeliveryItem]
    relics: list[str]

    # 1日の状態
    daily_nutrition: NutritionState
    caffeine: int

    # ゲーム状態
    is_game_over: bool
    is_game_clear: bool
    game_over_reason: str | None

    # 追加情報
    bag_capacity: int
    cooking_energy_cost: int
    can_cook: bool
    can_go_shopping: bool
    is_office_worker: bool  # 出勤キャラかどうか（昼食自動化用）

    # 体力警告フラグ
    commute_will_cause_game_over: bool  # 出勤で体力が0になるか
    shopping_will_cause_game_over: bool  # 買い出しで体力が0になるか

    # 気質システム
    temperament: TemperamentInfo | None  # 判定された気質（4日目以降）
    temperament_just_revealed: bool  # 気質が今回発表されたか

    # 週間ボスシステム
    current_boss: WeeklyBossInfo | None = None  # 今週のボス
    should_show_boss_preview: bool = False  # ボス予告を表示すべきか


class StartGameResponse(BaseModel):
    session_id: str
    state: GameState


class CharacterInfo(BaseModel):
    id: str
    name: str
    description: str
    initial_money: int
    initial_energy: int
    initial_stamina: int
    salary_amount: int
    bonus_amount: int
    has_bonus: bool
    rent_amount: int


class ShopItemInfo(BaseModel):
    name: str
    category: str
    price: int
    quantity: int
    is_sale: bool
    nutrition: NutritionState
    fullness: int
    expiry_days: int
    is_distant_only: bool = False  # 遠くのスーパー限定食材フラグ


class ShopResponse(BaseModel):
    items: list[ShopItemInfo]
    bag_capacity: int
    player_money: int


class OnlineProvisionInfo(BaseModel):
    name: str
    price: int
    is_sale: bool
    nutrition: NutritionState
    fullness: int
    caffeine: int


class OnlineRelicInfo(BaseModel):
    name: str
    description: str
    price: int
    is_sale: bool
    effect_type: str
    effect_value: float
    is_owned: bool
    is_pending: bool


class OnlineShopResponse(BaseModel):
    provisions: list[OnlineProvisionInfo]
    relics: list[OnlineRelicInfo]
    player_money: int
    card_debt: int


class NamedRecipeInfo(BaseModel):
    name: str
    required_ingredients: list[str]
    nutrition_multiplier: float
    fullness_bonus: int
    can_make: bool


class RecipesResponse(BaseModel):
    available: list[NamedRecipeInfo]


class CookResponse(BaseModel):
    dish: DishInfo
    state: GameState
    evaluation_comment: str
    auto_consume: AutoConsumeInfo | None = None


class CookPreviewResponse(BaseModel):
    dish_name: str
    nutrition: NutritionState  # この料理の栄養
    fullness: int              # この料理の満腹度
    is_named: bool
    named_recipe_name: str | None = None
    evaluation_comment: str
    can_make: bool
    # 食事トータル（複数料理時）
    meal_nutrition: NutritionState  # 食事トータル栄養
    meal_fullness: int              # 食事トータル満腹度
    dish_number: int                # 何品目か


class MakeBentoResponse(BaseModel):
    bento_name: str
    state: GameState
    auto_consume: AutoConsumeInfo | None = None


class GoShoppingResponse(BaseModel):
    state: GameState
    auto_consume: AutoConsumeInfo | None = None


class AdvancePhaseResponse(BaseModel):
    events: list[EventInfo]
    state: GameState
    deliveries: list[PendingDeliveryItem]
    salary_info: dict | None = None
    bonus_info: dict | None = None
    encouragement_message: str | None = None
    weekly_evaluation: WeeklyEvaluation | None = None  # 旧互換用
    boss_result: BossResult | None = None  # 金曜ボスイベント結果（新）
