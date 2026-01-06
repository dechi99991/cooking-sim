#!/usr/bin/env python3
"""一人暮らし自炊シミュレーション - メインエントリーポイント"""
import sys
sys.path.insert(0, '.')

from game.player import Player
from game.ingredients import create_initial_stock, get_ingredient, generate_daily_shop_items
from game.cooking import cook, create_cafeteria_dish
from game.day_cycle import GameManager, GamePhase
from ui.terminal import (
    clear_screen, show_status, show_nutrition, show_stock,
    show_recipe_suggestions, show_phase_header, show_dish,
    show_breakfast_menu, show_lunch_menu, show_dinner_menu,
    show_holiday_breakfast_menu, show_holiday_lunch_menu,
    show_shopping_menu, show_shop, show_discard_menu,
    show_online_shopping_menu, show_online_shop, show_card_settlement,
    show_game_over, show_game_clear, show_title, select_ingredients,
    show_game_result, show_provision_stock, select_provision,
    show_character_select, show_day_start, show_events, show_deliveries,
    confirm_cooking, show_holiday_activity_menu
)
from game.events import EventTiming
from game.provisions import get_provision


def trigger_events(game: GameManager, timing: EventTiming):
    """指定タイミングのイベントをチェックして発生させる"""
    context = game.get_event_context()
    results = game.events.check_and_trigger_events(timing, context, game)
    if results:
        show_events(results)
    return results


def check_and_pay_salary(game: GameManager):
    """給料日・ボーナスをチェックして支給"""
    if game.is_payday():
        gross, rent, net = game.pay_salary()
        print("💰 給料日です！")
        print(f"   総支給額: {gross:,}円")
        print(f"   家賃天引: -{rent:,}円")
        print(f"   手取り:   {net:,}円")

        if game.is_bonus_day():
            bonus = game.pay_bonus()
            print(f"🎉 ボーナス支給！ {bonus:,}円")

        print(f"現在の所持金: {game.player.money:,}円")
        print()


def eat_provision_once(game: GameManager) -> bool:
    """食糧を1つ食べる処理。食べたらTrue"""
    current_day = game.day_state.day
    result = select_provision(game.provisions, current_day)

    if result is None:
        return False

    item_type, value = result

    if item_type == "prepared":
        # 弁当などの調理済み料理
        dish = game.provisions.remove_prepared(value)
        if dish:
            game.player.add_fullness(dish.fullness)
            game.day_state.daily_nutrition.add(dish.nutrition)
            print(f"【{dish.dish_type}: {dish.name}】を食べました！")
            print(f"  満腹度: +{dish.fullness}")
            n = dish.nutrition
            print(f"  栄養: 活力{n.vitality} 心力{n.mental} 覚醒{n.awakening} 持続{n.sustain} 防衛{n.defense}")
            print(f"満腹感: {game.player.fullness}")
            game.stats.record_meal_eaten()
            return True

    elif item_type == "provision":
        # 通販食品
        name = value
        prov = get_provision(name)
        if prov:
            game.provisions.remove(name, 1)
            game.player.add_fullness(prov.fullness)
            game.day_state.daily_nutrition.add(prov.nutrition)
            # カフェイン摂取 → 気力回復
            if prov.caffeine > 0:
                game.add_caffeine(prov.caffeine)
                energy_boost = prov.caffeine * 2  # カフェイン1につき気力+2
                game.player.energy = min(game.player.energy + energy_boost, 10)
            print(f"【{name}】を食べました！")
            print(f"  満腹度: +{prov.fullness}")
            n = prov.nutrition
            print(f"  栄養: 活力{n.vitality} 心力{n.mental} 覚醒{n.awakening} 持続{n.sustain} 防衛{n.defense}")
            if prov.caffeine > 0:
                print(f"  ☕ カフェイン: +{prov.caffeine} → 気力+{prov.caffeine * 2}")
                if game.will_have_insomnia():
                    print(f"  ⚠ カフェイン過多！今夜は不眠になりそう...")
            print(f"満腹感: {game.player.fullness}  気力: {game.player.energy}")
            game.stats.record_meal_eaten()
            return True

    return False


