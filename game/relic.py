"""レリック（調理器具など）システム"""
import random
from dataclasses import dataclass


@dataclass
class Relic:
    """レリックデータ"""
    name: str
    price: int
    description: str
    effect_type: str  # "nutrition_boost", "energy_save", "freshness_extend", "fullness_boost", "stamina_save", "money_save"
    effect_target: str | None  # 対象食材カテゴリ（Noneなら全体）
    effect_value: float  # 効果値（倍率や加算値）
    category: str = "その他"  # レリックのカテゴリ


# レリックマスターデータ（100種類）
RELICS = {
    # === 調理器具・基本 (15種類) ===
    'フライパン': Relic(
        name='フライパン', price=2000, description='肉料理の栄養+20%',
        effect_type='nutrition_boost', effect_target='肉', effect_value=0.2, category='調理器具'
    ),
    '中華鍋': Relic(
        name='中華鍋', price=3000, description='野菜料理の栄養+25%',
        effect_type='nutrition_boost', effect_target='野菜', effect_value=0.25, category='調理器具'
    ),
    '片手鍋': Relic(
        name='片手鍋', price=1500, description='調理の気力消費-1',
        effect_type='energy_save', effect_target=None, effect_value=1, category='調理器具'
    ),
    '両手鍋': Relic(
        name='両手鍋', price=2500, description='穀物料理の満腹度+1',
        effect_type='fullness_boost', effect_target='穀物', effect_value=1, category='調理器具'
    ),
    '圧力鍋': Relic(
        name='圧力鍋', price=8000, description='全料理の満腹度+1',
        effect_type='fullness_boost', effect_target=None, effect_value=1, category='調理器具'
    ),
    '土鍋': Relic(
        name='土鍋', price=4000, description='穀物料理の栄養+30%',
        effect_type='nutrition_boost', effect_target='穀物', effect_value=0.3, category='調理器具'
    ),
    '卵焼き器': Relic(
        name='卵焼き器', price=1800, description='卵乳料理の栄養+25%',
        effect_type='nutrition_boost', effect_target='卵乳', effect_value=0.25, category='調理器具'
    ),
    'グリルパン': Relic(
        name='グリルパン', price=3500, description='魚料理の栄養+20%',
        effect_type='nutrition_boost', effect_target='魚', effect_value=0.2, category='調理器具'
    ),
    'ホーロー鍋': Relic(
        name='ホーロー鍋', price=5000, description='全料理の栄養+10%',
        effect_type='nutrition_boost', effect_target=None, effect_value=0.1, category='調理器具'
    ),
    'すき焼き鍋': Relic(
        name='すき焼き鍋', price=4500, description='肉料理の満腹度+2',
        effect_type='fullness_boost', effect_target='肉', effect_value=2, category='調理器具'
    ),
    '天ぷら鍋': Relic(
        name='天ぷら鍋', price=3000, description='野菜料理の満腹度+1',
        effect_type='fullness_boost', effect_target='野菜', effect_value=1, category='調理器具'
    ),
    'ミルクパン': Relic(
        name='ミルクパン', price=1200, description='卵乳料理の満腹度+1',
        effect_type='fullness_boost', effect_target='卵乳', effect_value=1, category='調理器具'
    ),
    'パスタ鍋': Relic(
        name='パスタ鍋', price=2800, description='穀物料理の栄養+15%',
        effect_type='nutrition_boost', effect_target='穀物', effect_value=0.15, category='調理器具'
    ),
    '蒸し器': Relic(
        name='蒸し器', price=3500, description='魚料理の栄養+25%',
        effect_type='nutrition_boost', effect_target='魚', effect_value=0.25, category='調理器具'
    ),
    'タジン鍋': Relic(
        name='タジン鍋', price=4000, description='野菜料理の栄養+20%',
        effect_type='nutrition_boost', effect_target='野菜', effect_value=0.2, category='調理器具'
    ),

    # === 家電 (20種類) ===
    '炊飯器': Relic(
        name='炊飯器', price=5000, description='米料理の満腹度+1',
        effect_type='fullness_boost', effect_target='穀物', effect_value=1, category='家電'
    ),
    '電子レンジ': Relic(
        name='電子レンジ', price=8000, description='調理の気力消費-1',
        effect_type='energy_save', effect_target=None, effect_value=1, category='家電'
    ),
    '冷蔵庫': Relic(
        name='冷蔵庫', price=15000, description='全食材の鮮度+3日',
        effect_type='freshness_extend', effect_target=None, effect_value=3, category='家電'
    ),
    'オーブン': Relic(
        name='オーブン', price=12000, description='肉料理の栄養+30%',
        effect_type='nutrition_boost', effect_target='肉', effect_value=0.3, category='家電'
    ),
    'トースター': Relic(
        name='トースター', price=3000, description='穀物料理の栄養+15%',
        effect_type='nutrition_boost', effect_target='穀物', effect_value=0.15, category='家電'
    ),
    'オーブンレンジ': Relic(
        name='オーブンレンジ', price=20000, description='調理の気力消費-2',
        effect_type='energy_save', effect_target=None, effect_value=2, category='家電'
    ),
    '電気ケトル': Relic(
        name='電気ケトル', price=2000, description='調理の気力消費-1',
        effect_type='energy_save', effect_target=None, effect_value=1, category='家電'
    ),
    'ホットプレート': Relic(
        name='ホットプレート', price=5000, description='肉料理の満腹度+1',
        effect_type='fullness_boost', effect_target='肉', effect_value=1, category='家電'
    ),
    'IHクッキングヒーター': Relic(
        name='IHクッキングヒーター', price=10000, description='全料理の栄養+15%',
        effect_type='nutrition_boost', effect_target=None, effect_value=0.15, category='家電'
    ),
    'フードプロセッサー': Relic(
        name='フードプロセッサー', price=7000, description='野菜料理の栄養+30%',
        effect_type='nutrition_boost', effect_target='野菜', effect_value=0.3, category='家電'
    ),
    'ミキサー': Relic(
        name='ミキサー', price=4000, description='果物料理の栄養+40%',
        effect_type='nutrition_boost', effect_target='果物', effect_value=0.4, category='家電'
    ),
    'ジューサー': Relic(
        name='ジューサー', price=5000, description='果物料理の栄養+35%',
        effect_type='nutrition_boost', effect_target='果物', effect_value=0.35, category='家電'
    ),
    'コーヒーメーカー': Relic(
        name='コーヒーメーカー', price=6000, description='調理の気力消費-1',
        effect_type='energy_save', effect_target=None, effect_value=1, category='家電'
    ),
    '電気圧力鍋': Relic(
        name='電気圧力鍋', price=15000, description='全料理の満腹度+2',
        effect_type='fullness_boost', effect_target=None, effect_value=2, category='家電'
    ),
    'スチームオーブン': Relic(
        name='スチームオーブン', price=25000, description='全料理の栄養+20%',
        effect_type='nutrition_boost', effect_target=None, effect_value=0.2, category='家電'
    ),
    '冷凍庫': Relic(
        name='冷凍庫', price=20000, description='全食材の鮮度+5日',
        effect_type='freshness_extend', effect_target=None, effect_value=5, category='家電'
    ),
    'ヨーグルトメーカー': Relic(
        name='ヨーグルトメーカー', price=3500, description='卵乳料理の栄養+30%',
        effect_type='nutrition_boost', effect_target='卵乳', effect_value=0.3, category='家電'
    ),
    'パン焼き機': Relic(
        name='パン焼き機', price=8000, description='穀物料理の満腹度+2',
        effect_type='fullness_boost', effect_target='穀物', effect_value=2, category='家電'
    ),
    '精米機': Relic(
        name='精米機', price=12000, description='穀物料理の栄養+25%',
        effect_type='nutrition_boost', effect_target='穀物', effect_value=0.25, category='家電'
    ),
    '低温調理器': Relic(
        name='低温調理器', price=10000, description='肉料理の栄養+35%',
        effect_type='nutrition_boost', effect_target='肉', effect_value=0.35, category='家電'
    ),

    # === 刃物・カトラリー (15種類) ===
    '三徳包丁': Relic(
        name='三徳包丁', price=3000, description='調理の気力消費-1',
        effect_type='energy_save', effect_target=None, effect_value=1, category='刃物'
    ),
    '出刃包丁': Relic(
        name='出刃包丁', price=5000, description='魚料理の栄養+30%',
        effect_type='nutrition_boost', effect_target='魚', effect_value=0.3, category='刃物'
    ),
    '柳刃包丁': Relic(
        name='柳刃包丁', price=8000, description='魚料理の栄養+40%',
        effect_type='nutrition_boost', effect_target='魚', effect_value=0.4, category='刃物'
    ),
    '菜切り包丁': Relic(
        name='菜切り包丁', price=4000, description='野菜料理の栄養+25%',
        effect_type='nutrition_boost', effect_target='野菜', effect_value=0.25, category='刃物'
    ),
    'ペティナイフ': Relic(
        name='ペティナイフ', price=2000, description='果物料理の栄養+25%',
        effect_type='nutrition_boost', effect_target='果物', effect_value=0.25, category='刃物'
    ),
    'パン切り包丁': Relic(
        name='パン切り包丁', price=2500, description='穀物料理の栄養+10%',
        effect_type='nutrition_boost', effect_target='穀物', effect_value=0.1, category='刃物'
    ),
    '骨スキ包丁': Relic(
        name='骨スキ包丁', price=6000, description='肉料理の栄養+25%',
        effect_type='nutrition_boost', effect_target='肉', effect_value=0.25, category='刃物'
    ),
    'キッチンバサミ': Relic(
        name='キッチンバサミ', price=1500, description='調理の気力消費-1',
        effect_type='energy_save', effect_target=None, effect_value=1, category='刃物'
    ),
    'ピーラー': Relic(
        name='ピーラー', price=500, description='野菜料理の栄養+10%',
        effect_type='nutrition_boost', effect_target='野菜', effect_value=0.1, category='刃物'
    ),
    'スライサー': Relic(
        name='スライサー', price=1000, description='野菜料理の栄養+15%',
        effect_type='nutrition_boost', effect_target='野菜', effect_value=0.15, category='刃物'
    ),
    'おろし金': Relic(
        name='おろし金', price=800, description='調味料の栄養+20%',
        effect_type='nutrition_boost', effect_target='調味料', effect_value=0.2, category='刃物'
    ),
    '千切りスライサー': Relic(
        name='千切りスライサー', price=1200, description='野菜料理の栄養+20%',
        effect_type='nutrition_boost', effect_target='野菜', effect_value=0.2, category='刃物'
    ),
    'みじん切り器': Relic(
        name='みじん切り器', price=1500, description='調理の気力消費-1',
        effect_type='energy_save', effect_target=None, effect_value=1, category='刃物'
    ),
    'うろこ取り': Relic(
        name='うろこ取り', price=600, description='魚料理の栄養+10%',
        effect_type='nutrition_boost', effect_target='魚', effect_value=0.1, category='刃物'
    ),
    '肉たたき': Relic(
        name='肉たたき', price=1000, description='肉料理の満腹度+1',
        effect_type='fullness_boost', effect_target='肉', effect_value=1, category='刃物'
    ),

    # === 調理補助・計量 (15種類) ===
    '計量カップ': Relic(
        name='計量カップ', price=500, description='全料理の栄養+5%',
        effect_type='nutrition_boost', effect_target=None, effect_value=0.05, category='計量'
    ),
    '計量スプーン': Relic(
        name='計量スプーン', price=300, description='調味料の栄養+15%',
        effect_type='nutrition_boost', effect_target='調味料', effect_value=0.15, category='計量'
    ),
    'キッチンスケール': Relic(
        name='キッチンスケール', price=2000, description='全料理の栄養+10%',
        effect_type='nutrition_boost', effect_target=None, effect_value=0.1, category='計量'
    ),
    'キッチンタイマー': Relic(
        name='キッチンタイマー', price=800, description='調理の気力消費-1',
        effect_type='energy_save', effect_target=None, effect_value=1, category='計量'
    ),
    '温度計': Relic(
        name='温度計', price=1500, description='肉料理の栄養+15%',
        effect_type='nutrition_boost', effect_target='肉', effect_value=0.15, category='計量'
    ),
    'ボウル（大）': Relic(
        name='ボウル（大）', price=1000, description='全料理の満腹度+1',
        effect_type='fullness_boost', effect_target=None, effect_value=1, category='計量'
    ),
    'ボウル（小）': Relic(
        name='ボウル（小）', price=600, description='調理の気力消費-1',
        effect_type='energy_save', effect_target=None, effect_value=1, category='計量'
    ),
    'ざる': Relic(
        name='ざる', price=800, description='野菜料理の栄養+10%',
        effect_type='nutrition_boost', effect_target='野菜', effect_value=0.1, category='計量'
    ),
    'バット': Relic(
        name='バット', price=700, description='魚料理の栄養+10%',
        effect_type='nutrition_boost', effect_target='魚', effect_value=0.1, category='計量'
    ),
    '泡立て器': Relic(
        name='泡立て器', price=600, description='卵乳料理の栄養+15%',
        effect_type='nutrition_boost', effect_target='卵乳', effect_value=0.15, category='計量'
    ),
    '木べら': Relic(
        name='木べら', price=400, description='調理の気力消費-1',
        effect_type='energy_save', effect_target=None, effect_value=1, category='計量'
    ),
    'フライ返し': Relic(
        name='フライ返し', price=500, description='肉料理の栄養+10%',
        effect_type='nutrition_boost', effect_target='肉', effect_value=0.1, category='計量'
    ),
    'おたま': Relic(
        name='おたま', price=400, description='全料理の栄養+5%',
        effect_type='nutrition_boost', effect_target=None, effect_value=0.05, category='計量'
    ),
    'トング': Relic(
        name='トング', price=600, description='肉料理の栄養+10%',
        effect_type='nutrition_boost', effect_target='肉', effect_value=0.1, category='計量'
    ),
    '菜箸': Relic(
        name='菜箸', price=300, description='調理の気力消費-1',
        effect_type='energy_save', effect_target=None, effect_value=1, category='計量'
    ),

    # === 保存・収納 (15種類) ===
    '保存容器セット': Relic(
        name='保存容器セット', price=2000, description='全食材の鮮度+2日',
        effect_type='freshness_extend', effect_target=None, effect_value=2, category='保存'
    ),
    'ラップ': Relic(
        name='ラップ', price=300, description='全食材の鮮度+1日',
        effect_type='freshness_extend', effect_target=None, effect_value=1, category='保存'
    ),
    'アルミホイル': Relic(
        name='アルミホイル', price=400, description='魚料理の栄養+15%',
        effect_type='nutrition_boost', effect_target='魚', effect_value=0.15, category='保存'
    ),
    'ジップロック': Relic(
        name='ジップロック', price=500, description='全食材の鮮度+2日',
        effect_type='freshness_extend', effect_target=None, effect_value=2, category='保存'
    ),
    '真空パック機': Relic(
        name='真空パック機', price=8000, description='全食材の鮮度+4日',
        effect_type='freshness_extend', effect_target=None, effect_value=4, category='保存'
    ),
    '漬物容器': Relic(
        name='漬物容器', price=1500, description='野菜の鮮度+3日',
        effect_type='freshness_extend', effect_target=None, effect_value=3, category='保存'
    ),
    '米びつ': Relic(
        name='米びつ', price=3000, description='穀物の鮮度+5日',
        effect_type='freshness_extend', effect_target=None, effect_value=5, category='保存'
    ),
    'オイルポット': Relic(
        name='オイルポット', price=1200, description='調味料の栄養+10%',
        effect_type='nutrition_boost', effect_target='調味料', effect_value=0.1, category='保存'
    ),
    '調味料ラック': Relic(
        name='調味料ラック', price=2000, description='調味料の鮮度+3日',
        effect_type='freshness_extend', effect_target=None, effect_value=3, category='保存'
    ),
    'スパイスラック': Relic(
        name='スパイスラック', price=2500, description='調味料の栄養+25%',
        effect_type='nutrition_boost', effect_target='調味料', effect_value=0.25, category='保存'
    ),
    '野菜ストッカー': Relic(
        name='野菜ストッカー', price=1800, description='野菜の鮮度+2日',
        effect_type='freshness_extend', effect_target=None, effect_value=2, category='保存'
    ),
    'ブレッドケース': Relic(
        name='ブレッドケース', price=2000, description='穀物の鮮度+3日',
        effect_type='freshness_extend', effect_target=None, effect_value=3, category='保存'
    ),
    '乾物入れ': Relic(
        name='乾物入れ', price=1500, description='きのこの鮮度+3日',
        effect_type='freshness_extend', effect_target=None, effect_value=3, category='保存'
    ),
    '果物かご': Relic(
        name='果物かご', price=1200, description='果物の鮮度+2日',
        effect_type='freshness_extend', effect_target=None, effect_value=2, category='保存'
    ),
    'ワインセラー': Relic(
        name='ワインセラー', price=30000, description='全食材の鮮度+7日',
        effect_type='freshness_extend', effect_target=None, effect_value=7, category='保存'
    ),

    # === 専門調理器具 (10種類) ===
    '寿司桶': Relic(
        name='寿司桶', price=3000, description='魚料理の満腹度+2',
        effect_type='fullness_boost', effect_target='魚', effect_value=2, category='専門'
    ),
    '蕎麦打ちセット': Relic(
        name='蕎麦打ちセット', price=5000, description='穀物料理の満腹度+2',
        effect_type='fullness_boost', effect_target='穀物', effect_value=2, category='専門'
    ),
    '製麺機': Relic(
        name='製麺機', price=8000, description='穀物料理の栄養+30%',
        effect_type='nutrition_boost', effect_target='穀物', effect_value=0.3, category='専門'
    ),
    '燻製器': Relic(
        name='燻製器', price=6000, description='肉料理の栄養+35%',
        effect_type='nutrition_boost', effect_target='肉', effect_value=0.35, category='専門'
    ),
    'チーズフォンデュ鍋': Relic(
        name='チーズフォンデュ鍋', price=4000, description='卵乳料理の満腹度+2',
        effect_type='fullness_boost', effect_target='卵乳', effect_value=2, category='専門'
    ),
    'たこ焼き器': Relic(
        name='たこ焼き器', price=2500, description='魚料理の満腹度+1',
        effect_type='fullness_boost', effect_target='魚', effect_value=1, category='専門'
    ),
    'ワッフルメーカー': Relic(
        name='ワッフルメーカー', price=3500, description='穀物料理の栄養+20%',
        effect_type='nutrition_boost', effect_target='穀物', effect_value=0.2, category='専門'
    ),
    'ピザストーン': Relic(
        name='ピザストーン', price=3000, description='穀物料理の栄養+25%',
        effect_type='nutrition_boost', effect_target='穀物', effect_value=0.25, category='専門'
    ),
    '餅つき機': Relic(
        name='餅つき機', price=10000, description='穀物料理の満腹度+3',
        effect_type='fullness_boost', effect_target='穀物', effect_value=3, category='専門'
    ),
    'アイスクリームメーカー': Relic(
        name='アイスクリームメーカー', price=5000, description='卵乳料理の栄養+30%',
        effect_type='nutrition_boost', effect_target='卵乳', effect_value=0.3, category='専門'
    ),

    # === 便利グッズ (10種類) ===
    'シリコンスチーマー': Relic(
        name='シリコンスチーマー', price=1500, description='野菜料理の栄養+20%',
        effect_type='nutrition_boost', effect_target='野菜', effect_value=0.2, category='便利'
    ),
    'レンジ用蒸し器': Relic(
        name='レンジ用蒸し器', price=1000, description='調理の気力消費-1',
        effect_type='energy_save', effect_target=None, effect_value=1, category='便利'
    ),
    '電子レンジパスタ調理器': Relic(
        name='電子レンジパスタ調理器', price=800, description='穀物料理の栄養+10%',
        effect_type='nutrition_boost', effect_target='穀物', effect_value=0.1, category='便利'
    ),
    '野菜水切り器': Relic(
        name='野菜水切り器', price=2000, description='野菜料理の栄養+15%',
        effect_type='nutrition_boost', effect_target='野菜', effect_value=0.15, category='便利'
    ),
    'にんにく絞り器': Relic(
        name='にんにく絞り器', price=1000, description='調味料の栄養+20%',
        effect_type='nutrition_boost', effect_target='調味料', effect_value=0.2, category='便利'
    ),
    'レモン絞り器': Relic(
        name='レモン絞り器', price=600, description='果物料理の栄養+20%',
        effect_type='nutrition_boost', effect_target='果物', effect_value=0.2, category='便利'
    ),
    'エッグスライサー': Relic(
        name='エッグスライサー', price=500, description='卵乳料理の栄養+10%',
        effect_type='nutrition_boost', effect_target='卵乳', effect_value=0.1, category='便利'
    ),
    'バターケース': Relic(
        name='バターケース', price=800, description='卵乳の鮮度+3日',
        effect_type='freshness_extend', effect_target=None, effect_value=3, category='便利'
    ),
    'まな板スタンド': Relic(
        name='まな板スタンド', price=1200, description='調理の気力消費-1',
        effect_type='energy_save', effect_target=None, effect_value=1, category='便利'
    ),
    '包丁スタンド': Relic(
        name='包丁スタンド', price=2500, description='調理の気力消費-1',
        effect_type='energy_save', effect_target=None, effect_value=1, category='便利'
    ),

    # === 買い物バッグ (5種類) ===
    'エコバッグ': Relic(
        name='エコバッグ', price=500, description='買い物バッグ容量+2',
        effect_type='bag_capacity', effect_target=None, effect_value=2, category='バッグ'
    ),
    '保冷バッグ': Relic(
        name='保冷バッグ', price=1500, description='買い物バッグ容量+3',
        effect_type='bag_capacity', effect_target=None, effect_value=3, category='バッグ'
    ),
    'マイバスケット': Relic(
        name='マイバスケット', price=800, description='買い物バッグ容量+3',
        effect_type='bag_capacity', effect_target=None, effect_value=3, category='バッグ'
    ),
    'キャリーカート': Relic(
        name='キャリーカート', price=3000, description='買い物バッグ容量+5',
        effect_type='bag_capacity', effect_target=None, effect_value=5, category='バッグ'
    ),
    'リュックサック': Relic(
        name='リュックサック', price=2000, description='買い物バッグ容量+4',
        effect_type='bag_capacity', effect_target=None, effect_value=4, category='バッグ'
    ),
}


