"""Pydanticスキーマ定義"""
from pydantic import BaseModel


# === リクエストスキーマ ===

class StartGameRequest(BaseModel):
    character_id: str | None = None


class CookRequest(BaseModel):
    ingredient_names: list[str]


class ShopBuyRequest(BaseModel):
    items: list[dict]  # [{ingredient_name: str, quantity: int}]


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


class DishInfo(BaseModel):
    name: str
    nutrition: NutritionState
    fullness: int
    ingredients: list[str]
    is_named: bool
    named_recipe_name: str | None = None


class GameState(BaseModel):
    session_id: str

    # 日付状態
    day: int
    month: int
    phase: str
    phase_display: str
    weather: str
    is_holiday: bool
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


class CookPreviewResponse(BaseModel):
    dish_name: str
    nutrition: NutritionState
    fullness: int
    is_named: bool
    named_recipe_name: str | None = None
    evaluation_comment: str
    can_make: bool


class MakeBentoResponse(BaseModel):
    bento_name: str
    state: GameState


class AdvancePhaseResponse(BaseModel):
    events: list[EventInfo]
    state: GameState
    deliveries: list[PendingDeliveryItem]
    salary_info: dict | None = None
    bonus_info: dict | None = None
