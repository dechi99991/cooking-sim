"""1日の流れ管理"""
from dataclasses import dataclass, field
from enum import Enum, auto
from .player import Player
from .nutrition import Nutrition
from .ingredients import Stock
from .cooking import Dish
from .result import GameStats, GameResult
from .relic import RelicInventory
from .provisions import ProvisionStock
from .events import EventManager
from .event_data import register_all_events
from .character import get_character
from .temperament import BehaviorTracker, get_temperament, calculate_nutrition_balance
from .constants import (
    COOKING_ENERGY_COST, BENTO_ENERGY_COST, COMMUTE_STAMINA_COST,
    CAFETERIA_PRICE, SLEEP_ENERGY_RECOVERY, SLEEP_STAMINA_RECOVERY,
    GAME_START_MONTH, GAME_START_DAY, GAME_DURATION_DAYS,
    SHOPPING_ENERGY_COST, SHOPPING_STAMINA_COST, SHOPPING_MIN_ENERGY,
    SHOPPING_BAG_CAPACITY,
    SALARY_AMOUNT, SALARY_DAY, BONUS_AMOUNT, BONUS_MONTHS,
    CAFFEINE_INSOMNIA_THRESHOLD, CAFFEINE_ENERGY_PENALTY, CAFFEINE_STAMINA_PENALTY,
    NUTRITION_HIGH_THRESHOLD, NUTRITION_STREAK_FOR_CAP
)


class MealTime(Enum):
    BREAKFAST = auto()
    LUNCH = auto()
    DINNER = auto()


class GamePhase(Enum):
    # 共通フェーズ
    BREAKFAST = auto()
    # 平日フェーズ
    GO_TO_WORK = auto()
    LUNCH = auto()
    LEAVE_WORK = auto()
    SHOPPING = auto()
    # 休日フェーズ
    HOLIDAY_SHOPPING_1 = auto()  # 朝食後の買い出し
    HOLIDAY_LUNCH = auto()
    HOLIDAY_SHOPPING_2 = auto()  # 昼食後の買い出し
    # 共通フェーズ
    DINNER = auto()
    ONLINE_SHOPPING = auto()  # 通販（夕食後）
    SLEEP = auto()
    DAY_END = auto()


# 平日のフェーズ順序
WEEKDAY_PHASES = [
    GamePhase.BREAKFAST,
    GamePhase.GO_TO_WORK,
    GamePhase.LUNCH,
    GamePhase.LEAVE_WORK,
    GamePhase.SHOPPING,
    GamePhase.DINNER,
    GamePhase.ONLINE_SHOPPING,
    GamePhase.SLEEP,
]

# 休日のフェーズ順序
HOLIDAY_PHASES = [
    GamePhase.BREAKFAST,
    GamePhase.HOLIDAY_SHOPPING_1,
    GamePhase.HOLIDAY_LUNCH,
    GamePhase.HOLIDAY_SHOPPING_2,
    GamePhase.DINNER,
    GamePhase.ONLINE_SHOPPING,
    GamePhase.SLEEP,
]

# 曜日名
WEEKDAY_NAMES = ['月', '火', '水', '木', '金', '土', '日']


@dataclass
class DayState:
    """1日の状態を管理"""
    day: int = GAME_START_DAY
    month: int = GAME_START_MONTH
    phase: GamePhase = GamePhase.BREAKFAST
    daily_nutrition: Nutrition = field(default_factory=Nutrition)
    caffeine: int = 0  # 1日のカフェイン摂取量

    def get_weekday(self) -> int:
        """曜日を取得 (0=月, 1=火, ..., 5=土, 6=日)"""
        # 4月1日を火曜日(1)とする
        return (self.day) % 7

    def get_weekday_name(self) -> str:
        """曜日名を取得（土日は「週末」）"""
        weekday = self.get_weekday()
        if weekday >= 5:  # 土日
            return '週末'
        return WEEKDAY_NAMES[weekday]

    def is_holiday(self) -> bool:
        """休日かどうか (土日)"""
        weekday = self.get_weekday()
        return weekday >= 5  # 5=土, 6=日

    def is_weekend(self) -> bool:
        """週末かどうか（土日）- is_holidayのエイリアス"""
        return self.is_holiday()

    def is_friday(self) -> bool:
        """金曜日かどうか"""
        return self.get_weekday() == 4

    def get_current_phases(self) -> list:
        """現在の日のフェーズ順序を取得"""
        return HOLIDAY_PHASES if self.is_holiday() else WEEKDAY_PHASES

    def next_phase(self):
        """次のフェーズへ進む"""
        phases = self.get_current_phases()
        current_index = phases.index(self.phase)
        if current_index < len(phases) - 1:
            self.phase = phases[current_index + 1]

    def start_new_day(self):
        """新しい日を開始（土曜日は日曜をスキップして2日進む）"""
        # 土曜日（weekday=5）の場合、日曜をスキップして月曜へ
        if self.get_weekday() == 5:
            self.day += 2  # 土→月
        else:
            self.day += 1
        self.phase = GamePhase.BREAKFAST
        self.daily_nutrition.reset()
        self.caffeine = 0

    def add_caffeine(self, amount: int):
        """カフェインを摂取"""
        self.caffeine += amount

    def get_date_string(self) -> str:
        """日付文字列を取得"""
        return f"{self.month}月{self.day}日({self.get_weekday_name()})"

    def is_game_complete(self) -> bool:
        """ゲームクリア判定"""
        return self.day > GAME_DURATION_DAYS


