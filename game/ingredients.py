"""食材データ・ストック管理"""
from __future__ import annotations
import random
from dataclasses import dataclass
from typing import TYPE_CHECKING
from .nutrition import Nutrition, create_nutrition

if TYPE_CHECKING:
    from .relic import RelicInventory


@dataclass
class Ingredient:
    """食材データ"""
    name: str
    price: int
    nutrition: Nutrition
    fullness: int  # 満腹度増加値
    freshness_days: int = 7  # 鮮度維持日数（この日数までは劣化なし）
    decay_rate: float = 0.1  # 1日あたりの栄養減衰率
    category: str = "その他"  # カテゴリ
    distant_only: bool = False  # 遠くのスーパー限定フラグ

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, Ingredient):
            return self.name == other.name
        return False


# 食材マスターデータ（100種類）
INGREDIENTS = {
    # === 穀物・主食 (10種類) ===
    '米': Ingredient(name='米', price=200, nutrition=create_nutrition(2, 1, 1, 3, 1), fullness=3, freshness_days=14, decay_rate=0.05, category='穀物'),
    'パン': Ingredient(name='パン', price=150, nutrition=create_nutrition(1, 1, 2, 2, 1), fullness=2, freshness_days=3, decay_rate=0.15, category='穀物'),
    'うどん': Ingredient(name='うどん', price=100, nutrition=create_nutrition(1, 1, 1, 3, 1), fullness=3, freshness_days=5, decay_rate=0.10, category='穀物'),
    'そば': Ingredient(name='そば', price=120, nutrition=create_nutrition(2, 1, 1, 2, 2), fullness=3, freshness_days=5, decay_rate=0.10, category='穀物'),
    'パスタ': Ingredient(name='パスタ', price=180, nutrition=create_nutrition(1, 1, 1, 3, 1), fullness=3, freshness_days=30, decay_rate=0.02, category='穀物'),
    'ラーメン': Ingredient(name='ラーメン', price=130, nutrition=create_nutrition(1, 2, 2, 2, 1), fullness=3, freshness_days=14, decay_rate=0.05, category='穀物'),
    'もち': Ingredient(name='もち', price=250, nutrition=create_nutrition(1, 1, 1, 4, 1), fullness=4, freshness_days=10, decay_rate=0.08, category='穀物'),
    'シリアル': Ingredient(name='シリアル', price=350, nutrition=create_nutrition(2, 2, 3, 2, 2), fullness=2, freshness_days=60, decay_rate=0.01, category='穀物'),
    'オートミール': Ingredient(name='オートミール', price=300, nutrition=create_nutrition(3, 2, 2, 3, 2), fullness=3, freshness_days=60, decay_rate=0.01, category='穀物'),
    '食パン': Ingredient(name='食パン', price=120, nutrition=create_nutrition(1, 1, 2, 2, 1), fullness=2, freshness_days=4, decay_rate=0.12, category='穀物'),

    # === 野菜 (20種類) ===
    'キャベツ': Ingredient(name='キャベツ', price=150, nutrition=create_nutrition(1, 2, 1, 1, 3), fullness=1, freshness_days=7, decay_rate=0.10, category='野菜'),
    'にんじん': Ingredient(name='にんじん', price=100, nutrition=create_nutrition(1, 1, 1, 1, 4), fullness=1, freshness_days=10, decay_rate=0.08, category='野菜'),
    'たまねぎ': Ingredient(name='たまねぎ', price=80, nutrition=create_nutrition(1, 1, 1, 2, 2), fullness=1, freshness_days=14, decay_rate=0.05, category='野菜'),
    'じゃがいも': Ingredient(name='じゃがいも', price=100, nutrition=create_nutrition(1, 1, 1, 3, 1), fullness=2, freshness_days=14, decay_rate=0.05, category='野菜'),
    'トマト': Ingredient(name='トマト', price=180, nutrition=create_nutrition(1, 2, 2, 1, 3), fullness=1, freshness_days=5, decay_rate=0.12, category='野菜'),
    'ほうれん草': Ingredient(name='ほうれん草', price=200, nutrition=create_nutrition(2, 2, 1, 1, 4), fullness=1, freshness_days=3, decay_rate=0.15, category='野菜'),
    'レタス': Ingredient(name='レタス', price=150, nutrition=create_nutrition(1, 1, 1, 1, 3), fullness=1, freshness_days=4, decay_rate=0.15, category='野菜'),
    'ピーマン': Ingredient(name='ピーマン', price=120, nutrition=create_nutrition(1, 2, 1, 1, 3), fullness=1, freshness_days=7, decay_rate=0.10, category='野菜'),
    'なす': Ingredient(name='なす', price=130, nutrition=create_nutrition(1, 1, 1, 1, 2), fullness=1, freshness_days=5, decay_rate=0.12, category='野菜'),
    'きゅうり': Ingredient(name='きゅうり', price=100, nutrition=create_nutrition(1, 1, 1, 1, 2), fullness=1, freshness_days=5, decay_rate=0.12, category='野菜'),
    'もやし': Ingredient(name='もやし', price=30, nutrition=create_nutrition(1, 1, 1, 1, 1), fullness=1, freshness_days=2, decay_rate=0.20, category='野菜'),
    'ねぎ': Ingredient(name='ねぎ', price=100, nutrition=create_nutrition(1, 1, 1, 1, 2), fullness=1, freshness_days=7, decay_rate=0.10, category='野菜'),
    'だいこん': Ingredient(name='だいこん', price=150, nutrition=create_nutrition(1, 1, 1, 2, 2), fullness=2, freshness_days=10, decay_rate=0.08, category='野菜'),
    'かぼちゃ': Ingredient(name='かぼちゃ', price=200, nutrition=create_nutrition(2, 1, 1, 2, 3), fullness=2, freshness_days=14, decay_rate=0.05, category='野菜'),
    'ブロッコリー': Ingredient(name='ブロッコリー', price=200, nutrition=create_nutrition(2, 2, 1, 1, 4), fullness=1, freshness_days=5, decay_rate=0.12, category='野菜'),
    'アスパラガス': Ingredient(name='アスパラガス', price=250, nutrition=create_nutrition(2, 2, 2, 1, 3), fullness=1, freshness_days=4, decay_rate=0.15, category='野菜'),
    'ごぼう': Ingredient(name='ごぼう', price=150, nutrition=create_nutrition(1, 1, 1, 2, 3), fullness=1, freshness_days=10, decay_rate=0.08, category='野菜'),
    'れんこん': Ingredient(name='れんこん', price=200, nutrition=create_nutrition(1, 1, 1, 2, 3), fullness=2, freshness_days=7, decay_rate=0.10, category='野菜'),
    'にら': Ingredient(name='にら', price=100, nutrition=create_nutrition(2, 1, 2, 1, 2), fullness=1, freshness_days=4, decay_rate=0.15, category='野菜'),
    '白菜': Ingredient(name='白菜', price=180, nutrition=create_nutrition(1, 1, 1, 1, 3), fullness=1, freshness_days=7, decay_rate=0.10, category='野菜'),

    # === 肉類 (15種類) ===
    '鶏むね肉': Ingredient(name='鶏むね肉', price=250, nutrition=create_nutrition(4, 1, 1, 2, 2), fullness=3, freshness_days=2, decay_rate=0.20, category='肉'),
    '鶏もも肉': Ingredient(name='鶏もも肉', price=280, nutrition=create_nutrition(4, 2, 1, 2, 2), fullness=3, freshness_days=2, decay_rate=0.20, category='肉'),
    '豚バラ肉': Ingredient(name='豚バラ肉', price=350, nutrition=create_nutrition(4, 2, 1, 3, 2), fullness=4, freshness_days=2, decay_rate=0.20, category='肉'),
    '豚ロース': Ingredient(name='豚ロース', price=400, nutrition=create_nutrition(4, 2, 1, 2, 2), fullness=3, freshness_days=2, decay_rate=0.20, category='肉'),
    '牛切り落とし': Ingredient(name='牛切り落とし', price=500, nutrition=create_nutrition(5, 2, 1, 2, 3), fullness=3, freshness_days=2, decay_rate=0.20, category='肉'),
    '牛ステーキ': Ingredient(name='牛ステーキ', price=800, nutrition=create_nutrition(5, 3, 2, 3, 3), fullness=4, freshness_days=2, decay_rate=0.20, category='肉'),
    'ひき肉': Ingredient(name='ひき肉', price=300, nutrition=create_nutrition(4, 1, 1, 2, 2), fullness=3, freshness_days=1, decay_rate=0.25, category='肉'),
    'ベーコン': Ingredient(name='ベーコン', price=350, nutrition=create_nutrition(3, 2, 2, 2, 2), fullness=2, freshness_days=7, decay_rate=0.10, category='肉'),
    'ハム': Ingredient(name='ハム', price=300, nutrition=create_nutrition(3, 1, 1, 2, 2), fullness=2, freshness_days=7, decay_rate=0.10, category='肉'),
    'ソーセージ': Ingredient(name='ソーセージ', price=280, nutrition=create_nutrition(3, 2, 2, 2, 2), fullness=2, freshness_days=7, decay_rate=0.10, category='肉'),
    '鶏ささみ': Ingredient(name='鶏ささみ', price=230, nutrition=create_nutrition(5, 1, 1, 1, 2), fullness=2, freshness_days=2, decay_rate=0.20, category='肉'),
    '手羽先': Ingredient(name='手羽先', price=200, nutrition=create_nutrition(3, 2, 1, 2, 2), fullness=2, freshness_days=2, decay_rate=0.20, category='肉'),
    'レバー': Ingredient(name='レバー', price=180, nutrition=create_nutrition(4, 3, 2, 1, 4), fullness=2, freshness_days=1, decay_rate=0.25, category='肉'),
    'ラム肉': Ingredient(name='ラム肉', price=600, nutrition=create_nutrition(4, 2, 1, 2, 3), fullness=3, freshness_days=2, decay_rate=0.20, category='肉'),
    '鶏レバー': Ingredient(name='鶏レバー', price=150, nutrition=create_nutrition(3, 3, 2, 1, 4), fullness=2, freshness_days=1, decay_rate=0.25, category='肉'),

    # === 魚介類 (15種類) ===
    'サーモン': Ingredient(name='サーモン', price=400, nutrition=create_nutrition(4, 3, 2, 2, 3), fullness=3, freshness_days=2, decay_rate=0.20, category='魚'),
    'マグロ': Ingredient(name='マグロ', price=500, nutrition=create_nutrition(5, 2, 2, 2, 3), fullness=3, freshness_days=1, decay_rate=0.25, category='魚'),
    'サバ': Ingredient(name='サバ', price=250, nutrition=create_nutrition(4, 3, 2, 2, 3), fullness=3, freshness_days=2, decay_rate=0.20, category='魚'),
    'アジ': Ingredient(name='アジ', price=200, nutrition=create_nutrition(3, 2, 2, 2, 3), fullness=2, freshness_days=2, decay_rate=0.20, category='魚'),
    'イワシ': Ingredient(name='イワシ', price=150, nutrition=create_nutrition(3, 3, 2, 2, 4), fullness=2, freshness_days=1, decay_rate=0.25, category='魚'),
    'タラ': Ingredient(name='タラ', price=300, nutrition=create_nutrition(4, 2, 1, 2, 2), fullness=2, freshness_days=2, decay_rate=0.20, category='魚'),
    'エビ': Ingredient(name='エビ', price=450, nutrition=create_nutrition(4, 2, 2, 1, 3), fullness=2, freshness_days=2, decay_rate=0.20, category='魚'),
    'イカ': Ingredient(name='イカ', price=350, nutrition=create_nutrition(3, 2, 2, 2, 2), fullness=2, freshness_days=2, decay_rate=0.20, category='魚'),
    'タコ': Ingredient(name='タコ', price=400, nutrition=create_nutrition(3, 2, 2, 2, 2), fullness=2, freshness_days=2, decay_rate=0.20, category='魚'),
    'ホタテ': Ingredient(name='ホタテ', price=500, nutrition=create_nutrition(4, 2, 2, 1, 3), fullness=2, freshness_days=2, decay_rate=0.20, category='魚'),
    'アサリ': Ingredient(name='アサリ', price=250, nutrition=create_nutrition(2, 3, 1, 1, 4), fullness=1, freshness_days=2, decay_rate=0.20, category='魚'),
    'シジミ': Ingredient(name='シジミ', price=200, nutrition=create_nutrition(2, 4, 1, 1, 4), fullness=1, freshness_days=2, decay_rate=0.20, category='魚'),
    'カキ': Ingredient(name='カキ', price=450, nutrition=create_nutrition(3, 4, 2, 1, 4), fullness=2, freshness_days=2, decay_rate=0.20, category='魚'),
    'ししゃも': Ingredient(name='ししゃも', price=200, nutrition=create_nutrition(3, 2, 2, 2, 3), fullness=2, freshness_days=3, decay_rate=0.18, category='魚'),
    'しらす': Ingredient(name='しらす', price=300, nutrition=create_nutrition(3, 2, 2, 1, 4), fullness=1, freshness_days=3, decay_rate=0.18, category='魚'),

    # === 卵・乳製品 (10種類) ===
    '卵': Ingredient(name='卵', price=100, nutrition=create_nutrition(3, 2, 2, 1, 2), fullness=2, freshness_days=14, decay_rate=0.05, category='卵乳'),
    '牛乳': Ingredient(name='牛乳', price=180, nutrition=create_nutrition(2, 2, 2, 1, 3), fullness=1, freshness_days=7, decay_rate=0.10, category='卵乳'),
    'ヨーグルト': Ingredient(name='ヨーグルト', price=150, nutrition=create_nutrition(2, 2, 2, 1, 3), fullness=1, freshness_days=10, decay_rate=0.08, category='卵乳'),
    'チーズ': Ingredient(name='チーズ', price=300, nutrition=create_nutrition(3, 2, 1, 2, 3), fullness=2, freshness_days=14, decay_rate=0.05, category='卵乳'),
    'バター': Ingredient(name='バター', price=350, nutrition=create_nutrition(1, 1, 1, 2, 1), fullness=1, freshness_days=30, decay_rate=0.02, category='卵乳'),
    '生クリーム': Ingredient(name='生クリーム', price=300, nutrition=create_nutrition(1, 1, 1, 2, 1), fullness=1, freshness_days=5, decay_rate=0.12, category='卵乳'),
    'クリームチーズ': Ingredient(name='クリームチーズ', price=350, nutrition=create_nutrition(2, 1, 1, 2, 2), fullness=2, freshness_days=14, decay_rate=0.05, category='卵乳'),
    'スライスチーズ': Ingredient(name='スライスチーズ', price=250, nutrition=create_nutrition(2, 2, 1, 2, 2), fullness=1, freshness_days=21, decay_rate=0.03, category='卵乳'),
    'モッツァレラ': Ingredient(name='モッツァレラ', price=400, nutrition=create_nutrition(3, 2, 1, 2, 2), fullness=2, freshness_days=7, decay_rate=0.10, category='卵乳'),
    'うずら卵': Ingredient(name='うずら卵', price=150, nutrition=create_nutrition(3, 2, 2, 1, 2), fullness=1, freshness_days=10, decay_rate=0.08, category='卵乳'),

    # === 豆類・大豆製品 (10種類) ===
    '納豆': Ingredient(name='納豆', price=80, nutrition=create_nutrition(2, 3, 2, 2, 3), fullness=1, freshness_days=7, decay_rate=0.10, category='豆'),
    '豆腐': Ingredient(name='豆腐', price=100, nutrition=create_nutrition(2, 2, 1, 1, 2), fullness=2, freshness_days=5, decay_rate=0.12, category='豆'),
    '油揚げ': Ingredient(name='油揚げ', price=80, nutrition=create_nutrition(2, 1, 1, 2, 1), fullness=1, freshness_days=5, decay_rate=0.12, category='豆'),
    '厚揚げ': Ingredient(name='厚揚げ', price=120, nutrition=create_nutrition(2, 2, 1, 2, 2), fullness=2, freshness_days=4, decay_rate=0.15, category='豆'),
    '豆乳': Ingredient(name='豆乳', price=180, nutrition=create_nutrition(2, 2, 1, 1, 2), fullness=1, freshness_days=10, decay_rate=0.08, category='豆'),
    '枝豆': Ingredient(name='枝豆', price=200, nutrition=create_nutrition(3, 2, 2, 2, 2), fullness=1, freshness_days=3, decay_rate=0.18, category='豆'),
    'ひよこ豆': Ingredient(name='ひよこ豆', price=250, nutrition=create_nutrition(2, 2, 1, 3, 2), fullness=2, freshness_days=30, decay_rate=0.02, category='豆'),
    '大豆': Ingredient(name='大豆', price=200, nutrition=create_nutrition(3, 2, 1, 3, 2), fullness=2, freshness_days=30, decay_rate=0.02, category='豆'),
    'がんもどき': Ingredient(name='がんもどき', price=150, nutrition=create_nutrition(2, 2, 1, 2, 2), fullness=2, freshness_days=4, decay_rate=0.15, category='豆'),
    'おから': Ingredient(name='おから', price=80, nutrition=create_nutrition(2, 1, 1, 2, 2), fullness=2, freshness_days=3, decay_rate=0.18, category='豆'),

    # === きのこ類 (5種類) ===
    'しいたけ': Ingredient(name='しいたけ', price=150, nutrition=create_nutrition(1, 2, 1, 1, 3), fullness=1, freshness_days=5, decay_rate=0.12, category='きのこ'),
    'えのき': Ingredient(name='えのき', price=100, nutrition=create_nutrition(1, 1, 1, 1, 2), fullness=1, freshness_days=5, decay_rate=0.12, category='きのこ'),
    'しめじ': Ingredient(name='しめじ', price=120, nutrition=create_nutrition(1, 2, 1, 1, 2), fullness=1, freshness_days=5, decay_rate=0.12, category='きのこ'),
    'まいたけ': Ingredient(name='まいたけ', price=180, nutrition=create_nutrition(1, 2, 1, 1, 3), fullness=1, freshness_days=4, decay_rate=0.15, category='きのこ'),
    'エリンギ': Ingredient(name='エリンギ', price=150, nutrition=create_nutrition(1, 1, 1, 2, 2), fullness=1, freshness_days=7, decay_rate=0.10, category='きのこ'),

    # === 果物 (5種類) ===
    'りんご': Ingredient(name='りんご', price=150, nutrition=create_nutrition(1, 2, 2, 1, 2), fullness=1, freshness_days=14, decay_rate=0.05, category='果物'),
    'バナナ': Ingredient(name='バナナ', price=100, nutrition=create_nutrition(2, 2, 3, 2, 1), fullness=2, freshness_days=5, decay_rate=0.12, category='果物'),
    'みかん': Ingredient(name='みかん', price=120, nutrition=create_nutrition(1, 1, 2, 1, 3), fullness=1, freshness_days=10, decay_rate=0.08, category='果物'),
    'レモン': Ingredient(name='レモン', price=100, nutrition=create_nutrition(1, 1, 2, 1, 4), fullness=0, freshness_days=14, decay_rate=0.05, category='果物'),
    'キウイ': Ingredient(name='キウイ', price=150, nutrition=create_nutrition(1, 2, 2, 1, 3), fullness=1, freshness_days=7, decay_rate=0.10, category='果物'),

    # === 調味料・その他 (10種類) ===
    'にんにく': Ingredient(name='にんにく', price=100, nutrition=create_nutrition(1, 1, 2, 1, 2), fullness=0, freshness_days=21, decay_rate=0.03, category='調味料'),
    'しょうが': Ingredient(name='しょうが', price=100, nutrition=create_nutrition(1, 1, 2, 1, 2), fullness=0, freshness_days=14, decay_rate=0.05, category='調味料'),
    'わかめ': Ingredient(name='わかめ', price=150, nutrition=create_nutrition(1, 2, 1, 1, 4), fullness=0, freshness_days=30, decay_rate=0.02, category='調味料'),
    '昆布': Ingredient(name='昆布', price=200, nutrition=create_nutrition(1, 2, 1, 1, 4), fullness=0, freshness_days=60, decay_rate=0.01, category='調味料'),
    'かつお節': Ingredient(name='かつお節', price=250, nutrition=create_nutrition(2, 2, 1, 1, 2), fullness=0, freshness_days=60, decay_rate=0.01, category='調味料'),
    '梅干し': Ingredient(name='梅干し', price=300, nutrition=create_nutrition(1, 1, 2, 1, 3), fullness=0, freshness_days=90, decay_rate=0.01, category='調味料'),
    'キムチ': Ingredient(name='キムチ', price=250, nutrition=create_nutrition(1, 2, 2, 1, 3), fullness=1, freshness_days=14, decay_rate=0.05, category='調味料'),
    '漬物': Ingredient(name='漬物', price=200, nutrition=create_nutrition(1, 1, 1, 1, 2), fullness=1, freshness_days=14, decay_rate=0.05, category='調味料'),
    'こんにゃく': Ingredient(name='こんにゃく', price=80, nutrition=create_nutrition(0, 0, 0, 1, 1), fullness=2, freshness_days=30, decay_rate=0.02, category='調味料'),
    '春雨': Ingredient(name='春雨', price=150, nutrition=create_nutrition(1, 0, 0, 2, 0), fullness=2, freshness_days=60, decay_rate=0.01, category='調味料'),
}