def eat_provision(game: GameManager) -> bool:
    """食糧を食べる処理（複数選択可能）。1つ以上食べたらTrue"""
    current_day = game.day_state.day
    ate_something = False

    while True:
        # まだ食糧があるか確認
        if game.provisions.is_empty(current_day):
            if not ate_something:
                print("食糧がありません。")
            break

        # 満腹チェック
        if game.player.fullness >= 10:
            print("満腹です！")
            break

        # 1つ食べる
        if eat_provision_once(game):
            ate_something = True
            # もっと食べるか確認
            print("\n続けて食べますか？")
            print("  1. もっと食べる")
            print("  2. 終わり")
            choice = input("選択: ").strip()
            if choice != "1":
                break
        else:
            # キャンセルされた
            break

    return ate_something


def cook_multiple_dishes(game: GameManager, meal_name: str = "食事") -> bool:
    """複数の料理を作って食べる処理。1つ以上作ったらTrue

    Args:
        game: GameManager
        meal_name: 食事名（表示用）

    Returns:
        1つ以上料理を作って食べたらTrue
    """
    from game.nutrition import Nutrition

    current_day = game.day_state.day
    cooked_count = 0

    # この食事での累計栄養と満腹度を追跡（評価用）
    meal_nutrition = Nutrition()
    meal_fullness = 0

    while game.can_cook() and not game.stock.is_empty():
        # 満腹チェック
        if game.player.fullness >= 10:
            print("満腹です！")
            break

        # 次の料理番号
        dish_number = cooked_count + 1

        # 2品目以降は在庫を表示
        if cooked_count > 0:
            print()
            print(f"─── {dish_number}品目を作る ───")
            show_stock(game.stock, current_day, game.relics)
            show_recipe_suggestions(game.stock)

        ingredients = select_ingredients(game.stock, current_day, game.relics)
        if not ingredients:
            if cooked_count == 0:
                print(f"{meal_name}を作りませんでした。")
            break

        # 食事トータルと料理番号を渡して評価
        if not confirm_cooking(ingredients, meal_nutrition, meal_fullness, dish_number):
            print("食材を選び直します。")
            continue  # ループの先頭に戻って再選択

        dish = cook(ingredients, game.stock, current_day, game.relics)
        if dish:
            game.consume_cooking_energy()
            print(f"\n【{dish_number}品目完成】")
            show_dish(dish)
            game.eat_dish(dish)
            game.stats.record_meal_eaten()
            game.stats.record_cooking()
            cooked_count += 1

            # 累計に追加（次の料理の評価用）
            meal_nutrition.add(dish.nutrition)
            meal_fullness += dish.fullness

            print(f"満腹感: {game.player.fullness}")

            # まだ作れるか確認
            if game.can_cook() and not game.stock.is_empty() and game.player.fullness < 10:
                print(f"\nもう1品（{cooked_count + 1}品目）作りますか？")
                print("  1. 作る")
                print("  2. 終わり")
                choice = input("選択: ").strip()
                if choice != "1":
                    break
            else:
                break
        else:
            # cook失敗（通常起きないが念のため）
            break

    return cooked_count > 0


def handle_wake_up(game: GameManager):
    """起床処理（天気決定とイベント）"""
    # 天気を決定
    weather = game.determine_weather()
    show_day_start(game.day_state, weather)

    # 起床時イベント
    trigger_events(game, EventTiming.WAKE_UP)


def handle_breakfast(game: GameManager):
    """朝食フェーズの処理（平日）"""
    # 起床処理（1日の開始）
    handle_wake_up(game)

    show_phase_header(GamePhase.BREAKFAST, game.day_state)
    check_and_pay_salary(game)
    game.reset_fullness_for_meal()
    current_day = game.day_state.day

    show_status(game.player, game.day_state)
    show_stock(game.stock, current_day, game.relics)
    show_provision_stock(game.provisions, current_day)
    show_recipe_suggestions(game.stock)

    choice = show_breakfast_menu(game)

    if choice == "1":
        # 自炊のみ（複数料理可）
        if not cook_multiple_dishes(game, "朝食"):
            game.stats.record_meal_skipped()

    elif choice == "2":
        # 自炊 + 弁当作成
        print("\n【朝食用】")
        cook_multiple_dishes(game, "朝食")

        print("\n【弁当用】")
        while game.can_make_bento() and not game.stock.is_empty():
            bento_ingredients = select_ingredients(game.stock, current_day, game.relics)
            if not bento_ingredients:
                print("弁当を作りませんでした。")
                break

            if not confirm_cooking(bento_ingredients):
                print("食材を選び直します。")
                continue  # ループの先頭に戻って再選択

            bento = cook(bento_ingredients, game.stock, current_day, game.relics)
            if bento:
                game.consume_bento_energy()
                print(f"弁当【{bento.name}】を作りました！")
                game.add_bento(bento)  # 食糧ストックに弁当として追加
                game.stats.record_bento()
            break  # 弁当作成成功またはcook失敗で終了

    elif choice == "3":
        # 食糧を食べる
        if not eat_provision(game):
            game.stats.record_meal_skipped()

    elif choice == "4":
        print("朝食を抜きました。")
        game.stats.record_meal_skipped()


