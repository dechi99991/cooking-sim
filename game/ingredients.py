"""食材データ・ストック管理"""
from dataclasses import dataclass
from .nutrition import Nutrition, create_nutrition


@dataclass
class Ingredient:
    """食材データ"""
    name: str
    price: int
    nutrition: Nutrition
    fullness: int  # 満腹度増加値
    freshness_days: int = 7  # 鮮度維持日数（この日数までは劣化なし）
    decay_rate: float = 0.1  # 1日あたりの栄養減衰率

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, Ingredient):
            return self.name == other.name
        return False


# 食材マスターデータ
INGREDIENTS = {
    '米': Ingredient(
        name='米',
        price=200,
        nutrition=create_nutrition(vitality=2, mental=1, awakening=1, sustain=3, defense=1),
        fullness=3,
        freshness_days=14,  # 長期保存可能
        decay_rate=0.05
    ),
    '卵': Ingredient(
        name='卵',
        price=100,
        nutrition=create_nutrition(vitality=3, mental=2, awakening=2, sustain=1, defense=2),
        fullness=2,
        freshness_days=5,
        decay_rate=0.10
    ),
    '野菜': Ingredient(
        name='野菜',
        price=150,
        nutrition=create_nutrition(vitality=1, mental=2, awakening=1, sustain=1, defense=3),
        fullness=1,
        freshness_days=3,  # 傷みやすい
        decay_rate=0.15
    ),
    '肉': Ingredient(
        name='肉',
        price=300,
        nutrition=create_nutrition(vitality=4, mental=1, awakening=1, sustain=2, defense=2),
        fullness=3,
        freshness_days=2,  # 最も傷みやすい
        decay_rate=0.20
    ),
    '納豆': Ingredient(
        name='納豆',
        price=80,
        nutrition=create_nutrition(vitality=2, mental=3, awakening=2, sustain=2, defense=3),
        fullness=1,
        freshness_days=7,  # 発酵食品
        decay_rate=0.10
    ),
}


class Stock:
    """食材ストック管理（鮮度対応版）

    内部構造: {食材名: [購入日1, 購入日2, ...]}
    各食材の個々の購入日を記録し、古いものから消費する。
    """

    def __init__(self):
        self._items: dict[str, list[int]] = {}

    def add(self, ingredient_name: str, quantity: int = 1, current_day: int = 1):
        """食材を追加する（購入日を記録）"""
        if ingredient_name not in self._items:
            self._items[ingredient_name] = []
        for _ in range(quantity):
            self._items[ingredient_name].append(current_day)

    def remove(self, ingredient_name: str, quantity: int = 1) -> list[int]:
        """食材を消費する（古いものから）。消費した食材の購入日リストを返す"""
        if ingredient_name not in self._items:
            return []
        items = self._items[ingredient_name]
        if len(items) < quantity:
            return []
        # 古いものから消費（リストはソート済み前提）
        consumed = items[:quantity]
        self._items[ingredient_name] = items[quantity:]
        if not self._items[ingredient_name]:
            del self._items[ingredient_name]
        return consumed

    def discard(self, ingredient_name: str, quantity: int = 1) -> int:
        """食材を廃棄する（古いものから）。廃棄した数を返す"""
        if ingredient_name not in self._items:
            return 0
        items = self._items[ingredient_name]
        discard_count = min(quantity, len(items))
        self._items[ingredient_name] = items[discard_count:]
        if not self._items[ingredient_name]:
            del self._items[ingredient_name]
        return discard_count

    def has(self, ingredient_name: str, quantity: int = 1) -> bool:
        """指定量の食材があるか確認"""
        return len(self._items.get(ingredient_name, [])) >= quantity

    def get_quantity(self, ingredient_name: str) -> int:
        """食材の数量を取得"""
        return len(self._items.get(ingredient_name, []))

    def get_all(self) -> dict[str, int]:
        """全ストックを取得（数量のみ、後方互換用）"""
        return {name: len(days) for name, days in self._items.items() if days}

    def get_all_with_days(self) -> dict[str, list[int]]:
        """全ストックを購入日付きで取得"""
        return {name: days.copy() for name, days in self._items.items() if days}

    def is_empty(self) -> bool:
        """ストックが空か確認"""
        return all(len(days) == 0 for days in self._items.values())

    def get_available_ingredients(self) -> list[str]:
        """利用可能な食材名のリストを取得"""
        return [name for name, days in self._items.items() if days]

    def get_oldest_day(self, ingredient_name: str) -> int | None:
        """指定食材の最も古い購入日を取得"""
        items = self._items.get(ingredient_name, [])
        return items[0] if items else None

    def calculate_freshness_modifier(self, ingredient_name: str, current_day: int) -> float:
        """最も古い食材の鮮度補正値を計算（0.1〜1.0）"""
        oldest_day = self.get_oldest_day(ingredient_name)
        if oldest_day is None:
            return 1.0

        ingredient = get_ingredient(ingredient_name)
        if ingredient is None:
            return 1.0

        elapsed_days = current_day - oldest_day
        if elapsed_days <= ingredient.freshness_days:
            return 1.0  # 鮮度維持期間内

        # 超過日数に応じて減衰
        excess_days = elapsed_days - ingredient.freshness_days
        modifier = 1.0 - (excess_days * ingredient.decay_rate)
        return max(0.1, modifier)  # 最低10%

    def get_freshness_status(self, ingredient_name: str, current_day: int) -> str:
        """鮮度ステータス文字列を取得"""
        oldest_day = self.get_oldest_day(ingredient_name)
        if oldest_day is None:
            return ""

        ingredient = get_ingredient(ingredient_name)
        if ingredient is None:
            return ""

        elapsed_days = current_day - oldest_day
        remaining = ingredient.freshness_days - elapsed_days

        if remaining > 0:
            if remaining >= ingredient.freshness_days:
                return "新鮮"
            return f"残り{remaining}日"
        else:
            modifier = self.calculate_freshness_modifier(ingredient_name, current_day)
            penalty = int((1.0 - modifier) * 100)
            return f"栄養-{penalty}%"

    def get_items_for_discard(self, current_day: int) -> list[tuple[str, int, int, float]]:
        """廃棄候補の食材リストを取得
        Returns: [(食材名, 数量, 経過日数, 鮮度補正値), ...]
        """
        result = []
        for name, days in self._items.items():
            if not days:
                continue
            oldest_day = days[0]
            elapsed = current_day - oldest_day
            modifier = self.calculate_freshness_modifier(name, current_day)
            result.append((name, len(days), elapsed, modifier))
        # 鮮度が低い順（modifier が小さい順）にソート
        result.sort(key=lambda x: x[3])
        return result


def get_ingredient(name: str) -> Ingredient | None:
    """食材名から食材データを取得"""
    return INGREDIENTS.get(name)


def get_all_ingredient_names() -> list[str]:
    """全食材名を取得"""
    return list(INGREDIENTS.keys())


def get_shop_items() -> list[tuple[str, int]]:
    """お店で買える食材リストを取得 (名前, 価格)"""
    return [(ing.name, ing.price) for ing in INGREDIENTS.values()]


def create_initial_stock(start_day: int = 1) -> Stock:
    """初期ストックを作成（新社会人スタート用）"""
    stock = Stock()
    # 親が持たせてくれた食材（ゲーム開始日に購入扱い）
    stock.add('米', 3, start_day)
    stock.add('卵', 2, start_day)
    stock.add('野菜', 1, start_day)
    stock.add('納豆', 2, start_day)
    return stock
