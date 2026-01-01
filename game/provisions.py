"""食糧（調理不要食品）システム"""
from dataclasses import dataclass
from .nutrition import Nutrition, create_nutrition


@dataclass
class Provision:
    """食糧データ（調理不要食品）"""
    name: str
    price: int
    nutrition: Nutrition
    fullness: int


# 食糧マスターデータ
PROVISIONS = {
    'カップ麺': Provision(
        name='カップ麺',
        price=150,
        nutrition=create_nutrition(vitality=1, mental=1, awakening=1, sustain=1, defense=0),
        fullness=5
    ),
    'レトルトカレー': Provision(
        name='レトルトカレー',
        price=300,
        nutrition=create_nutrition(vitality=2, mental=1, awakening=1, sustain=2, defense=1),
        fullness=6
    ),
    '冷凍弁当': Provision(
        name='冷凍弁当',
        price=400,
        nutrition=create_nutrition(vitality=2, mental=2, awakening=1, sustain=2, defense=2),
        fullness=6
    ),
    'パン': Provision(
        name='パン',
        price=100,
        nutrition=create_nutrition(vitality=1, mental=1, awakening=2, sustain=1, defense=0),
        fullness=3
    ),
    'おにぎり': Provision(
        name='おにぎり',
        price=120,
        nutrition=create_nutrition(vitality=1, mental=1, awakening=1, sustain=2, defense=1),
        fullness=4
    ),
}


class ProvisionStock:
    """食糧ストック管理"""

    def __init__(self):
        self._items: dict[str, int] = {}

    def add(self, name: str, quantity: int = 1):
        """食糧を追加"""
        if name not in self._items:
            self._items[name] = 0
        self._items[name] += quantity

    def remove(self, name: str, quantity: int = 1) -> bool:
        """食糧を消費。成功したらTrue"""
        if name in self._items and self._items[name] >= quantity:
            self._items[name] -= quantity
            if self._items[name] == 0:
                del self._items[name]
            return True
        return False

    def has(self, name: str, quantity: int = 1) -> bool:
        """指定量の食糧があるか確認"""
        return self._items.get(name, 0) >= quantity

    def get_quantity(self, name: str) -> int:
        """食糧の数量を取得"""
        return self._items.get(name, 0)

    def get_all(self) -> dict[str, int]:
        """全ストックを取得"""
        return self._items.copy()

    def is_empty(self) -> bool:
        """ストックが空か確認"""
        return len(self._items) == 0

    def get_available(self) -> list[str]:
        """利用可能な食糧名のリストを取得"""
        return [name for name, qty in self._items.items() if qty > 0]


def get_provision(name: str) -> Provision | None:
    """食糧名から食糧データを取得"""
    return PROVISIONS.get(name)


def get_all_provisions() -> list[Provision]:
    """全食糧リストを取得"""
    return list(PROVISIONS.values())


def get_shop_provisions() -> list[tuple[str, int]]:
    """通販で買える食糧リストを取得 (名前, 価格)"""
    return [(p.name, p.price) for p in PROVISIONS.values()]
