"""プロンプトテンプレート"""

# 基本スタイル（全カテゴリ共通）
BASE_STYLE = """
32x32 pixel art icon,
retro game style,
single item centered on transparent background,
clean pixel edges,
vibrant colors,
no text or labels,
simple and recognizable design
""".strip().replace("\n", " ")

# カテゴリ別プロンプトテンプレート
CATEGORY_TEMPLATES = {
    "ingredients": {
        "prefix": "A cute pixel art food ingredient icon of",
        "style": f"{BASE_STYLE}, kawaii style, fresh food appearance",
        "subcategory_hints": {
            "穀物": "grain or carbohydrate food",
            "野菜": "fresh vegetable",
            "肉": "raw meat piece",
            "魚": "fresh seafood or fish",
            "卵乳": "dairy or egg product",
            "豆": "bean or legume",
            "きのこ": "mushroom",
            "果物": "fresh fruit",
            "調味料": "seasoning or condiment bottle/container"
        }
    },
    "relics": {
        "prefix": "A pixel art magical item icon of",
        "style": f"{BASE_STYLE}, RPG game item style, slight glow effect, magical cooking tool",
        "subcategory_hints": {
            "調理器具": "cooking utensil or pan",
            "家電": "kitchen appliance",
            "収納": "storage container or shelf",
            "食器": "dish or tableware",
            "衛生": "cleaning or hygiene item",
            "便利グッズ": "useful kitchen gadget",
            "高級品": "premium luxury kitchen item with sparkle",
            "その他": "miscellaneous kitchen item"
        }
    },
    "recipes": {
        "prefix": "A delicious pixel art dish icon of",
        "style": f"{BASE_STYLE}, cooked food on a plate, appetizing appearance, steam effect if hot dish",
        "subcategory_hints": {}
    },
    "provisions": {
        "prefix": "A pixel art convenience food icon of",
        "style": f"{BASE_STYLE}, packaged food item, convenience store style",
        "subcategory_hints": {}
    }
}

# 特定アイテムの追加ヒント（必要に応じて）
ITEM_SPECIFIC_HINTS = {
    # 食材
    "米": "white rice grains in a small pile",
    "パン": "a loaf of bread",
    "カップ麺": "instant noodle cup with lid",
    "エナジードリンク": "energy drink can with lightning bolt design",
    "缶コーヒー": "canned coffee drink",
    # レリック
    "冷蔵庫": "small refrigerator with door",
    "電子レンジ": "microwave oven",
    "炊飯器": "rice cooker",
    # 料理
    "カレーライス": "Japanese curry rice on plate",
    "親子丼": "chicken and egg rice bowl",
    "TKG（卵かけごはん）": "raw egg on rice bowl",
}


def build_prompt(item_name: str, category: str, subcategory: str = "") -> str:
    """アイテム用のプロンプトを構築"""
    if category not in CATEGORY_TEMPLATES:
        raise ValueError(f"Unknown category: {category}")

    template = CATEGORY_TEMPLATES[category]
    prefix = template["prefix"]
    style = template["style"]

    # サブカテゴリヒント
    subcategory_hint = ""
    if subcategory and subcategory in template.get("subcategory_hints", {}):
        subcategory_hint = f"({template['subcategory_hints'][subcategory]})"

    # アイテム固有ヒント
    item_hint = ITEM_SPECIFIC_HINTS.get(item_name, "")

    # プロンプト組み立て
    if item_hint:
        prompt = f"{prefix} {item_name} ({item_hint}). {style}"
    elif subcategory_hint:
        prompt = f"{prefix} {item_name} {subcategory_hint}. {style}"
    else:
        prompt = f"{prefix} {item_name}. {style}"

    return prompt


def get_prompt_preview(item_name: str, category: str, subcategory: str = "") -> str:
    """プロンプトのプレビュー（デバッグ用）"""
    prompt = build_prompt(item_name, category, subcategory)
    return f"[{category}/{item_name}]\n{prompt}\n"


if __name__ == "__main__":
    # テスト: 各カテゴリのサンプルプロンプトを表示
    test_items = [
        ("米", "ingredients", "穀物"),
        ("キャベツ", "ingredients", "野菜"),
        ("鶏むね肉", "ingredients", "肉"),
        ("フライパン", "relics", "調理器具"),
        ("冷蔵庫", "relics", "家電"),
        ("カレーライス", "recipes", "料理"),
        ("親子丼", "recipes", "料理"),
        ("カップ麺", "provisions", "食糧"),
        ("エナジードリンク", "provisions", "食糧"),
    ]

    print("=== プロンプトサンプル ===\n")
    for name, cat, subcat in test_items:
        print(get_prompt_preview(name, cat, subcat))
