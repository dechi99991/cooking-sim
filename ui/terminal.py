"""ターミナルUI"""
from game.player import Player
from game.nutrition import Nutrition
from game.ingredients import Stock, get_ingredient, get_shop_items
from game.cooking import Dish, get_recipe_suggestions
from game.day_cycle import GameManager, GamePhase
from game.constants import (
    MAX_ENERGY, MAX_STAMINA, MAX_FULLNESS, CAFETERIA_PRICE,
    SHOPPING_ENERGY_COST, SHOPPING_STAMINA_COST
)


def clear_screen():
    """画面クリア"""
    print("\n" + "=" * 50 + "\n")


def show_status(player: Player, day_state):
    """ステータス表示"""
    print(f"【{day_state.get_date_string()}】")
    print(f"所持金: {player.money:,}円")
    print(f"気力: {player.energy}/{MAX_ENERGY}  体力: {player.stamina}/{MAX_STAMINA}  満腹感: {player.fullness}/{MAX_FULLNESS}")

    # ペナルティ表示
    penalties = []
    if player.energy_recovery_penalty > 0:
        penalties.append(f"気力回復-{player.energy_recovery_penalty}")
    if player.stamina_recovery_penalty > 0:
        penalties.append(f"体力回復-{player.stamina_recovery_penalty}")
    if player.fullness_decay_penalty > 0:
        penalties.append(f"満腹感減少+{player.fullness_decay_penalty}")
    if penalties:
        print(f"[ペナルティ: {', '.join(penalties)}]")
    print()


def show_nutrition(nutrition: Nutrition):
    """栄養状態表示"""
    status = nutrition.get_status()
    print("【本日の栄養摂取】")
    for name, data in status.items():
        mark = "○" if data['ok'] else "×"
        print(f"  {name}: {data['value']} {mark}")
    print()


def show_stock(stock: Stock):
    """ストック表示"""
    items = stock.get_all()
    if items:
        print("【食材ストック】")
        for name, qty in items.items():
            ingredient = get_ingredient(name)
            if ingredient:
                print(f"  {name}: {qty}個")
        print()
    else:
        print("【食材ストック】空\n")


def show_recipe_suggestions(stock: Stock):
    """作れる料理の候補を表示"""
    available = stock.get_available_ingredients()
    suggestions = get_recipe_suggestions(available)
    if suggestions:
        print("【作れる料理】")
        for dish_name, ingredients in suggestions:
            print(f"  {dish_name} ({', '.join(ingredients)})")
        print()


def get_input(prompt: str, valid_options: list[str]) -> str:
    """ユーザー入力を取得"""
    while True:
        choice = input(prompt).strip()
        if choice in valid_options:
            return choice
        print(f"無効な入力です。{valid_options}から選んでください。")


def get_number_input(prompt: str, min_val: int, max_val: int) -> int:
    """数値入力を取得"""
    while True:
        try:
            num = int(input(prompt).strip())
            if min_val <= num <= max_val:
                return num
            print(f"{min_val}から{max_val}の間で入力してください。")
        except ValueError:
            print("数値を入力してください。")


def select_ingredients(stock: Stock) -> list[str]:
    """食材選択UI"""
    available = stock.get_available_ingredients()
    if not available:
        print("食材がありません。")
        return []

    print("使う食材を選んでください（複数選択可、カンマ区切り）:")
    for i, name in enumerate(available, 1):
        qty = stock.get_quantity(name)
        print(f"  {i}. {name} (残り{qty}個)")
    print("  0. キャンセル")

    while True:
        choice = input("番号を入力: ").strip()
        if choice == "0":
            return []

        try:
            indices = [int(x.strip()) for x in choice.split(",")]
            selected = []
            valid = True
            for idx in indices:
                if 1 <= idx <= len(available):
                    selected.append(available[idx - 1])
                else:
                    valid = False
                    break
            if valid and selected:
                return selected
        except ValueError:
            pass

        print("無効な入力です。番号をカンマ区切りで入力してください。")


