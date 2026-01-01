"""プレイヤーステータス管理"""
from dataclasses import dataclass, field
from .constants import (
    INITIAL_MONEY, INITIAL_ENERGY, INITIAL_STAMINA, INITIAL_FULLNESS,
    MAX_ENERGY, MAX_STAMINA, MAX_FULLNESS
)


@dataclass
class Player:
    """プレイヤーの状態を管理するクラス"""
    money: int = INITIAL_MONEY
    energy: int = INITIAL_ENERGY      # 気力
    stamina: int = INITIAL_STAMINA    # 体力
    fullness: int = INITIAL_FULLNESS  # 満腹感

    # 翌日へのペナルティ（栄養不足による）
    energy_recovery_penalty: int = 0
    stamina_recovery_penalty: int = 0
    fullness_decay_penalty: int = 0

    # クレジットカード未払い残高
    card_debt: int = 0

    def consume_energy(self, amount: int) -> bool:
        """気力を消費する。消費可能ならTrue"""
        if self.energy >= amount:
            self.energy -= amount
            return True
        return False

    def consume_stamina(self, amount: int) -> bool:
        """体力を消費する。消費可能ならTrue"""
        if self.stamina >= amount:
            self.stamina -= amount
            return True
        return False

    def consume_money(self, amount: int) -> bool:
        """お金を消費する。消費可能ならTrue"""
        if self.money >= amount:
            self.money -= amount
            return True
        return False

    def add_fullness(self, amount: int) -> int:
        """満腹感を増加させる。実際に増加した量を返す"""
        before = self.fullness
        self.fullness = min(self.fullness + amount, MAX_FULLNESS)
        return self.fullness - before

    def reset_fullness(self):
        """満腹感をリセットする（各食事ターン開始時）"""
        self.fullness = 0

    def recover_energy(self, amount: int):
        """気力を回復する（ペナルティ適用後）"""
        actual = max(0, amount - self.energy_recovery_penalty)
        self.energy = min(self.energy + actual, MAX_ENERGY)

    def recover_stamina(self, amount: int):
        """体力を回復する（ペナルティ適用後）"""
        actual = max(0, amount - self.stamina_recovery_penalty)
        self.stamina = min(self.stamina + actual, MAX_STAMINA)

    def apply_penalties(self, energy_penalty: int, stamina_penalty: int, fullness_penalty: int):
        """翌日へのペナルティを設定する"""
        self.energy_recovery_penalty = energy_penalty
        self.stamina_recovery_penalty = stamina_penalty
        self.fullness_decay_penalty = fullness_penalty

    def clear_penalties(self):
        """ペナルティをクリアする"""
        self.energy_recovery_penalty = 0
        self.stamina_recovery_penalty = 0
        self.fullness_decay_penalty = 0

    def is_game_over(self) -> bool:
        """ゲームオーバー判定"""
        return self.money <= 0 or self.stamina <= 0

    def can_cook(self, energy_cost: int) -> bool:
        """調理可能か判定"""
        return self.energy >= energy_cost

    def add_card_debt(self, amount: int):
        """カードで購入（未払い残高を増やす）"""
        self.card_debt += amount

    def settle_card(self) -> int:
        """カード精算。精算後の残高を返す"""
        self.money -= self.card_debt
        settled_amount = self.card_debt
        self.card_debt = 0
        return self.money

    def get_final_balance(self) -> int:
        """カード精算後の残高を計算（実際には精算しない）"""
        return self.money - self.card_debt
