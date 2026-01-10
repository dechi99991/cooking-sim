"""週間ボスシステム

月曜朝に「今週のボス」が予告され、金曜日に判定が行われる。
プレイヤーは1週間かけて条件を満たす準備をする。
"""
from dataclasses import dataclass, field
import random


@dataclass
class WeeklyBoss:
    """週間ボスの定義"""
    id: str
    name: str
    description: str  # 月曜に表示する予告文
    category: str  # "event", "work", "life", "nutrition"

    # 条件（複数指定可能、すべて満たす必要あり）
    required_money: int = 0
    required_energy: int = 0
    required_stamina: int = 0
    required_item: str | None = None

    # 栄養条件（週間累計）
    required_nutrition: dict = field(default_factory=dict)  # {"mental": 20} など
    required_all_nutrients: int = 0  # 全栄養素がこの値以上

    # 報酬（成功時）
    reward_energy: int = 0
    reward_stamina: int = 0
    reward_money: int = 0
    success_message: str = ""

    # ペナルティ（失敗時）
    penalty_energy: int = 0
    penalty_stamina: int = 0
    penalty_debt: int = 0  # 借金追加
    failure_message: str = ""

    def get_requirements_text(self) -> str:
        """条件を人間が読める形式で返す"""
        parts = []
        if self.required_money > 0:
            parts.append(f"¥{self.required_money:,}")
        if self.required_energy > 0:
            parts.append(f"気力{self.required_energy}以上")
        if self.required_stamina > 0:
            parts.append(f"体力{self.required_stamina}以上")
        if self.required_item:
            parts.append(f"{self.required_item}が必要")
        if self.required_nutrition:
            for nutrient, value in self.required_nutrition.items():
                nutrient_names = {
                    "vitality": "活力素",
                    "mental": "精神素",
                    "awakening": "覚醒素",
                    "sustain": "持続素",
                    "defense": "防衛素",
                }
                name = nutrient_names.get(nutrient, nutrient)
                parts.append(f"週間{name}{value}以上")
        if self.required_all_nutrients > 0:
            parts.append(f"全栄養素{self.required_all_nutrients}以上")
        return " / ".join(parts) if parts else "条件なし"


