"""ランダムイベントデータ（280種類）"""
import random
from .events import RandomEvent, EventTiming, Weather


# === イベント効果関数 ===

def effect_energy(amount: int):
    """気力を増減"""
    def effect(gm):
        old = gm.player.energy
        if amount > 0:
            gm.player.recover_energy(amount)
            return f"気力が{amount}回復した！ ({old} → {gm.player.energy})"
        else:
            gm.player.consume_energy(-amount)
            return f"気力が{-amount}減少... ({old} → {gm.player.energy})"
    return effect


def effect_stamina(amount: int):
    """体力を増減"""
    def effect(gm):
        old = gm.player.stamina
        if amount > 0:
            gm.player.recover_stamina(amount)
            return f"体力が{amount}回復した！ ({old} → {gm.player.stamina})"
        else:
            gm.player.consume_stamina(-amount)
            return f"体力が{-amount}減少... ({old} → {gm.player.stamina})"
    return effect


def effect_money(amount: int):
    """所持金を増減"""
    def effect(gm):
        old = gm.player.money
        if amount > 0:
            gm.player.money += amount
            return f"{amount}円を手に入れた！ ({old:,} → {gm.player.money:,}円)"
        else:
            gm.player.consume_money(-amount)
            return f"{-amount}円を失った... ({old:,} → {gm.player.money:,}円)"
    return effect


def effect_fullness(amount: int):
    """満腹感を増減"""
    def effect(gm):
        old = gm.player.fullness
        if amount > 0:
            gm.player.add_fullness(amount)
            return f"満腹感が{amount}増加！ ({old} → {gm.player.fullness})"
        else:
            gm.player.fullness = max(0, gm.player.fullness + amount)
            return f"満腹感が{-amount}減少... ({old} → {gm.player.fullness})"
    return effect


def effect_add_ingredient(name: str, qty: int = 1):
    """食材を獲得"""
    def effect(gm):
        gm.stock.add(name, qty, gm.day_state.day)
        return f"{name}を{qty}個手に入れた！"
    return effect


def effect_lose_ingredient(name: str, qty: int = 1):
    """食材を失う"""
    def effect(gm):
        if gm.stock.has(name, qty):
            gm.stock.remove(name, qty)
            return f"{name}を{qty}個失った..."
        else:
            # 持っていない場合は別のペナルティ
            gm.player.consume_energy(1)
            return f"{name}がなかったので気力が減った..."
    return effect


def effect_add_provision(name: str, qty: int = 1):
    """食糧を獲得"""
    def effect(gm):
        gm.provisions.add(name, qty)
        return f"{name}を{qty}個手に入れた！"
    return effect


def effect_lose_random_ingredient():
    """ランダムな食材を失う"""
    def effect(gm):
        items = gm.stock.get_all_items()
        if items:
            name = random.choice(list(items.keys()))
            gm.stock.remove(name, 1)
            return f"{name}を1個失った..."
        else:
            return "食材がなかったので何も起きなかった"
    return effect


def effect_combined(*effects):
    """複数の効果を組み合わせ"""
    def effect(gm):
        results = []
        for eff in effects:
            results.append(eff(gm))
        return "\n".join(results)
    return effect


# === 条件関数 ===

def cond_sunny(ctx):
    return ctx.get('weather') == Weather.SUNNY

def cond_cloudy(ctx):
    return ctx.get('weather') == Weather.CLOUDY

def cond_rainy(ctx):
    return ctx.get('weather') in (Weather.RAINY, Weather.STORMY)

def cond_stormy(ctx):
    return ctx.get('weather') == Weather.STORMY

def cond_weekday(ctx):
    return not ctx.get('is_holiday', False)

def cond_holiday(ctx):
    return ctx.get('is_holiday', False)

def cond_low_energy(ctx):
    return ctx.get('energy', 10) <= 3

def cond_high_energy(ctx):
    return ctx.get('energy', 0) >= 8

def cond_low_stamina(ctx):
    return ctx.get('stamina', 10) <= 3

def cond_high_stamina(ctx):
    return ctx.get('stamina', 0) >= 8

def cond_low_money(ctx):
    return ctx.get('money', 0) < 5000

def cond_high_money(ctx):
    return ctx.get('money', 0) >= 50000

def cond_monday(ctx):
    return ctx.get('weekday') == 0

def cond_friday(ctx):
    return ctx.get('weekday') == 4

def cond_early_month(ctx):
    return ctx.get('day', 15) <= 10

def cond_late_month(ctx):
    return ctx.get('day', 1) >= 20


# === 起床時イベント (40種類) ===