def show_dish(dish: Dish):
    """料理情報を表示"""
    print(f"【{dish.name}】を作りました！")
    print(f"  満腹度: +{dish.fullness}")
    n = dish.nutrition
    print(f"  栄養: 活力{n.vitality} 心力{n.mental} 覚醒{n.awakening} 持続{n.sustain} 防衛{n.defense}")


def show_phase_header(phase: GamePhase, day_state):
    """フェーズヘッダー表示"""
    phase_names = {
        GamePhase.BREAKFAST: "朝食",
        GamePhase.GO_TO_WORK: "出勤",
        GamePhase.LUNCH: "昼食",
        GamePhase.LEAVE_WORK: "退勤",
        GamePhase.SHOPPING: "買い出し",
        GamePhase.HOLIDAY_SHOPPING_1: "買い出し",
        GamePhase.HOLIDAY_LUNCH: "昼食",
        GamePhase.HOLIDAY_SHOPPING_2: "買い出し",
        GamePhase.DINNER: "夕食",
        GamePhase.SLEEP: "就寝",
    }
    name = phase_names.get(phase, "")
    holiday_mark = "【休日】" if day_state.is_holiday() else ""
    print(f"\n{'─' * 20} {holiday_mark}{name} {'─' * 20}\n")


def show_breakfast_menu(game: GameManager) -> str:
    """朝食メニュー表示"""
    print("朝食の選択:")
    options = []

    if game.can_cook():
        print("  1. 自炊する")
        options.append("1")
    else:
        print("  1. 自炊する (気力または食材不足)")

    if game.can_make_bento():
        print("  2. 自炊して弁当も作る")
        options.append("2")
    else:
        print("  2. 自炊して弁当も作る (気力または食材不足)")

    print("  3. 食べない")
    options.append("3")

    return get_input("選択: ", options)


def show_lunch_menu(game: GameManager) -> str:
    """昼食メニュー表示（平日）"""
    print("昼食の選択:")
    options = []

    if game.day_state.has_bento:
        print("  1. 弁当を食べる")
        options.append("1")
    else:
        print("  1. 弁当を食べる (弁当がありません)")

    if game.can_use_cafeteria():
        print(f"  2. 社食 ({CAFETERIA_PRICE}円)")
        options.append("2")
    else:
        print(f"  2. 社食 (お金が足りません)")

    print("  3. 食べない")
    options.append("3")

    return get_input("選択: ", options)


def show_holiday_breakfast_menu(game: GameManager) -> str:
    """休日朝食メニュー表示（弁当作成なし）"""
    print("朝食の選択:")
    options = []

    if game.can_cook():
        print("  1. 自炊する")
        options.append("1")
    else:
        print("  1. 自炊する (気力または食材不足)")

    print("  2. 食べない")
    options.append("2")

    return get_input("選択: ", options)


def show_holiday_lunch_menu(game: GameManager) -> str:
    """休日昼食メニュー表示（自炊可能）"""
    print("昼食の選択:")
    options = []

    if game.can_cook():
        print("  1. 自炊する")
        options.append("1")
    else:
        print("  1. 自炊する (気力または食材不足)")

    print("  2. 食べない")
    options.append("2")

    return get_input("選択: ", options)


def show_dinner_menu(game: GameManager) -> str:
    """夕食メニュー表示"""
    print("夕食の選択:")
    options = []

    if game.can_cook():
        print("  1. 自炊する")
        options.append("1")
    else:
        print("  1. 自炊する (気力または食材不足)")

    print("  2. 食べない")
    options.append("2")

    return get_input("選択: ", options)


def show_shopping_menu(game: GameManager) -> str:
    """買い出しメニュー表示"""
    print(f"買い出しに行きますか？ (気力-{SHOPPING_ENERGY_COST}, 体力-{SHOPPING_STAMINA_COST})")
    options = []

    if game.can_go_shopping():
        print("  1. 買い出しに行く")
        options.append("1")
    else:
        print("  1. 買い出しに行く (気力不足)")

    print("  2. まっすぐ帰宅")
    options.append("2")

    return get_input("選択: ", options)


