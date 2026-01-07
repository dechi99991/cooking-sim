"""気質（Temperament）システム

プレイヤーの行動傾向から気質を判定し、ゲームプレイにボーナスを付与する。
気質は3日目終了時に判定され、4日目の朝に発表される。
"""
from dataclasses import dataclass, field


@dataclass
class Temperament:
    """気質データ"""
    id: str
    name: str
    description: str
    icon: str = ""
    # 効果
    on_cook_energy: int = 0           # 調理時の気力変化
    on_shop_energy: int = 0           # 買い物時の気力変化
    on_online_shop_energy: int = 0    # 通販時の気力変化
    penalty_reduction: float = 0.0    # 栄養ペナルティ軽減率 (0.0-1.0)
    fullness_decay_reduction: int = 0 # 満腹度減少軽減
    shop_discount: float = 0.0        # 買い物割引率 (0.0-1.0)
    sleep_bonus: int = 0              # 睡眠回復ボーナス
    eat_out_nutrition_bonus: float = 0.0  # 外食栄養ボーナス率


# === 気質定義 ===

TEMPERAMENTS: dict[str, Temperament] = {
    'cooking_lover': Temperament(
        id='cooking_lover',
        name='料理好き',
        description='調理時に気力+1回復',
        icon='👨‍🍳',
        on_cook_energy=1,
    ),
    'shopping_lover': Temperament(
        id='shopping_lover',
        name='買い物好き',
        description='買い物・通販で気力+1回復',
        icon='🛒',
        on_shop_energy=1,
        on_online_shop_energy=1,
    ),
    'health_conscious': Temperament(
        id='health_conscious',
        name='健康志向',
        description='栄養ペナルティ50%軽減',
        icon='🥗',
        penalty_reduction=0.5,
    ),
    'big_eater': Temperament(
        id='big_eater',
        name='大食い',
        description='満腹度が減りにくい',
        icon='🍖',
        fullness_decay_reduction=2,
    ),
    'frugal': Temperament(
        id='frugal',
        name='倹約家',
        description='買い物10%割引',
        icon='💰',
        shop_discount=0.1,
    ),
    'night_owl': Temperament(
        id='night_owl',
        name='夜型',
        description='睡眠回復+2',
        icon='🦉',
        sleep_bonus=2,
    ),
    'social': Temperament(
        id='social',
        name='社交的',
        description='外食の栄養効果50%アップ',
        icon='🎉',
        eat_out_nutrition_bonus=0.5,
    ),
    'tidy': Temperament(
        id='tidy',
        name='几帳面',
        description='毎日の睡眠回復+1',
        icon='🧹',
        sleep_bonus=1,
    ),
    'balanced': Temperament(
        id='balanced',
        name='バランス型',
        description='全体的に微ボーナス',
        icon='⚖️',
        on_cook_energy=0,  # 特別なボーナスなし（デフォルト）
    ),
}


def get_temperament(temperament_id: str) -> Temperament | None:
    """気質を取得"""
    return TEMPERAMENTS.get(temperament_id)


def get_all_temperaments() -> list[Temperament]:
    """全気質リストを取得"""
    return list(TEMPERAMENTS.values())


# === 行動トラッカー ===

@dataclass
class BehaviorTracker:
    """プレイヤーの行動を追跡するクラス

    最初の3日間の行動を記録し、気質判定に使用する。
    """
    cook_count: int = 0              # 調理回数
    shop_count: int = 0              # 買い物回数
    online_shop_count: int = 0       # 通販回数
    eat_out_count: int = 0           # 外食回数
    cleanup_count: int = 0           # 掃除回数
    rest_count: int = 0              # 休養回数
    total_spent: int = 0             # 総支出額
    total_nutrition_balance: float = 0.0  # 栄養バランス累計
    days_tracked: int = 0            # 追跡日数

    def record_cook(self):
        """調理を記録"""
        self.cook_count += 1

    def record_shop(self):
        """買い物を記録"""
        self.shop_count += 1

    def record_online_shop(self):
        """通販を記録"""
        self.online_shop_count += 1

    def record_eat_out(self):
        """外食を記録"""
        self.eat_out_count += 1

    def record_cleanup(self):
        """掃除を記録"""
        self.cleanup_count += 1

    def record_rest(self):
        """休養を記録"""
        self.rest_count += 1

    def record_spending(self, amount: int):
        """支出を記録"""
        self.total_spent += amount

    def record_nutrition_balance(self, balance: float):
        """栄養バランスを記録（1日の終わりに）"""
        self.total_nutrition_balance += balance
        self.days_tracked += 1

    def get_avg_nutrition_balance(self) -> float:
        """平均栄養バランスを取得"""
        if self.days_tracked == 0:
            return 0.0
        return self.total_nutrition_balance / self.days_tracked

    def determine_temperament(self) -> str:
        """行動傾向から気質を判定

        最も多い行動カテゴリに応じた気質を返す。
        """
        # 行動カテゴリとそのスコア
        scores = {
            'cooking_lover': self.cook_count * 2,  # 調理は重み2
            'shopping_lover': self.shop_count + self.online_shop_count,
            'social': self.eat_out_count * 3,  # 外食は重み3（回数少なめのため）
            'tidy': self.cleanup_count * 3,    # 掃除も重み3
            'night_owl': self.rest_count * 2,  # 休養が多い = 夜型傾向
        }

        # 支出が少ない = 倹約家
        # 平均支出が1日2000円未満なら倹約家傾向
        if self.days_tracked > 0:
            avg_spent = self.total_spent / self.days_tracked
            if avg_spent < 2000:
                scores['frugal'] = 5  # 倹約家スコア

        # 栄養バランスが良い = 健康志向
        avg_balance = self.get_avg_nutrition_balance()
        if avg_balance >= 0.7:  # 70%以上のバランス
            scores['health_conscious'] = 5

        # 大食い判定は難しいので、満腹度の記録が必要
        # ここでは省略（将来拡張可能）

        # 最高スコアの気質を選択
        if not scores or max(scores.values()) == 0:
            return 'balanced'  # デフォルト

        best_temperament = max(scores, key=lambda k: scores[k])

        # スコアが低すぎる場合はバランス型
        if scores[best_temperament] < 3:
            return 'balanced'

        return best_temperament


# === ユーティリティ ===

def calculate_nutrition_balance(daily_nutrition) -> float:
    """1日の栄養バランスを計算（0.0-1.0）

    各栄養素が5以上あれば「バランスが取れている」とみなす。
    5種類中何種類が5以上かで計算。
    """
    threshold = 5
    count = 0
    if daily_nutrition.vitality >= threshold:
        count += 1
    if daily_nutrition.mental >= threshold:
        count += 1
    if daily_nutrition.awakening >= threshold:
        count += 1
    if daily_nutrition.sustain >= threshold:
        count += 1
    if daily_nutrition.defense >= threshold:
        count += 1
    return count / 5.0
