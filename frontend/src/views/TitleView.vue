<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function startGame() {
  router.push('/select')
}
</script>

<template>
  <div class="title-view">
    <div class="title-content">
      <h1>自炊サバイバル</h1>
      <p class="subtitle">一人暮らしシミュレーションゲーム</p>

      <div class="description">
        <p>限られた予算と時間の中で、</p>
        <p>1ヶ月間の食生活を乗り切れ！</p>
      </div>

      <button class="start-btn" @click="startGame">
        ゲームスタート
      </button>

      <div class="info">
        <h3>ゲームの流れ</h3>
        <ul>
          <li>🌅 朝食: 作り置きを食べる</li>
          <li>🛒 買い物: 食材を購入</li>
          <li>🍳 夕食: 料理を作って食べる</li>
          <li>📦 通販: 食糧やアイテムを注文</li>
          <li>😴 就寝: 翌日へ</li>
        </ul>
      </div>

      <div class="release-notes">
        <h3>📝 更新情報</h3>
        <div class="release-entry">
          <div class="release-date">2025/01/10（その2）</div>
          <ul>
            <li>【大型更新】週間ボスシステムを刷新！</li>
            <li>月曜朝に「今週のボス」が予告されます（飲み会、締め切り、健康診断など）</li>
            <li>ボスには生存条件があり、金曜までに準備が必要</li>
            <li>条件達成で報酬、失敗でペナルティ（借金など）</li>
            <li>ステータスバーにボス情報を常時表示</li>
          </ul>
        </div>
        <div class="release-entry">
          <div class="release-date">2025/01/10</div>
          <ul>
            <li>金曜ボスイベント「週の総決算」を導入</li>
            <li>土日を「週末」として1ターンに統合（ゲーム期間: 約26ターン）</li>
          </ul>
        </div>
        <div class="release-entry">
          <div class="release-date">2025/01/07（その10）</div>
          <ul>
            <li>休日の買い物画面の文字色バグを修正</li>
            <li>休日アクション「友人と外食」追加（¥1,000 / 全栄養+3 / 気力+1）</li>
            <li>休日アクション「掃除・整理」追加（気力-1 / 翌日回復+2）</li>
            <li>「何もしない」オプションを削除</li>
            <li>気質システム導入: 3日間の行動傾向から気質が判定されます</li>
          </ul>
        </div>
        <div class="release-entry">
          <div class="release-date">2025/01/07（その9）</div>
          <ul>
            <li>体力・気力の最大値表示が正しく反映されるようになりました</li>
          </ul>
        </div>
        <div class="release-entry">
          <div class="release-date">2025/01/07（その8）</div>
          <ul>
            <li>難易度調整: 出退勤の体力消費を軽減（往復で2消費に）</li>
            <li>最初の3日間はランダムイベントが発生しません</li>
            <li>フリーランスには通勤・退勤イベントが発生しなくなりました</li>
            <li>根性回復が正しく発動しないバグを修正</li>
          </ul>
        </div>
        <div class="release-entry">
          <div class="release-date">2025/01/07（その7）</div>
          <ul>
            <li>根性回復システム追加: 体力0でも気力2消費で体力1回復</li>
            <li>体力も気力も尽きた時は「力尽きた」演出が表示されます</li>
          </ul>
        </div>
        <div class="release-entry">
          <div class="release-date">2025/01/07（その6）</div>
          <ul>
            <li>食材がない場合、料理コマンドを非表示に</li>
            <li>食糧がない場合、「食糧を食べる」を非表示に</li>
          </ul>
        </div>
        <div class="release-entry">
          <div class="release-date">2025/01/07（その5）</div>
          <ul>
            <li>5栄養素がイベント発生に影響するようになりました</li>
            <li>心力素が高いと気力マイナスイベントの発生率が下がります</li>
            <li>防衛素が高いと体力マイナスイベントの発生率が下がります</li>
            <li>活力素・覚醒素が3日連続高いと体力・気力上限が増加します</li>
            <li>イベント発生時に「なぜ起きたか」の理由が表示されます</li>
          </ul>
        </div>
        <div class="release-entry">
          <div class="release-date">2025/01/07（その4）</div>
          <ul>
            <li>ネームド料理を10種類追加（計27種類）</li>
            <li>買い物バッグ系レリックの効果を調整</li>
          </ul>
        </div>
        <div class="release-entry">
          <div class="release-date">2025/01/07（その3）</div>
          <ul>
            <li>体力が0になる行動の前に確認モーダルが表示されます</li>
            <li>フリーランス向けに「うぼあデリバリ」を追加（700円）</li>
            <li>フリーランスの平日昼食で自炊が選べるようになりました</li>
            <li>フリーランスの朝食スキップ時のバグを修正</li>
          </ul>
        </div>
        <div class="release-entry">
          <div class="release-date">2025/01/07（その2）</div>
          <ul>
            <li>昼食自動選択時に何を消費したか表示されるようになりました</li>
            <li>買い物でバッグが一杯になると警告が表示されます</li>
          </ul>
        </div>
        <div class="release-entry">
          <div class="release-date">2025/01/07</div>
          <ul>
            <li>出勤キャラの昼食が自動化されました（弁当→食糧→社食）</li>
            <li>調理画面で作れるレシピが表示されるようになりました</li>
            <li>1日の終わりにねぎらいメッセージが表示されます</li>
            <li>休日の買い物画面のUIを改善しました</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.title-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.title-content {
  text-align: center;
  color: white;
  max-width: 500px;
}

h1 {
  font-size: 3em;
  margin: 0 0 10px 0;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.subtitle {
  font-size: 1.2em;
  opacity: 0.9;
  margin: 0 0 30px 0;
}

.description {
  font-size: 1.1em;
  margin-bottom: 30px;
  line-height: 1.8;
}

.description p {
  margin: 0;
}

.start-btn {
  padding: 15px 50px;
  font-size: 1.3em;
  background: #f39c12;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.start-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.info {
  margin-top: 40px;
  background: rgba(255, 255, 255, 0.15);
  padding: 20px;
  border-radius: 12px;
  text-align: left;
}

.info h3 {
  margin: 0 0 15px 0;
  text-align: center;
}

.info ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.info li {
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.info li:last-child {
  border-bottom: none;
}

.release-notes {
  margin-top: 20px;
  background: rgba(255, 255, 255, 0.1);
  padding: 15px 20px;
  border-radius: 12px;
  text-align: left;
  font-size: 0.9em;
}

.release-notes h3 {
  margin: 0 0 10px 0;
  text-align: center;
}

.release-entry {
  margin-bottom: 10px;
}

.release-entry:last-child {
  margin-bottom: 0;
}

.release-date {
  font-size: 0.85em;
  opacity: 0.8;
  margin-bottom: 5px;
}

.release-notes ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.release-notes li {
  padding: 4px 0;
  padding-left: 1em;
  text-indent: -1em;
}

.release-notes li::before {
  content: "• ";
}
</style>
