"""キャラクター選択システム"""
from dataclasses import dataclass


@dataclass
class Character:
    """キャラクターデータ"""
    id: str                    # 識別子
    name: str                  # 表示名
    description: str           # 説明文

    # パラメータ（後で調整用）
    initial_money: int = 30000
    salary_amount: int = 200000
    bonus_amount: int = 400000
    has_bonus: bool = True
    initial_energy: int = 10
    initial_stamina: int = 10
    rent_amount: int = 60000   # 家賃（給料から天引き）
    is_office_worker: bool = True  # オフィス勤めか（通勤イベント発生有無）


# キャラクターマスターデータ
CHARACTERS = {
    'regular': Character(
        id='regular',
        name='正社員',
        description='安定した給料とボーナスあり。一般的な難易度。',
        initial_money=30000,
        salary_amount=200000,
        bonus_amount=400000,
        has_bonus=True,
        rent_amount=60000,
    ),
    'contract': Character(
        id='contract',
        name='契約社員',
        description='ボーナスなし。少し厳しめ。',
        initial_money=25000,
        salary_amount=180000,
        bonus_amount=0,
        has_bonus=False,
        rent_amount=50000,
    ),
    'freelance': Character(
        id='freelance',
        name='フリーランス',
        description='収入は高めだが不安定。上級者向け。',
        initial_money=50000,
        salary_amount=250000,
        bonus_amount=0,
        has_bonus=False,
        initial_energy=8,
        initial_stamina=8,
        rent_amount=70000,
        is_office_worker=False,  # 通勤イベントなし
    ),
}


def get_character(character_id: str) -> Character | None:
    """キャラクターIDからキャラクターを取得"""
    return CHARACTERS.get(character_id)


def get_all_characters() -> list[Character]:
    """全キャラクターリストを取得"""
    return list(CHARACTERS.values())


def get_default_character() -> Character:
    """デフォルトキャラクターを取得"""
    return CHARACTERS['regular']