WAKE_UP_EVENTS = [
    # 天気関連 (10種)
    RandomEvent(
        id='wake_sunny_mood', name='爽やかな目覚め',
        description='窓から差し込む朝日で気持ちよく目覚めた',
        timing=EventTiming.WAKE_UP, probability=0.15,
        condition=cond_sunny, effect=effect_energy(1)
    ),
    RandomEvent(
        id='wake_sunny_stretch', name='朝のストレッチ',
        description='晴れた朝に軽くストレッチをした',
        timing=EventTiming.WAKE_UP, probability=0.1,
        condition=cond_sunny, effect=effect_stamina(1)
    ),
    RandomEvent(
        id='wake_cloudy_lazy', name='曇りの朝',
        description='どんよりした天気で少し気だるい',
        timing=EventTiming.WAKE_UP, probability=0.1,
        condition=cond_cloudy, effect=effect_energy(-1)
    ),
    RandomEvent(
        id='wake_rain_cozy', name='雨音の朝',
        description='雨音を聞きながらゆっくり起きた',
        timing=EventTiming.WAKE_UP, probability=0.1,
        condition=cond_rainy, effect=effect_energy(1)
    ),
    RandomEvent(
        id='wake_rain_gloomy', name='憂鬱な雨',
        description='雨の日は気分が乗らない...',
        timing=EventTiming.WAKE_UP, probability=0.1,
        condition=cond_rainy, effect=effect_energy(-1)
    ),
    RandomEvent(
        id='wake_storm_anxiety', name='嵐の朝',
        description='激しい雨風で落ち着かない',
        timing=EventTiming.WAKE_UP, probability=0.3,
        condition=cond_stormy, effect=effect_combined(effect_energy(-1), effect_stamina(-1))
    ),
    RandomEvent(
        id='wake_sunny_bird', name='小鳥のさえずり',
        description='鳥の声で自然に目が覚めた',
        timing=EventTiming.WAKE_UP, probability=0.08,
        condition=cond_sunny, effect=effect_combined(effect_energy(1), effect_stamina(1))
    ),
    RandomEvent(
        id='wake_cloudy_sleep', name='二度寝の誘惑',
        description='曇りの日はつい二度寝してしまった',
        timing=EventTiming.WAKE_UP, probability=0.08,
        condition=cond_cloudy, effect=effect_stamina(1)
    ),
    RandomEvent(
        id='wake_rain_leak', name='雨漏り発見',
        description='窓際から雨漏りが...修理費がかかった',
        timing=EventTiming.WAKE_UP, probability=0.03,
        condition=cond_stormy, effect=effect_money(-500)
    ),
    RandomEvent(
        id='wake_sunny_laundry', name='洗濯日和',
        description='絶好の洗濯日和！気分も上がる',
        timing=EventTiming.WAKE_UP, probability=0.1,
        condition=cond_sunny, effect=effect_energy(1)
    ),

    # 体調関連 (10種)
    RandomEvent(
        id='wake_good_sleep', name='快眠',
        description='ぐっすり眠れて体調バッチリ',
        timing=EventTiming.WAKE_UP, probability=0.08,
        effect=effect_combined(effect_energy(2), effect_stamina(1))
    ),
    RandomEvent(
        id='wake_bad_sleep', name='寝不足',
        description='あまり眠れなかった...',
        timing=EventTiming.WAKE_UP, probability=0.08,
        effect=effect_combined(effect_energy(-1), effect_stamina(-1))
    ),
    RandomEvent(
        id='wake_nightmare', name='悪夢',
        description='嫌な夢を見て目が覚めた',
        timing=EventTiming.WAKE_UP, probability=0.05,
        effect=effect_energy(-2)
    ),
    RandomEvent(
        id='wake_good_dream', name='良い夢',
        description='素敵な夢を見て幸せな気分',
        timing=EventTiming.WAKE_UP, probability=0.05,
        effect=effect_energy(2)
    ),
    RandomEvent(
        id='wake_stiff_neck', name='寝違え',
        description='首を寝違えてしまった',
        timing=EventTiming.WAKE_UP, probability=0.05,
        effect=effect_stamina(-2)
    ),
    RandomEvent(
        id='wake_refreshed', name='スッキリ',
        description='すっきりと目が覚めた',
        timing=EventTiming.WAKE_UP, probability=0.1,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='wake_oversleep', name='寝坊しそう',
        description='危うく寝坊するところだった！',
        timing=EventTiming.WAKE_UP, probability=0.05,
        condition=cond_weekday,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='wake_early', name='早起き成功',
        description='目覚ましより早く起きられた',
        timing=EventTiming.WAKE_UP, probability=0.08,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='wake_headache', name='頭痛',
        description='朝から頭が痛い...',
        timing=EventTiming.WAKE_UP, probability=0.04,
        effect=effect_combined(effect_energy(-1), effect_stamina(-1))
    ),
    RandomEvent(
        id='wake_full_energy', name='絶好調',
        description='今日は調子がいい！',
        timing=EventTiming.WAKE_UP, probability=0.05,
        condition=cond_high_stamina,
        effect=effect_energy(2)
    ),

    # 発見・イベント系 (10種)
    RandomEvent(
        id='wake_find_coin', name='小銭発見',
        description='ベッドの下から小銭が出てきた',
        timing=EventTiming.WAKE_UP, probability=0.05,
        effect=effect_money(100)
    ),
    RandomEvent(
        id='wake_find_egg', name='卵のお裾分け',
        description='隣人から卵をもらった',
        timing=EventTiming.WAKE_UP, probability=0.03,
        effect=effect_add_ingredient('卵', 2)
    ),
    RandomEvent(
        id='wake_find_rice', name='米のお裾分け',
        description='実家から米が届いていた',
        timing=EventTiming.WAKE_UP, probability=0.02,
        effect=effect_add_ingredient('米', 3)
    ),
    RandomEvent(
        id='wake_pest', name='虫発見',
        description='台所で虫を発見...殺虫剤を買わないと',
        timing=EventTiming.WAKE_UP, probability=0.03,
        effect=effect_money(-300)
    ),
    RandomEvent(
        id='wake_mail_money', name='お年玉',
        description='親戚からお小遣いが届いていた',
        timing=EventTiming.WAKE_UP, probability=0.02,
        effect=effect_money(3000)
    ),
    RandomEvent(
        id='wake_bill', name='請求書',
        description='予想外の請求書が届いていた',
        timing=EventTiming.WAKE_UP, probability=0.03,
        effect=effect_money(-1000)
    ),
    RandomEvent(
        id='wake_neighbor_veg', name='野菜のお裾分け',
        description='隣人から野菜をもらった',
        timing=EventTiming.WAKE_UP, probability=0.03,
        effect=effect_add_ingredient('キャベツ', 1)
    ),
    RandomEvent(
        id='wake_expired_food', name='食材が傷んでいた',
        description='冷蔵庫の食材が傷んでいた...',
        timing=EventTiming.WAKE_UP, probability=0.04,
        effect=effect_lose_random_ingredient()
    ),
    RandomEvent(
        id='wake_coupon', name='クーポン発見',
        description='チラシにお得なクーポンが入っていた',
        timing=EventTiming.WAKE_UP, probability=0.05,
        effect=effect_money(200)
    ),
    RandomEvent(
        id='wake_point_expiry', name='ポイント期限切れ',
        description='貯めていたポイントの期限が切れていた...',
        timing=EventTiming.WAKE_UP, probability=0.03,
        effect=effect_energy(-1)
    ),

    # 月曜・金曜・曜日関連 (5種)
    RandomEvent(
        id='wake_monday_blues', name='月曜の憂鬱',
        description='また一週間が始まる...',
        timing=EventTiming.WAKE_UP, probability=0.2,
        condition=cond_monday,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='wake_friday_happy', name='花金',
        description='今日は金曜日！週末が楽しみ',
        timing=EventTiming.WAKE_UP, probability=0.2,
        condition=cond_friday,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='wake_holiday_relax', name='休日の朝',
        description='今日は休み！ゆっくりできる',
        timing=EventTiming.WAKE_UP, probability=0.15,
        condition=cond_holiday,
        effect=effect_combined(effect_energy(1), effect_stamina(1))
    ),
    RandomEvent(
        id='wake_holiday_plan', name='お出かけ予定',
        description='今日は楽しい予定がある！',
        timing=EventTiming.WAKE_UP, probability=0.08,
        condition=cond_holiday,
        effect=effect_energy(2)
    ),
    RandomEvent(
        id='wake_weekday_tired', name='平日の疲れ',
        description='平日は毎日疲れる...',
        timing=EventTiming.WAKE_UP, probability=0.05,
        condition=lambda ctx: cond_weekday(ctx) and cond_low_stamina(ctx),
        effect=effect_stamina(-1)
    ),

    # その他 (5種)
    RandomEvent(
        id='wake_sns_viral', name='SNSでバズった',
        description='昨日の投稿がバズっていた！',
        timing=EventTiming.WAKE_UP, probability=0.02,
        effect=effect_energy(2)
    ),
    RandomEvent(
        id='wake_sns_flame', name='SNS炎上',
        description='何かの発言が炎上していた...',
        timing=EventTiming.WAKE_UP, probability=0.02,
        effect=effect_combined(effect_energy(-2), effect_stamina(-1))
    ),
    RandomEvent(
        id='wake_phone_dead', name='スマホ充電切れ',
        description='スマホの充電が切れていた',
        timing=EventTiming.WAKE_UP, probability=0.04,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='wake_good_news', name='朗報',
        description='友人から良いニュースが届いた',
        timing=EventTiming.WAKE_UP, probability=0.05,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='wake_bad_news', name='悲報',
        description='残念なニュースを聞いた',
        timing=EventTiming.WAKE_UP, probability=0.04,
        effect=effect_energy(-1)
    ),
]


# === 出社時イベント (40種類) ===

