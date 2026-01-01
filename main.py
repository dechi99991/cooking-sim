#!/usr/bin/env python3
"""一人暮らし自炊シミュレーション - メインエントリーポイント"""
import sys
sys.path.insert(0, '.')

from game.player import Player
from game.ingredients import create_initial_stock
from game.cooking import cook, create_cafeteria_dish
from game.day_cycle import GameManager, GamePhase
from ui.terminal import (
    clear_screen, show_status, show_nutrition, show_stock,
    show_recipe_suggestions, show_phase_header, show_dish,
    show_breakfast_menu, show_lunch_menu, show_dinner_menu,
    show_holiday_breakfast_menu, show_holiday_lunch_menu,
    show_shopping_menu, show_shop,
    show_game_over, show_game_clear, show_title, select_ingredients,
    show_game_result
)


def handle_breakfast(game: GameManager):
    """朝食フェーズの処理（平日）"""
    show_phase_header(GamePhase.BREAKFAST, game.day_state)
    game.reset_fullness_for_meal()

    show_status(game.player, game.day_state)
    show_stock(game.stock)
    show_recipe_suggestions(game.stock)

    choice = show_breakfast_menu(game)

    if choice == "1":
        # 自炊のみ
        ingredients = select_ingredients(game.stock)
        if ingredients:
            dish = cook(ingredients, game.stock)
            if dish:
                game.consume_cooking_energy()
                show_dish(dish)
                game.eat_dish(dish)
                game.stats.record_meal_eaten()
                game.stats.record_cooking()
                print(f"満腹感: {game.player.fullness}")
            else:
                game.stats.record_meal_skipped()
        else:
            game.stats.record_meal_skipped()

    elif choice == "2":
        # 自炊 + 弁当作成
        print("\n【朝食用】")
        ingredients = select_ingredients(game.stock)
        if ingredients:
            dish = cook(ingredients, game.stock)
            if dish:
                game.consume_cooking_energy()
                show_dish(dish)
                game.eat_dish(dish)
                game.stats.record_meal_eaten()
                game.stats.record_cooking()
                print(f"満腹感: {game.player.fullness}")

        print("\n【弁当用】")
        if game.can_make_bento():
            bento_ingredients = select_ingredients(game.stock)
            if bento_ingredients:
                bento = cook(bento_ingredients, game.stock)
                if bento:
                    game.consume_bento_energy()
                    print(f"弁当【{bento.name}】を作りました！")
                    game.set_bento(bento)
                    game.stats.record_bento()

    elif choice == "3":
        print("朝食を抜きました。")
        game.stats.record_meal_skipped()


def handle_holiday_breakfast(game: GameManager):
    """休日朝食フェーズの処理"""
    show_phase_header(GamePhase.BREAKFAST, game.day_state)
    game.reset_fullness_for_meal()

    show_status(game.player, game.day_state)
    show_stock(game.stock)
    show_recipe_suggestions(game.stock)

    choice = show_holiday_breakfast_menu(game)

    if choice == "1":
        ingredients = select_ingredients(game.stock)
        if ingredients:
            dish = cook(ingredients, game.stock)
            if dish:
                game.consume_cooking_energy()
                show_dish(dish)
                game.eat_dish(dish)
                game.stats.record_meal_eaten()
                game.stats.record_cooking()
                print(f"満腹感: {game.player.fullness}")
            else:
                game.stats.record_meal_skipped()
        else:
            game.stats.record_meal_skipped()

    elif choice == "2":
        print("朝食を抜きました。")
        game.stats.record_meal_skipped()


def handle_go_to_work(game: GameManager):
    """出勤フェーズの処理"""
    show_phase_header(GamePhase.GO_TO_WORK, game.day_state)
    print("出勤します...")
    game.commute()
    print(f"体力: {game.player.stamina}")


def handle_lunch(game: GameManager):
    """昼食フェーズの処理"""
    show_phase_header(GamePhase.LUNCH, game.day_state)
    game.reset_fullness_for_meal()

    show_status(game.player, game.day_state)

    choice = show_lunch_menu(game)

    if choice == "1":
        # 弁当
        bento = game.eat_bento()
        if bento:
            print(f"弁当【{bento.name}】を食べました！")
            print(f"満腹感: {game.player.fullness}")
            game.stats.record_meal_eaten()

    elif choice == "2":
        # 社食
        game.consume_cafeteria_cost()
        dish = create_cafeteria_dish()
        game.eat_dish(dish)
        print("社食定食を食べました！")
        print(f"満腹感: {game.player.fullness}")
        game.stats.record_meal_eaten()
        game.stats.record_cafeteria()

    elif choice == "3":
        print("昼食を抜きました。")
        game.stats.record_meal_skipped()


def handle_leave_work(game: GameManager):
    """退勤フェーズの処理"""
    show_phase_header(GamePhase.LEAVE_WORK, game.day_state)
    print("退勤します...")
    game.commute()
    print(f"体力: {game.player.stamina}")


