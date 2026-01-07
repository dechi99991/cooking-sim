<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '../stores/game'
import { storeToRefs } from 'pinia'
import StatusBar from '../components/StatusBar.vue'
import StockList from '../components/StockList.vue'
import BreakfastPanel from '../components/BreakfastPanel.vue'
import LunchPanel from '../components/LunchPanel.vue'
import DinnerPanel from '../components/DinnerPanel.vue'
import ShopPanel from '../components/ShopPanel.vue'
import OnlineShopPanel from '../components/OnlineShopPanel.vue'
import HolidayPanel from '../components/HolidayPanel.vue'
import EventModal from '../components/EventModal.vue'
import GritRecoveryModal from '../components/GritRecoveryModal.vue'
import ExhaustedModal from '../components/ExhaustedModal.vue'

const router = useRouter()
const store = useGameStore()
const {
  state,
  loading,
  error,
  isGameOver,
  isGameClear,
  currentPhase,
  isHoliday,
  lastEvents,
  lastDeliveries,
  lastSalaryInfo,
  lastBonusInfo,
  lastEncouragementMessage,
} = storeToRefs(store)

const showEventModal = ref(false)
const showGritModal = ref(false)
const showExhaustedModal = ref(false)

// ゲームが開始されていない場合はキャラクター選択へ
onMounted(() => {
  if (!state.value) {
    router.push('/select')
  }
})

// ゲーム終了チェック
watch([isGameOver, isGameClear], ([gameOver, gameClear]) => {
  if (gameOver) {
    // 体力＆気力枯渇の場合は力尽きモーダルを表示
    if (state.value?.game_over_reason === 'exhausted') {
      showExhaustedModal.value = true
    } else {
      router.push('/result')
    }
  } else if (gameClear) {
    router.push('/result')
  }
})

// 根性回復モーダル表示
watch(() => state.value?.player.grit_used, (used) => {
  if (used) {
    showGritModal.value = true
  }
})

// フェーズ進行
async function advance() {
  await store.advancePhase()
  // イベントがある場合はモーダル表示
  if (lastEvents.value.length > 0 || lastDeliveries.value.length > 0 || lastSalaryInfo.value || lastBonusInfo.value || lastEncouragementMessage.value) {
    showEventModal.value = true
  }
}

function closeEventModal() {
  showEventModal.value = false
}

function closeGritModal() {
  showGritModal.value = false
}

function closeExhaustedModal() {
  showExhaustedModal.value = false
  router.push('/result')
}

// 各パネルの完了ハンドラ
function onMealDone() {
  advance()
}

function onHolidayActionDone() {
  advance()
}

function onShopDone() {
  advance()
}

// フェーズ表示名
const phaseTitle = computed(() => {
  switch (currentPhase.value) {
    case 'BREAKFAST': return isHoliday.value ? '休日の朝食' : '朝食'
    case 'LUNCH': return isHoliday.value ? '休日の昼食' : '昼食'
    case 'HOLIDAY_SHOPPING_1': return '休日の行動（午前）'
    case 'HOLIDAY_LUNCH': return '休日の昼食'
    case 'HOLIDAY_SHOPPING_2': return '休日の行動（午後）'
    case 'SHOPPING': return '買い物'
    case 'DINNER': return '夕食'
    case 'ONLINE_SHOPPING': return '通販'
    case 'SLEEP': return '就寝'
    default: return currentPhase.value
  }
})

// 進行ボタンのテキスト
const advanceButtonText = computed(() => {
  switch (currentPhase.value) {
    case 'BREAKFAST':
      if (isHoliday.value) return '次へ'
      return state.value?.is_office_worker ? '出勤する' : '次へ'
    case 'LUNCH':
      return '次へ'
    case 'HOLIDAY_SHOPPING_1':
    case 'HOLIDAY_LUNCH':
    case 'HOLIDAY_SHOPPING_2':
      return '次へ'
    case 'SHOPPING': return '帰宅する'
    case 'DINNER': return '通販を見る'
    case 'ONLINE_SHOPPING': return '寝る'
    case 'SLEEP': return '翌日へ'
    default: return '次へ'
  }
})

</script>

