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


def show_provision_stock(provisions):
    """食糧ストック表示"""
    items = provisions.get_all()
    if items:
        print("【食糧ストック】")
        for name, qty in items.items():
            prov = get_provision(name)
            if prov:
                caffeine_info = f", ☕気力+{prov.caffeine * 2}" if prov.caffeine > 0 else ""
                print(f"  {name}: {qty}個 (満腹{prov.fullness}{caffeine_info})")
        print()
    else:
        print("【食糧ストック】空\n")


def select_provision(provisions) -> str | None:
    """食糧選択UI
    Returns: 選択した食糧名、キャンセルならNone
    """
    available = provisions.get_available()
    if not available:
        print("食糧がありません。")
        return None

    print("食べる食糧を選んでください:")
    for i, name in enumerate(available, 1):
        qty = provisions.get_quantity(name)
        prov = get_provision(name)
        if prov:
            caffeine_info = f", ☕{prov.caffeine}→気力+{prov.caffeine * 2}" if prov.caffeine > 0 else ""
            print(f"  {i}. {name} (残り{qty}個, 満腹{prov.fullness}{caffeine_info})")
    print("  0. キャンセル")

    while True:
        choice = input("番号を入力: ").strip()
        if choice == "0":
            return None

        try:
            idx = int(choice)
            if 1 <= idx <= len(available):
                return available[idx - 1]
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

    if not game.provisions.is_empty():
        print("  3. 食糧を食べる")
        options.append("3")
    else:
        print("  3. 食糧を食べる (食糧がありません)")

    print("  4. 食べない")
    options.append("4")

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

    # 食糧は持参できる（職場で食べる）
    if not game.provisions.is_empty():
        print("  3. 食糧を食べる")
        options.append("3")
    else:
        print("  3. 食糧を食べる (食糧がありません)")

    print("  4. 食べない")
    options.append("4")

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

    if not game.provisions.is_empty():
        print("  2. 食糧を食べる")
        options.append("2")
    else:
        print("  2. 食糧を食べる (食糧がありません)")

    print("  3. 食べない")
    options.append("3")

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

    if not game.provisions.is_empty():
        print("  2. 食糧を食べる")
        options.append("2")
    else:
        print("  2. 食糧を食べる (食糧がありません)")

    print("  3. 食べない")
    options.append("3")

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

    if not game.provisions.is_empty():
        print("  2. 食糧を食べる")
        options.append("2")
    else:
        print("  2. 食糧を食べる (食糧がありません)")

    print("  3. 食べない")
    options.append("3")

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


def show_online_shop(player, relics, provisions) -> tuple[list[str], list[tuple[str, int]]]:
    """通販画面
    Args:
        player: プレイヤー
        relics: RelicInventory
        provisions: ProvisionStock
    Returns:
        (購入したレリック名リスト, [(食糧名, 数量), ...])
    """
    from game.relic import get_all_relics
    from game.provisions import get_all_provisions

    all_relics = get_all_relics()
    all_provisions = get_all_provisions()

    purchased_relics = []
    purchased_provisions = []

    while True:
        print("\n【オンラインショップ】")
        print(f"カード未払い残高: {player.card_debt:,}円")
        print()

        # レリック表示
        print("[レリック]")
        relic_options = []
        for i, relic in enumerate(all_relics, 1):
            owned = relics.has(relic.name)
            status = " [購入済]" if owned else ""
            print(f"  {i}. {relic.name} ({relic.price:,}円) - {relic.description}{status}")
            if not owned:
                relic_options.append((str(i), relic))

        # 食糧表示
        print("\n[食糧]")
        provision_start = len(all_relics) + 1
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
            if 1 <= idx <= len(all_relics):
                relic = all_relics[idx - 1]
                if relics.has(relic.name):
                    print("すでに購入済みです。")
                else:
                    player.add_card_debt(relic.price)
                    relics.add(relic.name)
                    purchased_relics.append(relic.name)
                    print(f"{relic.name}を購入しました！ (カード: +{relic.price:,}円)")

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
