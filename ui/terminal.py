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
from game.provisions import get_provision


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


def show_stock(stock: Stock, current_day: int = 1, freshness_extend: int = 0):
    """ストック表示（鮮度情報付き）"""
    items = stock.get_all()
    if items:
        print("【食材ストック】")
        for name, qty in items.items():
            ingredient = get_ingredient(name)
            if ingredient:
                freshness = stock.get_freshness_status(name, current_day, freshness_extend)
                print(f"  {name}: {qty}個 ({freshness})")
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


def show_provision_stock(provisions, current_day: int = 0):
    """食糧ストック表示（通販食品 + 弁当など）"""
    items = provisions.get_all()
    prepared = provisions.get_prepared(current_day) if current_day > 0 else []

    if items or prepared:
        print("【食糧ストック】")
        # 弁当など調理済み
        for dish in prepared:
            expiry_info = "今日まで" if dish.expiry_day == current_day else f"{dish.expiry_day}日まで"
            print(f"  {dish.dish_type}: {dish.name} (満腹{dish.fullness}, {expiry_info})")
        # 通販食品
        for name, qty in items.items():
            prov = get_provision(name)
            if prov:
                caffeine_info = f", ☕気力+{prov.caffeine * 2}" if prov.caffeine > 0 else ""
                print(f"  {name}: {qty}個 (満腹{prov.fullness}{caffeine_info})")
        print()
    else:
        print("【食糧ストック】空\n")


def select_provision(provisions, current_day: int = 0) -> tuple[str, str | int] | None:
    """食糧選択UI（通販食品 + 弁当など）
    Returns: ("provision", 食糧名) or ("prepared", インデックス) or None
    """
    available = provisions.get_available()
    prepared = provisions.get_prepared(current_day) if current_day > 0 else []

    if not available and not prepared:
        print("食糧がありません。")
        return None

    print("食べる食糧を選んでください:")
    option_map = {}  # 番号 -> ("provision", name) or ("prepared", index)
    num = 1

    # 弁当など調理済み
    for i, dish in enumerate(prepared):
        expiry_info = "今日まで" if dish.expiry_day == current_day else f"{dish.expiry_day}日まで"
        print(f"  {num}. {dish.dish_type}: {dish.name} (満腹{dish.fullness}, {expiry_info})")
        option_map[num] = ("prepared", i)
        num += 1

    # 通販食品
    for name in available:
        qty = provisions.get_quantity(name)
        prov = get_provision(name)
        if prov:
            caffeine_info = f", ☕{prov.caffeine}→気力+{prov.caffeine * 2}" if prov.caffeine > 0 else ""
            print(f"  {num}. {name} (残り{qty}個, 満腹{prov.fullness}{caffeine_info})")
            option_map[num] = ("provision", name)
            num += 1
    print("  0. キャンセル")

    while True:
        choice = input("番号を入力: ").strip()
        if choice == "0":
            return None

        try:
            idx = int(choice)
            if idx in option_map:
                return option_map[idx]
            print("無効な番号です。")
        except ValueError:
            print("数値を入力してください。")


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


def select_ingredients(stock: Stock, current_day: int = 1, freshness_extend: int = 0) -> list[str]:
    """食材選択UI（鮮度情報付き）"""
    available = stock.get_available_ingredients()
    if not available:
        print("食材がありません。")
        return []

    print("使う食材を選んでください（複数選択可、カンマ区切り）:")
    for i, name in enumerate(available, 1):
        qty = stock.get_quantity(name)
        freshness = stock.get_freshness_status(name, current_day, freshness_extend)
        print(f"  {i}. {name} (残り{qty}個, {freshness})")
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
        GamePhase.ONLINE_SHOPPING: "通販",
        GamePhase.SLEEP: "就寝",
    }
    name = phase_names.get(phase, "")
    holiday_mark = "【休日】" if day_state.is_holiday() else ""
    print(f"\n{'─' * 20} {holiday_mark}{name} {'─' * 20}\n")