def handle_holiday_breakfast(game: GameManager):
    """休日朝食フェーズの処理"""
    # 起床処理（1日の開始）
    handle_wake_up(game)

    show_phase_header(GamePhase.BREAKFAST, game.day_state)
    check_and_pay_salary(game)
    game.reset_fullness_for_meal()
    current_day = game.day_state.day

    show_status(game.player, game.day_state)
    show_stock(game.stock, current_day, game.relics)
    show_provision_stock(game.provisions, current_day)
    show_recipe_suggestions(game.stock)

    choice = show_holiday_breakfast_menu(game)

    if choice == "1":
        # 自炊（複数料理可）
        if not cook_multiple_dishes(game, "朝食"):
            game.stats.record_meal_skipped()

    elif choice == "2":
        # 食糧を食べる
        if not eat_provision(game):
            game.stats.record_meal_skipped()

    elif choice == "3":
        print("朝食を抜きました。")
        game.stats.record_meal_skipped()


def handle_go_to_work(game: GameManager):
    """出勤フェーズの処理"""
    show_phase_header(GamePhase.GO_TO_WORK, game.day_state)

    # 出社時イベント
    trigger_events(game, EventTiming.GO_TO_WORK)

    print("出勤します...")
    game.commute()
    print(f"体力: {game.player.stamina}")


def handle_lunch(game: GameManager):
    """昼食フェーズの処理"""
    show_phase_header(GamePhase.LUNCH, game.day_state)
    game.reset_fullness_for_meal()
    current_day = game.day_state.day

    show_status(game.player, game.day_state)
    show_provision_stock(game.provisions, current_day)

    choice = show_lunch_menu(game)

    if choice == "2":
        # 社食
        game.consume_cafeteria_cost()
        dish = create_cafeteria_dish()
        game.eat_dish(dish)
        print("社食定食を食べました！")
        print(f"満腹感: {game.player.fullness}")
        game.stats.record_meal_eaten()
        game.stats.record_cafeteria()

    elif choice == "3":
        # 食糧を食べる
        if not eat_provision(game):
            game.stats.record_meal_skipped()

    elif choice == "4":
        print("昼食を抜きました。")
        game.stats.record_meal_skipped()

    # 昼食後イベント
    trigger_events(game, EventTiming.AFTER_LUNCH)


def handle_leave_work(game: GameManager):
    """退勤フェーズの処理"""
    show_phase_header(GamePhase.LEAVE_WORK, game.day_state)

    # 退勤時イベント
    trigger_events(game, EventTiming.LEAVE_WORK)

    print("退勤します...")
    game.commute()
    print(f"体力: {game.player.stamina}")


def handle_shopping(game: GameManager):
    """買い出しフェーズの処理"""
    show_phase_header(GamePhase.SHOPPING, game.day_state)
    current_day = game.day_state.day
    show_status(game.player, game.day_state)
    show_stock(game.stock, current_day, game.relics)

    choice = show_shopping_menu(game)

    if choice == "1":
        # 買い出しに行く
        game.go_shopping()
        print(f"スーパーへ向かいます... (気力: {game.player.energy}, 体力: {game.player.stamina})")
        print()

        # 買い物中イベント
        trigger_events(game, EventTiming.AT_SHOP)

        # 本日の商品を生成（日付をシードにして毎日異なるラインナップ）
        shop_items = generate_daily_shop_items(seed=current_day)
        purchases = show_shop(game.player, shop_items, game.get_bag_capacity())

        if purchases:
            total_cost = 0
            total_items = 0
            print("\n【購入品】")
            for name, qty, freshness_days_left in purchases:
                ingredient = get_ingredient(name)
                if ingredient:
                    # 購入時の価格は既に支払い済み（show_shop内で計算）
                    # ここでは在庫に追加する
                    # 期限近い商品は「有効購入日」を調整して鮮度を短く
                    if freshness_days_left < ingredient.freshness_days:
                        # 残り鮮度日数から逆算した「有効購入日」を設定
                        effective_day = current_day - (ingredient.freshness_days - freshness_days_left)
                    else:
                        effective_day = current_day
                    game.stock.add(name, qty, effective_day)
                    print(f"  {name} x{qty}")
                    total_items += qty
            # 合計金額の計算（shop_itemsから逆引き）
            shop_item_map = {item.ingredient.name: item for item in shop_items}
            for name, qty, _ in purchases:
                if name in shop_item_map:
                    total_cost += shop_item_map[name].price * qty
            game.player.consume_money(total_cost)
            print(f"合計: {total_cost}円")
            print(f"残り所持金: {game.player.money:,}円")
            game.stats.record_shopping(total_cost, total_items)
        else:
            print("何も買いませんでした。")

        print("\n帰宅しました。")

        # 帰宅後：期限切れ食材がある場合は廃棄オプションを表示
        if game.stock.has_expired_items(current_day, game.relics):
            print()
            print("⚠ 期限切れの食材があります")
            discard_choice = input("廃棄しますか？ (1. する  2. しない): ").strip()
            if discard_choice == "1":
                discards = show_discard_menu(game.stock, current_day, game.relics)
                for name, qty in discards:
                    game.stock.discard(name, qty)

    elif choice == "2":
        print("まっすぐ帰宅します。")


