"""APIエンドポイント定義"""
from fastapi import APIRouter, HTTPException

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from game.character import get_all_characters, get_character
from game.ingredients import generate_daily_shop_items, get_ingredient
from game.cooking import cook, find_named_recipe, get_available_named_recipes, evaluate_cooking
from game.relic import generate_daily_relic_items, get_relic
from game.provisions import get_all_provisions
from game.day_cycle import GamePhase
from game.events import EventTiming

from .session import create_session, get_session
from .schemas import (
    StartGameRequest, StartGameResponse,
    CookRequest, CookResponse, CookPreviewResponse,
    MakeBentoRequest, MakeBentoResponse,
    ShopBuyRequest, ShopResponse, ShopItemInfo,
    OnlineShopBuyRequest, OnlineShopResponse, OnlineProvisionInfo, OnlineRelicInfo,
    EatProvisionRequest,
    HolidayActionRequest,
    AdvancePhaseResponse,
    RecipesResponse, NamedRecipeInfo,
    GameState, PlayerState, NutritionState, StockItem, ProvisionItem,
    PreparedItem, PendingDeliveryItem, EventInfo, DishInfo, CharacterInfo,
)

router = APIRouter(prefix="/api")


# === ヘルパー関数 ===

def _build_game_state(session_id: str, game) -> GameState:
    """GameManagerからGameStateを構築"""
    player = game.player
    day_state = game.day_state
    stock = game.stock
    provisions = game.provisions
    relics = game.relics

    current_day = day_state.day

    # 在庫アイテム構築
    # stock._items は {食材名: [購入日1, 購入日2, ...]} の形式
    stock_items = []
    for name, purchase_days in stock._items.items():
        ingredient = get_ingredient(name)
        if ingredient is None:
            continue

        # 購入日ごとにグループ化して数量をカウント
        from collections import Counter
        day_counts = Counter(purchase_days)

        for purchase_day, qty in day_counts.items():
            freshness_extend = relics.get_freshness_extend_for_purchase_day(purchase_day)
            expiry_day = purchase_day + ingredient.freshness_days + freshness_extend
            days_remaining = expiry_day - current_day
            stock_items.append(StockItem(
                name=name,
                category=ingredient.category,
                quantity=qty,
                purchase_day=purchase_day,
                expiry_day=expiry_day,
                days_remaining=days_remaining,
                is_expired=days_remaining < 0,
                nutrition=NutritionState(
                    vitality=ingredient.nutrition.vitality,
                    mental=ingredient.nutrition.mental,
                    awakening=ingredient.nutrition.awakening,
                    sustain=ingredient.nutrition.sustain,
                    defense=ingredient.nutrition.defense,
                ),
                fullness=ingredient.fullness,
            ))

    # 食糧アイテム構築
    provision_items = []
    for name, qty in provisions._items.items():
        from game.provisions import get_provision
        prov = get_provision(name)
        if prov:
            provision_items.append(ProvisionItem(
                name=name,
                quantity=qty,
                nutrition=NutritionState(
                    vitality=prov.nutrition.vitality,
                    mental=prov.nutrition.mental,
                    awakening=prov.nutrition.awakening,
                    sustain=prov.nutrition.sustain,
                    defense=prov.nutrition.defense,
                ),
                fullness=prov.fullness,
                caffeine=prov.caffeine,
            ))

    # 作り置き料理
    prepared_items = []
    for prep in provisions.get_prepared(current_day):
        prepared_items.append(PreparedItem(
            name=prep.name,
            dish_type=prep.dish_type,
            nutrition=NutritionState(
                vitality=prep.nutrition.vitality,
                mental=prep.nutrition.mental,
                awakening=prep.nutrition.awakening,
                sustain=prep.nutrition.sustain,
                defense=prep.nutrition.defense,
            ),
            fullness=prep.fullness,
            expiry_day=prep.expiry_day,
        ))

    # 配送待ち
    pending_items = []
    for pending in provisions.get_pending():
        pending_items.append(PendingDeliveryItem(
            item_type=pending.item_type,
            name=pending.name,
            quantity=pending.quantity,
            delivery_day=pending.delivery_day,
        ))

    # 栄養状態
    daily_nutr = day_state.daily_nutrition
    daily_nutrition = NutritionState(
        vitality=daily_nutr.vitality,
        mental=daily_nutr.mental,
        awakening=daily_nutr.awakening,
        sustain=daily_nutr.sustain,
        defense=daily_nutr.defense,
    )

    # フェーズ表示名
    phase_names = {
        GamePhase.BREAKFAST: "朝食",
        GamePhase.GO_TO_WORK: "出勤",
        GamePhase.LUNCH: "昼食",
        GamePhase.LEAVE_WORK: "退勤",
        GamePhase.SHOPPING: "買い出し",
        GamePhase.HOLIDAY_SHOPPING_1: "買い出し（午前）",
        GamePhase.HOLIDAY_LUNCH: "昼食",
        GamePhase.HOLIDAY_SHOPPING_2: "買い出し（午後）",
        GamePhase.DINNER: "夕食",
        GamePhase.ONLINE_SHOPPING: "通販",
        GamePhase.SLEEP: "就寝",
        GamePhase.DAY_END: "1日終了",
    }

    return GameState(
        session_id=session_id,
        day=day_state.day,
        month=day_state.month,
        phase=day_state.phase.name,
        phase_display=phase_names.get(day_state.phase, day_state.phase.name),
        weather=game.get_weather_display(),
        is_holiday=game.is_holiday(),
        weekday_name=day_state.get_weekday_name(),
        player=PlayerState(
            money=player.money,
            energy=player.energy,
            stamina=player.stamina,
            fullness=player.fullness,
            card_debt=player.card_debt,
        ),
        stock=stock_items,
        provisions=provision_items,
        prepared=prepared_items,
        pending_deliveries=pending_items,
        relics=relics.get_all(),
        daily_nutrition=daily_nutrition,
        caffeine=day_state.caffeine,
        is_game_over=game.is_game_over(),
        is_game_clear=game.is_game_complete(),
        game_over_reason=game.get_game_over_reason(),
        bag_capacity=game.get_bag_capacity(),
        cooking_energy_cost=game.get_cooking_energy_cost(),
        can_cook=game.can_cook(),
        can_go_shopping=game.can_go_shopping(),
    )