@dataclass
class ShopRelicItem:
    """通販に並ぶレリック"""
    relic: Relic
    price: int  # 実際の販売価格
    is_sale: bool  # セール品かどうか


def generate_daily_relic_items(seed: int | None = None,
                                owned_relics: set[str] | None = None) -> list[ShopRelicItem]:
    """その日の通販レリックを生成（5種類、1つセール）

    Args:
        seed: 乱数シード
        owned_relics: 所持済みレリック名のセット（除外用）
    """
    if seed is not None:
        random.seed(seed + 1000)  # 食材とシードをずらす

    # 所持済みレリックを除外
    all_relics = list(RELICS.values())
    if owned_relics:
        all_relics = [r for r in all_relics if r.name not in owned_relics]

    # 利用可能なレリックが5種類未満の場合は全て表示
    selected = random.sample(all_relics, min(5, len(all_relics)))

    shop_items = []
    if selected:
        sale_idx = random.randint(0, len(selected) - 1)

        for i, relic in enumerate(selected):
            if i == sale_idx:
                # 20%オフ
                price = int(relic.price * 0.8)
                shop_items.append(ShopRelicItem(relic, price, is_sale=True))
            else:
                shop_items.append(ShopRelicItem(relic, relic.price, is_sale=False))

    return shop_items


