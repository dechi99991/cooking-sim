"""レリック（調理器具など）システム"""
from dataclasses import dataclass


@dataclass
class Relic:
    """レリックデータ"""
    name: str
    price: int
    description: str
    effect_type: str  # "nutrition_boost", "energy_save", "freshness_extend", "fullness_boost"
    effect_target: str | None  # 対象食材名（Noneなら全体）
    effect_value: float  # 効果値（倍率や加算値）


# レリックマスターデータ
RELICS = {
    'フライパン': Relic(
        name='フライパン',
        price=2000,
        description='肉料理の栄養+20%',
        effect_type='nutrition_boost',
        effect_target='肉',
        effect_value=0.2
    ),
    '炊飯器': Relic(
        name='炊飯器',
        price=5000,
        description='米料理の満腹度+1',
        effect_type='fullness_boost',
        effect_target='米',
        effect_value=1
    ),
    '電子レンジ': Relic(
        name='電子レンジ',
        price=8000,
        description='調理の気力消費-1',
        effect_type='energy_save',
        effect_target=None,
        effect_value=1
    ),
    '冷蔵庫': Relic(
        name='冷蔵庫',
        price=15000,
        description='全食材の鮮度+3日',
        effect_type='freshness_extend',
        effect_target=None,
        effect_value=3
    ),
}


class RelicInventory:
    """所持レリック管理"""

    def __init__(self):
        self._owned: set[str] = set()

    def add(self, name: str) -> bool:
        """レリックを追加。既に持っていればFalse"""
        if name in self._owned:
            return False
        self._owned.add(name)
        return True

    def has(self, name: str) -> bool:
        """レリックを持っているか"""
        return name in self._owned

    def get_all(self) -> list[str]:
        """所持レリック一覧"""
        return list(self._owned)

    def get_nutrition_boost(self, ingredient_name: str) -> float:
        """指定食材の栄養ブースト倍率を取得"""
        boost = 0.0
        for relic_name in self._owned:
            relic = RELICS.get(relic_name)
            if relic and relic.effect_type == 'nutrition_boost':
                if relic.effect_target is None or relic.effect_target == ingredient_name:
                    boost += relic.effect_value
        return boost

    def get_fullness_boost(self, ingredient_name: str) -> int:
        """指定食材の満腹度ブースト値を取得"""
        boost = 0
        for relic_name in self._owned:
            relic = RELICS.get(relic_name)
            if relic and relic.effect_type == 'fullness_boost':
                if relic.effect_target is None or relic.effect_target == ingredient_name:
                    boost += int(relic.effect_value)
        return boost

    def get_energy_save(self) -> int:
        """調理時の気力消費軽減値を取得"""
        save = 0
        for relic_name in self._owned:
            relic = RELICS.get(relic_name)
            if relic and relic.effect_type == 'energy_save':
                save += int(relic.effect_value)
        return save

    def get_freshness_extend(self) -> int:
        """鮮度延長日数を取得"""
        extend = 0
        for relic_name in self._owned:
            relic = RELICS.get(relic_name)
            if relic and relic.effect_type == 'freshness_extend':
                extend += int(relic.effect_value)
        return extend


def get_relic(name: str) -> Relic | None:
    """レリック名からレリックデータを取得"""
    return RELICS.get(name)


def get_all_relics() -> list[Relic]:
    """全レリックリストを取得"""
    return list(RELICS.values())