def handle_holiday_shopping(game: GameManager, phase: GamePhase):
    """休日の買い出しフェーズの処理"""
    from game.constants import SHOPPING_ENERGY_COST, SHOPPING_STAMINA_COST

    show_phase_header(phase, game.day_state)
    current_day = game.day_state.day
    show_status(game.player, game.day_state)
    show_stock(game.stock, current_day, game.relics)
    show_recipe_suggestions(game.stock)

    choice = show_holiday_activity_menu(game)

    if choice == "shop":
        # 近所のスーパー（従来通り）
        game.go_shopping()
        print(f"スーパーへ向かいます... (気力: {game.player.energy}, 体力: {game.player.stamina})")
        print()

        trigger_events(game, EventTiming.AT_SHOP)

        phase_offset = 100 if phase == GamePhase.HOLIDAY_SHOPPING_2 else 0
        shop_items = generate_daily_shop_items(seed=current_day + phase_offset)
        purchases = show_shop(game.player, shop_items, game.get_bag_capacity())

        _process_purchases(game, purchases, shop_items, current_day)
        print("\n帰宅しました。")
        _check_expired_items(game, current_day)

    elif choice == "distant":
        # 遠出して買い物（コスト2倍、バッグ容量2倍）
        game.player.consume_energy(SHOPPING_ENERGY_COST * 2)
        game.player.consume_stamina(SHOPPING_STAMINA_COST * 2)
        print(f"遠出して大きなスーパーへ向かいます... (気力: {game.player.energy}, 体力: {game.player.stamina})")
        print()

        trigger_events(game, EventTiming.AT_SHOP)

        # 遠出用のシードで別ラインナップ
        phase_offset = 200 if phase == GamePhase.HOLIDAY_SHOPPING_2 else 150
        shop_items = generate_daily_shop_items(seed=current_day + phase_offset)
        # バッグ容量2倍
        purchases = show_shop(game.player, shop_items, game.get_bag_capacity() * 2)

        _process_purchases(game, purchases, shop_items, current_day)
        print("\n帰宅しました。疲れたけど、たくさん買えた！")
        _check_expired_items(game, current_day)

    elif choice == "batch":
        # 料理の作り置き
        print("作り置きを始めます。複数の弁当を作れます。")
        print()
        bento_count = 0
        while game.can_cook() and not game.stock.is_empty():
            print(f"【弁当 {bento_count + 1}個目】")
            show_stock(game.stock, current_day, game.relics)
            show_recipe_suggestions(game.stock)

            ingredients = select_ingredients(game.stock, current_day, game.relics)
            if not ingredients:
                print("作り置きを終了します。")
                break

            # 弁当は食事トータルでなく単品評価（dish_number で弁当番号を表示）
            if not confirm_cooking(ingredients, dish_number=bento_count + 1):
                print("この弁当はキャンセルしました。")
                continue

            bento = cook(ingredients, game.stock, current_day, game.relics)
            if bento:
                game.consume_cooking_energy()
                print(f"弁当【{bento.name}】を作りました！")
                # 作り置きは翌日まで有効
                game.provisions.add_prepared(
                    dish_name=bento.name,
                    nutrition=bento.nutrition,
                    fullness=bento.fullness,
                    expiry_day=current_day + 1,
                    dish_type="作り置き"
                )
                game.stats.record_bento()
                bento_count += 1
                print()

                # 続けるか確認
                if game.can_cook() and not game.stock.is_empty():
                    cont = input("もう1つ作りますか？ (1. はい  2. いいえ): ").strip()
                    if cont != "1":
                        break

        if bento_count > 0:
            print(f"\n作り置き完了！ {bento_count}個の弁当を作りました。")
        else:
            print("\n作り置きしませんでした。")

    elif choice == "rest":
        # のんびり休養
        print("のんびりと過ごしました...")
        game.player.recover_energy(2)
        game.player.recover_stamina(1)
        print(f"気力+2, 体力+1 (気力: {game.player.energy}, 体力: {game.player.stamina})")

    elif choice == "skip":
        print("特に何もせず過ごしました。")


