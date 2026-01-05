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
from .constants import (
    COOKING_ENERGY_COST, BENTO_ENERGY_COST, COMMUTE_STAMINA_COST,
    CAFETERIA_PRICE, SLEEP_ENERGY_RECOVERY, SLEEP_STAMINA_RECOVERY,
    GAME_START_MONTH, GAME_START_DAY, GAME_DURATION_DAYS,
    SHOPPING_ENERGY_COST, SHOPPING_STAMINA_COST, SHOPPING_MIN_ENERGY,
    SHOPPING_BAG_CAPACITY,
    SALARY_AMOUNT, SALARY_DAY, BONUS_AMOUNT, BONUS_MONTHS,
    CAFFEINE_INSOMNIA_THRESHOLD, CAFFEINE_ENERGY_PENALTY, CAFFEINE_STAMINA_PENALTY
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
        """曜日名を取得"""
        return WEEKDAY_NAMES[self.get_weekday()]

    def is_holiday(self) -> bool:
        """休日かどうか (土日)"""
        weekday = self.get_weekday()
        return weekday >= 5  # 5=土, 6=日

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
        """新しい日を開始"""
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


class GameManager:
    """ゲーム全体を管理するクラス"""

    def __init__(self, player: Player, stock: Stock,
                 has_bonus: bool = True,
                 salary_amount: int | None = None,
                 bonus_amount: int | None = None,
                 rent_amount: int = 0,
                 with_initial_relics: bool = True):
        self.player = player
        self.stock = stock
        self.day_state = DayState()
        self.stats = GameStats()  # 統計収集用
        self.relics = RelicInventory()  # レリック所持
        self.provisions = ProvisionStock()  # 食糧ストック
        self.events = EventManager()  # イベント管理
        register_all_events(self.events)  # 全イベントを登録
        self.has_bonus = has_bonus  # ボーナスの有無（キャラ設定用）
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

    def consume_cooking_energy(self):
        """調理の気力を消費（レリック効果適用）"""
        self.player.consume_energy(self.get_cooking_energy_cost())

    def consume_bento_energy(self):
        """弁当作成の気力を消費（レリック効果適用）"""
        self.player.consume_energy(self.get_bento_energy_cost())

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

    def commute(self):
        """出退勤処理"""
        self.player.consume_stamina(COMMUTE_STAMINA_COST)

    def can_go_shopping(self) -> bool:
        """買い出し可能か"""
        return self.player.energy >= SHOPPING_MIN_ENERGY

    def go_shopping(self):
        """買い出しの気力・体力を消費"""
        self.player.consume_energy(SHOPPING_ENERGY_COST)
        self.player.consume_stamina(SHOPPING_STAMINA_COST)

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

        # 回復
        self.player.recover_energy(SLEEP_ENERGY_RECOVERY)
        self.player.recover_stamina(SLEEP_STAMINA_RECOVERY)

        return has_insomnia

    def advance_phase(self):
        """フェーズを進める"""
        self.day_state.next_phase()

    def start_new_day(self):
        """新しい日を開始"""
        self.player.clear_penalties()
        self.player.reset_fullness()
        self.day_state.start_new_day()
        # 期限切れの弁当などを削除
        self.provisions.remove_expired_prepared(self.day_state.day)
        # イベントの日次リセット
        self.events.new_day()

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

    def get_freshness_extend(self) -> int:
        """レリック効果による鮮度延長日数を取得"""
        return self.relics.get_freshness_extend()

    def get_bag_capacity(self) -> int:
        """買い物バッグ容量を取得（レリック効果込み）"""
        return SHOPPING_BAG_CAPACITY + self.relics.get_bag_capacity_boost()

    def is_payday(self) -> bool:
        """今日が給料日かどうか"""
        return self.day_state.day == SALARY_DAY

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
        }