def show_day_start(day_state, weather_display: str):
    """1日の開始表示（起床時）"""
    print(f"\n{'=' * 50}")
    print(f"    {day_state.get_date_string()}  {weather_display}")
    print(f"{'=' * 50}\n")


def show_event(event_name: str, message: str):
    """イベント発生表示"""
    print(f"\n┌{'─' * 40}┐")
    print(f"│ 📢 {event_name}")
    print(f"├{'─' * 40}┤")
    for line in message.split('\n'):
        print(f"│ {line}")
    print(f"└{'─' * 40}┘\n")


def show_events(events: list):
    """複数イベント表示
    Args:
        events: EventResultのリスト
    """
    for result in events:
        show_event(result.event.name, result.message)


def show_breakfast_menu(game: GameManager) -> str:
    """朝食メニュー表示"""
    print("朝食の選択:")
    options = []
    option_map = {}
    num = 1
    current_day = game.day_state.day

    if game.can_cook():
        print(f"  {num}. 自炊する")
        option_map[str(num)] = "cook"
        options.append(str(num))
        num += 1

    if game.can_make_bento():
        print(f"  {num}. 自炊して弁当も作る")
        option_map[str(num)] = "cook_bento"
        options.append(str(num))
        num += 1

    if not game.provisions.is_empty(current_day):
        print(f"  {num}. 食糧を食べる")
        option_map[str(num)] = "provision"
        options.append(str(num))
        num += 1

    print(f"  {num}. 食べない")
    option_map[str(num)] = "skip"
    options.append(str(num))

    choice = get_input("選択: ", options)
    # 内部コードを返す
    action = option_map[choice]
    if action == "cook":
        return "1"
    elif action == "cook_bento":
        return "2"
    elif action == "provision":
        return "3"
    else:
        return "4"


def show_lunch_menu(game: GameManager) -> str:
    """昼食メニュー表示（平日）"""
    print("昼食の選択:")
    options = []
    option_map = {}
    num = 1
    current_day = game.day_state.day

    if game.can_use_cafeteria():
        print(f"  {num}. 社食 ({CAFETERIA_PRICE}円)")
        option_map[str(num)] = "cafeteria"
        options.append(str(num))
        num += 1

    # 食糧（弁当含む）がある場合
    if not game.provisions.is_empty(current_day):
        print(f"  {num}. 食糧を食べる")
        option_map[str(num)] = "provision"
        options.append(str(num))
        num += 1

    print(f"  {num}. 食べない")
    option_map[str(num)] = "skip"
    options.append(str(num))

    choice = get_input("選択: ", options)
    action = option_map[choice]
    if action == "cafeteria":
        return "2"
    elif action == "provision":
        return "3"
    else:
        return "4"


def show_holiday_breakfast_menu(game: GameManager) -> str:
    """休日朝食メニュー表示（弁当作成なし）"""
    print("朝食の選択:")
    options = []
    option_map = {}
    num = 1
    current_day = game.day_state.day

    if game.can_cook():
        print(f"  {num}. 自炊する")
        option_map[str(num)] = "cook"
        options.append(str(num))
        num += 1

    if not game.provisions.is_empty(current_day):
        print(f"  {num}. 食糧を食べる")
        option_map[str(num)] = "provision"
        options.append(str(num))
        num += 1

    print(f"  {num}. 食べない")
    option_map[str(num)] = "skip"
    options.append(str(num))

    choice = get_input("選択: ", options)
    action = option_map[choice]
    if action == "cook":
        return "1"
    elif action == "provision":
        return "2"
    else:
        return "3"


def show_holiday_lunch_menu(game: GameManager) -> str:
    """休日昼食メニュー表示（自炊可能）"""
    print("昼食の選択:")
    options = []
    option_map = {}
    num = 1
    current_day = game.day_state.day

    if game.can_cook():
        print(f"  {num}. 自炊する")
        option_map[str(num)] = "cook"
        options.append(str(num))
        num += 1

    if not game.provisions.is_empty(current_day):
        print(f"  {num}. 食糧を食べる")
        option_map[str(num)] = "provision"
        options.append(str(num))
        num += 1

    print(f"  {num}. 食べない")
    option_map[str(num)] = "skip"
    options.append(str(num))

    choice = get_input("選択: ", options)
    action = option_map[choice]
    if action == "cook":
        return "1"
    elif action == "provision":
        return "2"
    else:
        return "3"


