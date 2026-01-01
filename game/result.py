"""ゲーム結果（GameResult）"""
from dataclasses import dataclass, field


@dataclass
class GameResult:
    """ゲーム結果を記録するデータクラス

    シミュレーション環境での分析に使用する。
    1回のゲームプレイの結果をすべて記録する。
    """

    # === 基本結果 ===
    survived_days: int = 0
    is_game_over: bool = False
    is_game_clear: bool = False
    game_over_reason: str | None = None  # "money" / "stamina" / None

    # === 最終ステータス ===
    final_money: int = 0
    final_stamina: int = 0
    final_energy: int = 0

    # === 食事統計 ===
    total_meals_eaten: int = 0
    total_meals_skipped: int = 0
    total_meals_cooked: int = 0      # 自炊回数
    total_cafeteria_used: int = 0    # 社食利用回数
    total_bento_made: int = 0        # 弁当作成回数

    # === 買い出し統計 ===
    total_shopping_trips: int = 0
    total_money_spent_shopping: int = 0
    total_items_bought: int = 0

    # === 栄養統計 ===
    nutrition_penalties: dict = field(default_factory=lambda: {
        '活力素': 0,
        '心力素': 0,
        '覚醒素': 0,
        '持続素': 0,
        '防衛素': 0,
    })
    days_with_balanced_nutrition: int = 0  # バランス良い日数

    # === メタ情報 ===
    seed: int | None = None
    config_name: str = "default"

    def to_dict(self) -> dict:
        """辞書形式に変換（CSV出力用）"""
        result = {
            'survived_days': self.survived_days,
            'is_game_over': self.is_game_over,
            'is_game_clear': self.is_game_clear,
            'game_over_reason': self.game_over_reason or '',
            'final_money': self.final_money,
            'final_stamina': self.final_stamina,
            'final_energy': self.final_energy,
            'total_meals_eaten': self.total_meals_eaten,
            'total_meals_skipped': self.total_meals_skipped,
            'total_meals_cooked': self.total_meals_cooked,
            'total_cafeteria_used': self.total_cafeteria_used,
            'total_bento_made': self.total_bento_made,
            'total_shopping_trips': self.total_shopping_trips,
            'total_money_spent_shopping': self.total_money_spent_shopping,
            'total_items_bought': self.total_items_bought,
            'days_with_balanced_nutrition': self.days_with_balanced_nutrition,
            'seed': self.seed or '',
            'config_name': self.config_name,
        }
        # 栄養ペナルティを展開
        for nutrient, count in self.nutrition_penalties.items():
            result[f'penalty_{nutrient}'] = count
        return result


@dataclass
class GameStats:
    """ゲーム中のリアルタイム統計を記録するクラス

    GameManagerが保持し、ゲーム終了時にGameResultに変換する。
    """

    # 食事カウンター
    meals_eaten: int = 0
    meals_skipped: int = 0
    meals_cooked: int = 0
    cafeteria_used: int = 0
    bento_made: int = 0

    # 買い出しカウンター
    shopping_trips: int = 0
    money_spent_shopping: int = 0
    items_bought: int = 0

    # 栄養ペナルティカウンター
    nutrition_penalties: dict = field(default_factory=lambda: {
        '活力素': 0,
        '心力素': 0,
        '覚醒素': 0,
        '持続素': 0,
        '防衛素': 0,
    })
    days_balanced: int = 0

    def record_meal_eaten(self):
        """食事を記録"""
        self.meals_eaten += 1

    def record_meal_skipped(self):
        """食事抜きを記録"""
        self.meals_skipped += 1

    def record_cooking(self):
        """自炊を記録"""
        self.meals_cooked += 1

    def record_cafeteria(self):
        """社食利用を記録"""
        self.cafeteria_used += 1

    def record_bento(self):
        """弁当作成を記録"""
        self.bento_made += 1

    def record_shopping(self, money_spent: int, items_count: int):
        """買い出しを記録"""
        self.shopping_trips += 1
        self.money_spent_shopping += money_spent
        self.items_bought += items_count

    def record_nutrition_penalty(self, nutrient: str):
        """栄養ペナルティを記録"""
        if nutrient in self.nutrition_penalties:
            self.nutrition_penalties[nutrient] += 1

    def record_balanced_day(self):
        """バランスの良い日を記録"""
        self.days_balanced += 1

    def to_result(
        self,
        survived_days: int,
        is_game_over: bool,
        is_game_clear: bool,
        game_over_reason: str | None,
        final_money: int,
        final_stamina: int,
        final_energy: int,
        seed: int | None = None,
        config_name: str = "default"
    ) -> GameResult:
        """GameResultに変換"""
        return GameResult(
            survived_days=survived_days,
            is_game_over=is_game_over,
            is_game_clear=is_game_clear,
            game_over_reason=game_over_reason,
            final_money=final_money,
            final_stamina=final_stamina,
            final_energy=final_energy,
            total_meals_eaten=self.meals_eaten,
            total_meals_skipped=self.meals_skipped,
            total_meals_cooked=self.meals_cooked,
            total_cafeteria_used=self.cafeteria_used,
            total_bento_made=self.bento_made,
            total_shopping_trips=self.shopping_trips,
            total_money_spent_shopping=self.money_spent_shopping,
            total_items_bought=self.items_bought,
            nutrition_penalties=self.nutrition_penalties.copy(),
            days_with_balanced_nutrition=self.days_balanced,
            seed=seed,
            config_name=config_name,
        )