GO_TO_WORK_EVENTS = [
    # 天気関連 (10種)
    RandomEvent(
        id='commute_sunny_walk', name='快適な通勤',
        description='晴れた日の通勤は気持ちがいい',
        timing=EventTiming.GO_TO_WORK, probability=0.1,
        condition=cond_sunny,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='commute_rain_wet', name='雨に濡れた',
        description='傘を持っていなくて濡れてしまった',
        timing=EventTiming.GO_TO_WORK, probability=0.15,
        condition=cond_rainy,
        effect=effect_stamina(-1)
    ),
    RandomEvent(
        id='commute_rain_umbrella', name='傘を忘れた',
        description='傘を持ってくるのを忘れた...コンビニで買うことに',
        timing=EventTiming.GO_TO_WORK, probability=0.1,
        condition=cond_rainy,
        effect=effect_money(-500)
    ),
    RandomEvent(
        id='commute_storm_delay', name='電車遅延',
        description='嵐で電車が遅延...疲れた',
        timing=EventTiming.GO_TO_WORK, probability=0.4,
        condition=cond_stormy,
        effect=effect_combined(effect_energy(-1), effect_stamina(-1))
    ),
    RandomEvent(
        id='commute_sunny_detour', name='寄り道',
        description='天気がいいので少し遠回りした',
        timing=EventTiming.GO_TO_WORK, probability=0.08,
        condition=cond_sunny,
        effect=effect_combined(effect_stamina(-1), effect_energy(1))
    ),
    RandomEvent(
        id='commute_cloudy_fast', name='急いで出社',
        description='曇り空を見て急いで出社した',
        timing=EventTiming.GO_TO_WORK, probability=0.08,
        condition=cond_cloudy,
        effect=effect_stamina(-1)
    ),
    RandomEvent(
        id='commute_rain_taxi', name='タクシー利用',
        description='雨がひどくてタクシーを使った',
        timing=EventTiming.GO_TO_WORK, probability=0.08,
        condition=cond_stormy,
        effect=effect_money(-1000)
    ),
    RandomEvent(
        id='commute_sunny_coffee', name='朝のコーヒー',
        description='天気がいいのでカフェに寄った',
        timing=EventTiming.GO_TO_WORK, probability=0.06,
        condition=cond_sunny,
        effect=effect_combined(effect_money(-300), effect_energy(1))
    ),
    RandomEvent(
        id='commute_rain_splash', name='水たまり',
        description='車に水をかけられた...',
        timing=EventTiming.GO_TO_WORK, probability=0.1,
        condition=cond_rainy,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='commute_wind_strong', name='強風',
        description='強風で髪がボサボサに...',
        timing=EventTiming.GO_TO_WORK, probability=0.15,
        condition=cond_stormy,
        effect=effect_energy(-1)
    ),

    # 電車・通勤関連 (15種)
    RandomEvent(
        id='commute_crowded', name='満員電車',
        description='電車がぎゅうぎゅう詰めだった',
        timing=EventTiming.GO_TO_WORK, probability=0.15,
        condition=cond_weekday,
        effect=effect_stamina(-1)
    ),
    RandomEvent(
        id='commute_seat', name='座れた',
        description='珍しく電車で座れた！',
        timing=EventTiming.GO_TO_WORK, probability=0.08,
        condition=cond_weekday,
        effect=effect_stamina(1)
    ),
    RandomEvent(
        id='commute_delay', name='遅延',
        description='電車が遅延していた',
        timing=EventTiming.GO_TO_WORK, probability=0.1,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='commute_ac_cold', name='冷房が効きすぎ',
        description='電車の冷房が寒すぎた',
        timing=EventTiming.GO_TO_WORK, probability=0.06,
        effect=effect_stamina(-1)
    ),
    RandomEvent(
        id='commute_lost_item', name='落とし物',
        description='何かを落としてしまった...',
        timing=EventTiming.GO_TO_WORK, probability=0.03,
        effect=effect_money(-500)
    ),
    RandomEvent(
        id='commute_find_money', name='拾い物',
        description='道端で小銭を拾った',
        timing=EventTiming.GO_TO_WORK, probability=0.03,
        effect=effect_money(100)
    ),
    RandomEvent(
        id='commute_friend', name='友人に遭遇',
        description='通勤中に友人に会った',
        timing=EventTiming.GO_TO_WORK, probability=0.05,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='commute_cute_animal', name='かわいい動物',
        description='通勤中にかわいい犬を見かけた',
        timing=EventTiming.GO_TO_WORK, probability=0.06,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='commute_music', name='いい曲',
        description='通勤中にいい曲を発見した',
        timing=EventTiming.GO_TO_WORK, probability=0.08,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='commute_podcast', name='面白い番組',
        description='面白いポッドキャストを聴いていたら着いた',
        timing=EventTiming.GO_TO_WORK, probability=0.06,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='commute_trouble', name='トラブル',
        description='電車内でトラブルに巻き込まれた',
        timing=EventTiming.GO_TO_WORK, probability=0.04,
        effect=effect_combined(effect_energy(-1), effect_stamina(-1))
    ),
    RandomEvent(
        id='commute_forget_pass', name='定期忘れ',
        description='定期を忘れて切符を買うことに',
        timing=EventTiming.GO_TO_WORK, probability=0.05,
        effect=effect_money(-300)
    ),
    RandomEvent(
        id='commute_early_train', name='早い電車',
        description='いつもより早い電車に乗れた',
        timing=EventTiming.GO_TO_WORK, probability=0.08,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='commute_miss_train', name='電車を逃した',
        description='目の前で電車が行ってしまった',
        timing=EventTiming.GO_TO_WORK, probability=0.08,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='commute_nap', name='うたた寝',
        description='電車でうたた寝してしまった',
        timing=EventTiming.GO_TO_WORK, probability=0.06,
        effect=effect_stamina(1)
    ),

    # 会社関連 (10種)
    RandomEvent(
        id='work_meeting_cancel', name='会議キャンセル',
        description='今日の会議がキャンセルになった！',
        timing=EventTiming.GO_TO_WORK, probability=0.05,
        condition=cond_weekday,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='work_deadline', name='締め切り',
        description='今日が締め切りだった...',
        timing=EventTiming.GO_TO_WORK, probability=0.08,
        condition=cond_weekday,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='work_praise', name='褒められた',
        description='上司に仕事を褒められた',
        timing=EventTiming.GO_TO_WORK, probability=0.05,
        condition=cond_weekday,
        effect=effect_energy(2)
    ),
    RandomEvent(
        id='work_scolded', name='叱られた',
        description='上司に叱られてしまった',
        timing=EventTiming.GO_TO_WORK, probability=0.05,
        condition=cond_weekday,
        effect=effect_combined(effect_energy(-2), effect_stamina(-1))
    ),
    RandomEvent(
        id='work_bonus_rumor', name='ボーナスの噂',
        description='ボーナスが良いという噂を聞いた',
        timing=EventTiming.GO_TO_WORK, probability=0.03,
        condition=cond_weekday,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='work_overtime_notice', name='残業予告',
        description='今日は残業になりそう...',
        timing=EventTiming.GO_TO_WORK, probability=0.1,
        condition=cond_weekday,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='work_early_finish', name='早上がり予告',
        description='今日は早く帰れそう！',
        timing=EventTiming.GO_TO_WORK, probability=0.05,
        condition=cond_weekday,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='work_new_project', name='新プロジェクト',
        description='面白そうな新プロジェクトに配属された',
        timing=EventTiming.GO_TO_WORK, probability=0.03,
        condition=cond_weekday,
        effect=effect_energy(2)
    ),
    RandomEvent(
        id='work_boring_task', name='退屈な仕事',
        description='今日の仕事は退屈そう...',
        timing=EventTiming.GO_TO_WORK, probability=0.08,
        condition=cond_weekday,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='work_free_snack', name='差し入れ',
        description='誰かがお菓子を差し入れてくれた',
        timing=EventTiming.GO_TO_WORK, probability=0.06,
        condition=cond_weekday,
        effect=effect_fullness(1)
    ),

    # その他 (5種)
    RandomEvent(
        id='commute_motivate', name='やる気UP',
        description='今日は何かいいことがありそう！',
        timing=EventTiming.GO_TO_WORK, probability=0.05,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='commute_demotivate', name='やる気DOWN',
        description='なんだか気が乗らない...',
        timing=EventTiming.GO_TO_WORK, probability=0.05,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='commute_coffee_spill', name='コーヒーこぼす',
        description='コーヒーを服にこぼしてしまった',
        timing=EventTiming.GO_TO_WORK, probability=0.03,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='commute_street_food', name='屋台発見',
        description='美味しそうな屋台を見つけて食べた',
        timing=EventTiming.GO_TO_WORK, probability=0.04,
        effect=effect_combined(effect_money(-300), effect_fullness(2))
    ),
    RandomEvent(
        id='commute_construction', name='工事中',
        description='通勤路が工事中で遠回り',
        timing=EventTiming.GO_TO_WORK, probability=0.05,
        effect=effect_stamina(-1)
    ),
]


# === 昼食後イベント (40種類) ===