# 遠くのスーパー限定食材（15種類）
DISTANT_ONLY_INGREDIENTS = {
    # === 輸入品 (6種類) ===
    'オリーブオイル': Ingredient(name='オリーブオイル', price=600, nutrition=create_nutrition(1, 2, 1, 2, 2), fullness=0, freshness_days=90, decay_rate=0.01, category='調味料', distant_only=True),
    'パルメザンチーズ': Ingredient(name='パルメザンチーズ', price=800, nutrition=create_nutrition(4, 2, 1, 3, 3), fullness=1, freshness_days=30, decay_rate=0.02, category='卵乳', distant_only=True),
    '生ハム': Ingredient(name='生ハム', price=700, nutrition=create_nutrition(4, 2, 2, 2, 2), fullness=2, freshness_days=14, decay_rate=0.05, category='肉', distant_only=True),
    'アボカド': Ingredient(name='アボカド', price=250, nutrition=create_nutrition(2, 3, 2, 2, 3), fullness=2, freshness_days=5, decay_rate=0.12, category='野菜', distant_only=True),
    'マンゴー': Ingredient(name='マンゴー', price=400, nutrition=create_nutrition(2, 2, 3, 1, 3), fullness=2, freshness_days=5, decay_rate=0.12, category='果物', distant_only=True),
    'ココナッツミルク': Ingredient(name='ココナッツミルク', price=300, nutrition=create_nutrition(1, 1, 1, 2, 1), fullness=1, freshness_days=30, decay_rate=0.02, category='調味料', distant_only=True),

    # === 産直・高級品 (5種類) ===
    '有機野菜セット': Ingredient(name='有機野菜セット', price=500, nutrition=create_nutrition(2, 3, 2, 2, 5), fullness=2, freshness_days=5, decay_rate=0.12, category='野菜', distant_only=True),
    '地鶏': Ingredient(name='地鶏', price=450, nutrition=create_nutrition(5, 2, 2, 2, 3), fullness=3, freshness_days=2, decay_rate=0.20, category='肉', distant_only=True),
    '天然鯛': Ingredient(name='天然鯛', price=600, nutrition=create_nutrition(5, 3, 2, 2, 4), fullness=3, freshness_days=2, decay_rate=0.20, category='魚', distant_only=True),
    '産直たまご': Ingredient(name='産直たまご', price=350, nutrition=create_nutrition(4, 3, 3, 2, 3), fullness=2, freshness_days=14, decay_rate=0.05, category='卵乳', distant_only=True),
    'ブランド牛': Ingredient(name='ブランド牛', price=1200, nutrition=create_nutrition(6, 3, 2, 3, 4), fullness=4, freshness_days=2, decay_rate=0.20, category='肉', distant_only=True),

    # === エスニック食材 (4種類) ===
    'パクチー': Ingredient(name='パクチー', price=150, nutrition=create_nutrition(1, 2, 2, 1, 3), fullness=0, freshness_days=3, decay_rate=0.18, category='野菜', distant_only=True),
    'レモングラス': Ingredient(name='レモングラス', price=200, nutrition=create_nutrition(1, 2, 2, 1, 2), fullness=0, freshness_days=7, decay_rate=0.10, category='調味料', distant_only=True),
    'ナンプラー': Ingredient(name='ナンプラー', price=350, nutrition=create_nutrition(1, 2, 1, 1, 2), fullness=0, freshness_days=90, decay_rate=0.01, category='調味料', distant_only=True),
    'フォー麺': Ingredient(name='フォー麺', price=250, nutrition=create_nutrition(1, 1, 1, 3, 1), fullness=3, freshness_days=30, decay_rate=0.02, category='穀物', distant_only=True),
}

