"""調理システム（食材→料理変換）"""
from dataclasses import dataclass
from .nutrition import Nutrition, create_nutrition
from .ingredients import get_ingredient, Stock
from .relic import RelicInventory


@dataclass
class Dish:
    """料理データ"""
    name: str
    nutrition: Nutrition
    fullness: int
    ingredients_used: list[str]


# 料理レシピ定義（食材の組み合わせ → 料理名）
RECIPES = {
    frozenset(['米']): 'ごはん',
    frozenset(['米', '卵']): '卵かけごはん',
    frozenset(['米', '野菜', '肉']): '野菜炒め定食',
    frozenset(['卵']): '目玉焼き',
    frozenset(['野菜']): 'サラダ',
    frozenset(['肉']): '焼肉',
    frozenset(['納豆']): '納豆',
    frozenset(['米', '納豆']): '納豆ごはん',
    frozenset(['米', '肉']): '肉丼',
    frozenset(['米', '野菜']): '野菜ごはん',
    frozenset(['卵', '野菜']): '野菜オムレツ',
}


def cook(ingredient_names: list[str], stock: Stock, current_day: int = 1,
         relics: RelicInventory | None = None) -> Dish | None:
    """
    食材から料理を作成する（鮮度補正・レリック効果適用）
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

    # 料理名を決定
    ingredient_set = frozenset(ingredient_names)
    dish_name = RECIPES.get(ingredient_set, 'ミックス料理')

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

    # ストックから消費
    for name in ingredient_names:
        stock.remove(name)

    return Dish(
        name=dish_name,
        nutrition=total_nutrition,
        fullness=total_fullness,
        ingredients_used=ingredient_names.copy()
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
