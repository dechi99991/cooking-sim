"""ランダムイベントシステム"""
import random
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Callable, Any


class Weather(Enum):
    """天気"""
    SUNNY = auto()      # 晴れ
    CLOUDY = auto()     # 曇り
    RAINY = auto()      # 雨
    STORMY = auto()     # 嵐


WEATHER_NAMES = {
    Weather.SUNNY: '晴れ',
    Weather.CLOUDY: '曇り',
    Weather.RAINY: '雨',
    Weather.STORMY: '嵐',
}

WEATHER_ICONS = {
    Weather.SUNNY: '☀️',
    Weather.CLOUDY: '☁️',
    Weather.RAINY: '🌧️',
    Weather.STORMY: '⛈️',
}


class EventTiming(Enum):
    """イベント発生タイミング"""
    WAKE_UP = auto()        # 起床時
    GO_TO_WORK = auto()     # 出社時
    AFTER_LUNCH = auto()    # 昼食後
    AT_SHOP = auto()        # スーパーに行った時
    LEAVE_WORK = auto()     # 退勤時
    AFTER_WORK = auto()     # 帰宅後
    NIGHT = auto()          # 夜中（就寝前）


TIMING_NAMES = {
    EventTiming.WAKE_UP: '起床時',
    EventTiming.GO_TO_WORK: '出社時',
    EventTiming.AFTER_LUNCH: '昼食後',
    EventTiming.AT_SHOP: '買い物中',
    EventTiming.LEAVE_WORK: '退勤時',
    EventTiming.AFTER_WORK: '帰宅後',
    EventTiming.NIGHT: '夜中',
}


@dataclass
class RandomEvent:
    """ランダムイベント"""
    id: str                     # イベントID
    name: str                   # イベント名
    description: str            # 説明文
    timing: EventTiming         # 発生タイミング
    probability: float          # 発生確率 (0.0-1.0)
    condition: Callable[[dict], bool] | None = None  # 発生条件（Noneなら常に発生可能）
    effect: Callable[[Any], str] | None = None       # 効果（GameManagerを受け取る）
    once_per_day: bool = True   # 1日1回のみか
    reason: str = ""            # イベント発生の根拠（「小指をぶつけた！」など）
    effect_type: str | None = None  # 効果タイプ: "energy_negative", "stamina_negative" など

    def check_condition(self, context: dict) -> bool:
        """イベント発生条件をチェック"""
        if self.condition is None:
            return True
        return self.condition(context)

    def execute(self, game_manager) -> str:
        """イベント実行。結果メッセージを返す"""
        if self.effect is None:
            return self.description
        return self.effect(game_manager)


@dataclass
class EventResult:
    """イベント実行結果"""
    event: RandomEvent
    message: str