AFTER_LUNCH_EVENTS = [
    # 食後の体調 (15種)
    RandomEvent(
        id='lunch_sleepy', name='食後の眠気',
        description='お昼を食べたら眠くなってきた',
        timing=EventTiming.AFTER_LUNCH, probability=0.15,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='lunch_energized', name='パワーチャージ',
        description='しっかり食べてパワーチャージ！',
        timing=EventTiming.AFTER_LUNCH, probability=0.1,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='lunch_overeaten', name='食べ過ぎ',
        description='食べ過ぎてお腹が苦しい...',
        timing=EventTiming.AFTER_LUNCH, probability=0.08,
        effect=effect_stamina(-1)
    ),
    RandomEvent(
        id='lunch_heartburn', name='胃もたれ',
        description='ちょっと胃がもたれる...',
        timing=EventTiming.AFTER_LUNCH, probability=0.06,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='lunch_satisfied', name='満足感',
        description='美味しいお昼で満足！',
        timing=EventTiming.AFTER_LUNCH, probability=0.1,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='lunch_still_hungry', name='物足りない',
        description='まだちょっと物足りない...',
        timing=EventTiming.AFTER_LUNCH, probability=0.08,
        effect=effect_fullness(-1)
    ),
    RandomEvent(
        id='lunch_coffee_boost', name='食後のコーヒー',
        description='コーヒーを飲んでシャキッとした',
        timing=EventTiming.AFTER_LUNCH, probability=0.1,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='lunch_nap', name='昼寝',
        description='少し昼寝をした',
        timing=EventTiming.AFTER_LUNCH, probability=0.06,
        condition=cond_holiday,
        effect=effect_combined(effect_energy(1), effect_stamina(1))
    ),
    RandomEvent(
        id='lunch_walk', name='食後の散歩',
        description='食後に少し散歩した',
        timing=EventTiming.AFTER_LUNCH, probability=0.08,
        effect=effect_stamina(1)
    ),
    RandomEvent(
        id='lunch_dessert', name='デザート',
        description='ついデザートも食べてしまった',
        timing=EventTiming.AFTER_LUNCH, probability=0.06,
        effect=effect_combined(effect_money(-200), effect_fullness(1))
    ),
    RandomEvent(
        id='lunch_food_coma', name='食い倒れ',
        description='食べ過ぎで動けない...',
        timing=EventTiming.AFTER_LUNCH, probability=0.04,
        effect=effect_combined(effect_energy(-1), effect_stamina(-1))
    ),
    RandomEvent(
        id='lunch_refreshed', name='リフレッシュ',
        description='休憩でリフレッシュできた',
        timing=EventTiming.AFTER_LUNCH, probability=0.08,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='lunch_stomach_ache', name='お腹の調子',
        description='なんだかお腹の調子が悪い...',
        timing=EventTiming.AFTER_LUNCH, probability=0.04,
        effect=effect_stamina(-1)
    ),
    RandomEvent(
        id='lunch_healthy', name='健康的な昼食',
        description='バランスの良い食事で調子がいい',
        timing=EventTiming.AFTER_LUNCH, probability=0.06,
        effect=effect_combined(effect_energy(1), effect_stamina(1))
    ),
    RandomEvent(
        id='lunch_junk', name='ジャンクフード',
        description='ジャンクフードを食べてしまった...',
        timing=EventTiming.AFTER_LUNCH, probability=0.05,
        effect=effect_stamina(-1)
    ),

    # 仕事関連 (15種)
    RandomEvent(
        id='afternoon_meeting', name='午後の会議',
        description='午後から長い会議がある...',
        timing=EventTiming.AFTER_LUNCH, probability=0.1,
        condition=cond_weekday,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='afternoon_praise', name='仕事が評価された',
        description='午前の仕事が評価された！',
        timing=EventTiming.AFTER_LUNCH, probability=0.05,
        condition=cond_weekday,
        effect=effect_energy(2)
    ),
    RandomEvent(
        id='afternoon_error', name='ミス発覚',
        description='午前の仕事でミスが見つかった...',
        timing=EventTiming.AFTER_LUNCH, probability=0.06,
        condition=cond_weekday,
        effect=effect_energy(-2)
    ),
    RandomEvent(
        id='afternoon_break', name='休憩延長',
        description='少し長めに休憩できた',
        timing=EventTiming.AFTER_LUNCH, probability=0.06,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='afternoon_rush', name='午後の急ぎ仕事',
        description='急な仕事が入ってきた',
        timing=EventTiming.AFTER_LUNCH, probability=0.08,
        condition=cond_weekday,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='afternoon_chat', name='同僚との雑談',
        description='同僚と楽しく雑談した',
        timing=EventTiming.AFTER_LUNCH, probability=0.08,
        condition=cond_weekday,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='afternoon_snack', name='おやつタイム',
        description='同僚がお菓子をくれた',
        timing=EventTiming.AFTER_LUNCH, probability=0.06,
        condition=cond_weekday,
        effect=effect_fullness(1)
    ),
    RandomEvent(
        id='afternoon_progress', name='仕事が捗る',
        description='午後の仕事が順調に進んだ',
        timing=EventTiming.AFTER_LUNCH, probability=0.08,
        condition=cond_weekday,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='afternoon_stuck', name='行き詰まり',
        description='仕事が行き詰まってしまった',
        timing=EventTiming.AFTER_LUNCH, probability=0.08,
        condition=cond_weekday,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='afternoon_help', name='助けてもらった',
        description='困っていたら同僚が助けてくれた',
        timing=EventTiming.AFTER_LUNCH, probability=0.05,
        condition=cond_weekday,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='afternoon_helped', name='人を助けた',
        description='困っている同僚を助けた',
        timing=EventTiming.AFTER_LUNCH, probability=0.05,
        condition=cond_weekday,
        effect=effect_combined(effect_energy(1), effect_stamina(-1))
    ),
    RandomEvent(
        id='afternoon_news', name='良いニュース',
        description='会社で良いニュースがあった',
        timing=EventTiming.AFTER_LUNCH, probability=0.04,
        condition=cond_weekday,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='afternoon_bad_news', name='悪いニュース',
        description='会社であまり良くないニュースが...',
        timing=EventTiming.AFTER_LUNCH, probability=0.04,
        condition=cond_weekday,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='afternoon_visitor', name='来客',
        description='来客対応で疲れた',
        timing=EventTiming.AFTER_LUNCH, probability=0.05,
        condition=cond_weekday,
        effect=effect_stamina(-1)
    ),
    RandomEvent(
        id='afternoon_training', name='研修',
        description='午後から研修があった',
        timing=EventTiming.AFTER_LUNCH, probability=0.04,
        condition=cond_weekday,
        effect=effect_combined(effect_energy(-1), effect_stamina(-1))
    ),

    # 休日関連 (5種)
    RandomEvent(
        id='holiday_afternoon_relax', name='のんびり',
        description='午後はのんびり過ごした',
        timing=EventTiming.AFTER_LUNCH, probability=0.1,
        condition=cond_holiday,
        effect=effect_combined(effect_energy(1), effect_stamina(1))
    ),
    RandomEvent(
        id='holiday_afternoon_hobby', name='趣味の時間',
        description='趣味に没頭した',
        timing=EventTiming.AFTER_LUNCH, probability=0.08,
        condition=cond_holiday,
        effect=effect_energy(2)
    ),
    RandomEvent(
        id='holiday_afternoon_chores', name='家事',
        description='溜まっていた家事を片付けた',
        timing=EventTiming.AFTER_LUNCH, probability=0.1,
        condition=cond_holiday,
        effect=effect_stamina(-1)
    ),
    RandomEvent(
        id='holiday_afternoon_outing', name='お出かけ',
        description='午後は出かけることにした',
        timing=EventTiming.AFTER_LUNCH, probability=0.08,
        condition=cond_holiday,
        effect=effect_combined(effect_energy(1), effect_money(-500))
    ),
    RandomEvent(
        id='holiday_afternoon_gaming', name='ゲーム三昧',
        description='ついゲームに夢中になってしまった',
        timing=EventTiming.AFTER_LUNCH, probability=0.08,
        condition=cond_holiday,
        effect=effect_combined(effect_energy(1), effect_stamina(-1))
    ),

    # その他 (5種)
    RandomEvent(
        id='afternoon_call_friend', name='友人から連絡',
        description='友人から連絡が来た',
        timing=EventTiming.AFTER_LUNCH, probability=0.05,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='afternoon_call_spam', name='迷惑電話',
        description='迷惑電話がかかってきた',
        timing=EventTiming.AFTER_LUNCH, probability=0.04,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='afternoon_memory', name='思い出す',
        description='やり忘れていたことを思い出した',
        timing=EventTiming.AFTER_LUNCH, probability=0.05,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='afternoon_idea', name='良いアイデア',
        description='良いアイデアを思いついた！',
        timing=EventTiming.AFTER_LUNCH, probability=0.05,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='afternoon_motivation', name='やる気',
        description='午後もがんばろう！',
        timing=EventTiming.AFTER_LUNCH, probability=0.08,
        effect=effect_energy(1)
    ),
]


# === 買い物中イベント (40種類) ===

