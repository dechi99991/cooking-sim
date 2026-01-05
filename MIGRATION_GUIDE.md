# cooking-sim API移植ガイド

## 概要

Python製ターミナルゲーム「cooking-sim」を **Python API (FastAPI) + Vue.js フロントエンド** 構成に移植する。目的は友人にブラウザで遊んでもらい、Unity本格開発前にフィードバックを得ること。

## リポジトリ

https://github.com/dechi99991/cooking-sim

## 現在の構成

```
cooking-sim/
├── main.py              # エントリーポイント、ゲームループ
├── game/                # ゲームロジック（これをAPIとして公開）
│   ├── character.py     # キャラクター定義
│   ├── config.py        # ゲーム設定
│   ├── constants.py     # 定数定義
│   ├── cooking.py       # 調理システム
│   ├── day_cycle.py     # 日次サイクル管理（GameManager）
│   ├── event_data.py    # 300種類のイベント
│   ├── events.py        # イベントシステム
│   ├── ingredients.py   # 100種類の食材
│   ├── nutrition.py     # 栄養素システム
│   ├── player.py        # プレイヤー状態
│   ├── provisions.py    # 食糧・配送システム
│   ├── relic.py         # 100種類のレリック
│   └── result.py        # ゲーム結果・統計
└── ui/
    └── terminal.py      # ターミナルUI（これをVueに置き換え）
```

---

## Phase 1: FastAPI サーバー構築

### 目標
`game/` のロジックをそのまま活かし、REST APIとして公開する。

### 新規作成ファイル

```
cooking-sim/
├── api/
│   ├── __init__.py
│   ├── main.py          # FastAPIアプリ
│   ├── routes.py        # エンドポイント定義
│   ├── schemas.py       # Pydanticモデル（リクエスト/レスポンス）
│   └── session.py       # ゲームセッション管理（インメモリ）
└── requirements.txt     # FastAPI, uvicorn, pydantic追加
```

### エンドポイント設計

#### セッション管理
```
POST /api/game/start
  - body: { character_id: string }
  - response: { session_id: string, initial_state: GameState }

GET /api/game/{session_id}/state
  - response: GameState
```

#### ゲームアクション
```
POST /api/game/{session_id}/cook
  - body: { ingredient_ids: string[] }
  - response: { dish: Dish, updated_state: GameState }

POST /api/game/{session_id}/shop/buy
  - body: { items: [{ingredient_id: string, quantity: int}] }
  - response: { updated_state: GameState }

POST /api/game/{session_id}/online-shop/buy
  - body: { item_type: "provision" | "relic", item_id: string }
  - response: { updated_state: GameState }

POST /api/game/{session_id}/eat-provision
  - body: { provision_id: string }
  - response: { updated_state: GameState }

POST /api/game/{session_id}/advance-phase
  - response: { events: Event[], updated_state: GameState }

POST /api/game/{session_id}/holiday-action
  - body: { action: "outing" | "prep" | "rest" }
  - response: { updated_state: GameState }
```

#### データ取得
```
GET /api/game/{session_id}/shop
  - response: { items: ShopItem[], bag_capacity: int }

GET /api/game/{session_id}/online-shop
  - response: { provisions: Provision[], relics: Relic[] }

GET /api/game/{session_id}/stock
  - response: { ingredients: StockItem[] }

GET /api/game/{session_id}/recipes
  - response: { available: NamedRecipe[] }

GET /api/characters
  - response: Character[]
```

### GameState スキーマ

```python
class GameState(BaseModel):
    session_id: str
    
    # 日付状態
    day: int
    month: int
    phase: str  # GamePhase.name
    weather: str
    is_holiday: bool
    
    # プレイヤー状態
    player: PlayerState  # money, energy, stamina, fullness, card_debt
    
    # 在庫
    stock: list[StockItem]
    provisions: list[ProvisionItem]
    relics: list[str]  # レリック名リスト
    
    # 1日の状態
    daily_nutrition: NutritionState
    caffeine: int
    
    # ゲーム状態
    is_game_over: bool
    is_game_clear: bool
    game_over_reason: str | None
```

### セッション管理

- インメモリ辞書で `{session_id: GameManager}` を保持
- UUIDでセッションID生成
- タイムアウト処理は後回しでOK

### 実装の注意点

1. **`main.py` のロジックを参考に**
   - `handle_*` 関数群がフェーズごとの処理
   - これらをAPI経由で呼び出せるようにラップ

2. **イベント処理**
   - `trigger_events()` の結果をレスポンスに含める
   - フロントで表示できるよう `description` を返す

