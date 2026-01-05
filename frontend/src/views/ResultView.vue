<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '../stores/game'
import { storeToRefs } from 'pinia'

const router = useRouter()
const store = useGameStore()
const { state, isGameClear, isGameOver } = storeToRefs(store)

const resultType = computed(() => {
  if (isGameClear.value) return 'clear'
  if (isGameOver.value) return 'over'
  return 'unknown'
})

function restart() {
  store.resetGame()
  router.push('/')
}
</script>

<template>
  <div class="result-view" :class="resultType">
    <div class="result-content">
      <!-- ゲームクリア -->
      <template v-if="resultType === 'clear'">
        <div class="icon">🎉</div>
        <h1>ゲームクリア！</h1>
        <p class="message">おめでとうございます！1ヶ月を乗り切りました！</p>
      </template>

      <!-- ゲームオーバー -->
      <template v-else-if="resultType === 'over'">
        <div class="icon">😵</div>
        <h1>ゲームオーバー</h1>
        <p class="message">{{ state?.game_over_reason || '残念ながら生活を続けられませんでした...' }}</p>
      </template>

      <!-- 結果詳細 -->
      <div v-if="state" class="stats">
        <h3>最終ステータス</h3>
        <div class="stats-grid">
          <div class="stat">
            <span class="label">到達日数</span>
            <span class="value">{{ state.day }}日目</span>
          </div>
          <div class="stat">
            <span class="label">所持金</span>
            <span class="value">¥{{ state.player.money.toLocaleString() }}</span>
          </div>
          <div class="stat">
            <span class="label">気力</span>
            <span class="value">{{ state.player.energy }}/10</span>
          </div>
          <div class="stat">
            <span class="label">体力</span>
            <span class="value">{{ state.player.stamina }}/10</span>
          </div>
          <div class="stat">
            <span class="label">所持レリック</span>
            <span class="value">{{ state.relics.length }}個</span>
          </div>
          <div class="stat">
            <span class="label">食材在庫</span>
            <span class="value">{{ state.stock.length }}品</span>
          </div>
        </div>

        <div v-if="state.relics.length > 0" class="relics">
          <h4>取得レリック</h4>
          <div class="relic-list">
            <span v-for="relic in state.relics" :key="relic" class="relic">
              {{ relic }}
            </span>
          </div>
        </div>
      </div>

      <button class="restart-btn" @click="restart">
        タイトルに戻る
      </button>
    </div>
  </div>
</template>

<style scoped>
.result-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.result-view.clear {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.result-view.over {
  background: linear-gradient(135deg, #434343 0%, #000000 100%);
}

.result-content {
  text-align: center;
  color: white;
  max-width: 500px;
}

.icon {
  font-size: 5em;
  margin-bottom: 20px;
}

h1 {
  font-size: 2.5em;
  margin: 0 0 15px 0;
}

.message {
  font-size: 1.2em;
  opacity: 0.9;
  margin-bottom: 30px;
}

.stats {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 30px;
}

.stats h3 {
  margin: 0 0 15px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.stat {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.label {
  opacity: 0.8;
}

.value {
  font-weight: bold;
}

.relics {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.relics h4 {
  margin: 0 0 10px 0;
  opacity: 0.8;
}

.relic-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.relic {
  background: rgba(255, 255, 255, 0.2);
  padding: 5px 12px;
  border-radius: 4px;
  font-size: 0.9em;
}

.restart-btn {
  padding: 15px 40px;
  font-size: 1.1em;
  background: white;
  color: #2c3e50;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.restart-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
}
</style>