@dataclass
class AutoConsumeResult:
    """カフェイン自動消費の結果"""
    consumed_name: str
    caffeine_amount: int
    energy_restored: int
    will_cause_insomnia: bool


@dataclass
class WeeklyStats:
    """週間統計を管理（金曜ボスイベント用）"""
    nutrition: Nutrition = field(default_factory=Nutrition)  # 週間累計栄養
    food_spending: int = 0  # 週間食費支出
    meals_cooked: int = 0   # 自炊回数
    days_tracked: int = 0   # 追跡日数

    def add_daily(self, daily_nutrition: Nutrition, daily_spending: int, cooked: bool):
        """1日分を追加"""
        self.nutrition.add(daily_nutrition)
        self.food_spending += daily_spending
        if cooked:
            self.meals_cooked += 1
        self.days_tracked += 1

    def reset(self):
        """週の開始時にリセット"""
        self.nutrition = Nutrition()
        self.food_spending = 0
        self.meals_cooked = 0
        self.days_tracked = 0

    def evaluate(self) -> dict:
        """週間評価を計算"""
        # 栄養評価: 各栄養素が閾値(25)以上かチェック
        threshold = 25  # 5日 * 5
        nutrients_ok = 0
        if self.nutrition.vitality >= threshold:
            nutrients_ok += 1
        if self.nutrition.mental >= threshold:
            nutrients_ok += 1
        if self.nutrition.awakening >= threshold:
            nutrients_ok += 1
        if self.nutrition.sustain >= threshold:
            nutrients_ok += 1
        if self.nutrition.defense >= threshold:
            nutrients_ok += 1

        nutrition_grades = ['E', 'D', 'C', 'B', 'A', 'S']
        nutrition_grade = nutrition_grades[nutrients_ok]

        # 節約評価
        budget = 7000  # 週間予算
        saving_success = self.food_spending <= budget
        overspending = self.food_spending > budget * 1.5

        return {
            'nutrition_grade': nutrition_grade,
            'nutrients_ok': nutrients_ok,
            'saving_success': saving_success,
            'overspending': overspending,
            'food_spending': self.food_spending,
            'meals_cooked': self.meals_cooked,
            'days_tracked': self.days_tracked,
        }


@dataclass
class NutritionStreak:
    """栄養素の連続日数トラッキング

    各栄養素が「高い」状態（閾値以上）を何日連続で達成したかを追跡する。
    活力素・覚醒素の連続高値は上限増加イベントの条件となる。
    """
    vitality: int = 0   # 活力素の連続高値日数
    mental: int = 0     # 心力素の連続高値日数
    awakening: int = 0  # 覚醒素の連続高値日数
    sustain: int = 0    # 持続素の連続高値日数
    defense: int = 0    # 防衛素の連続高値日数

    def update(self, daily_nutrition: Nutrition, threshold: int = NUTRITION_HIGH_THRESHOLD):
        """1日の栄養に基づいてストリークを更新"""
        self.vitality = self.vitality + 1 if daily_nutrition.vitality >= threshold else 0
        self.mental = self.mental + 1 if daily_nutrition.mental >= threshold else 0
        self.awakening = self.awakening + 1 if daily_nutrition.awakening >= threshold else 0
        self.sustain = self.sustain + 1 if daily_nutrition.sustain >= threshold else 0
        self.defense = self.defense + 1 if daily_nutrition.defense >= threshold else 0

    def reset(self, nutrient: str):
        """特定の栄養素のストリークをリセット（イベント発生後など）"""
        if nutrient == 'vitality':
            self.vitality = 0
        elif nutrient == 'mental':
            self.mental = 0
        elif nutrient == 'awakening':
            self.awakening = 0
        elif nutrient == 'sustain':
            self.sustain = 0
        elif nutrient == 'defense':
            self.defense = 0