class EventManager:
    """イベント管理クラス"""

    def __init__(self):
        self.weather: Weather = Weather.SUNNY
        self._events: dict[str, RandomEvent] = {}  # 登録されたイベント
        self._triggered_today: set[str] = set()    # 今日発生したイベントID

    def get_weather_name(self) -> str:
        """天気名を取得"""
        return WEATHER_NAMES[self.weather]

    def get_weather_icon(self) -> str:
        """天気アイコンを取得"""
        return WEATHER_ICONS[self.weather]

    def get_weather_display(self) -> str:
        """天気の表示文字列を取得"""
        return f"{self.get_weather_icon()} {self.get_weather_name()}"

    def determine_weather(self, seed: int | None = None) -> Weather:
        """天気を決定

        確率: 晴れ50%, 曇り30%, 雨15%, 嵐5%
        """
        if seed is not None:
            random.seed(seed)

        roll = random.random()
        if roll < 0.50:
            self.weather = Weather.SUNNY
        elif roll < 0.80:
            self.weather = Weather.CLOUDY
        elif roll < 0.95:
            self.weather = Weather.RAINY
        else:
            self.weather = Weather.STORMY

        return self.weather

    def register_event(self, event: RandomEvent):
        """イベントを登録"""
        self._events[event.id] = event

    def register_events(self, events: list[RandomEvent]):
        """複数イベントを登録"""
        for event in events:
            self.register_event(event)

    def get_event(self, event_id: str) -> RandomEvent | None:
        """イベントを取得"""
        return self._events.get(event_id)

    def check_and_trigger_events(
        self,
        timing: EventTiming,
        context: dict,
        game_manager
    ) -> list[EventResult]:
        """指定タイミングのイベントをチェックし、発生したものを実行

        Args:
            timing: イベント発生タイミング
            context: イベント条件判定用のコンテキスト（天気、曜日など）
            game_manager: GameManagerインスタンス

        Returns:
            発生したイベントの結果リスト
        """
        results = []

        # コンテキストに天気を追加
        context['weather'] = self.weather

        # 栄養素による確率補正を計算
        daily_nutrition = context.get('daily_nutrition', {})
        mental = daily_nutrition.get('mental', 0)
        defense = daily_nutrition.get('defense', 0)

        for event_id, event in self._events.items():
            # タイミングが一致しない場合はスキップ
            if event.timing != timing:
                continue

            # 1日1回制限のチェック
            if event.once_per_day and event_id in self._triggered_today:
                continue

            # 条件チェック
            if not event.check_condition(context):
                continue

            # 確率を計算（栄養素による補正を適用）
            probability = event.probability

            # effect_typeを取得（明示的指定 > effect関数のタグ）
            effect_type = event.effect_type
            if effect_type is None and event.effect is not None:
                effect_type = getattr(event.effect, '_effect_type', None)

            if effect_type == 'energy_negative' and mental > 0:
                # 心力素が高いほど気力マイナスイベントの確率が下がる（最大50%減）
                reduction = min(0.5, mental * 0.05)
                probability *= (1 - reduction)
            elif effect_type == 'stamina_negative' and defense > 0:
                # 防衛素が高いほど体力マイナスイベントの確率が下がる（最大50%減）
                reduction = min(0.5, defense * 0.05)
                probability *= (1 - reduction)

            # 確率判定
            if random.random() >= probability:
                continue

            # イベント発生
            message = event.execute(game_manager)
            results.append(EventResult(event=event, message=message))

            if event.once_per_day:
                self._triggered_today.add(event_id)

        return results

    def force_trigger_event(self, event_id: str, game_manager) -> EventResult | None:
        """イベントを強制発生"""
        event = self._events.get(event_id)
        if event is None:
            return None

        message = event.execute(game_manager)
        return EventResult(event=event, message=message)

    def new_day(self):
        """新しい日の開始処理"""
        self._triggered_today.clear()

    def get_events_by_timing(self, timing: EventTiming) -> list[RandomEvent]:
        """指定タイミングのイベント一覧を取得"""
        return [e for e in self._events.values() if e.timing == timing]

    def get_all_events(self) -> list[RandomEvent]:
        """全イベント一覧を取得"""
        return list(self._events.values())

    def is_rainy(self) -> bool:
        """雨かどうか"""
        return self.weather in (Weather.RAINY, Weather.STORMY)

    def is_stormy(self) -> bool:
        """嵐かどうか"""
        return self.weather == Weather.STORMY


# === サンプルイベント（後で別ファイルに移動可能） ===

def create_sample_events() -> list[RandomEvent]:
    """サンプルイベントを作成（テスト用）"""
    events = []

    # 起床時イベント例
    events.append(RandomEvent(
        id='morning_mood_good',
        name='気分爽快',
        description='よく眠れた！今日は気分がいい。',
        timing=EventTiming.WAKE_UP,
        probability=0.1,
        condition=lambda ctx: ctx.get('weather') == Weather.SUNNY,
        effect=lambda gm: '気分爽快で目覚めた！（気力+1）',
    ))

    return events