# ボス定義
WEEKLY_BOSSES: dict[str, WeeklyBoss] = {
    # === イベント系 ===
    "drinking_party": WeeklyBoss(
        id="drinking_party",
        name="飲み会",
        description="今週金曜は職場の飲み会がある。参加費と体力が必要だ...",
        category="event",
        required_money=3000,
        required_stamina=3,
        reward_energy=2,
        success_message="飲み会で同僚と親睦を深めた！気分がいい。",
        penalty_stamina=3,
        penalty_debt=3000,
        failure_message="体調不良で参加できず...でも参加費は取られた。",
    ),
    "welcome_party": WeeklyBoss(
        id="welcome_party",
        name="歓迎会",
        description="新人の歓迎会が金曜にある。幹事として気力と資金が必要だ！",
        category="event",
        required_money=5000,
        required_energy=2,
        reward_stamina=2,
        reward_energy=1,
        success_message="歓迎会は大成功！新人にも感謝された。",
        penalty_energy=2,
        penalty_debt=5000,
        failure_message="準備不足で歓迎会がグダグダに...自腹で補填。",
    ),
    "group_date": WeeklyBoss(
        id="group_date",
        name="合コン",
        description="友人に誘われて金曜は合コン。資金と気合が必要！",
        category="event",
        required_money=4000,
        required_energy=3,
        reward_energy=3,
        success_message="楽しい出会いがあった！気分最高！",
        penalty_energy=3,
        penalty_debt=4000,
        failure_message="テンション低くて場を白けさせた...最悪。",
    ),

    # === 仕事系 ===
    "deadline": WeeklyBoss(
        id="deadline",
        name="締め切り",
        description="重要な仕事の締め切りが金曜日！気力を保っておかないと...",
        category="work",
        required_energy=5,
        reward_stamina=1,
        reward_money=500,
        success_message="締め切りに間に合った！上司からボーナスも！",
        penalty_energy=3,
        failure_message="締め切りに間に合わず...信用を失った。",
    ),
    "presentation": WeeklyBoss(
        id="presentation",
        name="プレゼン",
        description="金曜日に大事なプレゼンがある。心身ともに万全で臨みたい！",
        category="work",
        required_energy=4,
        required_stamina=4,
        reward_energy=2,
        reward_money=1000,
        success_message="プレゼン大成功！評価が上がった！",
        penalty_energy=2,
        penalty_stamina=2,
        failure_message="プレゼンでしどろもどろ...恥ずかしい。",
    ),
    "boss_mood": WeeklyBoss(
        id="boss_mood",
        name="上司の機嫌",
        description="上司の機嫌が悪そうだ...金曜まで気力を保って乗り切れ！",
        category="work",
        required_energy=3,
        success_message="なんとか上司の機嫌を損ねずに済んだ。",
        penalty_energy=2,
        failure_message="上司に怒られた...精神的にキツい。",
    ),

    # === 生活系 ===
    "sudden_expense": WeeklyBoss(
        id="sudden_expense",
        name="急な出費",
        description="家電が壊れそうだ...金曜までに5000円用意しておこう。",
        category="life",
        required_money=5000,
        success_message="無事に家電を買い替えられた。",
        penalty_debt=5000,
        failure_message="金が足りず...カードで払うしかない。",
    ),
    "electricity_bill": WeeklyBoss(
        id="electricity_bill",
        name="電気代高騰",
        description="今月の電気代が高い予感...3000円は用意しておきたい。",
        category="life",
        required_money=3000,
        success_message="電気代を払えた。節電を心がけよう。",
        penalty_debt=3000,
        failure_message="電気代が払えず滞納...追加料金発生。",
    ),
    "friend_wedding": WeeklyBoss(
        id="friend_wedding",
        name="友人の結婚式",
        description="友人の結婚式が金曜！ご祝儀と気力を用意しなければ！",
        category="life",
        required_money=10000,
        required_energy=2,
        reward_energy=3,
        success_message="感動的な式だった！幸せをお裾分けしてもらった。",
        penalty_energy=2,
        penalty_debt=10000,
        failure_message="祝儀が足りず借金...申し訳ない気持ちでいっぱい。",
    ),

    # === 栄養系 ===
    "health_checkup": WeeklyBoss(
        id="health_checkup",
        name="健康診断",
        description="金曜は健康診断！免疫力（防衛素）を高めておこう。",
        category="nutrition",
        required_nutrition={"defense": 20},
        reward_stamina=2,
        success_message="健康診断オールA！体の調子がいい。",
        penalty_stamina=2,
        failure_message="要再検査...不摂生がたたった。",
    ),
    "mental_check": WeeklyBoss(
        id="mental_check",
        name="メンタルチェック",
        description="ストレスチェックが金曜にある。精神素を高めて臨もう。",
        category="nutrition",
        required_nutrition={"mental": 20},
        reward_energy=2,
        success_message="メンタル良好！ストレス耐性がついた。",
        penalty_energy=2,
        failure_message="ストレス過多と診断...休養を取るよう言われた。",
    ),
    "stamina_test": WeeklyBoss(
        id="stamina_test",
        name="体力測定",
        description="職場で体力測定がある！活力素を意識した食事を。",
        category="nutrition",
        required_nutrition={"vitality": 20},
        reward_stamina=1,
        reward_energy=1,
        success_message="体力年齢が若い！いい調子だ。",
        penalty_stamina=1,
        penalty_energy=1,
        failure_message="体力年齢が実年齢より上...ショック。",
    ),
    "nutrition_audit": WeeklyBoss(
        id="nutrition_audit",
        name="栄養バランス審査",
        description="栄養士のチェックが入る！全栄養素をバランスよく摂ろう。",
        category="nutrition",
        required_all_nutrients=15,
        reward_energy=3,
        reward_stamina=2,
        success_message="完璧な栄養バランス！お手本にしたいと言われた。",
        penalty_energy=2,
        penalty_stamina=1,
        failure_message="偏食を指摘された...反省。",
    ),
}


def get_boss(boss_id: str) -> WeeklyBoss | None:
    """ボスIDからボスを取得"""
    return WEEKLY_BOSSES.get(boss_id)


def select_weekly_boss(week_number: int, seed: int | None = None) -> WeeklyBoss | None:
    """週番号に基づいてボスを選択

    Args:
        week_number: 週番号（1週目, 2週目, ...）
        seed: ランダムシード（再現性のため）

    Returns:
        選択されたボス、または1週目はNone
    """
    # 1週目はチュートリアル（ボスなし）
    if week_number <= 1:
        return None

    # シード設定
    if seed is not None:
        random.seed(seed + week_number * 100)

    # 全ボスからランダム選択
    boss_list = list(WEEKLY_BOSSES.values())
    return random.choice(boss_list)


def get_week_number(day: int) -> int:
    """日数から週番号を計算（1週目, 2週目, ...）

    Args:
        day: ゲーム日（1〜30）

    Returns:
        週番号（1〜5）
    """
    # day 1-7: week 1, day 8-14: week 2, etc.
    return (day - 1) // 7 + 1
