"""栄養システム"""
from dataclasses import dataclass, field
from .constants import NUTRITION_MIN_THRESHOLD, PENALTY_VITALITY, PENALTY_MENTAL, PENALTY_SUSTAIN


@dataclass
class Nutrition:
    """栄養素5種を管理するクラス"""
    vitality: int = 0   # 活力素: 体力回復
    mental: int = 0     # 心力素: 気力回復
    awakening: int = 0  # 覚醒素: 目覚め（Phase 1では未使用）
    sustain: int = 0    # 持続素: 満腹感持続
    defense: int = 0    # 防衛素: 体調（Phase 1では未使用）

    def add(self, other: 'Nutrition'):
        """栄養を加算する"""
        self.vitality += other.vitality
        self.mental += other.mental
        self.awakening += other.awakening
        self.sustain += other.sustain
        self.defense += other.defense

    def reset(self):
        """1日の栄養をリセットする"""
        self.vitality = 0
        self.mental = 0
        self.awakening = 0
        self.sustain = 0
        self.defense = 0

    def calculate_penalties(self) -> tuple[int, int, int]:
        """
        栄養不足によるペナルティを計算する
        Returns: (energy_penalty, stamina_penalty, fullness_penalty)
        """
        energy_penalty = 0
        stamina_penalty = 0
        fullness_penalty = 0

        # 活力素不足 → 体力回復ペナルティ
        if self.vitality < NUTRITION_MIN_THRESHOLD:
            stamina_penalty = PENALTY_VITALITY

        # 心力素不足 → 気力回復ペナルティ
        if self.mental < NUTRITION_MIN_THRESHOLD:
            energy_penalty = PENALTY_MENTAL

        # 持続素不足 → 満腹感減少ペナルティ
        if self.sustain < NUTRITION_MIN_THRESHOLD:
            fullness_penalty = PENALTY_SUSTAIN

        return energy_penalty, stamina_penalty, fullness_penalty

    def get_status(self) -> dict:
        """現在の栄養状態を辞書で返す"""
        threshold = NUTRITION_MIN_THRESHOLD
        return {
            '活力素': {'value': self.vitality, 'ok': self.vitality >= threshold},
            '心力素': {'value': self.mental, 'ok': self.mental >= threshold},
            '覚醒素': {'value': self.awakening, 'ok': self.awakening >= threshold},
            '持続素': {'value': self.sustain, 'ok': self.sustain >= threshold},
            '防衛素': {'value': self.defense, 'ok': self.defense >= threshold},
        }


def create_nutrition(vitality: int, mental: int, awakening: int, sustain: int, defense: int) -> Nutrition:
    """栄養オブジェクトを作成するヘルパー関数"""
    return Nutrition(
        vitality=vitality,
        mental=mental,
        awakening=awakening,
        sustain=sustain,
        defense=defense
    )