def _process_purchases(game: GameManager, purchases: list, shop_items: list, current_day: int):
    """買い物処理（共通ロジック）"""
    if purchases:
        total_cost = 0
        total_items = 0
        print("\n【購入品】")
        for name, qty, freshness_days_left in purchases:
            ingredient = get_ingredient(name)
            if ingredient:
                if freshness_days_left < ingredient.freshness_days:
                    effective_day = current_day - (ingredient.freshness_days - freshness_days_left)
                else:
                    effective_day = current_day
                game.stock.add(name, qty, effective_day)
                print(f"  {name} x{qty}")
                total_items += qty
        shop_item_map = {item.ingredient.name: item for item in shop_items}
        for name, qty, _ in purchases:
            if name in shop_item_map:
                total_cost += shop_item_map[name].price * qty
        game.player.consume_money(total_cost)
        print(f"合計: {total_cost}円")
        print(f"残り所持金: {game.player.money:,}円")
        game.stats.record_shopping(total_cost, total_items)
    else:
        print("何も買いませんでした。")


def _check_expired_items(game: GameManager, current_day: int):
    """期限切れ食材チェック（共通ロジック）"""
    if game.stock.has_expired_items(current_day, game.relics):
        print()
        print("⚠ 期限切れの食材があります")
        discard_choice = input("廃棄しますか？ (1. する  2. しない): ").strip()
        if discard_choice == "1":
            discards = show_discard_menu(game.stock, current_day, game.relics)
            for name, qty in discards:
                game.stock.discard(name, qty)


def handle_holiday_lunch(game: GameManager):
    """休日昼食フェーズの処理"""
    show_phase_header(GamePhase.HOLIDAY_LUNCH, game.day_state)
    game.reset_fullness_for_meal()
    current_day = game.day_state.day

    show_status(game.player, game.day_state)
    show_stock(game.stock, current_day, game.relics)
    show_provision_stock(game.provisions, current_day)
    show_recipe_suggestions(game.stock)

    choice = show_holiday_lunch_menu(game)

    if choice == "1":
        # 自炊（複数料理可）
        if not cook_multiple_dishes(game, "昼食"):
            game.stats.record_meal_skipped()

    elif choice == "2":
        # 食糧を食べる
        if not eat_provision(game):
            game.stats.record_meal_skipped()

    elif choice == "3":
        print("昼食を抜きました。")
        game.stats.record_meal_skipped()


def handle_dinner(game: GameManager):
    """夕食フェーズの処理"""
    show_phase_header(GamePhase.DINNER, game.day_state)

    # 配送処理（通販で注文した商品が届く）
    deliveries = game.process_deliveries()
    show_deliveries(deliveries)

    # 帰宅後イベント
    trigger_events(game, EventTiming.AFTER_WORK)

    game.reset_fullness_for_meal()
    current_day = game.day_state.day

    show_status(game.player, game.day_state)
    show_stock(game.stock, current_day, game.relics)
    show_provision_stock(game.provisions, current_day)
    show_recipe_suggestions(game.stock)

    choice = show_dinner_menu(game)

    if choice == "1":
        # 自炊（複数料理可）
        if not cook_multiple_dishes(game, "夕食"):
            game.stats.record_meal_skipped()

    elif choice == "2":
        # 食糧を食べる
        if not eat_provision(game):
            game.stats.record_meal_skipped()

    elif choice == "3":
        print("夕食を抜きました。")
        game.stats.record_meal_skipped()


