<script setup lang="ts">
import { computed } from 'vue'
import { useGameStore } from '../stores/game'
import { storeToRefs } from 'pinia'

const store = useGameStore()
const { stockByCategory } = storeToRefs(store)

const categories = computed(() => Object.keys(stockByCategory.value))
</script>

<template>
  <div class="stock-list">
    <h3>在庫一覧</h3>
    <div v-if="categories.length === 0" class="empty">
      在庫がありません
    </div>
    <div v-else class="categories">
      <div v-for="category in categories" :key="category" class="category">
        <h4>{{ category }}</h4>
        <div class="items">
          <div
            v-for="item in stockByCategory[category]"
            :key="`${item.name}-${item.purchase_day}`"
            class="item"
            :class="{ expired: item.is_expired, expiring: item.days_remaining <= 1 && !item.is_expired }"
          >
            <span class="name">{{ item.name }}</span>
            <span class="quantity">x{{ item.quantity }}</span>
            <span class="expiry">
              <template v-if="item.is_expired">期限切れ</template>
              <template v-else-if="item.days_remaining <= 1">本日中</template>
              <template v-else>残{{ item.days_remaining }}日</template>
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stock-list {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
}

h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
}

h4 {
  margin: 0 0 8px 0;
  color: #7f8c8d;
  font-size: 0.9em;
}

.empty {
  color: #95a5a6;
  text-align: center;
  padding: 20px;
}

.categories {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.item {
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px 12px;
  display: flex;
  gap: 8px;
  align-items: center;
  font-size: 0.9em;
}

.item.expired {
  background: #fadbd8;
  border-color: #e74c3c;
  opacity: 0.7;
}

.item.expiring {
  background: #fef9e7;
  border-color: #f39c12;
}

.name {
  font-weight: bold;
}

.quantity {
  color: #3498db;
}

.expiry {
  color: #95a5a6;
  font-size: 0.85em;
}

.item.expired .expiry {
  color: #e74c3c;
}

.item.expiring .expiry {
  color: #f39c12;
}
</style>