AT_SHOP_EVENTS = [
    # セール・値引き関連 (10種)
    RandomEvent(
        id='shop_big_sale', name='大特価',
        description='大特価セールをやっていた！',
        timing=EventTiming.AT_SHOP, probability=0.08,
        effect=effect_money(300)
    ),
    RandomEvent(
        id='shop_coupon', name='クーポン配布',
        description='店頭でクーポンをもらった',
        timing=EventTiming.AT_SHOP, probability=0.1,
        effect=effect_money(100)
    ),
    RandomEvent(
        id='shop_point_card', name='ポイント5倍',
        description='今日はポイント5倍デーだった！',
        timing=EventTiming.AT_SHOP, probability=0.06,
        effect=effect_money(200)
    ),
    RandomEvent(
        id='shop_sold_out', name='売り切れ',
        description='欲しかった商品が売り切れていた',
        timing=EventTiming.AT_SHOP, probability=0.08,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='shop_expensive', name='値上げ',
        description='いつもの商品が値上げしていた',
        timing=EventTiming.AT_SHOP, probability=0.08,
        effect=effect_money(-100)
    ),
    RandomEvent(
        id='shop_free_sample', name='試食',
        description='美味しい試食があった',
        timing=EventTiming.AT_SHOP, probability=0.1,
        effect=effect_fullness(1)
    ),
    RandomEvent(
        id='shop_lottery', name='ガラポン当選',
        description='ガラポンで当たりが出た！',
        timing=EventTiming.AT_SHOP, probability=0.03,
        effect=effect_money(500)
    ),
    RandomEvent(
        id='shop_lottery_lose', name='ガラポンハズレ',
        description='ガラポンはハズレだった',
        timing=EventTiming.AT_SHOP, probability=0.05,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='shop_bargain_hunt', name='掘り出し物',
        description='思わぬ掘り出し物を発見！',
        timing=EventTiming.AT_SHOP, probability=0.05,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='shop_impulse_buy', name='衝動買い',
        description='つい余計なものを買ってしまった',
        timing=EventTiming.AT_SHOP, probability=0.08,
        effect=effect_money(-500)
    ),

    # 食材発見 (15種)
    RandomEvent(
        id='shop_find_egg', name='卵のセール',
        description='卵が特売だった！おまけでもらえた',
        timing=EventTiming.AT_SHOP, probability=0.05,
        effect=effect_add_ingredient('卵', 2)
    ),
    RandomEvent(
        id='shop_find_tofu', name='豆腐のおまけ',
        description='豆腐を買ったらもう1個おまけでもらえた',
        timing=EventTiming.AT_SHOP, probability=0.04,
        effect=effect_add_ingredient('豆腐', 1)
    ),
    RandomEvent(
        id='shop_find_veg', name='野菜の詰め合わせ',
        description='お買い得な野菜詰め合わせを発見',
        timing=EventTiming.AT_SHOP, probability=0.04,
        effect=effect_add_ingredient('キャベツ', 1)
    ),
    RandomEvent(
        id='shop_find_meat', name='肉の特売',
        description='肉が特売価格だった！',
        timing=EventTiming.AT_SHOP, probability=0.04,
        effect=effect_add_ingredient('豚バラ肉', 1)
    ),
    RandomEvent(
        id='shop_find_fish', name='魚の特売',
        description='新鮮な魚が特売だった',
        timing=EventTiming.AT_SHOP, probability=0.04,
        effect=effect_add_ingredient('鮭', 1)
    ),
    RandomEvent(
        id='shop_find_natto', name='納豆3パック',
        description='納豆3パックセットがお得だった',
        timing=EventTiming.AT_SHOP, probability=0.05,
        effect=effect_add_ingredient('納豆', 2)
    ),
    RandomEvent(
        id='shop_find_rice', name='米のサービス',
        description='米を買ったらサービスでもう少しもらえた',
        timing=EventTiming.AT_SHOP, probability=0.03,
        effect=effect_add_ingredient('米', 1)
    ),
    RandomEvent(
        id='shop_find_onion', name='玉ねぎのおまけ',
        description='玉ねぎをおまけでもらえた',
        timing=EventTiming.AT_SHOP, probability=0.05,
        effect=effect_add_ingredient('玉ねぎ', 1)
    ),
    RandomEvent(
        id='shop_find_carrot', name='にんじんのおまけ',
        description='にんじんをおまけでもらえた',
        timing=EventTiming.AT_SHOP, probability=0.05,
        effect=effect_add_ingredient('にんじん', 1)
    ),
    RandomEvent(
        id='shop_find_potato', name='じゃがいものおまけ',
        description='じゃがいもをおまけでもらえた',
        timing=EventTiming.AT_SHOP, probability=0.05,
        effect=effect_add_ingredient('じゃがいも', 1)
    ),
    RandomEvent(
        id='shop_find_mushroom', name='きのこのおまけ',
        description='しめじをおまけでもらえた',
        timing=EventTiming.AT_SHOP, probability=0.04,
        effect=effect_add_ingredient('しめじ', 1)
    ),
    RandomEvent(
        id='shop_find_instant', name='カップ麺のおまけ',
        description='カップ麺をおまけでもらえた',
        timing=EventTiming.AT_SHOP, probability=0.04,
        effect=effect_add_provision('カップ麺', 1)
    ),
    RandomEvent(
        id='shop_find_bread', name='パンのサービス',
        description='パンをサービスでもらった',
        timing=EventTiming.AT_SHOP, probability=0.04,
        effect=effect_add_provision('パン', 1)
    ),
    RandomEvent(
        id='shop_find_retort', name='レトルトのおまけ',
        description='レトルトカレーをおまけでもらえた',
        timing=EventTiming.AT_SHOP, probability=0.03,
        effect=effect_add_provision('レトルトカレー', 1)
    ),
    RandomEvent(
        id='shop_find_onigiri', name='おにぎりサービス',
        description='おにぎりをサービスでもらった',
        timing=EventTiming.AT_SHOP, probability=0.04,
        effect=effect_add_provision('おにぎり', 1)
    ),

    # 店内でのハプニング (10種)
    RandomEvent(
        id='shop_crowded', name='混雑',
        description='店がとても混んでいた',
        timing=EventTiming.AT_SHOP, probability=0.12,
        effect=effect_stamina(-1)
    ),
    RandomEvent(
        id='shop_empty', name='空いてる',
        description='店が空いていてスムーズに買えた',
        timing=EventTiming.AT_SHOP, probability=0.1,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='shop_cart_hit', name='カートがぶつかった',
        description='他の客のカートがぶつかってきた',
        timing=EventTiming.AT_SHOP, probability=0.04,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='shop_long_line', name='長いレジ待ち',
        description='レジがとても混んでいた',
        timing=EventTiming.AT_SHOP, probability=0.1,
        effect=effect_stamina(-1)
    ),
    RandomEvent(
        id='shop_fast_checkout', name='すいてるレジ',
        description='空いてるレジがあってすぐ会計できた',
        timing=EventTiming.AT_SHOP, probability=0.08,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='shop_bag_forget', name='エコバッグ忘れ',
        description='エコバッグを忘れて袋を買うことに',
        timing=EventTiming.AT_SHOP, probability=0.06,
        effect=effect_money(-10)
    ),
    RandomEvent(
        id='shop_drop_item', name='商品を落とした',
        description='うっかり商品を落としてしまった',
        timing=EventTiming.AT_SHOP, probability=0.04,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='shop_nice_staff', name='親切な店員',
        description='店員さんがとても親切だった',
        timing=EventTiming.AT_SHOP, probability=0.06,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='shop_rude_staff', name='愛想のない店員',
        description='店員さんの態度が良くなかった',
        timing=EventTiming.AT_SHOP, probability=0.04,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='shop_meet_neighbor', name='知り合いに遭遇',
        description='知り合いに会って話し込んでしまった',
        timing=EventTiming.AT_SHOP, probability=0.05,
        effect=effect_combined(effect_energy(1), effect_stamina(-1))
    ),

    # 天気関連 (5種)
    RandomEvent(
        id='shop_rain_start', name='雨が降り出した',
        description='買い物中に雨が降り出した',
        timing=EventTiming.AT_SHOP, probability=0.15,
        condition=cond_cloudy,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='shop_rain_stop', name='雨が止んだ',
        description='買い物中に雨が止んだ！',
        timing=EventTiming.AT_SHOP, probability=0.15,
        condition=cond_rainy,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='shop_sunny_nice', name='いい天気',
        description='天気が良くて買い物日和',
        timing=EventTiming.AT_SHOP, probability=0.1,
        condition=cond_sunny,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='shop_hot', name='暑い',
        description='店内が暑くて疲れた',
        timing=EventTiming.AT_SHOP, probability=0.06,
        condition=cond_sunny,
        effect=effect_stamina(-1)
    ),
    RandomEvent(
        id='shop_cold', name='冷房が効きすぎ',
        description='店内の冷房が効きすぎていた',
        timing=EventTiming.AT_SHOP, probability=0.06,
        condition=cond_rainy,
        effect=effect_stamina(-1)
    ),
]


# === 退勤時イベント (40種類) ===