# 全食材（通常 + 限定）を統合した辞書
ALL_INGREDIENTS = {**INGREDIENTS, **DISTANT_ONLY_INGREDIENTS}


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

    def calculate_freshness_modifier(self, ingredient_name: str, current_day: int,
                                       freshness_extend: int | RelicInventory = 0) -> float:
        """最も古い食材の鮮度補正値を計算（0.1〜1.0）
        Args:
            ingredient_name: 食材名
            current_day: 現在のゲーム日
            freshness_extend: 鮮度延長日数（int）またはRelicInventory
                              RelicInventoryの場合、食材購入日を考慮して適切な延長日数を計算
        """
        oldest_day = self.get_oldest_day(ingredient_name)
        if oldest_day is None:
            return 1.0

        ingredient = get_ingredient(ingredient_name)
        if ingredient is None:
            return 1.0

        # 鮮度延長日数を計算
        if isinstance(freshness_extend, int):
            extend_days = freshness_extend
        else:
            # RelicInventoryの場合、食材購入日を考慮
            extend_days = freshness_extend.get_freshness_extend_for_purchase_day(oldest_day)

        # レリック効果で鮮度維持日数を延長
        effective_freshness_days = ingredient.freshness_days + extend_days

        elapsed_days = current_day - oldest_day
        if elapsed_days <= effective_freshness_days:
            return 1.0  # 鮮度維持期間内

        # 超過日数に応じて減衰
        excess_days = elapsed_days - effective_freshness_days
        modifier = 1.0 - (excess_days * ingredient.decay_rate)
        return max(0.1, modifier)  # 最低10%

    def get_freshness_status(self, ingredient_name: str, current_day: int,
                             freshness_extend: int | RelicInventory = 0) -> str:
        """鮮度ステータス文字列を取得
        Args:
            ingredient_name: 食材名
            current_day: 現在のゲーム日
            freshness_extend: 鮮度延長日数（int）またはRelicInventory
        """
        oldest_day = self.get_oldest_day(ingredient_name)
        if oldest_day is None:
            return ""

        ingredient = get_ingredient(ingredient_name)
        if ingredient is None:
            return ""

        # 鮮度延長日数を計算
        if isinstance(freshness_extend, int):
            extend_days = freshness_extend
        else:
            # RelicInventoryの場合、食材購入日を考慮
            extend_days = freshness_extend.get_freshness_extend_for_purchase_day(oldest_day)

        # レリック効果で鮮度維持日数を延長
        effective_freshness_days = ingredient.freshness_days + extend_days

        elapsed_days = current_day - oldest_day
        remaining = effective_freshness_days - elapsed_days

        if remaining > 0:
            if remaining >= effective_freshness_days:
                return "新鮮"
            return f"残り{remaining}日"
        else:
            modifier = self.calculate_freshness_modifier(ingredient_name, current_day, freshness_extend)
            penalty = int((1.0 - modifier) * 100)
            return f"栄養-{penalty}%"

    def get_items_for_discard(self, current_day: int,
                               freshness_extend: int | RelicInventory = 0) -> list[tuple[str, int, int, float]]:
        """廃棄候補の食材リストを取得（期限切れのみ）
        Args:
            current_day: 現在のゲーム日
            freshness_extend: 鮮度延長日数（int）またはRelicInventory
        Returns: [(食材名, 数量, 経過日数, 鮮度補正値), ...]
        """
        result = []
        for name, days in self._items.items():
            if not days:
                continue
            oldest_day = days[0]
            elapsed = current_day - oldest_day
            modifier = self.calculate_freshness_modifier(name, current_day, freshness_extend)
            # 期限切れ（鮮度が落ちた）もののみ対象
            if modifier < 1.0:
                result.append((name, len(days), elapsed, modifier))
        # 鮮度が低い順（modifier が小さい順）にソート
        result.sort(key=lambda x: x[3])
        return result

    def has_expired_items(self, current_day: int, freshness_extend: int | RelicInventory = 0) -> bool:
        """期限切れ食材があるかチェック"""
        for name in self._items:
            modifier = self.calculate_freshness_modifier(name, current_day, freshness_extend)
            if modifier < 1.0:
                return True
        return False