def show_shop(player: Player) -> list[tuple[str, int]]:
    """お店の商品表示と購入UI"""
    items = get_shop_items()
    purchases = []

    print("【スーパーマーケット】")
    print(f"所持金: {player.money:,}円")
    print()
    print("購入する食材を選んでください:")
    for i, (name, price) in enumerate(items, 1):
        print(f"  {i}. {name} ({price}円)")
    print("  0. 購入完了")
    print()

    remaining_money = player.money
    while True:
        print(f"残り所持金: {remaining_money:,}円")
        choice = input("番号を入力 (0で終了): ").strip()

        if choice == "0":
            break

        try:
            idx = int(choice)
            if 1 <= idx <= len(items):
                name, price = items[idx - 1]
                if remaining_money >= price:
                    qty = input(f"{name}を何個買いますか？ (1-10): ").strip()
                    try:
                        qty_num = int(qty)
                        if 1 <= qty_num <= 10:
                            total_price = price * qty_num
                            if remaining_money >= total_price:
                                purchases.append((name, qty_num))
                                remaining_money -= total_price
                                print(f"{name}を{qty_num}個購入しました！ (-{total_price}円)")
                            else:
                                print("お金が足りません。")
                        else:
                            print("1から10の間で入力してください。")
                    except ValueError:
                        print("数値を入力してください。")
                else:
                    print("お金が足りません。")
            else:
                print("無効な番号です。")
        except ValueError:
            print("数値を入力してください。")

    return purchases


def show_game_over():
    """ゲームオーバー表示"""
    print("\n" + "=" * 50)
    print("       ゲームオーバー")
    print("=" * 50)
    print("体力またはお金が尽きてしまいました...")
    print("一人暮らしは大変ですね。")


def show_game_clear(player: Player, day_state):
    """ゲームクリア表示"""
    print("\n" + "=" * 50)
    print("       ゲームクリア！")
    print("=" * 50)
    print(f"1ヶ月間を生き延びました！")
    print(f"最終所持金: {player.money:,}円")
    print("素晴らしい自炊生活でした！")


def show_title():
    """タイトル表示"""
    print("=" * 50)
    print("    一人暮らし自炊シミュレーション")
    print("=" * 50)
    print()
    print("新社会人として一人暮らしを始めます。")
    print("1ヶ月間、食事をしながら生き延びましょう。")
    print()
    print("・体力が0になるとゲームオーバー")
    print("・所持金が0になるとゲームオーバー")
    print("・栄養バランスが偏ると翌日ペナルティ")
    print()
    input("Enterキーでスタート...")


def show_game_result(result):
    """ゲーム結果の詳細を表示"""
    print("\n" + "─" * 50)
    print("         プレイ統計")
    print("─" * 50)

    print(f"\n【生存日数】 {result.survived_days}日")

    print(f"\n【最終ステータス】")
    print(f"  所持金: {result.final_money:,}円")
    print(f"  気力: {result.final_energy}")
    print(f"  体力: {result.final_stamina}")

    print(f"\n【食事】")
    print(f"  食べた回数: {result.total_meals_eaten}")
    print(f"  抜いた回数: {result.total_meals_skipped}")
    print(f"  自炊回数: {result.total_meals_cooked}")
    print(f"  社食利用: {result.total_cafeteria_used}")
    print(f"  弁当作成: {result.total_bento_made}")

    print(f"\n【買い出し】")
    print(f"  買い出し回数: {result.total_shopping_trips}")
    print(f"  購入アイテム数: {result.total_items_bought}")
    print(f"  買い出し総額: {result.total_money_spent_shopping:,}円")

    print(f"\n【栄養バランス】")
    print(f"  バランス良い日: {result.days_with_balanced_nutrition}日")
    penalty_count = sum(result.nutrition_penalties.values())
    if penalty_count > 0:
        print(f"  ペナルティ発生:")
        for nutrient, count in result.nutrition_penalties.items():
            if count > 0:
                print(f"    {nutrient}: {count}回")

    print("─" * 50)
