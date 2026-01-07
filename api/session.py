"""ゲームセッション管理"""
import uuid
from typing import TYPE_CHECKING

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from game.player import Player
from game.ingredients import create_initial_stock
from game.day_cycle import GameManager
from game.character import get_character, get_default_character

if TYPE_CHECKING:
    from game.day_cycle import GameManager


# インメモリセッションストア
_sessions: dict[str, GameManager] = {}


def create_session(character_id: str | None = None) -> tuple[str, GameManager]:
    """新しいゲームセッションを作成

    Args:
        character_id: キャラクターID（省略時はデフォルト）

    Returns:
        (session_id, GameManager)
    """
    # キャラクター取得
    if character_id:
        character = get_character(character_id)
        if character is None:
            character = get_default_character()
    else:
        character = get_default_character()

    # プレイヤー初期化
    player = Player(
        money=character.initial_money,
        energy=character.initial_energy,
        stamina=character.initial_stamina,
    )

    # 食材在庫初期化
    stock = create_initial_stock()

    # GameManager初期化
    game = GameManager(
        player, stock,
        has_bonus=character.has_bonus,
        salary_amount=character.salary_amount,
        bonus_amount=character.bonus_amount,
        rent_amount=character.rent_amount,
        character_id=character.id,
    )

    # 天気を決定（1日目開始時）
    game.determine_weather()

    # セッションID生成・保存
    session_id = str(uuid.uuid4())
    _sessions[session_id] = game

    return session_id, game


def get_session(session_id: str) -> GameManager | None:
    """セッションを取得

    Args:
        session_id: セッションID

    Returns:
        GameManager or None
    """
    return _sessions.get(session_id)


def delete_session(session_id: str) -> bool:
    """セッションを削除

    Args:
        session_id: セッションID

    Returns:
        削除成功時True
    """
    if session_id in _sessions:
        del _sessions[session_id]
        return True
    return False


def get_session_count() -> int:
    """アクティブセッション数を取得"""
    return len(_sessions)