def show_dinner_menu(game: GameManager) -> str:
    """夕食メニュー表示"""
    print("夕食の選択:")
    options = []
    option_map = {}
    num = 1
    current_day = game.day_state.day

    if game.can_cook():
        print(f"  {num}. 自炊する")
        option_map[str(num)] = "cook"
        options.append(str(num))
        num += 1

    if not game.provisions.is_empty(current_day):
        print(f"  {num}. 食糧を食べる")
        option_map[str(num)] = "provision"
        options.append(str(num))
        num += 1

    print(f"  {num}. 食べない")
    option_map[str(num)] = "skip"
    options.append(str(num))

    choice = get_input("選択: ", options)
    action = option_map[choice]
    if action == "cook":
        return "1"
    elif action == "provision":
        return "2"
    else:
        return "3"


def show_shopping_menu(game: GameManager) -> str:
    """買い出しメニュー表示"""
    print(f"買い出しに行きますか？ (気力-{SHOPPING_ENERGY_COST}, 体力-{SHOPPING_STAMINA_COST})")
    options = []
    option_map = {}
    num = 1

    if game.can_go_shopping():
        print(f"  {num}. 買い出しに行く")
        option_map[str(num)] = "shop"
        options.append(str(num))
        num += 1

    print(f"  {num}. まっすぐ帰宅")
    option_map[str(num)] = "skip"
    options.append(str(num))

    choice = get_input("選択: ", options)
    action = option_map[choice]
    if action == "shop":
        return "1"
    else:
        return "2"


def show_shop(player: Player, shop_items: list) -> list[tuple[str, int, int]]:
    """お店の商品表示と購入UI
    Args:
        player: プレイヤー
        shop_items: ShopItemのリスト（generate_daily_shop_itemsで生成）
    Returns:
        [(食材名, 数量, 残り鮮度日数), ...]
    """
    purchases = []

    print("【スーパーマーケット】本日のラインナップ")
    print(f"所持金: {player.money:,}円")
    print()
    print("購入する食材を選んでください:")
    for i, item in enumerate(shop_items, 1):
        name = item.ingredient.name
        original_price = item.ingredient.price
        price = item.price
        category = item.ingredient.category

        if item.discount_type == "sale":
            print(f"  {i}. {name} ({price}円) [2割引!] 元{original_price}円 [{category}]")
        elif item.discount_type == "near_expiry":
            print(f"  {i}. {name} ({price}円) [半額!期限今日] 元{original_price}円 [{category}]")
        else:
            print(f"  {i}. {name} ({price}円) [{category}]")
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
            if 1 <= idx <= len(shop_items):
                item = shop_items[idx - 1]
                name = item.ingredient.name
                price = item.price
                freshness = item.freshness_days_left
                if remaining_money >= price:
                    qty = input(f"{name}を何個買いますか？ (1-10): ").strip()
                    try:
                        qty_num = int(qty)
                        if 1 <= qty_num <= 10:
                            total_price = price * qty_num
                            if remaining_money >= total_price:
                                purchases.append((name, qty_num, freshness))
                                remaining_money -= total_price
                                if item.discount_type == "near_expiry":
                                    print(f"{name}を{qty_num}個購入！ (-{total_price}円) ※期限注意")
                                else:
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