def get_ingredient(name: str) -> Ingredient | None:
    """食材名から食材データを取得（限定食材含む）"""
    return ALL_INGREDIENTS.get(name)


def get_all_ingredient_names() -> list[str]:
    """全食材名を取得"""
    return list(INGREDIENTS.keys())


def get_shop_items() -> list[tuple[str, int]]:
    """お店で買える食材リストを取得 (名前, 価格)"""
    return [(ing.name, ing.price) for ing in INGREDIENTS.values()]


@dataclass
class ShopItem:
    """店頭に並ぶ商品"""
    ingredient: Ingredient
    price: int  # 実際の販売価格
    discount_type: str  # "none", "sale", "near_expiry"
    freshness_days_left: int  # 購入時の残り鮮度日数（near_expiryの場合は少ない）


def generate_daily_shop_items(seed: int | None = None) -> list[ShopItem]:
    """その日の店頭商品を生成（5種類、カテゴリ固定、1つ2割引、1つ半額で期限近い）

    カテゴリ構成:
    - 穀物: 1（米など主食を確保）
    - 野菜: 1
    - 肉または魚: 1
    - 卵乳または豆: 1
    - その他（きのこ、果物、調味料）: 1
    """
    if seed is not None:
        random.seed(seed)

    # カテゴリ別に食材を分類
    by_category: dict[str, list[Ingredient]] = {}
    for ing in INGREDIENTS.values():
        if ing.category not in by_category:
            by_category[ing.category] = []
        by_category[ing.category].append(ing)

    selected = []

    # 1. 穀物から1つ（米など主食）
    if '穀物' in by_category:
        selected.append(random.choice(by_category['穀物']))

    # 2. 野菜から1つ
    if '野菜' in by_category:
        selected.append(random.choice(by_category['野菜']))

    # 3. 肉か魚から1つ
    meat_fish = by_category.get('肉', []) + by_category.get('魚', [])
    if meat_fish:
        selected.append(random.choice(meat_fish))

    # 4. 卵乳か豆から1つ
    egg_bean = by_category.get('卵乳', []) + by_category.get('豆', [])
    if egg_bean:
        selected.append(random.choice(egg_bean))

    # 5. その他から1つ（きのこ、果物、調味料）
    others = by_category.get('きのこ', []) + by_category.get('果物', []) + by_category.get('調味料', [])
    if others:
        selected.append(random.choice(others))

    # 足りない場合はランダムに追加
    all_ingredients = list(INGREDIENTS.values())
    while len(selected) < 5:
        ing = random.choice(all_ingredients)
        if ing not in selected:
            selected.append(ing)

    # シャッフル
    random.shuffle(selected)

    # 価格設定
    shop_items = []
    discount_idx = random.randint(0, len(selected) - 1)  # 2割引の商品
    near_expiry_idx = (discount_idx + 1 + random.randint(0, len(selected) - 2)) % len(selected)  # 半額商品

    for i, ing in enumerate(selected):
        if i == discount_idx:
            # 2割引
            price = int(ing.price * 0.8)
            shop_items.append(ShopItem(ing, price, "sale", ing.freshness_days))
        elif i == near_expiry_idx:
            # 半額だが期限近い（残り1日）
            price = int(ing.price * 0.5)
            shop_items.append(ShopItem(ing, price, "near_expiry", 1))
        else:
            # 通常価格
            shop_items.append(ShopItem(ing, ing.price, "none", ing.freshness_days))

    return shop_items


