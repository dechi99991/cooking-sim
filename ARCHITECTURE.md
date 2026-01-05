# cooking-sim アーキテクチャ

作成日: 2026-01-05

## ディレクトリ構成

```
cooking-sim/
├── main.py              # エントリーポイント、ゲームループ
├── TODO_NEXT.md         # 実装予定・完了タスク一覧
├── ARCHITECTURE.md      # 本ファイル
├── game/                # ゲームロジック
│   ├── character.py     # キャラクター定義
│   ├── config.py        # ゲーム設定
│   ├── constants.py     # 定数定義
│   ├── cooking.py       # 調理システム
│   ├── day_cycle.py     # 日次サイクル管理
│   ├── event_data.py    # イベントデータ
│   ├── events.py        # イベントシステム
│   ├── ingredients.py   # 食材データ
│   ├── nutrition.py     # 栄養素システム
│   ├── player.py        # プレイヤー状態
│   ├── provisions.py    # 食糧・配送システム
│   ├── relic.py         # レリックシステム
│   └── result.py        # ゲーム結果・統計
└── ui/                  # ユーザーインターフェース
    └── terminal.py      # ターミナルUI
```

---

## main.py

ゲームのエントリーポイント。ゲームループとフェーズハンドラを実装。

### 主要関数

| 関数 | 説明 |
|------|------|
| `main()` | エントリーポイント |
| `game_loop(game)` | メインゲームループ |
| `handle_breakfast(game)` | 朝食フェーズ処理 |
| `handle_lunch(game)` | 昼食フェーズ処理 |
| `handle_dinner(game)` | 夕食フェーズ処理（配送処理含む） |
| `handle_shopping(game)` | 買い物フェーズ処理 |
| `handle_holiday_shopping(game, phase)` | 休日買い物処理 |
| `handle_online_shopping(game)` | 通販フェーズ処理 |
| `handle_sleep(game)` | 就寝フェーズ処理 |
| `cook_multiple_dishes(game, meal_name)` | 複数料理作成ヘルパー |
| `eat_provision(game)` | 食糧消費処理 |
| `trigger_events(game, timing)` | イベント発火処理 |

---

## game/ ディレクトリ

### character.py

キャラクター定義。ゲーム開始時に選択可能。

```python
class Character:
    id: str              # キャラクターID
    name: str            # 名前
    description: str     # 説明
    initial_money: int   # 初期所持金
    initial_energy: int  # 初期気力
    initial_stamina: int # 初期体力
    salary_amount: int   # 月給
    bonus_amount: int    # ボーナス
    has_bonus: bool      # ボーナス有無
    rent_amount: int     # 家賃
```

### config.py

ゲーム設定の定義。

```python
class GameConfig:
    energy_cost: int          # 調理気力コスト
    stamina_recovery: int     # 睡眠時体力回復
    energy_recovery: int      # 睡眠時気力回復
    # ... その他設定
```

### constants.py

ゲーム定数の定義。

- `GAME_START_MONTH`, `GAME_START_DAY`: ゲーム開始日（4月1日）
- `GAME_DURATION_DAYS`: ゲーム期間（30日）
- `COOKING_ENERGY_COST`: 調理気力コスト
- `SHOPPING_BAG_CAPACITY`: 買い物バッグ容量
- `CAFFEINE_INSOMNIA_THRESHOLD`: 不眠発生カフェイン量
- etc.

### cooking.py

調理システムとネームド料理の管理。

```python
class Dish:
    name: str                # 料理名
    nutrition: Nutrition     # 栄養素
    fullness: int           # 満腹度
    ingredients: list[str]  # 使用食材

class NamedRecipe:
    name: str                    # 料理名
    required_ingredients: frozenset  # 必要食材
    nutrition_multiplier: float  # 栄養倍率
    fullness_bonus: int         # 満腹度ボーナス

class CookingEvaluation:
    total_fullness: int      # 合計満腹度
    total_nutrition: Nutrition
    is_named: bool           # ネームド料理か
    fullness_good: bool      # 満腹度評価
    nutrition_good: bool     # 栄養評価
```

