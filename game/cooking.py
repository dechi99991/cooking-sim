"""調理システム（食材→料理変換）"""
from dataclasses import dataclass, field
from .nutrition import Nutrition, create_nutrition
from .ingredients import get_ingredient, Stock, INGREDIENTS
from .relic import RelicInventory


@dataclass
class Dish:
    """料理データ"""
    name: str
    nutrition: Nutrition
    fullness: int
    ingredients_used: list[str]
    is_named: bool = False  # ネームド料理かどうか
    bonus_info: str = ""  # ボーナス情報（表示用）


@dataclass
class NamedRecipe:
    """ネームド料理レシピ"""
    name: str
    ingredients: frozenset[str]  # 必要な食材名（完全一致）
    nutrition_multiplier: float = 1.0  # 栄養倍率
    fullness_bonus: int = 0  # 満腹度ボーナス
    description: str = ""  # 説明


# ネームド料理レシピ（ボーナス付き）
NAMED_RECIPES: list[NamedRecipe] = [
    # === 定番料理 ===
    NamedRecipe(
        name='カレーライス',
        ingredients=frozenset(['米', 'じゃがいも', 'にんじん', 'たまねぎ']),
        nutrition_multiplier=1.3, fullness_bonus=2,
        description='定番の家庭料理'
    ),
    NamedRecipe(
        name='肉じゃが',
        ingredients=frozenset(['じゃがいも', 'にんじん', 'たまねぎ', '豚バラ肉']),
        nutrition_multiplier=1.3, fullness_bonus=2,
        description='ほっこり和食の定番'
    ),
    NamedRecipe(
        name='親子丼',
        ingredients=frozenset(['米', '鶏もも肉', '卵', 'たまねぎ']),
        nutrition_multiplier=1.4, fullness_bonus=2,
        description='鶏肉と卵の絶妙なハーモニー'
    ),
    NamedRecipe(
        name='豚キムチ',
        ingredients=frozenset(['豚バラ肉', 'キムチ']),
        nutrition_multiplier=1.2, fullness_bonus=1,
        description='ピリ辛でご飯が進む'
    ),
    NamedRecipe(
        name='麻婆豆腐',
        ingredients=frozenset(['豆腐', 'ひき肉', 'ねぎ']),
        nutrition_multiplier=1.3, fullness_bonus=1,
        description='ご飯のお供に最高'
    ),
    # === 朝食系 ===
    NamedRecipe(
        name='TKG（卵かけごはん）',
        ingredients=frozenset(['米', '卵']),
        nutrition_multiplier=1.2, fullness_bonus=1,
        description='シンプルイズベスト'
    ),
    NamedRecipe(
        name='納豆ごはん',
        ingredients=frozenset(['米', '納豆']),
        nutrition_multiplier=1.2, fullness_bonus=1,
        description='朝の定番'
    ),
    NamedRecipe(
        name='目玉焼き定食',
        ingredients=frozenset(['米', '卵', 'ベーコン']),
        nutrition_multiplier=1.3, fullness_bonus=1,
        description='朝食の王道'
    ),
    # === 麺類 ===
    NamedRecipe(
        name='ナポリタン',
        ingredients=frozenset(['パスタ', 'ソーセージ', 'ピーマン', 'たまねぎ']),
        nutrition_multiplier=1.3, fullness_bonus=2,
        description='懐かしの洋食'
    ),
    NamedRecipe(
        name='焼きうどん',
        ingredients=frozenset(['うどん', 'キャベツ', '豚バラ肉']),
        nutrition_multiplier=1.2, fullness_bonus=2,
        description='手軽で満足'
    ),
    NamedRecipe(
        name='カルボナーラ',
        ingredients=frozenset(['パスタ', 'ベーコン', '卵', 'チーズ']),
        nutrition_multiplier=1.4, fullness_bonus=2,
        description='濃厚クリーミー'
    ),
    # === サラダ・副菜 ===
    NamedRecipe(
        name='豚しゃぶサラダ',
        ingredients=frozenset(['豚ロース', 'レタス', 'トマト']),
        nutrition_multiplier=1.3, fullness_bonus=1,
        description='さっぱりヘルシー'
    ),
    NamedRecipe(
        name='ほうれん草のおひたし',
        ingredients=frozenset(['ほうれん草', 'かつお節']),
        nutrition_multiplier=1.2, fullness_bonus=0,
        description='和の副菜'
    ),
    # === 魚料理 ===
    NamedRecipe(
        name='サーモン丼',
        ingredients=frozenset(['米', 'サーモン']),
        nutrition_multiplier=1.3, fullness_bonus=1,
        description='脂ののった海鮮丼'
    ),
    NamedRecipe(
        name='アジフライ定食',
        ingredients=frozenset(['米', 'アジ', 'キャベツ']),
        nutrition_multiplier=1.3, fullness_bonus=2,
        description='サクサクの揚げ物'
    ),
    # === 鍋・煮込み ===
    NamedRecipe(
        name='豚汁',
        ingredients=frozenset(['豚バラ肉', 'だいこん', 'にんじん', '豆腐']),
        nutrition_multiplier=1.4, fullness_bonus=2,
        description='具だくさんで栄養満点'
    ),
    NamedRecipe(
        name='味噌汁',
        ingredients=frozenset(['豆腐', 'わかめ', 'ねぎ']),
        nutrition_multiplier=1.2, fullness_bonus=1,
        description='和食の基本'
    ),
]