LEAVE_WORK_EVENTS = [
    # 残業関連 (10種)
    RandomEvent(
        id='leave_overtime', name='残業',
        description='残業で遅くなってしまった',
        timing=EventTiming.LEAVE_WORK, probability=0.12,
        condition=cond_weekday,
        effect=effect_combined(effect_energy(-1), effect_stamina(-1))
    ),
    RandomEvent(
        id='leave_early', name='早上がり',
        description='今日は早く帰れた！',
        timing=EventTiming.LEAVE_WORK, probability=0.08,
        condition=cond_weekday,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='leave_on_time', name='定時退社',
        description='今日は定時で帰れた',
        timing=EventTiming.LEAVE_WORK, probability=0.1,
        condition=cond_weekday,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='leave_hard_day', name='大変な一日',
        description='今日は大変な一日だった...',
        timing=EventTiming.LEAVE_WORK, probability=0.1,
        condition=cond_weekday,
        effect=effect_combined(effect_energy(-2), effect_stamina(-1))
    ),
    RandomEvent(
        id='leave_easy_day', name='楽な一日',
        description='今日は比較的楽な一日だった',
        timing=EventTiming.LEAVE_WORK, probability=0.08,
        condition=cond_weekday,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='leave_achievement', name='達成感',
        description='今日の仕事をやり遂げた！',
        timing=EventTiming.LEAVE_WORK, probability=0.06,
        condition=cond_weekday,
        effect=effect_energy(2)
    ),
    RandomEvent(
        id='leave_frustration', name='仕事の不満',
        description='仕事でイライラすることがあった',
        timing=EventTiming.LEAVE_WORK, probability=0.08,
        condition=cond_weekday,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='leave_tired', name='疲労困憊',
        description='もうヘトヘト...',
        timing=EventTiming.LEAVE_WORK, probability=0.08,
        condition=lambda ctx: cond_weekday(ctx) and cond_low_stamina(ctx),
        effect=effect_stamina(-1)
    ),
    RandomEvent(
        id='leave_overtime_pay', name='残業代',
        description='残業代がもらえる！',
        timing=EventTiming.LEAVE_WORK, probability=0.05,
        condition=cond_weekday,
        effect=effect_money(1000)
    ),
    RandomEvent(
        id='leave_no_overtime', name='残業なし',
        description='今月は残業が少なかった',
        timing=EventTiming.LEAVE_WORK, probability=0.05,
        condition=cond_weekday,
        effect=effect_energy(1)
    ),

    # 帰り道 (15種)
    RandomEvent(
        id='leave_rain', name='帰りの雨',
        description='帰り道で雨に降られた',
        timing=EventTiming.LEAVE_WORK, probability=0.15,
        condition=cond_rainy,
        effect=effect_stamina(-1)
    ),
    RandomEvent(
        id='leave_nice_weather', name='帰りの良い天気',
        description='帰り道の天気が気持ちいい',
        timing=EventTiming.LEAVE_WORK, probability=0.1,
        condition=cond_sunny,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='leave_sunset', name='きれいな夕焼け',
        description='きれいな夕焼けを見た',
        timing=EventTiming.LEAVE_WORK, probability=0.08,
        condition=cond_sunny,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='leave_friend_meet', name='友人と遭遇',
        description='帰り道で友人に会った',
        timing=EventTiming.LEAVE_WORK, probability=0.05,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='leave_drink', name='飲みに誘われた',
        description='同僚に飲みに誘われた',
        timing=EventTiming.LEAVE_WORK, probability=0.06,
        condition=cond_weekday,
        effect=effect_combined(effect_money(-2000), effect_energy(1), effect_fullness(3))
    ),
    RandomEvent(
        id='leave_train_delay', name='電車遅延',
        description='帰りの電車が遅延していた',
        timing=EventTiming.LEAVE_WORK, probability=0.1,
        effect=effect_stamina(-1)
    ),
    RandomEvent(
        id='leave_train_crowded', name='帰りの満員電車',
        description='帰りの電車がぎゅうぎゅう',
        timing=EventTiming.LEAVE_WORK, probability=0.12,
        condition=cond_weekday,
        effect=effect_stamina(-1)
    ),
    RandomEvent(
        id='leave_train_seat', name='座れた',
        description='帰りの電車で座れた！',
        timing=EventTiming.LEAVE_WORK, probability=0.08,
        effect=effect_stamina(1)
    ),
    RandomEvent(
        id='leave_find_money', name='お金を拾った',
        description='道端でお金を拾った',
        timing=EventTiming.LEAVE_WORK, probability=0.02,
        effect=effect_money(500)
    ),
    RandomEvent(
        id='leave_lose_item', name='落とし物',
        description='何かを落としてしまった',
        timing=EventTiming.LEAVE_WORK, probability=0.03,
        effect=effect_money(-300)
    ),
    RandomEvent(
        id='leave_cafe', name='カフェに寄った',
        description='帰りにカフェでひと息ついた',
        timing=EventTiming.LEAVE_WORK, probability=0.05,
        effect=effect_combined(effect_money(-400), effect_energy(1))
    ),
    RandomEvent(
        id='leave_convenience', name='コンビニ寄り道',
        description='コンビニで買い食いしてしまった',
        timing=EventTiming.LEAVE_WORK, probability=0.08,
        effect=effect_combined(effect_money(-300), effect_fullness(2))
    ),
    RandomEvent(
        id='leave_bookstore', name='本屋寄り道',
        description='本屋で本を買ってしまった',
        timing=EventTiming.LEAVE_WORK, probability=0.04,
        effect=effect_combined(effect_money(-800), effect_energy(1))
    ),
    RandomEvent(
        id='leave_walk', name='歩いて帰宅',
        description='天気がいいので歩いて帰った',
        timing=EventTiming.LEAVE_WORK, probability=0.05,
        condition=cond_sunny,
        effect=effect_combined(effect_stamina(-1), effect_energy(1))
    ),
    RandomEvent(
        id='leave_run', name='走って帰宅',
        description='雨が降りそうなので走って帰った',
        timing=EventTiming.LEAVE_WORK, probability=0.08,
        condition=cond_cloudy,
        effect=effect_stamina(-1)
    ),

    # その他 (15種)
    RandomEvent(
        id='leave_good_news', name='良いニュース',
        description='帰り道に良いニュースを聞いた',
        timing=EventTiming.LEAVE_WORK, probability=0.04,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='leave_bad_news', name='悪いニュース',
        description='帰り道に悪いニュースを聞いた',
        timing=EventTiming.LEAVE_WORK, probability=0.04,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='leave_music', name='良い曲',
        description='帰り道にいい曲を聴いた',
        timing=EventTiming.LEAVE_WORK, probability=0.06,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='leave_call', name='電話',
        description='帰り道に長電話してしまった',
        timing=EventTiming.LEAVE_WORK, probability=0.04,
        effect=effect_combined(effect_energy(1), effect_stamina(-1))
    ),
    RandomEvent(
        id='leave_friday', name='週末！',
        description='今週も終わり！週末だ！',
        timing=EventTiming.LEAVE_WORK, probability=0.3,
        condition=cond_friday,
        effect=effect_energy(2)
    ),
    RandomEvent(
        id='leave_monday_end', name='月曜終了',
        description='月曜日を乗り越えた！',
        timing=EventTiming.LEAVE_WORK, probability=0.2,
        condition=cond_monday,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='leave_gym', name='ジム寄り道',
        description='ジムに寄って運動した',
        timing=EventTiming.LEAVE_WORK, probability=0.04,
        effect=effect_combined(effect_stamina(-1), effect_energy(1), effect_money(-500))
    ),
    RandomEvent(
        id='leave_gift', name='お土産',
        description='同僚からお土産をもらった',
        timing=EventTiming.LEAVE_WORK, probability=0.04,
        condition=cond_weekday,
        effect=effect_add_provision('おにぎり', 1)
    ),
    RandomEvent(
        id='leave_street_food', name='屋台',
        description='屋台で美味しそうなものを見つけた',
        timing=EventTiming.LEAVE_WORK, probability=0.04,
        effect=effect_combined(effect_money(-400), effect_fullness(2))
    ),
    RandomEvent(
        id='leave_medicine', name='薬局寄り道',
        description='疲れたので栄養ドリンクを買った',
        timing=EventTiming.LEAVE_WORK, probability=0.05,
        condition=cond_low_stamina,
        effect=effect_combined(effect_money(-300), effect_stamina(1))
    ),
    RandomEvent(
        id='leave_accident', name='事故渋滞',
        description='事故渋滞で電車が止まった',
        timing=EventTiming.LEAVE_WORK, probability=0.04,
        effect=effect_combined(effect_energy(-1), effect_stamina(-1))
    ),
    RandomEvent(
        id='leave_feel_sick', name='気分が悪い',
        description='なんだか気分が悪い...',
        timing=EventTiming.LEAVE_WORK, probability=0.04,
        condition=cond_low_stamina,
        effect=effect_stamina(-1)
    ),
    RandomEvent(
        id='leave_energetic', name='まだ元気',
        description='まだまだ元気がある！',
        timing=EventTiming.LEAVE_WORK, probability=0.05,
        condition=cond_high_stamina,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='leave_stress', name='ストレス',
        description='仕事のストレスが溜まっている...',
        timing=EventTiming.LEAVE_WORK, probability=0.06,
        condition=cond_weekday,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='leave_relief', name='安堵',
        description='やっと仕事が終わった...ほっとした',
        timing=EventTiming.LEAVE_WORK, probability=0.08,
        condition=cond_weekday,
        effect=effect_energy(1)
    ),
]


# === 帰宅後イベント (40種類) ===

AFTER_WORK_EVENTS = [
    # 家での発見 (10種)
    RandomEvent(
        id='home_package', name='届け物',
        description='注文していた荷物が届いていた',
        timing=EventTiming.AFTER_WORK, probability=0.06,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='home_mail', name='郵便物',
        description='大切な郵便物が届いていた',
        timing=EventTiming.AFTER_WORK, probability=0.05,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='home_bill', name='請求書',
        description='高額な請求書が届いていた...',
        timing=EventTiming.AFTER_WORK, probability=0.04,
        effect=effect_combined(effect_money(-1000), effect_energy(-1))
    ),
    RandomEvent(
        id='home_gift', name='プレゼント',
        description='友人からプレゼントが届いていた！',
        timing=EventTiming.AFTER_WORK, probability=0.02,
        effect=effect_energy(2)
    ),
    RandomEvent(
        id='home_broken', name='故障発見',
        description='家電が故障していた...',
        timing=EventTiming.AFTER_WORK, probability=0.03,
        effect=effect_combined(effect_money(-2000), effect_energy(-1))
    ),
    RandomEvent(
        id='home_clean', name='掃除完了',
        description='部屋が片付いていて気持ちいい',
        timing=EventTiming.AFTER_WORK, probability=0.05,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='home_messy', name='散らかった部屋',
        description='部屋が散らかっていて憂鬱...',
        timing=EventTiming.AFTER_WORK, probability=0.06,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='home_food_gift', name='食材の差し入れ',
        description='親から食材が届いていた！',
        timing=EventTiming.AFTER_WORK, probability=0.03,
        effect=effect_combined(effect_add_ingredient('米', 2), effect_add_ingredient('卵', 3))
    ),
    RandomEvent(
        id='home_neighbor', name='隣人からのお裾分け',
        description='隣人からお裾分けをもらった',
        timing=EventTiming.AFTER_WORK, probability=0.04,
        effect=effect_add_ingredient('キャベツ', 1)
    ),
    RandomEvent(
        id='home_expired', name='食材が腐っていた',
        description='冷蔵庫の中身が傷んでいた...',
        timing=EventTiming.AFTER_WORK, probability=0.05,
        effect=effect_lose_random_ingredient()
    ),

    # リラックス (15種)
    RandomEvent(
        id='home_relax_bath', name='お風呂でリラックス',
        description='ゆっくりお風呂に入ってリラックス',
        timing=EventTiming.AFTER_WORK, probability=0.1,
        effect=effect_combined(effect_energy(1), effect_stamina(1))
    ),
    RandomEvent(
        id='home_relax_tv', name='テレビでリラックス',
        description='好きな番組を見てリラックス',
        timing=EventTiming.AFTER_WORK, probability=0.08,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='home_relax_music', name='音楽でリラックス',
        description='好きな音楽を聴いてリラックス',
        timing=EventTiming.AFTER_WORK, probability=0.08,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='home_relax_game', name='ゲームでリラックス',
        description='少しゲームをしてリラックス',
        timing=EventTiming.AFTER_WORK, probability=0.08,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='home_relax_read', name='読書でリラックス',
        description='本を読んでリラックス',
        timing=EventTiming.AFTER_WORK, probability=0.06,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='home_relax_pet', name='ペットと遊ぶ',
        description='ペットと遊んで癒された',
        timing=EventTiming.AFTER_WORK, probability=0.04,
        effect=effect_energy(2)
    ),
    RandomEvent(
        id='home_stretch', name='ストレッチ',
        description='ストレッチをして体をほぐした',
        timing=EventTiming.AFTER_WORK, probability=0.06,
        effect=effect_stamina(1)
    ),
    RandomEvent(
        id='home_yoga', name='ヨガ',
        description='軽くヨガをして心身をリフレッシュ',
        timing=EventTiming.AFTER_WORK, probability=0.04,
        effect=effect_combined(effect_energy(1), effect_stamina(1))
    ),
    RandomEvent(
        id='home_meditation', name='瞑想',
        description='少し瞑想して心を落ち着けた',
        timing=EventTiming.AFTER_WORK, probability=0.04,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='home_snack', name='おやつタイム',
        description='少しおやつを食べてしまった',
        timing=EventTiming.AFTER_WORK, probability=0.08,
        effect=effect_fullness(1)
    ),
    RandomEvent(
        id='home_beer', name='晩酌',
        description='今日は一杯飲んでしまった',
        timing=EventTiming.AFTER_WORK, probability=0.06,
        effect=effect_combined(effect_money(-300), effect_energy(1))
    ),
    RandomEvent(
        id='home_call_friend', name='友人と電話',
        description='友人と電話で話して楽しかった',
        timing=EventTiming.AFTER_WORK, probability=0.05,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='home_sns', name='SNSタイム',
        description='SNSをチェックしていたら時間が過ぎた',
        timing=EventTiming.AFTER_WORK, probability=0.08,
        effect=effect_combined(effect_energy(1), effect_stamina(-1))
    ),
    RandomEvent(
        id='home_video', name='動画視聴',
        description='つい動画を見過ぎてしまった',
        timing=EventTiming.AFTER_WORK, probability=0.08,
        effect=effect_combined(effect_energy(1), effect_stamina(-1))
    ),
    RandomEvent(
        id='home_nap', name='うたた寝',
        description='ついうたた寝してしまった',
        timing=EventTiming.AFTER_WORK, probability=0.06,
        effect=effect_stamina(1)
    ),

    # 家事・トラブル (10種)
    RandomEvent(
        id='home_laundry', name='洗濯',
        description='洗濯物を片付けた',
        timing=EventTiming.AFTER_WORK, probability=0.08,
        effect=effect_stamina(-1)
    ),
    RandomEvent(
        id='home_cleaning', name='掃除',
        description='少し部屋を掃除した',
        timing=EventTiming.AFTER_WORK, probability=0.06,
        effect=effect_stamina(-1)
    ),
    RandomEvent(
        id='home_dishes', name='皿洗い',
        description='溜まっていた皿を洗った',
        timing=EventTiming.AFTER_WORK, probability=0.08,
        effect=effect_stamina(-1)
    ),
    RandomEvent(
        id='home_trash', name='ゴミ出し',
        description='ゴミをまとめて出した',
        timing=EventTiming.AFTER_WORK, probability=0.06,
        effect=effect_stamina(-1)
    ),
    RandomEvent(
        id='home_pest', name='虫が出た',
        description='部屋に虫が出て大騒ぎ',
        timing=EventTiming.AFTER_WORK, probability=0.03,
        effect=effect_combined(effect_energy(-1), effect_stamina(-1))
    ),
    RandomEvent(
        id='home_noise', name='騒音',
        description='隣の部屋がうるさい...',
        timing=EventTiming.AFTER_WORK, probability=0.05,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='home_leak', name='水漏れ',
        description='水道から水漏れが...',
        timing=EventTiming.AFTER_WORK, probability=0.02,
        effect=effect_combined(effect_money(-3000), effect_energy(-2))
    ),
    RandomEvent(
        id='home_power_out', name='停電',
        description='一時的に停電した',
        timing=EventTiming.AFTER_WORK, probability=0.02,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='home_internet_down', name='ネット不調',
        description='インターネットの調子が悪い',
        timing=EventTiming.AFTER_WORK, probability=0.04,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='home_repair', name='修理',
        description='壊れていたものを直した',
        timing=EventTiming.AFTER_WORK, probability=0.04,
        effect=effect_combined(effect_energy(1), effect_stamina(-1))
    ),

    # その他 (5種)
    RandomEvent(
        id='home_study', name='勉強',
        description='少し勉強をした',
        timing=EventTiming.AFTER_WORK, probability=0.04,
        effect=effect_combined(effect_energy(1), effect_stamina(-1))
    ),
    RandomEvent(
        id='home_hobby', name='趣味の時間',
        description='趣味に没頭した',
        timing=EventTiming.AFTER_WORK, probability=0.06,
        effect=effect_energy(2)
    ),
    RandomEvent(
        id='home_tired', name='疲れて何もできない',
        description='疲れて何もする気が起きない...',
        timing=EventTiming.AFTER_WORK, probability=0.08,
        condition=cond_low_stamina,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='home_energetic', name='まだ元気',
        description='帰ってきてもまだ元気がある！',
        timing=EventTiming.AFTER_WORK, probability=0.05,
        condition=cond_high_stamina,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='home_productive', name='生産的な夜',
        description='色々なことを片付けられた',
        timing=EventTiming.AFTER_WORK, probability=0.05,
        condition=cond_high_energy,
        effect=effect_energy(1)
    ),
]