**ネームド料理**: 17種類（カレーライス、親子丼、TKG、etc.）

### day_cycle.py

日次サイクルとゲーム状態管理の中核。

```python
class GamePhase(Enum):
    BREAKFAST         # 朝食
    GO_TO_WORK        # 出勤
    LUNCH             # 昼食
    LEAVE_WORK        # 退勤
    SHOPPING          # 買い出し
    HOLIDAY_SHOPPING_1  # 休日買い出し1
    HOLIDAY_LUNCH     # 休日昼食
    HOLIDAY_SHOPPING_2  # 休日買い出し2
    DINNER            # 夕食
    ONLINE_SHOPPING   # 通販
    SLEEP             # 就寝

class DayState:
    day: int              # ゲーム日数
    month: int            # 月
    phase: GamePhase      # 現在のフェーズ
    daily_nutrition: Nutrition  # 1日の摂取栄養
    caffeine: int         # カフェイン摂取量

class GameManager:
    player: Player        # プレイヤー
    stock: Stock          # 食材在庫
    day_state: DayState   # 日付状態
    stats: GameStats      # 統計
    relics: RelicInventory  # レリック所持
    provisions: ProvisionStock  # 食糧ストック
    events: EventManager  # イベント管理
```

**フェーズ順序**:
- 平日: BREAKFAST → GO_TO_WORK → LUNCH → LEAVE_WORK → SHOPPING → DINNER → ONLINE_SHOPPING → SLEEP
- 休日: BREAKFAST → HOLIDAY_SHOPPING_1 → HOLIDAY_LUNCH → HOLIDAY_SHOPPING_2 → DINNER → ONLINE_SHOPPING → SLEEP

### event_data.py

300種類のランダムイベント定義。

**イベント効果関数**:
- `effect_energy(amount)`: 気力増減
- `effect_stamina(amount)`: 体力増減
- `effect_money(amount)`: 所持金増減
- `effect_fullness(amount)`: 満腹度増減
- `effect_add_ingredient(name, qty)`: 食材追加
- `effect_combined(*effects)`: 複合効果

**イベント条件関数**:
- `cond_sunny/cloudy/rainy/stormy`: 天気条件
- `cond_weekday/holiday`: 平日・休日条件
- `cond_low_energy/high_energy`: 気力条件
- etc.

### events.py

イベントシステムの基盤。

```python
class Weather(Enum):
    SUNNY   # 晴れ
    CLOUDY  # 曇り
    RAINY   # 雨
    STORMY  # 嵐

class EventTiming(Enum):
    WAKE_UP      # 起床時
    AT_SHOP      # 買い物中
    AFTER_WORK   # 退勤後
    AFTER_MEAL   # 食事後
    BEFORE_SLEEP # 就寝前

class RandomEvent:
    id: str           # イベントID
    description: str  # 説明文
    timing: EventTiming
    effect: callable  # 効果関数
    condition: callable  # 発生条件

class EventManager:
    # イベント管理、天気決定、イベント抽選
```

### ingredients.py

100種類の食材データと在庫管理。

```python
class Ingredient:
    name: str           # 食材名
    price: int          # 価格
    category: str       # カテゴリ
    nutrition: Nutrition  # 栄養素
    fullness: int       # 満腹度
    expiry_days: int    # 賞味期限
    caffeine: int       # カフェイン量

class Stock:
    # 食材在庫管理（購入日追跡、期限管理）

class ShopItem:
    ingredient: Ingredient
    quantity: int
    is_sale: bool
```

**カテゴリ**: 穀物、野菜、肉魚、卵乳豆、その他

### nutrition.py

栄養素システム。

```python
class Nutrition:
    vitality: int   # 活力素（体力回復）
    mental: int     # 心力素（気力回復）
    awakening: int  # 覚醒素（カフェイン）
    sustain: int    # 持続素（満腹度維持）
    defense: int    # 防御素（ペナルティ軽減）
```

### player.py

プレイヤー状態管理。