def find_named_recipe(ingredient_names: list[str]) -> NamedRecipe | None:
    """食材リストからマッチするネームド料理を探す"""
    ingredient_set = frozenset(ingredient_names)
    for recipe in NAMED_RECIPES:
        if recipe.ingredients == ingredient_set:
            return recipe
    return None


def get_available_named_recipes(available_ingredients: list[str]) -> list[NamedRecipe]:
    """利用可能な食材から作れるネームド料理のリストを返す"""
    available_set = set(available_ingredients)
    result = []
    for recipe in NAMED_RECIPES:
        if recipe.ingredients.issubset(available_set):
            result.append(recipe)
    return result


# 旧レシピ定義（後方互換用、ネームドでないときの名前決定に使用）
SIMPLE_RECIPES = {
    frozenset(['米']): 'ごはん',
    frozenset(['卵']): '目玉焼き',
    frozenset(['納豆']): '納豆',
}


def cook(ingredient_names: list[str], stock: Stock, current_day: int = 1,
         relics: RelicInventory | None = None) -> Dish | None:
    """
    食材から料理を作成する（鮮度補正・レリック効果・ネームド料理ボーナス適用）
    Args:
        ingredient_names: 使用する食材名のリスト
        stock: 食材ストック
        current_day: 現在のゲーム日（鮮度計算用）
        relics: レリックインベントリ（効果適用用）
    Returns:
        作成された料理、または失敗時はNone
    """
    if not ingredient_names:
        return None

    # ストックから食材を確認
    for name in ingredient_names:
        if not stock.has(name):
            return None

    # ネームド料理をチェック
    named_recipe = find_named_recipe(ingredient_names)
    is_named = named_recipe is not None

    # 料理名を決定
    ingredient_set = frozenset(ingredient_names)
    if named_recipe:
        dish_name = named_recipe.name
    else:
        dish_name = SIMPLE_RECIPES.get(ingredient_set, 'ミックス料理')

    # 各食材の鮮度補正値を先に計算（消費前に、レリック効果適用）
    # RelicInventoryを渡して食材購入日を考慮した鮮度延長を計算
    freshness_arg = relics if relics else 0
    freshness_modifiers = {}
    for name in ingredient_names:
        freshness_modifiers[name] = stock.calculate_freshness_modifier(name, current_day, freshness_arg)

    # 栄養値と満腹度を計算（食材の合算、鮮度補正・レリック効果適用）
    total_nutrition = Nutrition()
    total_fullness = 0

    for name in ingredient_names:
        ingredient = get_ingredient(name)
        if ingredient:
            modifier = freshness_modifiers[name]
            # 栄養値に鮮度補正を適用
            modified_nutrition = ingredient.nutrition.apply_modifier(modifier)

            # レリックによる栄養ブースト（加算）
            if relics:
                nutrition_boost = relics.get_nutrition_boost(name)
                if nutrition_boost > 0:
                    boost_nutrition = ingredient.nutrition.apply_modifier(nutrition_boost)
                    modified_nutrition.add(boost_nutrition)

            total_nutrition.add(modified_nutrition)

            # 満腹度（レリック効果で加算あり）
            fullness = ingredient.fullness
            if relics:
                fullness += relics.get_fullness_boost(name)
            total_fullness += fullness

    # ネームド料理ボーナスを適用
    bonus_info = ""
    if named_recipe:
        # 栄養倍率を適用
        if named_recipe.nutrition_multiplier != 1.0:
            total_nutrition = total_nutrition.apply_modifier(named_recipe.nutrition_multiplier)
        # 満腹度ボーナスを適用
        total_fullness += named_recipe.fullness_bonus
        # ボーナス情報を作成
        bonus_parts = []
        if named_recipe.nutrition_multiplier > 1.0:
            bonus_parts.append(f"栄養{int(named_recipe.nutrition_multiplier * 100)}%")
        if named_recipe.fullness_bonus > 0:
            bonus_parts.append(f"満腹+{named_recipe.fullness_bonus}")
        bonus_info = " ".join(bonus_parts)

    # ストックから消費
    for name in ingredient_names:
        stock.remove(name)

    return Dish(
        name=dish_name,
        nutrition=total_nutrition,
        fullness=total_fullness,
        ingredients_used=ingredient_names.copy(),
        is_named=is_named,
        bonus_info=bonus_info
    )


