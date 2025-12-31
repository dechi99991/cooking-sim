"""1日の流れ管理"""
from dataclasses import dataclass, field
from enum import Enum, auto
from .player import Player
from .nutrition import Nutrition
from .ingredients import Stock
from .cooking import Dish
from .constants import (
    COOKING_ENERGY_COST, BENTO_ENERGY_COST, COMMUTE_STAMINA_COST,
    CAFETERIA_PRICE, SLEEP_ENERGY_RECOVERY, SLEEP_STAMINA_RECOVERY,
    GAME_START_MONTH, GAME_START_DAY, GAME_DURATION_DAYS,
    SHOPPING_ENERGY_COST, SHOPPING_STAMINA_COST, SHOPPING_MIN_ENERGY
)


class MealTime(Enum):
    BREAKFAST = auto()
    LUNCH = auto()
    DINNER = auto()


class GamePhase(Enum):
    BREAKFAST = auto()
    GO_TO_WORK = auto()
    LUNCH = auto()
    LEAVE_WORK = auto()
    SHOPPING = auto()  # 買い出し（退勤後、夕食前）
    DINNER = auto()
    SLEEP = auto()
    DAY_END = auto()


@dataclass
class DayState:
    """1日の状態を管理"""
    day: int = GAME_START_DAY
    month: int = GAME_START_MONTH
    phase: GamePhase = GamePhase.BREAKFAST
    daily_nutrition: Nutrition = field(default_factory=Nutrition)
    has_bento: bool = False
    bento: Dish | None = None

    def next_phase(self):
        """次のフェーズへ進む"""
        phases = list(GamePhase)
        current_index = phases.index(self.phase)
        if current_index < len(phases) - 1:
            self.phase = phases[current_index + 1]

    def start_new_day(self):
        """新しい日を開始"""
        self.day += 1
        self.phase = GamePhase.BREAKFAST
        self.daily_nutrition.reset()
        self.has_bento = False
        self.bento = None

    def get_date_string(self) -> str:
        """日付文字列を取得"""
        return f"{self.month}月{self.day}日"

    def is_game_complete(self) -> bool:
        """ゲームクリア判定"""
        return self.day > GAME_DURATION_DAYS


class GameManager:
    """ゲーム全体を管理するクラス"""

    def __init__(self, player: Player, stock: Stock):
        self.player = player
        self.stock = stock
        self.day_state = DayState()

    def can_cook(self) -> bool:
        """調理可能か"""
        return self.player.can_cook(COOKING_ENERGY_COST) and not self.stock.is_empty()

    def can_make_bento(self) -> bool:
        """弁当作成可能か"""
        return self.player.can_cook(BENTO_ENERGY_COST) and not self.stock.is_empty()

    def can_use_cafeteria(self) -> bool:
        """社食利用可能か"""
        return self.player.money >= CAFETERIA_PRICE

    def consume_cooking_energy(self):
        """調理の気力を消費"""
        self.player.consume_energy(COOKING_ENERGY_COST)

    def consume_bento_energy(self):
        """弁当作成の気力を消費"""
        self.player.consume_energy(BENTO_ENERGY_COST)

    def consume_cafeteria_cost(self):
        """社食の費用を消費"""
        self.player.consume_money(CAFETERIA_PRICE)

    def eat_dish(self, dish: Dish):
        """料理を食べる"""
        actual_fullness = self.player.add_fullness(dish.fullness)
        self.day_state.daily_nutrition.add(dish.nutrition)
        return actual_fullness

    def set_bento(self, dish: Dish):
        """弁当をセット"""
        self.day_state.has_bento = True
        self.day_state.bento = dish

    def eat_bento(self) -> Dish | None:
        """弁当を食べる"""
        if self.day_state.has_bento and self.day_state.bento:
            bento = self.day_state.bento
            self.eat_dish(bento)
            self.day_state.has_bento = False
            self.day_state.bento = None
            return bento
        return None

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

    def sleep(self):
        """就寝処理"""
        # ペナルティ計算
        energy_penalty, stamina_penalty, fullness_penalty = \
            self.day_state.daily_nutrition.calculate_penalties()
        self.player.apply_penalties(energy_penalty, stamina_penalty, fullness_penalty)

        # 回復
        self.player.recover_energy(SLEEP_ENERGY_RECOVERY)
        self.player.recover_stamina(SLEEP_STAMINA_RECOVERY)

    def advance_phase(self):
        """フェーズを進める"""
        self.day_state.next_phase()

    def start_new_day(self):
        """新しい日を開始"""
        self.player.clear_penalties()
        self.player.reset_fullness()
        self.day_state.start_new_day()

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