def _get_game_or_404(session_id: str):
    """セッションを取得、なければ404"""
    game = get_session(session_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return game


# === キャラクター ===

@router.get("/characters")
def list_characters() -> list[CharacterInfo]:
    """キャラクター一覧を取得"""
    characters = get_all_characters()
    return [
        CharacterInfo(
            id=c.id,
            name=c.name,
            description=c.description,
            initial_money=c.initial_money,
            initial_energy=c.initial_energy,
            initial_stamina=c.initial_stamina,
            salary_amount=c.salary_amount,
            bonus_amount=c.bonus_amount,
            has_bonus=c.has_bonus,
            rent_amount=c.rent_amount,
        )
        for c in characters
    ]


# === ゲームセッション ===

@router.post("/game/start")
def start_game(request: StartGameRequest) -> StartGameResponse:
    """ゲームを開始"""
    session_id, game = create_session(request.character_id)
    state = _build_game_state(session_id, game)
    return StartGameResponse(session_id=session_id, state=state)


@router.get("/game/{session_id}/state")
def get_game_state(session_id: str) -> GameState:
    """現在のゲーム状態を取得"""
    game = _get_game_or_404(session_id)
    return _build_game_state(session_id, game)


# === 買い物 ===

@router.post("/game/{session_id}/go-shopping")
def go_shopping(session_id: str) -> GameState:
    """買い出しに行く（気力・体力を消費）"""
    game = _get_game_or_404(session_id)

    if not game.can_go_shopping():
        raise HTTPException(status_code=400, detail="Cannot go shopping (not enough energy)")

    # 買い物のイベントトリガー
    events = _trigger_events(game, EventTiming.AT_SHOP)

    # 気力・体力を消費
    game.go_shopping()

    return _build_game_state(session_id, game)


@router.get("/game/{session_id}/shop")
def get_shop(session_id: str) -> ShopResponse:
    """ショップ情報を取得"""
    game = _get_game_or_404(session_id)
    current_day = game.day_state.day

    # 日付をシードにしてショップアイテム生成
    shop_items = generate_daily_shop_items(seed=current_day)

    items = []
    for item in shop_items:
        ing = item.ingredient
        items.append(ShopItemInfo(
            name=ing.name,
            category=ing.category,
            price=item.price,
            quantity=item.quantity,
            is_sale=item.is_sale,
            nutrition=NutritionState(
                vitality=ing.nutrition.vitality,
                mental=ing.nutrition.mental,
                awakening=ing.nutrition.awakening,
                sustain=ing.nutrition.sustain,
                defense=ing.nutrition.defense,
            ),
            fullness=ing.fullness,
            expiry_days=ing.freshness_days,
        ))

    return ShopResponse(
        items=items,
        bag_capacity=game.get_bag_capacity(),
        player_money=game.player.money,
    )


@router.post("/game/{session_id}/shop/buy")
def buy_from_shop(session_id: str, request: ShopBuyRequest) -> GameState:
    """ショップで購入"""
    game = _get_game_or_404(session_id)
    current_day = game.day_state.day

    shop_items = generate_daily_shop_items(seed=current_day)
    shop_dict = {item.ingredient.name: item for item in shop_items}

    total_cost = 0
    total_items = 0

    for item in request.items:
        name = item.get("ingredient_name")
        qty = item.get("quantity", 1)

        if name not in shop_dict:
            raise HTTPException(status_code=400, detail=f"Item not found: {name}")

        shop_item = shop_dict[name]
        cost = shop_item.price * qty
        total_cost += cost
        total_items += qty

    # バッグ容量チェック
    if total_items > game.get_bag_capacity():
        raise HTTPException(status_code=400, detail="Bag capacity exceeded")

    # 所持金チェック
    if total_cost > game.player.money:
        raise HTTPException(status_code=400, detail="Not enough money")

    # 購入処理
    for item in request.items:
        name = item.get("ingredient_name")
        qty = item.get("quantity", 1)
        shop_item = shop_dict[name]

        game.player.consume_money(shop_item.price * qty)
        game.stock.add(name, qty, current_day)
        game.stats.record_shopping(shop_item.price * qty)

    return _build_game_state(session_id, game)


# === 通販 ===

@router.get("/game/{session_id}/online-shop")
def get_online_shop(session_id: str) -> OnlineShopResponse:
    """通販情報を取得"""
    game = _get_game_or_404(session_id)
    current_day = game.day_state.day

    # 食糧
    all_provisions = get_all_provisions()
    provisions = []
    for prov in all_provisions:
        provisions.append(OnlineProvisionInfo(
            name=prov.name,
            price=prov.price,
            is_sale=False,  # TODO: セール処理
            nutrition=NutritionState(
                vitality=prov.nutrition.vitality,
                mental=prov.nutrition.mental,
                awakening=prov.nutrition.awakening,
                sustain=prov.nutrition.sustain,
                defense=prov.nutrition.defense,
            ),
            fullness=prov.fullness,
            caffeine=prov.caffeine,
        ))

    # レリック
    owned_relics = set(game.relics.get_all())
    pending_relics = set(
        p.name for p in game.provisions.get_pending()
        if p.item_type == "relic"
    )
    relic_items = generate_daily_relic_items(
        seed=current_day,
        owned_relics=owned_relics,
        pending_relics=pending_relics,
    )

    relics = []
    for item in relic_items:
        r = item.relic
        relics.append(OnlineRelicInfo(
            name=r.name,
            description=r.description,
            price=item.price,
            is_sale=item.is_sale,
            effect_type=r.effect_type,
            effect_value=r.effect_value,
            is_owned=r.name in owned_relics,
            is_pending=r.name in pending_relics,
        ))

    return OnlineShopResponse(
        provisions=provisions,
        relics=relics,
        player_money=game.player.money,
        card_debt=game.player.card_debt,
    )


@router.post("/game/{session_id}/online-shop/buy")
def buy_from_online_shop(session_id: str, request: OnlineShopBuyRequest) -> GameState:
    """通販で購入（翌日配送、カード払い）"""
    game = _get_game_or_404(session_id)

    if request.item_type == "provision":
        from game.provisions import get_provision
        prov = get_provision(request.item_name)
        if prov is None:
            raise HTTPException(status_code=400, detail=f"Provision not found: {request.item_name}")

        total = prov.price * request.quantity
        game.player.add_card_debt(total)
        game.add_pending_delivery("provision", request.item_name, request.quantity)

    elif request.item_type == "relic":
        relic = get_relic(request.item_name)
        if relic is None:
            raise HTTPException(status_code=400, detail=f"Relic not found: {request.item_name}")

        # 既に所持or配送待ちチェック
        if game.relics.has(request.item_name):
            raise HTTPException(status_code=400, detail="Already owned")
        pending_names = [p.name for p in game.provisions.get_pending() if p.item_type == "relic"]
        if request.item_name in pending_names:
            raise HTTPException(status_code=400, detail="Already pending")

        game.player.add_card_debt(relic.price)
        game.add_pending_delivery("relic", request.item_name, 1)

    else:
        raise HTTPException(status_code=400, detail=f"Invalid item_type: {request.item_type}")

    return _build_game_state(session_id, game)


# === 調理 ===

@router.get("/game/{session_id}/recipes")
def get_recipes(session_id: str) -> RecipesResponse:
    """作成可能なネームド料理を取得"""
    game = _get_game_or_404(session_id)
    current_day = game.day_state.day

    # 利用可能な食材名リスト
    available = game.stock.get_available_ingredients()

    recipes = get_available_named_recipes(available)
    return RecipesResponse(
        available=[
            NamedRecipeInfo(
                name=r.name,
                required_ingredients=list(r.required_ingredients),
                nutrition_multiplier=r.nutrition_multiplier,
                fullness_bonus=r.fullness_bonus,
                can_make=True,
            )
            for r in recipes
        ]
    )


@router.post("/game/{session_id}/cook/preview")
def cook_preview(session_id: str, request: CookRequest) -> CookPreviewResponse:
    """調理プレビュー（確認用）"""
    game = _get_game_or_404(session_id)

    if not request.ingredient_names:
        raise HTTPException(status_code=400, detail="No ingredients selected")

    # 調理可能かチェック
    can_make = game.can_cook() and not game.stock.is_empty()

    # ネームド料理判定
    named_recipe = find_named_recipe(request.ingredient_names)

    # 料理名を決定
    if named_recipe:
        dish_name = named_recipe.name
    else:
        # 適当な名前を生成
        dish_name = "炒め物" if len(request.ingredient_names) > 1 else f"{request.ingredient_names[0]}料理"

    # 栄養値を計算（プレビュー用）
    from game.ingredients import get_ingredient
    total_nutrition = {"vitality": 0, "mental": 0, "awakening": 0, "sustain": 0, "defense": 0}
    total_fullness = 0

    for name in request.ingredient_names:
        ing = get_ingredient(name)
        if ing:
            total_nutrition["vitality"] += ing.nutrition.vitality
            total_nutrition["mental"] += ing.nutrition.mental
            total_nutrition["awakening"] += ing.nutrition.awakening
            total_nutrition["sustain"] += ing.nutrition.sustain
            total_nutrition["defense"] += ing.nutrition.defense
            total_fullness += ing.fullness

    # ネームド料理ボーナス
    if named_recipe:
        for key in total_nutrition:
            total_nutrition[key] = int(total_nutrition[key] * named_recipe.nutrition_multiplier)
        total_fullness += named_recipe.fullness_bonus

    # 調理評価
    evaluation = evaluate_cooking(request.ingredient_names)
    if evaluation.fullness_good and evaluation.nutrition_good:
        comment = "これなら腹いっぱいだし栄養もいいだろう！"
    elif evaluation.fullness_good:
        comment = "量は十分だが、栄養が偏っているな..."
    elif evaluation.nutrition_good:
        comment = "栄養はいいが、これでは物足りないな..."
    else:
        comment = "これでは腹も空くし、栄養も偏っているだろう..."

    return CookPreviewResponse(
        dish_name=dish_name,
        nutrition=NutritionState(
            vitality=total_nutrition["vitality"],
            mental=total_nutrition["mental"],
            awakening=total_nutrition["awakening"],
            sustain=total_nutrition["sustain"],
            defense=total_nutrition["defense"],
        ),
        fullness=total_fullness,
        is_named=named_recipe is not None,
        named_recipe_name=named_recipe.name if named_recipe else None,
        evaluation_comment=comment,
        can_make=can_make,
    )


@router.post("/game/{session_id}/cook/confirm")
def cook_confirm(session_id: str, request: CookRequest) -> CookResponse:
    """調理を確定実行"""
    game = _get_game_or_404(session_id)
    current_day = game.day_state.day

    if not game.can_cook():
        raise HTTPException(status_code=400, detail="Cannot cook (not enough energy or no ingredients)")

    if not request.ingredient_names:
        raise HTTPException(status_code=400, detail="No ingredients selected")

    # 調理評価
    evaluation = evaluate_cooking(request.ingredient_names)
    if evaluation.fullness_good and evaluation.nutrition_good:
        comment = "これなら腹いっぱいだし栄養もいいだろう！"
    elif evaluation.fullness_good:
        comment = "量は十分だが、栄養が偏っているな..."
    elif evaluation.nutrition_good:
        comment = "栄養はいいが、これでは物足りないな..."
    else:
        comment = "これでは腹も空くし、栄養も偏っているだろう..."

    # 調理実行
    dish = cook(request.ingredient_names, game.stock, current_day, game.relics)
    if dish is None:
        raise HTTPException(status_code=400, detail="Cooking failed")

    # 気力消費・食事
    game.consume_cooking_energy()
    game.eat_dish(dish)
    game.stats.record_meal_eaten()
    game.stats.record_cooking()

    # ネームド料理判定
    named_recipe = find_named_recipe(request.ingredient_names)

    dish_info = DishInfo(
        name=dish.name,
        nutrition=NutritionState(
            vitality=dish.nutrition.vitality,
            mental=dish.nutrition.mental,
            awakening=dish.nutrition.awakening,
            sustain=dish.nutrition.sustain,
            defense=dish.nutrition.defense,
        ),
        fullness=dish.fullness,
        ingredients=dish.ingredients_used,
        is_named=named_recipe is not None,
        named_recipe_name=named_recipe.name if named_recipe else None,
    )

    return CookResponse(
        dish=dish_info,
        state=_build_game_state(session_id, game),
        evaluation_comment=comment,
    )


# === 食糧消費 ===

@router.post("/game/{session_id}/eat-provision")
def eat_provision(session_id: str, request: EatProvisionRequest) -> GameState:
    """食糧を消費"""
    game = _get_game_or_404(session_id)

    from game.provisions import get_provision

    for name in request.provision_names:
        prov = get_provision(name)
        if prov is None:
            continue

        if game.provisions.get_quantity(name) <= 0:
            continue

        game.provisions.remove(name)
        game.player.add_fullness(prov.fullness)
        game.day_state.daily_nutrition.add(prov.nutrition)

        if prov.caffeine > 0:
            game.add_caffeine(prov.caffeine)

        game.stats.record_meal_eaten()

    return _build_game_state(session_id, game)


@router.post("/game/{session_id}/eat-prepared")
def eat_prepared(session_id: str, prepared_index: int) -> GameState:
    """作り置き料理を食べる"""
    game = _get_game_or_404(session_id)
    current_day = game.day_state.day

    # 作り置きリストを取得
    prepared_list = game.provisions.get_prepared(current_day)
    if prepared_index < 0 or prepared_index >= len(prepared_list):
        raise HTTPException(status_code=400, detail="Invalid prepared dish index")

    # 作り置きを削除して食べる
    dish = game.provisions.remove_prepared(prepared_index)
    if dish is None:
        raise HTTPException(status_code=400, detail="Failed to remove prepared dish")

    game.player.add_fullness(dish.fullness)
    game.day_state.daily_nutrition.add(dish.nutrition)
    game.stats.record_meal_eaten()

    return _build_game_state(session_id, game)


@router.post("/game/{session_id}/eat-cafeteria")
def eat_cafeteria(session_id: str) -> GameState:
    """社食を食べる（平日昼食用）"""
    game = _get_game_or_404(session_id)

    CAFETERIA_COST = 500

    if game.player.money < CAFETERIA_COST:
        raise HTTPException(status_code=400, detail="Not enough money for cafeteria")

    # 社食を食べる
    game.player.money -= CAFETERIA_COST

    # 社食の栄養（固定値）
    from game.nutrition import Nutrition
    cafeteria_nutrition = Nutrition(vitality=3, mental=2, awakening=1, sustain=3, defense=2)
    cafeteria_fullness = 7

    game.player.add_fullness(cafeteria_fullness)
    game.day_state.daily_nutrition.add(cafeteria_nutrition)
    game.stats.record_meal_eaten()

    return _build_game_state(session_id, game)


@router.post("/game/{session_id}/make-bento")
def make_bento(session_id: str, request: MakeBentoRequest) -> MakeBentoResponse:
    """弁当を作成"""
    game = _get_game_or_404(session_id)
    current_day = game.day_state.day

    if not game.can_make_bento():
        raise HTTPException(status_code=400, detail="Cannot make bento")

    if not request.ingredient_names:
        raise HTTPException(status_code=400, detail="No ingredients selected")

    # 弁当を調理（食べない）
    dish = cook(request.ingredient_names, game.stock, current_day, game.relics)
    if dish is None:
        raise HTTPException(status_code=400, detail="Cooking failed")

    # 弁当作成の気力消費
    game.consume_bento_energy()

    # 弁当として食糧ストックに追加
    game.add_bento(dish)
    game.stats.record_bento()

    return MakeBentoResponse(
        bento_name=dish.name,
        state=_build_game_state(session_id, game),
    )


# === ヘルパー: イベントトリガー ===

def _trigger_events(game, timing: EventTiming) -> list[EventInfo]:
    """イベントをトリガーし、EventInfoリストを返す"""
    context = game.get_event_context()
    results = game.events.check_and_trigger_events(timing, context, game)
    return [
        EventInfo(
            id=r.event.id,
            name=r.event.name,
            description=r.message,
            timing=timing.name,
        )
        for r in results
    ]


# === フェーズ進行 ===

@router.post("/game/{session_id}/advance-phase")
def advance_phase(session_id: str) -> AdvancePhaseResponse:
    """フェーズを進行"""
    game = _get_game_or_404(session_id)

    events = []
    deliveries = []
    salary_info = None
    bonus_info = None

    # UIが不要なフェーズは自動スキップ（出勤・退勤のみ）
    auto_skip_phases = [
        GamePhase.GO_TO_WORK,
        GamePhase.LEAVE_WORK,
    ]

    while True:
        current_phase = game.get_current_phase()

        # 特定フェーズでの処理
        if current_phase == GamePhase.DINNER:
            # 配送処理
            delivered = game.process_deliveries()
            for d in delivered:
                deliveries.append(PendingDeliveryItem(
                    item_type=d.item_type,
                    name=d.name,
                    quantity=d.quantity,
                    delivery_day=d.delivery_day,
                ))

        elif current_phase == GamePhase.GO_TO_WORK:
            # 出勤イベント
            events.extend(_trigger_events(game, EventTiming.GO_TO_WORK))
            game.commute()

        elif current_phase == GamePhase.LEAVE_WORK:
            # 退勤イベント
            events.extend(_trigger_events(game, EventTiming.LEAVE_WORK))
            game.commute()

        elif current_phase == GamePhase.SLEEP:
            # 就寝処理
            has_insomnia = game.sleep()
            game.start_new_day()

            # 起床イベント
            events.extend(_trigger_events(game, EventTiming.WAKE_UP))

            # 給料日チェック
            if game.is_payday():
                gross, rent, net = game.pay_salary()
                salary_info = {"gross": gross, "rent": rent, "net": net}

                if game.is_bonus_day():
                    bonus = game.pay_bonus()
                    bonus_info = {"amount": bonus}

            # 天気決定
            game.determine_weather()

        # フェーズ進行
        if current_phase != GamePhase.SLEEP:
            game.advance_phase()

        # 次のフェーズがUIを必要とするか確認
        next_phase = game.get_current_phase()
        if next_phase not in auto_skip_phases:
            break

    return AdvancePhaseResponse(
        events=events,
        state=_build_game_state(session_id, game),
        deliveries=deliveries,
        salary_info=salary_info,
        bonus_info=bonus_info,
    )


# === 休日アクション ===

@router.post("/game/{session_id}/holiday-action")
def holiday_action(session_id: str, request: HolidayActionRequest) -> GameState:
    """休日アクションを実行"""
    game = _get_game_or_404(session_id)

    if not game.is_holiday():
        raise HTTPException(status_code=400, detail="Not a holiday")

    if request.action == "rest":
        # 休養: 気力+2, 体力+1
        game.player.energy = min(game.player.energy + 2, 10)
        game.player.stamina = min(game.player.stamina + 1, 10)

    # local, outing, prep はフロントエンド側で処理を分岐

    return _build_game_state(session_id, game)
