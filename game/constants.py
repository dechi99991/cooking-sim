"""ゲーム定数・初期値

後方互換性のため、GameConfigのデフォルト値をエクスポートする。
新規コードでは直接GameConfigを使用することを推奨。
"""
from .config import DEFAULT_CONFIG, GameConfig

# === 後方互換性のための定数エクスポート ===
# 既存コードが壊れないようにする

# プレイヤー初期値
INITIAL_MONEY = DEFAULT_CONFIG.initial_money
INITIAL_ENERGY = DEFAULT_CONFIG.initial_energy
INITIAL_STAMINA = DEFAULT_CONFIG.initial_stamina
INITIAL_FULLNESS = DEFAULT_CONFIG.initial_fullness

MAX_ENERGY = DEFAULT_CONFIG.max_energy
MAX_STAMINA = DEFAULT_CONFIG.max_stamina
MAX_FULLNESS = DEFAULT_CONFIG.max_fullness

# 栄養素の1日最低ライン
NUTRITION_MIN_THRESHOLD = DEFAULT_CONFIG.nutrition_min_threshold

# 栄養不足ペナルティ
PENALTY_VITALITY = DEFAULT_CONFIG.penalty_vitality
PENALTY_MENTAL = DEFAULT_CONFIG.penalty_mental
PENALTY_SUSTAIN = DEFAULT_CONFIG.penalty_sustain

# アクション消費
COOKING_ENERGY_COST = DEFAULT_CONFIG.cooking_energy_cost
BENTO_ENERGY_COST = DEFAULT_CONFIG.bento_energy_cost
COMMUTE_STAMINA_COST = DEFAULT_CONFIG.commute_stamina_cost

# 社食
CAFETERIA_PRICE = DEFAULT_CONFIG.cafeteria_price
CAFETERIA_NUTRITION = DEFAULT_CONFIG.cafeteria_nutrition
CAFETERIA_FULLNESS = DEFAULT_CONFIG.cafeteria_fullness

# 買い出し
SHOPPING_ENERGY_COST = DEFAULT_CONFIG.shopping_energy_cost
SHOPPING_STAMINA_COST = DEFAULT_CONFIG.shopping_stamina_cost
SHOPPING_MIN_ENERGY = DEFAULT_CONFIG.shopping_min_energy

# 睡眠回復
SLEEP_ENERGY_RECOVERY = DEFAULT_CONFIG.sleep_energy_recovery
SLEEP_STAMINA_RECOVERY = DEFAULT_CONFIG.sleep_stamina_recovery

# ゲーム期間
GAME_START_DAY = DEFAULT_CONFIG.game_start_day
GAME_START_MONTH = DEFAULT_CONFIG.game_start_month
GAME_DURATION_DAYS = DEFAULT_CONFIG.game_duration_days
