"""既存データファイルからアイテム情報を抽出"""
import sys
from pathlib import Path
from dataclasses import dataclass

# プロジェクトルートをパスに追加
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from game.ingredients import INGREDIENTS
from game.relic import RELICS
from game.cooking import NAMED_RECIPES
from game.provisions import PROVISIONS


@dataclass
class ItemInfo:
    """抽出したアイテム情報"""
    name: str
    category: str
    subcategory: str = ""  # 食材のカテゴリ（穀物、野菜など）
    description: str = ""


def extract_ingredients() -> list[ItemInfo]:
    """食材データを抽出"""
    items = []
    for name, ingredient in INGREDIENTS.items():
        items.append(ItemInfo(
            name=name,
            category="ingredients",
            subcategory=ingredient.category,
            description=f"{ingredient.category}の食材"
        ))
    return items


def extract_relics() -> list[ItemInfo]:
    """レリックデータを抽出"""
    items = []
    for name, relic in RELICS.items():
        items.append(ItemInfo(
            name=name,
            category="relics",
            subcategory=relic.category,
            description=relic.description
        ))
    return items


def extract_recipes() -> list[ItemInfo]:
    """ネームド料理を抽出"""
    items = []
    for recipe in NAMED_RECIPES:
        ingredients_str = "、".join(sorted(recipe.ingredients))
        items.append(ItemInfo(
            name=recipe.name,
            category="recipes",
            subcategory="料理",
            description=f"{recipe.description}（{ingredients_str}）"
        ))
    return items


def extract_provisions() -> list[ItemInfo]:
    """食糧データを抽出"""
    items = []
    for name, provision in PROVISIONS.items():
        caffeine_note = "（カフェイン入り）" if provision.caffeine > 0 else ""
        items.append(ItemInfo(
            name=name,
            category="provisions",
            subcategory="食糧",
            description=f"調理不要食品{caffeine_note}"
        ))
    return items


def extract_all_items() -> dict[str, list[ItemInfo]]:
    """全アイテム情報を抽出"""
    return {
        "ingredients": extract_ingredients(),
        "relics": extract_relics(),
        "recipes": extract_recipes(),
        "provisions": extract_provisions()
    }


def get_item_names_by_category(category: str) -> list[str]:
    """カテゴリごとのアイテム名リストを取得"""
    extractors = {
        "ingredients": extract_ingredients,
        "relics": extract_relics,
        "recipes": extract_recipes,
        "provisions": extract_provisions
    }
    if category not in extractors:
        raise ValueError(f"Unknown category: {category}")
    return [item.name for item in extractors[category]()]


def get_all_item_count() -> dict[str, int]:
    """カテゴリごとのアイテム数を取得"""
    all_items = extract_all_items()
    return {category: len(items) for category, items in all_items.items()}


if __name__ == "__main__":
    # テスト実行
    counts = get_all_item_count()
    total = sum(counts.values())
    print(f"=== アイテム数統計 ===")
    for category, count in counts.items():
        print(f"  {category}: {count}")
    print(f"  合計: {total}")

    print(f"\n=== サンプル（各カテゴリ3件）===")
    all_items = extract_all_items()
    for category, items in all_items.items():
        print(f"\n[{category}]")
        for item in items[:3]:
            print(f"  - {item.name}: {item.description}")