def generate_distant_shop_items(seed: int | None = None) -> list[ShopItem]:
    """遠くのスーパーの店頭商品を生成（7種類、限定食材含む、セール多め）

    特徴:
    - 通常食材5種類 + 限定食材2種類
    - セール率が高い（50%の確率でセール）
    - 限定食材は必ず含まれる
    """
    if seed is not None:
        random.seed(seed + 1000)  # 近所と異なるシードを使用

    # カテゴリ別に食材を分類（通常食材のみ）
    by_category: dict[str, list[Ingredient]] = {}
    for ing in INGREDIENTS.values():
        if ing.category not in by_category:
            by_category[ing.category] = []
        by_category[ing.category].append(ing)

    selected = []

    # 1. 穀物から1つ
    if '穀物' in by_category:
        selected.append(random.choice(by_category['穀物']))

    # 2. 野菜から1つ
    if '野菜' in by_category:
        selected.append(random.choice(by_category['野菜']))

    # 3. 肉か魚から1つ
    meat_fish = by_category.get('肉', []) + by_category.get('魚', [])
    if meat_fish:
        selected.append(random.choice(meat_fish))

    # 4. 卵乳か豆から1つ
    egg_bean = by_category.get('卵乳', []) + by_category.get('豆', [])
    if egg_bean:
        selected.append(random.choice(egg_bean))

    # 5. その他から1つ
    others = by_category.get('きのこ', []) + by_category.get('果物', []) + by_category.get('調味料', [])
    if others:
        selected.append(random.choice(others))

    # 6-7. 限定食材から2つ
    distant_list = list(DISTANT_ONLY_INGREDIENTS.values())
    random.shuffle(distant_list)
    selected.extend(distant_list[:2])

    # シャッフル
    random.shuffle(selected)

    # 価格設定（セール率50%）
    shop_items = []
    sale_count = 0
    max_sales = 3  # 最大3つまでセール

    for ing in selected:
        # 50%の確率でセール（最大3つまで）
        is_sale = random.random() < 0.5 and sale_count < max_sales

        if is_sale:
            sale_count += 1
            # 2割引
            price = int(ing.price * 0.8)
            shop_items.append(ShopItem(ing, price, "sale", ing.freshness_days))
        else:
            # 通常価格
            shop_items.append(ShopItem(ing, ing.price, "none", ing.freshness_days))

    return shop_items


def create_initial_stock(start_day: int = 1) -> Stock:
    """初期ストックを作成（新社会人スタート用）"""
    stock = Stock()
    # 親が持たせてくれた食材（ゲーム開始日に購入扱い）
    stock.add('米', 3, start_day)
    stock.add('卵', 2, start_day)
    stock.add('キャベツ', 1, start_day)
    stock.add('納豆', 2, start_day)
    return stock
