<script setup lang="ts">
import { computed } from 'vue'
import { useGameStore } from '../stores/game'
import { storeToRefs } from 'pinia'

const store = useGameStore()
const { state } = storeToRefs(store)

const preparedDishes = computed(() => state.value?.prepared ?? [])
</script>

<template>
  <div class="prepared-list">
    <h3>作り置き料理</h3>

    <div v-if="preparedDishes.length === 0" class="empty">
      作り置きはありません
    </div>

    <div v-else class="dishes">
      <div v-for="(dish, idx) in preparedDishes" :key="idx" class="dish">
        <div class="dish-header">
          <span class="name">{{ dish.name }}</span>
          <span class="type">{{ dish.dish_type }}</span>
        </div>
        <div class="dish-stats">
          <span>満腹: +{{ dish.fullness }}</span>
          <span class="expiry">期限: {{ dish.expiry_day }}日目</span>
        </div>
        <div class="dish-nutrition">
          <span>活{{ dish.nutrition.vitality }}</span>
          <span>精{{ dish.nutrition.mental }}</span>
          <span>覚{{ dish.nutrition.awakening }}</span>
          <span>持{{ dish.nutrition.sustain }}</span>
          <span>防{{ dish.nutrition.defense }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.prepared-list {
  background: #fff;
  border-radius: 8px;
  padding: 15px;
  border: 1px solid #ddd;
}

h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
}

.empty {
  color: #95a5a6;
  text-align: center;
  padding: 20px;
}

.dishes {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.dish {
  background: #fef9e7;
  border: 1px solid #f39c12;
  border-radius: 8px;
  padding: 10px;
}

.dish-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.name {
  font-weight: bold;
}

.type {
  color: #7f8c8d;
  font-size: 0.85em;
}

.dish-stats {
  display: flex;
  gap: 15px;
  font-size: 0.85em;
  color: #7f8c8d;
  margin-bottom: 5px;
}

.expiry {
  color: #e67e22;
}

.dish-nutrition {
  display: flex;
  gap: 8px;
  font-size: 0.8em;
  color: #95a5a6;
}
</style>
