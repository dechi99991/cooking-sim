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
        fullness=3
    ),
    '卵': Ingredient(
        name='卵',
        price=100,
        nutrition=create_nutrition(vitality=3, mental=2, awakening=2, sustain=1, defense=2),
        fullness=2
    ),
    '野菜': Ingredient(
        name='野菜',
        price=150,
        nutrition=create_nutrition(vitality=1, mental=2, awakening=1, sustain=1, defense=3),
        fullness=1
    ),
    '肉': Ingredient(
        name='肉',
        price=300,
        nutrition=create_nutrition(vitality=4, mental=1, awakening=1, sustain=2, defense=2),
        fullness=3
    ),
    '納豆': Ingredient(
        name='納豆',
        price=80,
        nutrition=create_nutrition(vitality=2, mental=3, awakening=2, sustain=2, defense=3),
        fullness=1
    ),
}


class Stock:
    """食材ストック管理"""

    def __init__(self):
        self._items: dict[str, int] = {}

    def add(self, ingredient_name: str, quantity: int = 1):
        """食材を追加する"""
        if ingredient_name in self._items:
            self._items[ingredient_name] += quantity
        else:
            self._items[ingredient_name] = quantity

    def remove(self, ingredient_name: str, quantity: int = 1) -> bool:
        """食材を消費する。成功したらTrue"""
        if ingredient_name in self._items and self._items[ingredient_name] >= quantity:
            self._items[ingredient_name] -= quantity
            if self._items[ingredient_name] == 0:
                del self._items[ingredient_name]
            return True
        return False

    def has(self, ingredient_name: str, quantity: int = 1) -> bool:
        """指定量の食材があるか確認"""
        return self._items.get(ingredient_name, 0) >= quantity

    def get_quantity(self, ingredient_name: str) -> int:
        """食材の数量を取得"""
        return self._items.get(ingredient_name, 0)

    def get_all(self) -> dict[str, int]:
        """全ストックを取得"""
        return self._items.copy()

    def is_empty(self) -> bool:
        """ストックが空か確認"""
        return len(self._items) == 0

    def get_available_ingredients(self) -> list[str]:
        """利用可能な食材名のリストを取得"""
        return [name for name, qty in self._items.items() if qty > 0]


def get_ingredient(name: str) -> Ingredient | None:
    """食材名から食材データを取得"""
    return INGREDIENTS.get(name)


def get_all_ingredient_names() -> list[str]:
    """全食材名を取得"""
    return list(INGREDIENTS.keys())


def get_shop_items() -> list[tuple[str, int]]:
    """お店で買える食材リストを取得 (名前, 価格)"""
    return [(ing.name, ing.price) for ing in INGREDIENTS.values()]


def create_initial_stock() -> Stock:
    """初期ストックを作成（新社会人スタート用）"""
    stock = Stock()
    # 親が持たせてくれた食材
    stock.add('米', 3)
    stock.add('卵', 2)
    stock.add('野菜', 1)
    stock.add('納豆', 2)
    return stock