<template>
  <div class="game-view">
    <StatusBar />

    <div v-if="error" class="error-bar">
      {{ error }}
    </div>

    <div class="game-content">
      <div class="main-panel">
        <h2>{{ phaseTitle }}</h2>

        <!-- 朝食フェーズ -->
        <template v-if="currentPhase === 'BREAKFAST'">
          <BreakfastPanel :is-holiday="isHoliday" @done="onMealDone" />
        </template>

        <!-- 昼食フェーズ（平日：社食あり、休日：自炊あり） -->
        <template v-else-if="currentPhase === 'LUNCH'">
          <LunchPanel :is-holiday="isHoliday" :auto-eat="state?.is_office_worker && !isHoliday" @done="onMealDone" />
        </template>

        <!-- 休日行動フェーズ1 -->
        <template v-else-if="currentPhase === 'HOLIDAY_SHOPPING_1'">
          <HolidayPanel @done="onHolidayActionDone" />
        </template>

        <!-- 休日昼食フェーズ -->
        <template v-else-if="currentPhase === 'HOLIDAY_LUNCH'">
          <LunchPanel :is-holiday="true" :auto-eat="false" @done="onMealDone" />
        </template>

        <!-- 休日行動フェーズ2 -->
        <template v-else-if="currentPhase === 'HOLIDAY_SHOPPING_2'">
          <HolidayPanel @done="onHolidayActionDone" />
        </template>

        <!-- 買い物フェーズ -->
        <template v-else-if="currentPhase === 'SHOPPING'">
          <ShopPanel @done="onShopDone" />
        </template>

        <!-- 夕食フェーズ -->
        <template v-else-if="currentPhase === 'DINNER'">
          <DinnerPanel @done="onMealDone" />
        </template>

        <!-- 通販フェーズ -->
        <template v-else-if="currentPhase === 'ONLINE_SHOPPING'">
          <OnlineShopPanel @done="advance" />
        </template>

        <!-- 就寝フェーズ -->
        <template v-else-if="currentPhase === 'SLEEP'">
          <div class="sleep-panel">
            <div class="sleep-icon">😴</div>
            <p>お疲れ様でした。ゆっくり休みましょう。</p>

            <div class="daily-nutrition" v-if="state">
              <h4>本日の栄養摂取</h4>
              <div class="nutrition-grid">
                <div class="nutrition-item">
                  <span class="label">活力</span>
                  <span class="value">{{ state.daily_nutrition.vitality }}</span>
                </div>
                <div class="nutrition-item">
                  <span class="label">精神</span>
                  <span class="value">{{ state.daily_nutrition.mental }}</span>
                </div>
                <div class="nutrition-item">
                  <span class="label">覚醒</span>
                  <span class="value">{{ state.daily_nutrition.awakening }}</span>
                </div>
                <div class="nutrition-item">
                  <span class="label">持続</span>
                  <span class="value">{{ state.daily_nutrition.sustain }}</span>
                </div>
                <div class="nutrition-item">
                  <span class="label">防御</span>
                  <span class="value">{{ state.daily_nutrition.defense }}</span>
                </div>
              </div>
            </div>
          </div>
          <button
            class="advance-btn"
            :disabled="loading"
            @click="advance"
          >
            {{ advanceButtonText }}
          </button>
        </template>

        <!-- その他のフェーズ（フォールバック） -->
        <template v-else>
          <div class="unknown-phase">
            <p>フェーズ: {{ currentPhase }}</p>
            <button
              class="advance-btn"
              :disabled="loading"
              @click="advance"
            >
              次へ
            </button>
          </div>
        </template>
      </div>

      <div class="side-panel">
        <StockList />
      </div>
    </div>

    <!-- イベントモーダル -->
    <EventModal
      v-if="showEventModal"
      :events="lastEvents"
      :deliveries="lastDeliveries"
      :salary-info="lastSalaryInfo"
      :bonus-info="lastBonusInfo"
      :encouragement-message="lastEncouragementMessage"
      @close="closeEventModal"
    />

    <!-- 根性回復モーダル -->
    <GritRecoveryModal
      :show="showGritModal"
      @close="closeGritModal"
    />

    <!-- 力尽きモーダル -->
    <ExhaustedModal
      :show="showExhaustedModal"
      @close="closeExhaustedModal"
    />
  </div>
</template>

<style scoped>
.game-view {
  min-height: 100vh;
  background: #f0f2f5;
}

.error-bar {
  background: #e74c3c;
  color: white;
  padding: 10px;
  text-align: center;
}

.game-content {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 20px;
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

@media (max-width: 900px) {
  .game-content {
    grid-template-columns: 1fr;
  }
}

.main-panel {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.main-panel h2 {
  margin: 0 0 20px 0;
  color: #2c3e50;
  padding-bottom: 10px;
  border-bottom: 2px solid #3498db;
}

.side-panel {
  position: sticky;
  top: 20px;
  height: fit-content;
}

.advance-btn {
  display: block;
  width: 100%;
  margin-top: 20px;
  padding: 15px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.1em;
  transition: all 0.2s;
}

.advance-btn:hover {
  background: #2980b9;
}

.advance-btn:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.sleep-panel {
  text-align: center;
  padding: 40px 20px;
}

.sleep-icon {
  font-size: 4em;
  margin-bottom: 20px;
}

.daily-nutrition {
  margin-top: 30px;
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
}

.daily-nutrition h4 {
  margin: 0 0 15px 0;
  color: #7f8c8d;
}

.nutrition-grid {
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
}

.nutrition-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 20px;
  background: white;
  border-radius: 8px;
}

.nutrition-item .label {
  font-size: 0.85em;
  color: #7f8c8d;
}

.nutrition-item .value {
  font-size: 1.5em;
  font-weight: bold;
  color: #2c3e50;
}

.unknown-phase {
  text-align: center;
  padding: 40px;
  color: #7f8c8d;
}
</style>