def handle_online_shopping(game: GameManager):
    """通販フェーズの処理"""
    show_phase_header(GamePhase.ONLINE_SHOPPING, game.day_state)

    choice = show_online_shopping_menu()

    if choice == "1":
        show_online_shop(game, game.day_state.day)
    else:
        print("通販をスキップしました。")


def handle_sleep(game: GameManager):
    """就寝フェーズの処理"""
    show_phase_header(GamePhase.SLEEP, game.day_state)

    # 夜中イベント
    trigger_events(game, EventTiming.NIGHT)

    print("1日が終わりました。")
    show_nutrition(game.day_state.daily_nutrition)

    # カフェイン摂取量の表示
    caffeine = game.get_caffeine()
    if caffeine > 0:
        print(f"本日のカフェイン摂取量: {caffeine}")

    # ペナルティチェック
    energy_p, stamina_p, fullness_p = game.day_state.daily_nutrition.calculate_penalties()
    if energy_p or stamina_p or fullness_p:
        print("【栄養不足のペナルティ】")
        if stamina_p:
            print(f"  ・活力素不足: 明日の体力回復-{stamina_p}")
        if energy_p:
            print(f"  ・心力素不足: 明日の気力回復-{energy_p}")
        if fullness_p:
            print(f"  ・持続素不足: 明日の満腹感減少+{fullness_p}")
    else:
        print("バランスの良い食事でした！")

    # 就寝処理（不眠チェック含む）
    has_insomnia = game.sleep()

    if has_insomnia:
        print("\n☕ カフェインの摂りすぎで眠れませんでした...")
        print("  → 明日の気力・体力回復にペナルティ")

    print(f"\n就寝... 気力と体力が回復しました。")
    print(f"気力: {game.player.energy}  体力: {game.player.stamina}")

    input("\nEnterキーで次の日へ...")


def game_loop(game: GameManager):
    """メインゲームループ"""
    while True:
        phase = game.get_current_phase()
        is_holiday = game.is_holiday()

        # 朝食
        if phase == GamePhase.BREAKFAST:
            if is_holiday:
                handle_holiday_breakfast(game)
            else:
                handle_breakfast(game)

        # 平日フェーズ
        elif phase == GamePhase.GO_TO_WORK:
            handle_go_to_work(game)
        elif phase == GamePhase.LUNCH:
            handle_lunch(game)
        elif phase == GamePhase.LEAVE_WORK:
            handle_leave_work(game)
        elif phase == GamePhase.SHOPPING:
            handle_shopping(game)

        # 休日フェーズ
        elif phase == GamePhase.HOLIDAY_SHOPPING_1:
            handle_holiday_shopping(game, phase)
        elif phase == GamePhase.HOLIDAY_LUNCH:
            handle_holiday_lunch(game)
        elif phase == GamePhase.HOLIDAY_SHOPPING_2:
            handle_holiday_shopping(game, phase)

        # 共通フェーズ
        elif phase == GamePhase.DINNER:
            handle_dinner(game)
        elif phase == GamePhase.ONLINE_SHOPPING:
            handle_online_shopping(game)
        elif phase == GamePhase.SLEEP:
            handle_sleep(game)
            game.start_new_day()

            # ゲーム終了判定
            if game.is_game_complete():
                clear_screen()
                # カード精算チェック
                if game.player.get_final_balance() < 0:
                    show_card_settlement(game.player)
                    show_game_over("card")
                else:
                    show_game_clear(game.player, game.day_state)
                show_game_result(game.get_result())
                break
            continue

        # ゲームオーバー判定
        if game.is_game_over():
            clear_screen()
            show_game_over()
            show_game_result(game.get_result())
            break

        game.advance_phase()


def main():
    """メイン関数"""
    clear_screen()
    show_title()
    clear_screen()

    # キャラクター選択
    character = show_character_select()
    clear_screen()

    # 初期化（キャラクター設定を反映）
    player = Player(
        money=character.initial_money,
        energy=character.initial_energy,
        stamina=character.initial_stamina,
    )
    stock = create_initial_stock()
    game = GameManager(
        player, stock,
        has_bonus=character.has_bonus,
        salary_amount=character.salary_amount,
        bonus_amount=character.bonus_amount,
        rent_amount=character.rent_amount,
    )

    # ゲーム開始
    print(f"【{character.name}】でスタート！")
    print(f"【初期状態】")
    show_status(player, game.day_state)
    show_stock(stock, game.day_state.day, game.relics)

    # ゲームループ
    game_loop(game)

    print("\nゲーム終了。ありがとうございました！")


if __name__ == "__main__":
    main()