class RelicInventory:
    """所持レリック管理"""

    def __init__(self):
        self._owned: dict[str, int] = {}  # レリック名 → 取得日

    def add(self, name: str, acquired_day: int = 1) -> bool:
        """レリックを追加。既に持っていればFalse
        Args:
            name: レリック名
            acquired_day: 取得日（ゲーム日数）
        """
        if name in self._owned:
            return False
        self._owned[name] = acquired_day
        return True

    def has(self, name: str) -> bool:
        """レリックを持っているか"""
        return name in self._owned

    def get_all(self) -> list[str]:
        """所持レリック一覧"""
        return list(self._owned.keys())

    def count(self) -> int:
        """所持レリック数"""
        return len(self._owned)

    def get_acquired_day(self, name: str) -> int | None:
        """レリックの取得日を取得"""
        return self._owned.get(name)

    def get_nutrition_boost(self, ingredient_name: str) -> float:
        """指定食材の栄養ブースト倍率を取得"""
        boost = 0.0
        for relic_name in self._owned:
            relic = RELICS.get(relic_name)
            if relic and relic.effect_type == 'nutrition_boost':
                if relic.effect_target is None or relic.effect_target == ingredient_name:
                    boost += relic.effect_value
        return boost

    def get_fullness_boost(self, ingredient_name: str) -> int:
        """指定食材の満腹度ブースト値を取得"""
        boost = 0
        for relic_name in self._owned:
            relic = RELICS.get(relic_name)
            if relic and relic.effect_type == 'fullness_boost':
                if relic.effect_target is None or relic.effect_target == ingredient_name:
                    boost += int(relic.effect_value)
        return boost

    def get_energy_save(self) -> int:
        """調理時の気力消費軽減値を取得"""
        save = 0
        for relic_name in self._owned:
            relic = RELICS.get(relic_name)
            if relic and relic.effect_type == 'energy_save':
                save += int(relic.effect_value)
        return save

    def get_freshness_extend(self) -> int:
        """鮮度延長日数を取得（全レリックの合計）"""
        extend = 0
        for relic_name in self._owned:
            relic = RELICS.get(relic_name)
            if relic and relic.effect_type == 'freshness_extend':
                extend += int(relic.effect_value)
        return extend

    def get_freshness_extend_for_purchase_day(self, purchase_day: int) -> int:
        """指定購入日の食材に適用される鮮度延長日数を取得

        レリック取得日以降に購入した食材にのみ効果を適用する。
        これにより、レリック取得前に既に期限切れだった食材が
        復活することを防ぐ。

        Args:
            purchase_day: 食材の購入日

        Returns:
            適用される鮮度延長日数
        """
        extend = 0
        for relic_name, acquired_day in self._owned.items():
            # レリック取得日 <= 食材購入日 の場合のみ効果を適用
            # （レリックを持っている状態で購入した食材のみ恩恵を受ける）
            if acquired_day > purchase_day:
                continue
            relic = RELICS.get(relic_name)
            if relic and relic.effect_type == 'freshness_extend':
                extend += int(relic.effect_value)
        return extend

    def get_bag_capacity_boost(self) -> int:
        """買い物バッグ容量の増加値を取得"""
        boost = 0
        for relic_name in self._owned:
            relic = RELICS.get(relic_name)
            if relic and relic.effect_type == 'bag_capacity':
                boost += int(relic.effect_value)
        return boost

    def add_initial_relics(self):
        """初期レリック（冷蔵庫・電子レンジ）を追加

        ゲーム開始時に最初から所持している想定のレリック。
        取得日を0にすることで、全ての食材に効果が適用される。
        """
        self.add('冷蔵庫', acquired_day=0)
        self.add('電子レンジ', acquired_day=0)

    def has_initial_relics(self) -> bool:
        """初期レリックを持っているか"""
        return self.has('冷蔵庫') and self.has('電子レンジ')


# 初期レリックの定数
INITIAL_RELICS = ['冷蔵庫', '電子レンジ']


def get_relic(name: str) -> Relic | None:
    """レリック名からレリックデータを取得"""
    return RELICS.get(name)


def get_all_relics() -> list[Relic]:
    """全レリックリストを取得"""
    return list(RELICS.values())
