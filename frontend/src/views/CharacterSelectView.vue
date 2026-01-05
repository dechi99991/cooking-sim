<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '../stores/game'
import { storeToRefs } from 'pinia'

const router = useRouter()
const store = useGameStore()
const { characters, loading, error } = storeToRefs(store)

onMounted(() => {
  store.fetchCharacters()
})

async function selectCharacter(id: string) {
  await store.startGame(id)
  console.log('After startGame - state:', store.state, 'error:', error.value)
  if (!error.value && store.state) {
    router.push('/game')
  }
}

async function startDefault() {
  await store.startGame()
  console.log('After startGame - state:', store.state, 'error:', error.value)
  if (!error.value && store.state) {
    router.push('/game')
  }
}
</script>

<template>
  <div class="select-view">
    <h1>キャラクター選択</h1>

    <div v-if="error" class="error">エラー: {{ error }}</div>
    <div v-if="loading" class="loading">読み込み中...</div>

    <div v-if="!loading && characters.length > 0" class="characters">
      <div
        v-for="char in characters"
        :key="char.id"
        class="character-card"
        @click="selectCharacter(char.id)"
      >
        <h2>{{ char.name }}</h2>
        <p class="description">{{ char.description }}</p>
        <div class="stats">
          <div class="stat">
            <span class="label">初期所持金</span>
            <span class="value">¥{{ char.initial_money.toLocaleString() }}</span>
          </div>
          <div class="stat">
            <span class="label">月給</span>
            <span class="value">¥{{ char.salary_amount.toLocaleString() }}</span>
          </div>
          <div class="stat">
            <span class="label">家賃</span>
            <span class="value">¥{{ char.rent_amount.toLocaleString() }}</span>
          </div>
          <div v-if="char.has_bonus" class="stat">
            <span class="label">ボーナス</span>
            <span class="value bonus">¥{{ char.bonus_amount.toLocaleString() }}</span>
          </div>
          <div class="stat">
            <span class="label">気力</span>
            <span class="value">{{ char.initial_energy }}/10</span>
          </div>
          <div class="stat">
            <span class="label">体力</span>
            <span class="value">{{ char.initial_stamina }}/10</span>
          </div>
        </div>
      </div>
    </div>

    <button class="default-btn" @click="startDefault" :disabled="loading">
      デフォルトで開始
    </button>

    <button class="back-btn" @click="router.push('/')">
      戻る
    </button>
  </div>
</template>

<style scoped>
.select-view {
  min-height: 100vh;
  padding: 40px 20px;
  background: #f8f9fa;
}

h1 {
  text-align: center;
  color: #2c3e50;
  margin: 0 0 30px 0;
}

.loading, .error {
  text-align: center;
  padding: 40px;
}

.error {
  color: #e74c3c;
}

.characters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  max-width: 1000px;
  margin: 0 auto 30px;
}

.character-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.character-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
}

.character-card h2 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.description {
  color: #7f8c8d;
  margin: 0 0 15px 0;
  font-size: 0.95em;
}

.stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.stat {
  display: flex;
  justify-content: space-between;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
}

.label {
  color: #7f8c8d;
  font-size: 0.85em;
}

.value {
  font-weight: bold;
  color: #2c3e50;
}

.value.bonus {
  color: #f39c12;
}

.default-btn, .back-btn {
  display: block;
  margin: 10px auto;
  padding: 12px 40px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1em;
}

.default-btn {
  background: #3498db;
  color: white;
}

.default-btn:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.back-btn {
  background: transparent;
  color: #7f8c8d;
  border: 1px solid #ddd;
}
</style>