```python
class Player:
    money: int            # 所持金
    energy: int           # 気力
    stamina: int          # 体力
    fullness: int         # 満腹度
    card_debt: int        # カード債務
    energy_recovery_penalty: int   # 気力回復ペナルティ
    stamina_recovery_penalty: int  # 体力回復ペナルティ
```

### provisions.py

食糧（カップ麺、弁当等）と配送システム。

```python
class Provision:
    name: str           # 食糧名
    price: int          # 価格
    nutrition: Nutrition
    fullness: int
    caffeine: int

class PreparedDish:
    # 作り置き弁当

class PendingDelivery:
    item_type: str      # "provision" or "relic"
    name: str
    quantity: int
    delivery_day: int   # 配送日

class ProvisionStock:
    # 食糧在庫、配送待ち管理
```

### relic.py

100種類のレリック（アイテム）システム。

```python
class Relic:
    name: str           # レリック名
    description: str    # 説明
    price: int          # 価格
    effect_type: str    # 効果タイプ
    effect_value: float # 効果値
    effect_target: str  # 対象（食材名等）

class RelicInventory:
    _owned: dict[str, int]  # {レリック名: 取得日}

    # 効果取得メソッド
    get_freshness_extend()      # 鮮度延長日数
    get_bag_capacity_boost()    # バッグ容量追加
    get_energy_save()           # 気力消費軽減
    get_nutrition_boost()       # 栄養ブースト
```

**効果タイプ**:
- `freshness_extend`: 鮮度延長
- `bag_capacity`: バッグ容量増加
- `energy_save`: 調理気力軽減
- `nutrition_boost`: 栄養素強化
- `fullness_boost`: 満腹度強化

**初期レリック**: 冷蔵庫（鮮度+3日）、電子レンジ（気力-1）

### result.py

ゲーム結果と統計。

```python
class GameResult:
    survived_days: int      # 生存日数
    is_game_over: bool
    is_game_clear: bool
    game_over_reason: str   # "money" or "stamina"
    total_meals: int
    cooking_count: int
    # ... その他統計

class GameStats:
    # プレイ中の統計収集
```

---

## ui/ ディレクトリ

### terminal.py

全てのターミナルUI処理。

**主要関数**:
- `show_title()`: タイトル画面
- `show_character_select()`: キャラクター選択
- `show_status(player, day_state)`: ステータス表示
- `show_stock(stock, current_day, relics)`: 在庫表示
- `show_shop(player, shop_items, bag_capacity)`: 買い物UI
- `show_online_shop(player, game_manager)`: 通販UI
- `select_ingredients(stock, current_day, relics)`: 食材選択UI
- `show_recipe_suggestions(stock)`: ネームド料理サジェスト
- `confirm_cooking(ingredients)`: 調理確認UI
- `show_holiday_activity_menu()`: 休日活動選択
- `show_game_result(result)`: 結果表示

---

## ゲームフロー

```
main()
  ├── show_title()
  ├── show_character_select()
  ├── Player / Stock / GameManager 初期化
  └── game_loop(game)
        └── while True:
              ├── handle_breakfast / handle_holiday_breakfast
              ├── handle_go_to_work（平日のみ）
              ├── handle_lunch / handle_holiday_lunch
              ├── handle_leave_work（平日のみ）
              ├── handle_shopping / handle_holiday_shopping
              ├── handle_dinner（配送処理）
              ├── handle_online_shopping
              ├── handle_sleep
              │     └── start_new_day()
              └── ゲームオーバー / クリア判定
```

---

## 実装済み機能

- 100種類の食材
- 100種類のレリック（毎日5種ランダム）
- 300種類のランダムイベント（休日イベント20種含む）
- 17種類のネームド料理 + サジェスト表示
- 通販の翌日配送システム
- 買い物バッグ上限 + 拡張レリック5種
- 調理前評価コメント + 確認UI
- 休日専用選択肢（遠出買い物、作り置き、休養）
- 初期レリック（冷蔵庫・電子レンジ）
- 天気システム
- カフェイン・不眠システム
- クレジットカード払い
- 複数料理の同時作成