class GameManager:
    """ゲーム全体を管理するクラス"""

    def __init__(self, player: Player, stock: Stock,
                 has_bonus: bool = True,
                 salary_amount: int | None = None,
                 bonus_amount: int | None = None,
                 rent_amount: int = 0,
                 with_initial_relics: bool = True,
                 character_id: str = 'regular'):
        self.player = player
        self.stock = stock
        self.character_id = character_id  # キャラクターID
        self.day_state = DayState()
        self.stats = GameStats()  # 統計収集用
        self.relics = RelicInventory()  # レリック所持
        self.provisions = ProvisionStock()  # 食糧ストック
        self.events = EventManager()  # イベント管理
        register_all_events(self.events)  # 全イベントを登録
        self.has_bonus = has_bonus  # ボーナスの有無（キャラ設定用）
        self.nutrition_streak = NutritionStreak()  # 栄養素連続高値トラッキング
        self.behavior_tracker = BehaviorTracker()  # 行動トラッカー（気質判定用）
        self.weekly_stats = WeeklyStats()  # 週間統計（金曜ボスイベント用）
        self._daily_food_spending = 0  # 1日の食費追跡
        self._daily_cooked = False  # 1日に自炊したか
        self.temperament_id: str | None = None  # 判定された気質ID
        self.temperament_just_revealed: bool = False  # 気質が今発表されたかどうか
        # キャラクター別の給料・ボーナス・家賃
        self._salary_amount = salary_amount if salary_amount is not None else SALARY_AMOUNT
        self._bonus_amount = bonus_amount if bonus_amount is not None else BONUS_AMOUNT
        self._rent_amount = rent_amount  # 家賃（給料から天引き）
        # 初期レリック（冷蔵庫・電子レンジ）
        if with_initial_relics:
            self.relics.add_initial_relics()

    def get_cooking_energy_cost(self) -> int:
        """レリック効果を反映した調理気力コストを取得"""
        base_cost = COOKING_ENERGY_COST
        save = self.relics.get_energy_save()
        return max(1, base_cost - save)  # 最低1

    def get_bento_energy_cost(self) -> int:
        """レリック効果を反映した弁当作成気力コストを取得"""
        base_cost = BENTO_ENERGY_COST
        save = self.relics.get_energy_save()
        return max(1, base_cost - save)  # 最低1

    def can_cook(self) -> bool:
        """調理可能か"""
        return self.player.can_cook(self.get_cooking_energy_cost()) and not self.stock.is_empty()

    def can_make_bento(self) -> bool:
        """弁当作成可能か"""
        return self.player.can_cook(self.get_bento_energy_cost()) and not self.stock.is_empty()

    def can_use_cafeteria(self) -> bool:
        """社食利用可能か"""
        return self.player.money >= CAFETERIA_PRICE

    def consume_cooking_energy(self) -> AutoConsumeResult | None:
        """調理の気力を消費（レリック効果適用、カフェイン自動消費）"""
        cost = self.get_cooking_energy_cost()
        auto_result = self.try_auto_consume_caffeine(cost)
        self.player.consume_energy(cost)
        return auto_result

    def consume_bento_energy(self) -> AutoConsumeResult | None:
        """弁当作成の気力を消費（レリック効果適用、カフェイン自動消費）"""
        cost = self.get_bento_energy_cost()
        auto_result = self.try_auto_consume_caffeine(cost)
        self.player.consume_energy(cost)
        return auto_result

    def consume_cafeteria_cost(self):
        """社食の費用を消費"""
        self.player.consume_money(CAFETERIA_PRICE)

    def eat_dish(self, dish: Dish):
        """料理を食べる"""
        actual_fullness = self.player.add_fullness(dish.fullness)
        self.day_state.daily_nutrition.add(dish.nutrition)
        return actual_fullness

    def add_bento(self, dish: Dish):
        """弁当を食糧ストックに追加（当日期限）"""
        current_day = self.day_state.day
        self.provisions.add_prepared(
            dish_name=dish.name,
            nutrition=dish.nutrition,
            fullness=dish.fullness,
            expiry_day=current_day,  # 当日中のみ有効
            dish_type="弁当"
        )

    def has_bento(self) -> bool:
        """弁当があるか確認"""
        return self.provisions.has_prepared(self.day_state.day)

    def get_bentos(self) -> list:
        """利用可能な弁当リストを取得"""
        from .provisions import PreparedDish
        return self.provisions.get_prepared(self.day_state.day)

    def add_caffeine(self, amount: int):
        """カフェインを摂取"""
        self.day_state.add_caffeine(amount)

    def get_caffeine(self) -> int:
        """現在のカフェイン摂取量を取得"""
        return self.day_state.caffeine

    def will_have_insomnia(self) -> bool:
        """現在のカフェイン量で不眠になるかどうか"""
        return self.day_state.caffeine >= CAFFEINE_INSOMNIA_THRESHOLD

    def try_auto_consume_caffeine(self, energy_needed: int) -> AutoConsumeResult | None:
        """気力が足りない場合にカフェイン飲料を自動消費する

        Args:
            energy_needed: 必要な気力

        Returns:
            消費した場合はAutoConsumeResult、しなかった場合はNone
        """
        from .provisions import get_provision

        # 気力が足りている場合は何もしない
        if self.player.energy >= energy_needed:
            return None

        # カフェイン飲料を取得（カフェイン量が少ない順）
        caffeinated = self.provisions.get_caffeinated_provisions()
        if not caffeinated:
            return None

        # 最もカフェイン量が少ない飲料を消費
        name, caffeine, qty = caffeinated[0]
        prov = get_provision(name)
        if not prov:
            return None

        # 消費処理
        self.provisions.remove(name, 1)
        energy_boost = caffeine * 2
        self.player.energy = min(self.player.energy + energy_boost, 10)
        self.add_caffeine(caffeine)

        # 栄養・満腹度も追加
        self.day_state.daily_nutrition.add(prov.nutrition)
        self.player.add_fullness(prov.fullness)

        return AutoConsumeResult(
            consumed_name=name,
            caffeine_amount=caffeine,
            energy_restored=energy_boost,
            will_cause_insomnia=self.will_have_insomnia()
        )

    def commute(self):
        """出退勤処理"""
        self.player.consume_stamina(COMMUTE_STAMINA_COST)

    def can_go_shopping(self) -> bool:
        """買い出し可能か"""
        return self.player.energy >= SHOPPING_MIN_ENERGY

    def go_shopping(self) -> AutoConsumeResult | None:
        """買い出しの気力・体力を消費（カフェイン自動消費）"""
        auto_result = self.try_auto_consume_caffeine(SHOPPING_ENERGY_COST)
        # 体力消費を先に（根性回復が必要な場合、気力を使うため）
        self.player.consume_stamina(SHOPPING_STAMINA_COST)
        self.player.consume_energy(SHOPPING_ENERGY_COST)
        return auto_result

    def sleep(self) -> bool:
        """就寝処理。不眠が発生したらTrueを返す"""
        # ペナルティ計算
        energy_penalty, stamina_penalty, fullness_penalty = \
            self.day_state.daily_nutrition.calculate_penalties()
        self.player.apply_penalties(energy_penalty, stamina_penalty, fullness_penalty)

        # 統計記録: 栄養ペナルティ
        if energy_penalty > 0:
            self.stats.record_nutrition_penalty('心力素')
        if stamina_penalty > 0:
            self.stats.record_nutrition_penalty('活力素')
        if fullness_penalty > 0:
            self.stats.record_nutrition_penalty('持続素')

        # バランス良い日かどうか
        if energy_penalty == 0 and stamina_penalty == 0 and fullness_penalty == 0:
            self.stats.record_balanced_day()

        # カフェインによる不眠チェック
        has_insomnia = self.day_state.caffeine >= CAFFEINE_INSOMNIA_THRESHOLD
        if has_insomnia:
            # 不眠ペナルティを追加適用
            self.player.energy_recovery_penalty += CAFFEINE_ENERGY_PENALTY
            self.player.stamina_recovery_penalty += CAFFEINE_STAMINA_PENALTY
            self.stats.record_insomnia()

        # 回復（掃除・整理ボーナス + 気質ボーナスを含む）
        sleep_bonus = self.player.next_sleep_bonus + self.get_temperament_sleep_bonus()
        self.player.recover_energy(SLEEP_ENERGY_RECOVERY + sleep_bonus)
        self.player.recover_stamina(SLEEP_STAMINA_RECOVERY + sleep_bonus)
        self.player.next_sleep_bonus = 0  # 一時ボーナスをリセット

        return has_insomnia

    def advance_phase(self):
        """フェーズを進める"""
        self.day_state.next_phase()

    def start_new_day(self):
        """新しい日を開始"""
        # 栄養ストリークを更新（栄養リセット前に）
        self.nutrition_streak.update(self.day_state.daily_nutrition)

        # 行動トラッカー: 栄養バランスを記録（3日目まで）
        if self.day_state.day <= 3:
            balance = calculate_nutrition_balance(self.day_state.daily_nutrition)
            self.behavior_tracker.record_nutrition_balance(balance)

        # 週間統計に本日分を追加（平日のみ: 月～金）
        weekday = self.day_state.get_weekday()
        if weekday < 5:  # 月～金
            self.weekly_stats.add_daily(
                self.day_state.daily_nutrition,
                self._daily_food_spending,
                self._daily_cooked
            )

        self.player.clear_penalties()
        self.player.reset_fullness()

        # 現在の曜日を保存（日付進行後の判定に使用）
        was_weekend = weekday >= 5

        self.day_state.start_new_day()

        # 週末から月曜日に移行したら週間統計をリセット
        if was_weekend:
            self.weekly_stats.reset()

        # 日次の食費・自炊フラグをリセット
        self._daily_food_spending = 0
        self._daily_cooked = False

        # 期限切れの弁当などを削除
        self.provisions.remove_expired_prepared(self.day_state.day)
        # イベントの日次リセット
        self.events.new_day()

        # 4日目の朝に気質を判定
        self.temperament_just_revealed = False
        if self.day_state.day == 4 and self.temperament_id is None:
            self.temperament_id = self.behavior_tracker.determine_temperament()
            self.temperament_just_revealed = True

    def process_deliveries(self) -> list:
        """配送処理。届いた商品リストを返す"""
        from .provisions import PendingDelivery
        current_day = self.day_state.day
        delivered = self.provisions.process_deliveries(current_day)

        # レリックの配送処理（取得日を記録）
        for item in delivered:
            if item.item_type == "relic":
                self.relics.add(item.name, current_day)

        return delivered

    def add_pending_delivery(self, item_type: str, name: str, quantity: int = 1):
        """翌日配送の商品を追加"""
        delivery_day = self.day_state.day + 1
        self.provisions.add_pending(item_type, name, quantity, delivery_day)

    def is_game_over(self) -> bool:
        """ゲームオーバー判定"""
        return self.player.is_game_over()

    def is_game_complete(self) -> bool:
        """ゲームクリア判定"""
        return self.day_state.is_game_complete()

    def get_current_phase(self) -> GamePhase:
        """現在のフェーズを取得"""
        return self.day_state.phase

    def reset_fullness_for_meal(self):
        """食事ターン開始時に満腹感をリセット"""
        self.player.reset_fullness()

    def is_holiday(self) -> bool:
        """休日かどうか"""
        return self.day_state.is_holiday()

    def is_friday(self) -> bool:
        """金曜日かどうか"""
        return self.day_state.is_friday()

    def is_weekend(self) -> bool:
        """週末かどうか"""
        return self.day_state.is_weekend()

    def record_food_spending(self, amount: int):
        """食費支出を記録"""
        self._daily_food_spending += amount

    def record_daily_cook(self):
        """本日自炊したことを記録"""
        self._daily_cooked = True

    def get_freshness_extend(self) -> int:
        """レリック効果による鮮度延長日数を取得"""
        return self.relics.get_freshness_extend()

    def get_bag_capacity(self) -> int:
        """買い物バッグ容量を取得（レリック効果込み）

        買い物は帰宅（DINNER）前に行われるため、当日届いたレリックは
        翌日の買い物から効果を発揮する。
        """
        current_day = self.day_state.day
        return SHOPPING_BAG_CAPACITY + self.relics.get_bag_capacity_boost(current_day)

    def is_payday(self) -> bool:
        """今日が給料日かどうか（25日が週末の場合は金曜に前倒し）"""
        day = self.day_state.day

        # 通常の25日チェック
        if day == SALARY_DAY:
            return True

        # 25日が土曜(weekday=5)の場合、24日(金)に前倒し
        # 25日が日曜(weekday=6)の場合、23日(金)に前倒し
        # ただし日曜日は実際にはスキップされるので、土曜日のケースのみ考慮
        if day == 24:
            # 25日の曜日を計算
            salary_weekday = (SALARY_DAY) % 7
            if salary_weekday == 5:  # 25日が土曜日
                return self.day_state.get_weekday() == 4  # 今日が金曜なら給料日

        return False

    def execute_friday_boss_event(self) -> dict:
        """金曜ボスイベントを実行し、評価結果を返す"""
        eval_result = self.weekly_stats.evaluate()
        grade = eval_result['nutrition_grade']
        saving = eval_result['saving_success']
        overspending = eval_result['overspending']

        energy_change = 0
        stamina_change = 0
        money_change = 0
        message = ""

        # 総合評価
        if grade == 'S' and saving:
            rank = 'SS'
            energy_change = 3
            stamina_change = 2
            money_change = 1000
            message = "完璧な一週間！栄養バランスも節約もバッチリ！"
        elif grade in ['S', 'A'] and saving:
            rank = 'S'
            energy_change = 2
            stamina_change = 1
            message = "素晴らしい一週間！よく頑張りました！"
        elif grade in ['A', 'B'] or (grade in ['S', 'A'] and not saving):
            rank = 'A'
            energy_change = 1
            message = "まずまずの一週間。この調子で！"
        elif grade in ['B', 'C']:
            rank = 'B'
            message = "可もなく不可もなく。来週も頑張ろう。"
        elif grade == 'D':
            rank = 'C'
            energy_change = -1
            message = "ちょっと栄養が偏ってるかも...来週は気をつけよう。"
        else:  # E grade or E with overspending
            rank = 'F'
            energy_change = -2
            stamina_change = -1
            message = "うーん...栄養も節約もちょっと厳しい結果に...来週こそ！"

        # 効果を適用
        if energy_change > 0:
            self.player.recover_energy(energy_change)
        elif energy_change < 0:
            self.player.consume_energy(abs(energy_change))

        if stamina_change > 0:
            self.player.recover_stamina(stamina_change)
        elif stamina_change < 0:
            self.player.consume_stamina(abs(stamina_change))

        if money_change > 0:
            self.player.money += money_change

        return {
            'rank': rank,
            'nutrition_grade': grade,
            'nutrients_ok': eval_result['nutrients_ok'],
            'saving_success': saving,
            'overspending': overspending,
            'food_spending': eval_result['food_spending'],
            'meals_cooked': eval_result['meals_cooked'],
            'energy_change': energy_change,
            'stamina_change': stamina_change,
            'money_change': money_change,
            'message': message,
        }

    def is_bonus_day(self) -> bool:
        """今日がボーナス支給日かどうか"""
        if not self.has_bonus:
            return False
        return self.day_state.month in BONUS_MONTHS and self.day_state.day == SALARY_DAY

    def pay_salary(self) -> tuple[int, int, int]:
        """給料を支払う。(総支給額, 家賃, 手取り)を返す"""
        gross = self._salary_amount
        rent = self._rent_amount
        net = gross - rent
        self.player.money += net
        self.stats.record_salary(net)
        return gross, rent, net

    def pay_bonus(self) -> int:
        """ボーナスを支払う。支払った金額を返す"""
        if not self.has_bonus:
            return 0
        amount = self._bonus_amount
        self.player.money += amount
        self.stats.record_bonus(amount)
        return amount

    def get_game_over_reason(self) -> str | None:
        """ゲームオーバーの理由を取得"""
        if self.player.money <= 0:
            return "money"
        if self.player.stamina <= 0:
            # 体力も気力も足りない場合は"exhausted"（根性回復不可）
            if self.player.energy < 2:
                return "exhausted"
            return "stamina"
        return None

    def get_result(self) -> GameResult:
        """ゲーム結果を取得"""
        return self.stats.to_result(
            survived_days=self.day_state.day,
            is_game_over=self.is_game_over(),
            is_game_clear=self.is_game_complete(),
            game_over_reason=self.get_game_over_reason(),
            final_money=self.player.money,
            final_stamina=self.player.stamina,
            final_energy=self.player.energy,
        )

    # === イベント関連 ===

    def determine_weather(self) -> str:
        """今日の天気を決定し、表示文字列を返す"""
        # 日付をシードにして天気を決定（同じ日は同じ天気）
        seed = self.day_state.day + self.day_state.month * 100
        self.events.determine_weather(seed)
        return self.events.get_weather_display()

    def get_weather_display(self) -> str:
        """天気の表示文字列を取得"""
        return self.events.get_weather_display()

    def get_event_context(self) -> dict:
        """イベント判定用のコンテキストを取得"""
        daily = self.day_state.daily_nutrition
        streak = self.nutrition_streak
        # キャラクター情報を取得
        character = get_character(self.character_id)
        is_office_worker = character.is_office_worker if character else True
        return {
            'day': self.day_state.day,
            'month': self.day_state.month,
            'weekday': self.day_state.get_weekday(),
            'is_holiday': self.is_holiday(),
            'weather': self.events.weather,
            'money': self.player.money,
            'energy': self.player.energy,
            'stamina': self.player.stamina,
            'fullness': self.player.fullness,
            'is_office_worker': is_office_worker,  # オフィス勤めか
            # 栄養素情報
            'daily_nutrition': {
                'vitality': daily.vitality,
                'mental': daily.mental,
                'awakening': daily.awakening,
                'sustain': daily.sustain,
                'defense': daily.defense,
            },
            # 連続高値日数（上限増加イベント用）
            'nutrition_streak': {
                'vitality': streak.vitality,
                'mental': streak.mental,
                'awakening': streak.awakening,
                'sustain': streak.sustain,
                'defense': streak.defense,
            },
        }

    # === 気質（Temperament）関連 ===

    def get_temperament(self):
        """判定された気質を取得"""
        if self.temperament_id is None:
            return None
        return get_temperament(self.temperament_id)

    def get_temperament_info(self) -> dict | None:
        """気質情報を辞書形式で取得"""
        temp = self.get_temperament()
        if temp is None:
            return None
        return {
            'id': temp.id,
            'name': temp.name,
            'description': temp.description,
            'icon': temp.icon,
        }

    def record_behavior_cook(self):
        """調理行動を記録"""
        if self.day_state.day <= 3:
            self.behavior_tracker.record_cook()

    def record_behavior_shop(self):
        """買い物行動を記録"""
        if self.day_state.day <= 3:
            self.behavior_tracker.record_shop()

    def record_behavior_online_shop(self):
        """通販行動を記録"""
        if self.day_state.day <= 3:
            self.behavior_tracker.record_online_shop()

    def record_behavior_eat_out(self):
        """外食行動を記録"""
        if self.day_state.day <= 3:
            self.behavior_tracker.record_eat_out()

    def record_behavior_cleanup(self):
        """掃除行動を記録"""
        if self.day_state.day <= 3:
            self.behavior_tracker.record_cleanup()

    def record_behavior_rest(self):
        """休養行動を記録"""
        if self.day_state.day <= 3:
            self.behavior_tracker.record_rest()

    def record_behavior_spending(self, amount: int):
        """支出を記録"""
        if self.day_state.day <= 3:
            self.behavior_tracker.record_spending(amount)

    def get_temperament_cook_bonus(self) -> int:
        """気質による調理時の気力ボーナスを取得"""
        temp = self.get_temperament()
        if temp is None:
            return 0
        return temp.on_cook_energy

    def get_temperament_shop_bonus(self) -> int:
        """気質による買い物時の気力ボーナスを取得"""
        temp = self.get_temperament()
        if temp is None:
            return 0
        return temp.on_shop_energy

    def get_temperament_online_shop_bonus(self) -> int:
        """気質による通販時の気力ボーナスを取得"""
        temp = self.get_temperament()
        if temp is None:
            return 0
        return temp.on_online_shop_energy

    def get_temperament_sleep_bonus(self) -> int:
        """気質による睡眠回復ボーナスを取得"""
        temp = self.get_temperament()
        if temp is None:
            return 0
        return temp.sleep_bonus

    def get_temperament_penalty_reduction(self) -> float:
        """気質による栄養ペナルティ軽減率を取得"""
        temp = self.get_temperament()
        if temp is None:
            return 0.0
        return temp.penalty_reduction

    def get_temperament_shop_discount(self) -> float:
        """気質による買い物割引率を取得"""
        temp = self.get_temperament()
        if temp is None:
            return 0.0
        return temp.shop_discount