def get_recipe_suggestions(available_ingredients: list[str]) -> list[tuple[str, list[str]]]:
    """
    利用可能な食材から作れる料理の候補を返す
    Returns: [(料理名, [必要な食材リスト]), ...]
    """
    available_set = set(available_ingredients)
    suggestions = []

    for ingredients_frozenset, dish_name in RECIPES.items():
        if ingredients_frozenset.issubset(available_set):
            suggestions.append((dish_name, list(ingredients_frozenset)))

    return suggestions


@dataclass
class CookingEvaluation:
    """調理評価結果"""
    total_fullness: int
    total_nutrition: Nutrition
    is_named: bool
    named_recipe_name: str | None
    # 評価
    fullness_good: bool  # 満腹度が十分か
    nutrition_good: bool  # 栄養バランスが良いか


def evaluate_cooking(ingredient_names: list[str]) -> CookingEvaluation:
    """
    選択した食材の調理結果を事前評価する（確認用）
    """
    from .constants import NUTRITION_MIN_THRESHOLD

    if not ingredient_names:
        return CookingEvaluation(
            total_fullness=0,
            total_nutrition=Nutrition(),
            is_named=False,
            named_recipe_name=None,
            fullness_good=False,
            nutrition_good=False
        )

    # ネームド料理をチェック
    named_recipe = find_named_recipe(ingredient_names)
    is_named = named_recipe is not None

    # 栄養値と満腹度を計算（鮮度補正なし、ベース値で評価）
    total_nutrition = Nutrition()
    total_fullness = 0

    for name in ingredient_names:
        ingredient = get_ingredient(name)
        if ingredient:
            total_nutrition.add(ingredient.nutrition)
            total_fullness += ingredient.fullness

    # ネームド料理ボーナスを適用
    if named_recipe:
        if named_recipe.nutrition_multiplier != 1.0:
            total_nutrition = total_nutrition.apply_modifier(named_recipe.nutrition_multiplier)
        total_fullness += named_recipe.fullness_bonus

    # 評価: 満腹度が5以上なら良い
    fullness_good = total_fullness >= 5

    # 評価: 主要な栄養素のうち2つ以上が閾値以上なら良い
    nutrients = [
        total_nutrition.vitality,
        total_nutrition.mental,
        total_nutrition.sustain
    ]
    nutrition_good = sum(1 for n in nutrients if n >= NUTRITION_MIN_THRESHOLD) >= 2

    return CookingEvaluation(
        total_fullness=total_fullness,
        total_nutrition=total_nutrition,
        is_named=is_named,
        named_recipe_name=named_recipe.name if named_recipe else None,
        fullness_good=fullness_good,
        nutrition_good=nutrition_good
    )


def create_cafeteria_dish() -> Dish:
    """社食の料理を作成"""
    from .constants import CAFETERIA_NUTRITION, CAFETERIA_FULLNESS

    return Dish(
        name='社食定食',
        nutrition=create_nutrition(
            vitality=CAFETERIA_NUTRITION,
            mental=CAFETERIA_NUTRITION,
            awakening=CAFETERIA_NUTRITION,
            sustain=CAFETERIA_NUTRITION,
            defense=CAFETERIA_NUTRITION
        ),
        fullness=CAFETERIA_FULLNESS,
        ingredients_used=[]
    )