# === 夜中イベント (40種類) ===

NIGHT_EVENTS = [
    # 睡眠関連 (15種)
    RandomEvent(
        id='night_sleepy', name='眠い',
        description='もう眠くてたまらない...',
        timing=EventTiming.NIGHT, probability=0.1,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='night_cant_sleep', name='眠れない',
        description='なんだか眠れない...',
        timing=EventTiming.NIGHT, probability=0.08,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='night_good_tired', name='良い疲れ',
        description='心地よい疲れで眠れそう',
        timing=EventTiming.NIGHT, probability=0.08,
        effect=effect_stamina(1)
    ),
    RandomEvent(
        id='night_anxiety', name='不安',
        description='なんだか不安で眠れない...',
        timing=EventTiming.NIGHT, probability=0.05,
        effect=effect_combined(effect_energy(-1), effect_stamina(-1))
    ),
    RandomEvent(
        id='night_peace', name='平穏',
        description='平穏な夜だ',
        timing=EventTiming.NIGHT, probability=0.1,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='night_reflection', name='振り返り',
        description='今日一日を振り返った',
        timing=EventTiming.NIGHT, probability=0.06,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='night_regret', name='後悔',
        description='今日の行動を後悔している...',
        timing=EventTiming.NIGHT, probability=0.05,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='night_satisfaction', name='満足感',
        description='今日は良い一日だった',
        timing=EventTiming.NIGHT, probability=0.08,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='night_worry_money', name='お金の心配',
        description='お金のことが心配になってきた...',
        timing=EventTiming.NIGHT, probability=0.08,
        condition=cond_low_money,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='night_worry_health', name='健康の心配',
        description='最近の体調が心配...',
        timing=EventTiming.NIGHT, probability=0.06,
        condition=cond_low_stamina,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='night_plan_tomorrow', name='明日の計画',
        description='明日の予定を立てた',
        timing=EventTiming.NIGHT, probability=0.06,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='night_forget_alarm', name='目覚まし忘れ',
        description='目覚ましをセットし忘れそうになった',
        timing=EventTiming.NIGHT, probability=0.04,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='night_set_alarm', name='目覚ましセット',
        description='ちゃんと目覚ましをセットした',
        timing=EventTiming.NIGHT, probability=0.08,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='night_hot', name='暑くて眠れない',
        description='部屋が暑くて眠れない...',
        timing=EventTiming.NIGHT, probability=0.05,
        condition=cond_sunny,
        effect=effect_stamina(-1)
    ),
    RandomEvent(
        id='night_cold', name='寒くて眠れない',
        description='部屋が寒くて眠れない...',
        timing=EventTiming.NIGHT, probability=0.05,
        condition=cond_rainy,
        effect=effect_stamina(-1)
    ),

    # 夜の出来事 (15種)
    RandomEvent(
        id='night_late_snack', name='夜食',
        description='つい夜食を食べてしまった',
        timing=EventTiming.NIGHT, probability=0.08,
        effect=effect_combined(effect_fullness(2), effect_stamina(-1))
    ),
    RandomEvent(
        id='night_late_game', name='夜更かしゲーム',
        description='ゲームに夢中で夜更かし',
        timing=EventTiming.NIGHT, probability=0.06,
        effect=effect_combined(effect_energy(1), effect_stamina(-1))
    ),
    RandomEvent(
        id='night_late_video', name='夜更かし動画',
        description='動画を見すぎて夜更かし',
        timing=EventTiming.NIGHT, probability=0.06,
        effect=effect_combined(effect_energy(1), effect_stamina(-1))
    ),
    RandomEvent(
        id='night_late_sns', name='夜更かしSNS',
        description='SNSを見すぎて夜更かし',
        timing=EventTiming.NIGHT, probability=0.06,
        effect=effect_stamina(-1)
    ),
    RandomEvent(
        id='night_reading', name='夜の読書',
        description='本を読んでから寝ることにした',
        timing=EventTiming.NIGHT, probability=0.05,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='night_music', name='夜の音楽',
        description='静かな音楽を聴いてリラックス',
        timing=EventTiming.NIGHT, probability=0.06,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='night_tea', name='ホットドリンク',
        description='温かい飲み物を飲んで落ち着いた',
        timing=EventTiming.NIGHT, probability=0.06,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='night_noise', name='夜の騒音',
        description='外がうるさくて気になる',
        timing=EventTiming.NIGHT, probability=0.05,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='night_storm', name='夜の嵐',
        description='外で嵐が荒れている...',
        timing=EventTiming.NIGHT, probability=0.3,
        condition=cond_stormy,
        effect=effect_combined(effect_energy(-1), effect_stamina(-1))
    ),
    RandomEvent(
        id='night_rain_sound', name='雨音',
        description='雨の音を聞きながら眠れそう',
        timing=EventTiming.NIGHT, probability=0.15,
        condition=cond_rainy,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='night_moonlight', name='月明かり',
        description='きれいな月明かりが窓から差し込む',
        timing=EventTiming.NIGHT, probability=0.08,
        condition=cond_sunny,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='night_stars', name='星空',
        description='窓から星空が見えた',
        timing=EventTiming.NIGHT, probability=0.06,
        condition=cond_sunny,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='night_call', name='深夜の電話',
        description='深夜に電話がかかってきた',
        timing=EventTiming.NIGHT, probability=0.03,
        effect=effect_combined(effect_energy(-1), effect_stamina(-1))
    ),
    RandomEvent(
        id='night_message', name='深夜のメッセージ',
        description='友人から深夜にメッセージが来た',
        timing=EventTiming.NIGHT, probability=0.05,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='night_nightmare_worry', name='嫌な予感',
        description='なんだか嫌な予感がする...',
        timing=EventTiming.NIGHT, probability=0.04,
        effect=effect_energy(-1)
    ),

    # 週末・曜日関連 (5種)
    RandomEvent(
        id='night_friday_happy', name='金曜の夜',
        description='金曜の夜だ！明日は休み！',
        timing=EventTiming.NIGHT, probability=0.3,
        condition=cond_friday,
        effect=effect_energy(2)
    ),
    RandomEvent(
        id='night_sunday_blues', name='日曜の夜',
        description='明日からまた仕事か...',
        timing=EventTiming.NIGHT, probability=0.25,
        condition=lambda ctx: ctx.get('weekday') == 6,  # 日曜
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='night_holiday_relax', name='休日の夜',
        description='休日の夜はリラックスできる',
        timing=EventTiming.NIGHT, probability=0.15,
        condition=cond_holiday,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='night_weekday_tired', name='平日の疲れ',
        description='平日の疲れが溜まっている...',
        timing=EventTiming.NIGHT, probability=0.1,
        condition=cond_weekday,
        effect=effect_stamina(-1)
    ),
    RandomEvent(
        id='night_early_sleep', name='早寝',
        description='今日は早めに寝ることにした',
        timing=EventTiming.NIGHT, probability=0.08,
        effect=effect_stamina(1)
    ),

    # その他 (5種)
    RandomEvent(
        id='night_motivation', name='明日への意気込み',
        description='明日もがんばろう！',
        timing=EventTiming.NIGHT, probability=0.08,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='night_gratitude', name='感謝',
        description='今日一日に感謝',
        timing=EventTiming.NIGHT, probability=0.06,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='night_dream_goal', name='夢を思う',
        description='将来の夢について考えた',
        timing=EventTiming.NIGHT, probability=0.04,
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='night_loneliness', name='孤独',
        description='ちょっと寂しい気持ちになった',
        timing=EventTiming.NIGHT, probability=0.05,
        effect=effect_energy(-1)
    ),
    RandomEvent(
        id='night_find_money', name='ポケットから小銭',
        description='ポケットから忘れていた小銭が出てきた',
        timing=EventTiming.NIGHT, probability=0.03,
        effect=effect_money(100)
    ),
]


