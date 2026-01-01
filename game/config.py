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

    # === アクション消費 ===
    cooking_energy_cost: int = 2      # 調理の気力消費
    bento_energy_cost: int = 3        # 弁当作成の気力消費
    commute_stamina_cost: int = 2     # 出退勤の体力消費

    # === 社食 ===
    cafeteria_price: int = 500
    cafeteria_nutrition: int = 3  # 各栄養素
    cafeteria_fullness: int = 5

    # === 買い出し ===
    shopping_energy_cost: int = 2     # 買い出しの気力消費
    shopping_stamina_cost: int = 1    # 買い出しの体力消費
    shopping_min_energy: int = 3      # 買い出しに必要な最低気力

    # === 睡眠回復 ===
    sleep_energy_recovery: int = 10   # 気力回復量
    sleep_stamina_recovery: int = 5   # 体力回復量

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
