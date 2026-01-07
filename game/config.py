"""ゲーム設定（GameConfig）"""
from dataclasses import dataclass, field


@dataclass
class GameConfig:
    """ゲーム設定を管理するデータクラス

    シミュレーション環境から設定を注入可能にするため、
    すべてのパラメータをここで一元管理する。
    """

    # === プレイヤー初期値 ===
    initial_money: int = 30000
    initial_energy: int = 10
    initial_stamina: int = 10
    initial_fullness: int = 0

    # === 最大値 ===
    max_energy: int = 10
    max_stamina: int = 10
    max_fullness: int = 10

    # === 栄養システム ===
    nutrition_min_threshold: int = 5  # 1日の最低ライン
    penalty_vitality: int = 2   # 活力素不足: 体力回復ペナルティ
    penalty_mental: int = 2     # 心力素不足: 気力回復ペナルティ
    penalty_sustain: int = 2    # 持続素不足: 満腹感減少ペナルティ

    # === 栄養素による上限増加イベント ===
    nutrition_high_threshold: int = 8  # 「高い」と判定する閾値
    nutrition_streak_for_cap: int = 3  # 上限増加イベント発生に必要な連続日数

    # === アクション消費 ===
    cooking_energy_cost: int = 2      # 調理の気力消費
    bento_energy_cost: int = 3        # 弁当作成の気力消費
    commute_stamina_cost: int = 1     # 出退勤の体力消費（往復で2消費）

    # === 社食 ===
    cafeteria_price: int = 500
    cafeteria_nutrition: int = 3  # 各栄養素
    cafeteria_fullness: int = 5

    # === デリバリー（うぼあデリバリ） ===
    delivery_price: int = 700  # 社食より割高
    delivery_nutrition: int = 2  # 栄養は社食より劣る
    delivery_fullness: int = 6  # 量は多め

    # === 買い出し ===
    shopping_energy_cost: int = 2     # 買い出しの気力消費
    shopping_stamina_cost: int = 1    # 買い出しの体力消費
    shopping_min_energy: int = 3      # 買い出しに必要な最低気力
    shopping_bag_capacity: int = 5    # 1回の買い物で持てる食材数

    # === 睡眠回復 ===
    sleep_energy_recovery: int = 10   # 気力回復量
    sleep_stamina_recovery: int = 5   # 体力回復量

    # === カフェイン ===
    caffeine_insomnia_threshold: int = 3  # 不眠になるカフェイン閾値
    caffeine_energy_penalty: int = 2      # 不眠時の気力回復ペナルティ
    caffeine_stamina_penalty: int = 1     # 不眠時の体力回復ペナルティ

    # === ゲーム期間 ===
    game_start_day: int = 1
    game_start_month: int = 4
    game_duration_days: int = 30  # 1ヶ月

    # === 給料・ボーナス ===
    salary_amount: int = 200000       # 月給（20万円）
    salary_day: int = 25              # 給料日
    bonus_amount: int = 400000        # ボーナス（40万円）
    bonus_months: tuple[int, ...] = (6, 12)  # ボーナス月
    has_bonus: bool = True            # ボーナスの有無（キャラ設定用）

    # === 乱数シード（シミュレーション用） ===
    seed: int | None = None


# デフォルト設定のインスタンス
DEFAULT_CONFIG = GameConfig()


def create_easy_config() -> GameConfig:
    """簡単モードの設定を作成"""
    return GameConfig(
        initial_money=50000,
        initial_energy=12,
        initial_stamina=12,
        max_energy=12,
        max_stamina=12,
        cooking_energy_cost=1,
        cafeteria_price=300,
    )


def create_hard_config() -> GameConfig:
    """難しいモードの設定を作成"""
    return GameConfig(
        initial_money=20000,
        initial_energy=8,
        initial_stamina=8,
        max_energy=8,
        max_stamina=8,
        cooking_energy_cost=3,
        cafeteria_price=800,
        nutrition_min_threshold=7,
    )