# === 休日専用イベント (20種類) ===

HOLIDAY_EVENTS = [
    # 起床時 (5種)
    RandomEvent(
        id='holiday_wake_late', name='朝寝坊',
        description='休日だしゆっくり寝てしまった',
        timing=EventTiming.WAKE_UP, probability=0.15,
        condition=cond_holiday, effect=effect_combined(effect_stamina(2), effect_energy(-1))
    ),
    RandomEvent(
        id='holiday_wake_refresh', name='休日の朝',
        description='のんびりした休日の朝。リフレッシュできた',
        timing=EventTiming.WAKE_UP, probability=0.12,
        condition=cond_holiday, effect=effect_combined(effect_energy(2), effect_stamina(1))
    ),
    RandomEvent(
        id='holiday_wake_brunch', name='ブランチの予定',
        description='今日は友人とブランチの約束がある',
        timing=EventTiming.WAKE_UP, probability=0.05,
        condition=cond_holiday, effect=effect_energy(1)
    ),
    RandomEvent(
        id='holiday_wake_cleaning', name='大掃除日和',
        description='今日は部屋を掃除しよう！',
        timing=EventTiming.WAKE_UP, probability=0.08,
        condition=lambda ctx: cond_holiday(ctx) and cond_sunny(ctx),
        effect=effect_energy(1)
    ),
    RandomEvent(
        id='holiday_wake_lazy', name='ダラダラ休日',
        description='何もする気が起きない...',
        timing=EventTiming.WAKE_UP, probability=0.1,
        condition=cond_holiday, effect=effect_energy(-1)
    ),

    # 買い物中 (5種)
    RandomEvent(
        id='holiday_shop_crowded', name='休日の混雑',
        description='休日でスーパーが混んでいる...',
        timing=EventTiming.AT_SHOP, probability=0.2,
        condition=cond_holiday, effect=effect_stamina(-1)
    ),
    RandomEvent(
        id='holiday_shop_sale', name='週末セール',
        description='週末限定セールでお得に買い物できた！',
        timing=EventTiming.AT_SHOP, probability=0.1,
        condition=cond_holiday, effect=effect_money(200)
    ),
    RandomEvent(
        id='holiday_shop_friend', name='友人に遭遇',
        description='買い物中に友人に会った。おすそ分けをもらった',
        timing=EventTiming.AT_SHOP, probability=0.05,
        condition=cond_holiday, effect=effect_add_ingredient('卵', 1)
    ),
    RandomEvent(
        id='holiday_shop_sample', name='試食コーナー',
        description='試食コーナーでいろいろ味見できた',
        timing=EventTiming.AT_SHOP, probability=0.08,
        condition=cond_holiday, effect=effect_fullness(1)
    ),
    RandomEvent(
        id='holiday_shop_bargain', name='特売品発見',
        description='タイムセールでお肉が半額！',
        timing=EventTiming.AT_SHOP, probability=0.06,
        condition=cond_holiday, effect=effect_add_ingredient('豚バラ肉', 1)
    ),

    # 昼食後 (5種)
    RandomEvent(
        id='holiday_lunch_nap', name='昼寝',
        description='食後についうとうと...',
        timing=EventTiming.AFTER_LUNCH, probability=0.15,
        condition=cond_holiday, effect=effect_combined(effect_stamina(1), effect_energy(1))
    ),
    RandomEvent(
        id='holiday_lunch_walk', name='散歩',
        description='食後に近所を散歩した',
        timing=EventTiming.AFTER_LUNCH, probability=0.1,
        condition=lambda ctx: cond_holiday(ctx) and cond_sunny(ctx),
        effect=effect_combined(effect_stamina(1), effect_energy(1))
    ),
    RandomEvent(
        id='holiday_lunch_game', name='ゲーム三昧',
        description='積みゲーを消化した',
        timing=EventTiming.AFTER_LUNCH, probability=0.08,
        condition=cond_holiday, effect=effect_energy(1)
    ),
    RandomEvent(
        id='holiday_lunch_movie', name='映画鑑賞',
        description='録画していた映画を見た',
        timing=EventTiming.AFTER_LUNCH, probability=0.08,
        condition=cond_holiday, effect=effect_energy(1)
    ),
    RandomEvent(
        id='holiday_lunch_bbq', name='友人とBBQ',
        description='友人に誘われてBBQに行った。楽しかった！',
        timing=EventTiming.AFTER_LUNCH, probability=0.03,
        condition=lambda ctx: cond_holiday(ctx) and cond_sunny(ctx),
        effect=effect_combined(effect_fullness(3), effect_energy(2), effect_money(-1000))
    ),

    # 夜 (5種)
    RandomEvent(
        id='holiday_night_tired', name='休日の疲れ',
        description='遊び疲れた...',
        timing=EventTiming.NIGHT, probability=0.1,
        condition=cond_holiday, effect=effect_stamina(-1)
    ),
    RandomEvent(
        id='holiday_night_satisfied', name='充実した休日',
        description='良い休日だった。明日からまた頑張ろう',
        timing=EventTiming.NIGHT, probability=0.12,
        condition=cond_holiday, effect=effect_combined(effect_energy(1), effect_stamina(1))
    ),
    RandomEvent(
        id='holiday_night_sunday', name='サザエさん症候群',
        description='明日から仕事か...',
        timing=EventTiming.NIGHT, probability=0.15,
        condition=lambda ctx: ctx.get('weekday') == 6,  # 日曜日
        effect=effect_energy(-2)
    ),
    RandomEvent(
        id='holiday_night_hobby', name='趣味の時間',
        description='好きなことに没頭できた',
        timing=EventTiming.NIGHT, probability=0.08,
        condition=cond_holiday, effect=effect_energy(1)
    ),
    RandomEvent(
        id='holiday_night_call', name='実家から電話',
        description='実家から元気かと電話があった',
        timing=EventTiming.NIGHT, probability=0.04,
        condition=cond_holiday, effect=effect_combined(effect_energy(1), effect_money(5000))
    ),
]


# === 全イベントを取得 ===

def get_all_events() -> list[RandomEvent]:
    """全イベントを取得"""
    return (
        WAKE_UP_EVENTS +
        GO_TO_WORK_EVENTS +
        AFTER_LUNCH_EVENTS +
        AT_SHOP_EVENTS +
        LEAVE_WORK_EVENTS +
        AFTER_WORK_EVENTS +
        NIGHT_EVENTS +
        HOLIDAY_EVENTS
    )


def register_all_events(event_manager):
    """全イベントをEventManagerに登録"""
    event_manager.register_events(get_all_events())