3. **ランダム性の扱い**
   - 天気、ショップ品揃え、イベント抽選はサーバー側で決定
   - フロントは結果を受け取るだけ

---

## Phase 2: Vue.js フロントエンド

### 目標
APIを叩いてゲームをプレイできるUIを構築。

### 技術スタック
- Vue 3 + Composition API
- Vite
- Pinia（状態管理）
- Axios（API通信）

### ディレクトリ構成

```
frontend/
├── src/
│   ├── api/
│   │   └── game.ts      # APIクライアント
│   ├── stores/
│   │   └── game.ts      # Piniaストア
│   ├── components/
│   │   ├── StatusBar.vue      # ステータス表示
│   │   ├── StockList.vue      # 在庫一覧
│   │   ├── ShopView.vue       # 買い物画面
│   │   ├── CookingView.vue    # 調理画面
│   │   ├── OnlineShop.vue     # 通販画面
│   │   ├── EventModal.vue     # イベント表示
│   │   └── ResultScreen.vue   # 結果画面
│   ├── views/
│   │   ├── TitleView.vue      # タイトル
│   │   ├── CharacterSelect.vue
│   │   └── GameView.vue       # メインゲーム画面
│   ├── App.vue
│   └── main.ts
└── package.json
```

### 画面フロー

```
TitleView → CharacterSelect → GameView
                                  ├── StatusBar（常時表示）
                                  ├── フェーズに応じた画面切り替え
                                  │   ├── BREAKFAST/LUNCH/DINNER → CookingView
                                  │   ├── SHOPPING → ShopView
                                  │   ├── ONLINE_SHOPPING → OnlineShop
                                  │   └── SLEEP → 自動進行
                                  └── EventModal（イベント発生時）
```

### 状態管理（Pinia）

```typescript
interface GameStore {
  sessionId: string | null
  state: GameState | null
  
  // アクション
  startGame(characterId: string): Promise<void>
  cook(ingredientIds: string[]): Promise<void>
  buyItems(items: CartItem[]): Promise<void>
  advancePhase(): Promise<void>
  // ...
}
```

### UI要件（ターミナル版を参考に）

1. **ステータスバー**
   - 日付、天気、所持金、気力、体力、満腹度
   - terminal.py の `show_status()` 参照

2. **在庫表示**
   - 食材名、数量、残り日数
   - 期限切れ間近は警告表示

3. **買い物画面**
   - カテゴリ別表示
   - セール品ハイライト
   - バッグ容量制限の表示

4. **調理画面**
   - 食材選択（複数選択）
   - ネームド料理サジェスト
   - 調理前評価コメント

5. **通販画面**
   - 食糧タブ / レリックタブ
   - 翌日配送の説明

---

## Phase 3: デプロイ

### 構成

```
[Railway / Render]
├── Backend (FastAPI)
│   └── /api/* → uvicorn
└── Frontend (Vue)
    └── /* → 静的ファイル配信
```

### Railway の場合

```toml
# railway.toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn api.main:app --host 0.0.0.0 --port $PORT"
```

フロントエンドは `dist/` をビルドして同じサーバーから配信するか、別サービスとして立てる。

---

## 優先順位

### 必須（友人に遊んでもらう最小構成）

1. [ ] FastAPI基盤（セッション管理、基本エンドポイント）
2. [ ] 1日のサイクルが回るAPI（朝食→就寝）
3. [ ] Vueで最低限のUI（ステータス、調理、買い物）
4. [ ] どこかにデプロイ

### 後回し可

- レリック詳細効果の表示
- イベント演出
- サウンド
- セーブ/ロード
- セッションタイムアウト

---

## 参考：main.py のフェーズハンドラ対応表

| main.py 関数 | APIエンドポイント |
|-------------|-----------------|
| `handle_breakfast` | POST /cook + POST /advance-phase |
| `handle_lunch` | POST /cook or POST /eat-provision |
| `handle_dinner` | POST /cook + POST /advance-phase（配送処理） |
| `handle_shopping` | GET /shop + POST /shop/buy |
| `handle_online_shopping` | GET /online-shop + POST /online-shop/buy |
| `handle_sleep` | POST /advance-phase |
| `handle_holiday_shopping` | POST /holiday-action + GET /shop |

---

## 質問があれば

実装中に判断に迷ったら、以下を優先：
1. ターミナル版と同じ挙動を維持
2. シンプルな実装を選ぶ
3. バランス調整は後からできるようにパラメータ化