def handle_shopping(game: GameManager):
    """買い出しフェーズの処理"""
    show_phase_header(GamePhase.SHOPPING, game.day_state)
    show_status(game.player, game.day_state)
    show_stock(game.stock)

    choice = show_shopping_menu(game)

    if choice == "1":
        # 買い出しに行く
        game.go_shopping()
        print(f"スーパーへ向かいます... (気力: {game.player.energy}, 体力: {game.player.stamina})")
        print()

        purchases = show_shop(game.player)

        if purchases:
            total_cost = 0
            total_items = 0
            print("\n【購入品】")
            for name, qty in purchases:
                from game.ingredients import get_ingredient
                ingredient = get_ingredient(name)
                if ingredient:
                    cost = ingredient.price * qty
                    total_cost += cost
                    total_items += qty
                    game.player.consume_money(cost)
                    game.stock.add(name, qty)
                    print(f"  {name} x{qty}")
            print(f"合計: {total_cost}円")
            print(f"残り所持金: {game.player.money:,}円")
            game.stats.record_shopping(total_cost, total_items)
        else:
            print("何も買いませんでした。")

    elif choice == "2":
        print("まっすぐ帰宅します。")


def handle_holiday_shopping(game: GameManager, phase: GamePhase):
    """休日の買い出しフェーズの処理"""
    show_phase_header(phase, game.day_state)
    show_status(game.player, game.day_state)
    show_stock(game.stock)

    choice = show_shopping_menu(game)

    if choice == "1":
        game.go_shopping()
        print(f"スーパーへ向かいます... (気力: {game.player.energy}, 体力: {game.player.stamina})")
        print()

        purchases = show_shop(game.player)

        if purchases:
            total_cost = 0
            total_items = 0
            print("\n【購入品】")
            for name, qty in purchases:
                from game.ingredients import get_ingredient
                ingredient = get_ingredient(name)
                if ingredient:
                    cost = ingredient.price * qty
                    total_cost += cost
                    total_items += qty
                    game.player.consume_money(cost)
                    game.stock.add(name, qty)
                    print(f"  {name} x{qty}")
            print(f"合計: {total_cost}円")
            print(f"残り所持金: {game.player.money:,}円")
            game.stats.record_shopping(total_cost, total_items)
        else:
            print("何も買いませんでした。")

    elif choice == "2":
        print("買い出しに行きませんでした。")


def handle_holiday_lunch(game: GameManager):
    """休日昼食フェーズの処理"""
    show_phase_header(GamePhase.HOLIDAY_LUNCH, game.day_state)
    game.reset_fullness_for_meal()

    show_status(game.player, game.day_state)
    show_stock(game.stock)
    show_recipe_suggestions(game.stock)

    choice = show_holiday_lunch_menu(game)

    if choice == "1":
        ingredients = select_ingredients(game.stock)
        if ingredients:
            dish = cook(ingredients, game.stock)
            if dish:
                game.consume_cooking_energy()
                show_dish(dish)
                game.eat_dish(dish)
                game.stats.record_meal_eaten()
                game.stats.record_cooking()
                print(f"満腹感: {game.player.fullness}")
            else:
                game.stats.record_meal_skipped()
        else:
            game.stats.record_meal_skipped()

    elif choice == "2":
        print("昼食を抜きました。")
        game.stats.record_meal_skipped()


def handle_dinner(game: GameManager):
    """夕食フェーズの処理"""
    show_phase_header(GamePhase.DINNER, game.day_state)
    game.reset_fullness_for_meal()

    show_status(game.player, game.day_state)
    show_stock(game.stock)
    show_recipe_suggestions(game.stock)

    choice = show_dinner_menu(game)

    if choice == "1":
        # 自炊
        ingredients = select_ingredients(game.stock)
        if ingredients:
            dish = cook(ingredients, game.stock)
            if dish:
                game.consume_cooking_energy()
                show_dish(dish)
                game.eat_dish(dish)
                game.stats.record_meal_eaten()
                game.stats.record_cooking()
                print(f"満腹感: {game.player.fullness}")
            else:
                game.stats.record_meal_skipped()
        else:
            game.stats.record_meal_skipped()

    elif choice == "2":
        print("夕食を抜きました。")
        game.stats.record_meal_skipped()


def handle_sleep(game: GameManager):
    """就寝フェーズの処理"""
    show_phase_header(GamePhase.SLEEP, game.day_state)

    print("1日が終わりました。")
    show_nutrition(game.day_state.daily_nutrition)

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

    game.sleep()
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
        elif phase == GamePhase.SLEEP:
            handle_sleep(game)
            game.start_new_day()

            # ゲーム終了判定
            if game.is_game_complete():
                clear_screen()
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

    # 初期化
    player = Player()
    stock = create_initial_stock()
    game = GameManager(player, stock)

    # ゲーム開始
    print(f"【初期状態】")
    show_status(player, game.day_state)
    show_stock(stock)

    # ゲームループ
    game_loop(game)

    print("\nゲーム終了。ありがとうございました！")


if __name__ == "__main__":
    main()