def show_discard_menu(stock: Stock, current_day: int, freshness_extend: int = 0) -> list[tuple[str, int]]:
    """食材廃棄メニュー
    Returns: [(食材名, 廃棄数), ...]
    """
    items = stock.get_items_for_discard(current_day, freshness_extend)
    if not items:
        print("廃棄できる食材がありません。")
        return []

    discards = []
    print("【食材の廃棄】")
    print("廃棄する食材を選んでください:")
    for i, (name, qty, elapsed, modifier) in enumerate(items, 1):
        if modifier < 1.0:
            penalty = int((1.0 - modifier) * 100)
            print(f"  {i}. {name} x{qty} ({elapsed}日経過, 栄養-{penalty}%)")
        else:
            print(f"  {i}. {name} x{qty} ({elapsed}日経過, 新鮮)")
    print("  0. 廃棄しない")

    while True:
        choice = input("番号を入力 (0で終了): ").strip()
        if choice == "0":
            break

        try:
            idx = int(choice)
            if 1 <= idx <= len(items):
                name, qty, _, _ = items[idx - 1]
                if qty == 1:
                    discards.append((name, 1))
                    print(f"{name}を1個廃棄しました。")
                    # リストを更新
                    items = [(n, q - 1 if n == name else q, e, m)
                             for n, q, e, m in items if q > 1 or n != name]
                else:
                    qty_input = input(f"{name}を何個廃棄しますか？ (1-{qty}): ").strip()
                    try:
                        discard_qty = int(qty_input)
                        if 1 <= discard_qty <= qty:
                            discards.append((name, discard_qty))
                            print(f"{name}を{discard_qty}個廃棄しました。")
                            # リストを更新
                            items = [(n, q - discard_qty if n == name else q, e, m)
                                     for n, q, e, m in items if (q - discard_qty if n == name else q) > 0]
                        else:
                            print(f"1から{qty}の間で入力してください。")
                    except ValueError:
                        print("数値を入力してください。")
            else:
                print("無効な番号です。")
        except ValueError:
            print("数値を入力してください。")

    return discards


def show_online_shopping_menu() -> str:
    """通販するか選択"""
    print("通販サイトを見ますか？")
    print("  1. 通販する")
    print("  2. しない")
    return get_input("選択: ", ["1", "2"])


def show_online_shop(player, relics, provisions, current_day: int = 1) -> tuple[list[str], list[tuple[str, int]]]:
    """通販画面
    Args:
        player: プレイヤー
        relics: RelicInventory
        provisions: ProvisionStock
        current_day: 現在の日（レリックのラインナップ決定用）
    Returns:
        (購入したレリック名リスト, [(食糧名, 数量), ...])
    """
    from game.relic import generate_daily_relic_items
    from game.provisions import get_all_provisions

    # 本日のレリックラインナップを生成
    daily_relics = generate_daily_relic_items(seed=current_day)
    all_provisions = get_all_provisions()

    purchased_relics = []
    purchased_provisions = []

    while True:
        print("\n【オンラインショップ】")
        print(f"カード未払い残高: {player.card_debt:,}円")
        print(f"所持レリック: {relics.count()}個")
        print()

        # 本日のレリック表示
        print("[本日のレリック] ※毎日ラインナップが変わります")
        for i, item in enumerate(daily_relics, 1):
            owned = relics.has(item.relic.name)
            if owned:
                status = " [購入済]"
            elif item.is_sale:
                status = f" [セール! 元{item.relic.price:,}円]"
            else:
                status = ""
            print(f"  {i}. {item.relic.name} ({item.price:,}円) - {item.relic.description}{status}")

        # 食糧表示
        print("\n[食糧]")
        provision_start = len(daily_relics) + 1
        for i, prov in enumerate(all_provisions, provision_start):
            caffeine_info = f", ☕気力+{prov.caffeine * 2}" if prov.caffeine > 0 else ""
            print(f"  {i}. {prov.name} ({prov.price:,}円) - 満腹{prov.fullness}{caffeine_info}")

        print("\n  0. 購入完了")

        choice = input("番号を入力: ").strip()
        if choice == "0":
            break

        try:
            idx = int(choice)
            # レリック購入
            if 1 <= idx <= len(daily_relics):
                item = daily_relics[idx - 1]
                if relics.has(item.relic.name):
                    print("すでに購入済みです。")
                else:
                    player.add_card_debt(item.price)
                    relics.add(item.relic.name)
                    purchased_relics.append(item.relic.name)
                    if item.is_sale:
                        print(f"{item.relic.name}をセール価格で購入！ (カード: +{item.price:,}円)")
                    else:
                        print(f"{item.relic.name}を購入しました！ (カード: +{item.price:,}円)")

            # 食糧購入
            elif provision_start <= idx < provision_start + len(all_provisions):
                prov = all_provisions[idx - provision_start]
                qty_input = input(f"{prov.name}を何個買いますか？ (1-10): ").strip()
                try:
                    qty = int(qty_input)
                    if 1 <= qty <= 10:
                        total = prov.price * qty
                        player.add_card_debt(total)
                        provisions.add(prov.name, qty)
                        purchased_provisions.append((prov.name, qty))
                        print(f"{prov.name}を{qty}個購入しました！ (カード: +{total:,}円)")
                    else:
                        print("1から10の間で入力してください。")
                except ValueError:
                    print("数値を入力してください。")
            else:
                print("無効な番号です。")
        except ValueError:
            print("数値を入力してください。")

    return purchased_relics, purchased_provisions


