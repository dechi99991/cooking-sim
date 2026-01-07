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
    caffeine: int = 0  # カフェイン量（0=なし）


@dataclass
class PreparedDish:
    """調理済み料理（弁当など）"""
    name: str
    nutrition: Nutrition
    fullness: int
    expiry_day: int  # 期限日（この日まで食べられる）
    dish_type: str = "弁当"  # "弁当", "作り置き" など


@dataclass
class PendingDelivery:
    """配送待ちの商品"""
    item_type: str  # "provision" or "relic"
    name: str
    quantity: int
    delivery_day: int  # 届く日


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
    # カフェイン飲料
    '缶コーヒー': Provision(
        name='缶コーヒー',
        price=130,
        nutrition=create_nutrition(vitality=0, mental=1, awakening=2, sustain=0, defense=0),
        fullness=1,
        caffeine=1
    ),
    'エナジードリンク': Provision(
        name='エナジードリンク',
        price=200,
        nutrition=create_nutrition(vitality=0, mental=2, awakening=3, sustain=0, defense=0),
        fullness=1,
        caffeine=2
    ),
    'インスタントコーヒー': Provision(
        name='インスタントコーヒー',
        price=80,
        nutrition=create_nutrition(vitality=0, mental=1, awakening=1, sustain=0, defense=0),
        fullness=0,
        caffeine=1
    ),
}


class ProvisionStock:
    """食糧ストック管理（通販食品 + 弁当などの調理済み料理）"""

    def __init__(self):
        self._items: dict[str, int] = {}  # 通販食品
        self._prepared: list[PreparedDish] = []  # 弁当など調理済み
        self._pending: list[PendingDelivery] = []  # 配送待ち

    # === 通販食品の管理 ===

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

    def get_available(self) -> list[str]:
        """利用可能な食糧名のリストを取得"""
        return [name for name, qty in self._items.items() if qty > 0]

    # === 弁当・調理済み料理の管理 ===

    def add_prepared(self, dish_name: str, nutrition: Nutrition, fullness: int,
                     expiry_day: int, dish_type: str = "弁当"):
        """調理済み料理（弁当など）を追加"""
        prepared = PreparedDish(
            name=dish_name,
            nutrition=nutrition,
            fullness=fullness,
            expiry_day=expiry_day,
            dish_type=dish_type
        )
        self._prepared.append(prepared)

    def get_prepared(self, current_day: int) -> list[PreparedDish]:
        """有効な調理済み料理のリストを取得（期限内のもの）"""
        return [p for p in self._prepared if p.expiry_day >= current_day]

    def remove_prepared(self, index: int) -> PreparedDish | None:
        """指定インデックスの調理済み料理を消費して返す"""
        valid_prepared = [p for p in self._prepared]
        if 0 <= index < len(valid_prepared):
            dish = valid_prepared[index]
            self._prepared.remove(dish)
            return dish
        return None

    def remove_expired_prepared(self, current_day: int) -> list[PreparedDish]:
        """期限切れの調理済み料理を削除して返す"""
        expired = [p for p in self._prepared if p.expiry_day < current_day]
        self._prepared = [p for p in self._prepared if p.expiry_day >= current_day]
        return expired

    def has_prepared(self, current_day: int) -> bool:
        """有効な調理済み料理があるか確認"""
        return any(p.expiry_day >= current_day for p in self._prepared)

    def count_prepared(self, current_day: int) -> int:
        """有効な調理済み料理の数を取得"""
        return len([p for p in self._prepared if p.expiry_day >= current_day])

    # === 全体のチェック ===

    def is_empty(self, current_day: int = 0) -> bool:
        """ストックが空か確認（通販食品 + 有効な調理済み）"""
        has_items = len(self._items) > 0
        has_prepared = self.has_prepared(current_day) if current_day > 0 else len(self._prepared) > 0
        return not has_items and not has_prepared

    # === 配送待ち管理 ===

    def add_pending(self, item_type: str, name: str, quantity: int, delivery_day: int):
        """配送待ちを追加"""
        self._pending.append(PendingDelivery(
            item_type=item_type,
            name=name,
            quantity=quantity,
            delivery_day=delivery_day
        ))

    def get_pending(self) -> list[PendingDelivery]:
        """配送待ちリストを取得"""
        return self._pending.copy()

    def process_deliveries(self, current_day: int) -> list[PendingDelivery]:
        """配送処理。届いた商品をストックに追加し、届いた商品リストを返す

        Note: レリックの配送はGameManager側で処理する必要がある
        """
        delivered = []
        remaining = []

        for item in self._pending:
            if item.delivery_day <= current_day:
                if item.item_type == "provision":
                    self.add(item.name, item.quantity)
                delivered.append(item)
            else:
                remaining.append(item)

        self._pending = remaining
        return delivered

    def has_pending(self) -> bool:
        """配送待ちがあるか"""
        return len(self._pending) > 0

    def count_pending(self) -> int:
        """配送待ちの数"""
        return len(self._pending)

    def get_caffeinated_provisions(self) -> list[tuple[str, int, int]]:
        """カフェイン飲料をカフェイン量昇順で取得

        Returns:
            list of (name, caffeine_amount, quantity)
        """
        result = []
        for name, qty in self._items.items():
            if qty > 0:
                prov = get_provision(name)
                if prov and prov.caffeine > 0:
                    result.append((name, prov.caffeine, qty))
        # カフェイン量が少ない順にソート
        return sorted(result, key=lambda x: x[1])


def get_provision(name: str) -> Provision | None:
    """食糧名から食糧データを取得"""
    return PROVISIONS.get(name)


def get_all_provisions() -> list[Provision]:
    """全食糧リストを取得"""
    return list(PROVISIONS.values())


def get_shop_provisions() -> list[tuple[str, int]]:
    """通販で買える食糧リストを取得 (名前, 価格)"""
    return [(p.name, p.price) for p in PROVISIONS.values()]