def show_game_over(reason: str = "stamina"):
    """ゲームオーバー表示"""
    print("\n" + "=" * 50)
    print("       ゲームオーバー")
    print("=" * 50)
    if reason == "card":
        print("カードの支払いができませんでした...")
        print("計画的な買い物を心がけましょう。")
    else:
        print("体力またはお金が尽きてしまいました...")
        print("一人暮らしは大変ですね。")


def show_card_settlement(player: Player) -> bool:
    """カード精算を表示。精算成功ならTrue"""
    if player.card_debt == 0:
        return True

    print("\n【カード精算】")
    print(f"  現金残高: {player.money:,}円")
    print(f"  カード未払い: {player.card_debt:,}円")
    print("  " + "─" * 20)
    final = player.get_final_balance()
    print(f"  最終残高: {final:,}円")
    print()
    return final >= 0


def show_game_clear(player: Player, day_state):
    """ゲームクリア表示"""
    print("\n" + "=" * 50)
    print("       ゲームクリア！")
    print("=" * 50)
    print(f"1ヶ月間を生き延びました！")

    if player.card_debt > 0:
        show_card_settlement(player)
        final = player.get_final_balance()
        print(f"最終残高: {final:,}円")
    else:
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


def show_character_select():
    """キャラクター選択画面
    Returns: 選択されたCharacter
    """
    from game.character import get_all_characters

    characters = get_all_characters()

    print("=" * 50)
    print("    キャラクター選択")
    print("=" * 50)
    print()

    for i, char in enumerate(characters, 1):
        print(f"  {i}. {char.name}")
        print(f"     {char.description}")
        print(f"     初期所持金: {char.initial_money:,}円")
        net_salary = char.salary_amount - char.rent_amount
        print(f"     月給: {char.salary_amount:,}円 (家賃{char.rent_amount:,}円天引 → 手取{net_salary:,}円)", end="")
        if char.has_bonus:
            print(f" / ボーナス: {char.bonus_amount:,}円")
        else:
            print()
        print()

    while True:
        choice = input("キャラクターを選択 (1-{}): ".format(len(characters))).strip()
        try:
            idx = int(choice)
            if 1 <= idx <= len(characters):
                selected = characters[idx - 1]
                print(f"\n{selected.name}を選択しました。\n")
                return selected
        except ValueError:
            pass
        print("無効な入力です。")


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

    if result.total_salary_received > 0 or result.total_bonus_received > 0:
        print(f"\n【収入】")
        if result.total_salary_received > 0:
            print(f"  給料: {result.total_salary_received:,}円")
        if result.total_bonus_received > 0:
            print(f"  ボーナス: {result.total_bonus_received:,}円")

    print(f"\n【栄養バランス】")
    print(f"  バランス良い日: {result.days_with_balanced_nutrition}日")
    penalty_count = sum(result.nutrition_penalties.values())
    if penalty_count > 0:
        print(f"  ペナルティ発生:")
        for nutrient, count in result.nutrition_penalties.items():
            if count > 0:
                print(f"    {nutrient}: {count}回")

    if result.total_insomnia_nights > 0:
        print(f"\n【カフェイン】")
        print(f"  不眠になった夜: {result.total_insomnia_nights}回")

    print("─" * 50)
