<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useGameStore } from '../stores/game'
import { storeToRefs } from 'pinia'

defineProps<{
  isDistant?: boolean
}>()

const emit = defineEmits<{
  done: []
}>()

const store = useGameStore()
const { state, shopData, loading } = storeToRefs(store)

const cart = ref<Record<string, number>>({})

const cartTotal = computed(() => {
  if (!shopData.value) return 0
  let total = 0
  for (const [name, qty] of Object.entries(cart.value)) {
    const item = shopData.value.items.find(i => i.name === name)
    if (item) total += item.price * qty
  }
  return total
})

const cartCount = computed(() => {
  return Object.values(cart.value).reduce((a, b) => a + b, 0)
})

const canBuy = computed(() => {
  if (!shopData.value) return false
  return cartTotal.value > 0 &&
         cartTotal.value <= shopData.value.player_money &&
         cartCount.value <= shopData.value.bag_capacity
})

function addToCart(name: string) {
  if (!shopData.value) return
  const item = shopData.value.items.find(i => i.name === name)
  if (!item || item.quantity <= (cart.value[name] || 0)) return
  if (cartCount.value >= shopData.value.bag_capacity) return

  cart.value[name] = (cart.value[name] || 0) + 1
}

function removeFromCart(name: string) {
  if (cart.value[name]) {
    cart.value[name]--
    if (cart.value[name] === 0) {
      delete cart.value[name]
    }
  }
}

async function checkout() {
  if (!canBuy.value) return
  const items = Object.entries(cart.value).map(([name, qty]) => ({
    ingredient_name: name,
    quantity: qty,
  }))
  await store.buyFromShop(items)
  cart.value = {}
  await store.fetchShop()
}

// ショップデータ取得
watch(() => state.value?.phase, async (phase) => {
  if (phase === 'SHOPPING') {
    await store.fetchShop()
    cart.value = {}
  }
}, { immediate: true })

// カテゴリ別アイテム
const itemsByCategory = computed(() => {
  if (!shopData.value) return {}
  const result: Record<string, typeof shopData.value.items> = {}
  for (const item of shopData.value.items) {
    if (!result[item.category]) {
      result[item.category] = []
    }
    result[item.category]!.push(item)
  }
  return result
})
</script>

<template>
  <div class="shop-panel">
    <h3>ショップ</h3>

    <div v-if="!shopData" class="loading">読み込み中...</div>

    <template v-else>
      <div class="shop-info">
        <span>所持金: ¥{{ shopData.player_money.toLocaleString() }}</span>
        <span>バッグ: {{ cartCount }}/{{ shopData.bag_capacity }}</span>
      </div>

      <div class="categories">
        <div v-for="(items, category) in itemsByCategory" :key="category" class="category">
          <h4>{{ category }}</h4>
          <div class="items">
            <div
              v-for="item in items"
              :key="item.name"
              class="item"
              :class="{ sale: item.is_sale, soldout: item.quantity === 0 }"
            >
              <div class="item-header">
                <span class="name">{{ item.name }}</span>
                <span v-if="item.is_sale" class="sale-badge">SALE</span>
              </div>
              <div class="item-info">
                <span class="price">¥{{ item.price }}</span>
                <span class="stock">在庫: {{ item.quantity }}</span>
                <span class="expiry">鮮度: {{ item.expiry_days }}日</span>
              </div>
              <div class="item-nutrition">
                <span>活{{ item.nutrition.vitality }}</span>
                <span>精{{ item.nutrition.mental }}</span>
                <span>覚{{ item.nutrition.awakening }}</span>
                <span>持{{ item.nutrition.sustain }}</span>
                <span>防{{ item.nutrition.defense }}</span>
                <span>満{{ item.fullness }}</span>
              </div>
              <div class="item-actions">
                <button
                  class="minus"
                  :disabled="!cart[item.name]"
                  @click="removeFromCart(item.name)"
                >-</button>
                <span class="qty">{{ cart[item.name] || 0 }}</span>
                <button
                  class="plus"
                  :disabled="item.quantity <= (cart[item.name] || 0) || cartCount >= shopData.bag_capacity"
                  @click="addToCart(item.name)"
                >+</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- カート -->
      <div v-if="cartCount > 0" class="cart">
        <h4>カート</h4>
        <div class="cart-items">
          <span v-for="(qty, name) in cart" :key="name" class="cart-item">
            {{ name }} x{{ qty }}
          </span>
        </div>
        <div class="cart-total">
          合計: ¥{{ cartTotal.toLocaleString() }}
        </div>
        <button
          class="checkout-btn"
          :disabled="!canBuy || loading"
          @click="checkout"
        >
          購入する
        </button>
      </div>

      <!-- 帰宅ボタン -->
      <button
        class="done-btn"
        :disabled="loading"
        @click="emit('done')"
      >
        帰宅する
      </button>
    </template>
  </div>
</template>

<style scoped>
.shop-panel {
  background: #fff;
  border-radius: 8px;
  padding: 15px;
  border: 1px solid #ddd;
}

h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
}

h4 {
  margin: 0 0 10px 0;
  color: #7f8c8d;
  font-size: 0.9em;
}

.loading {
  text-align: center;
  color: #95a5a6;
  padding: 20px;
}

.shop-info {
  display: flex;
  justify-content: space-between;
  background: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.categories {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.items {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
}

.item {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 10px;
}

.item.sale {
  border-color: #e74c3c;
  background: #fef5f5;
}

.item.soldout {
  opacity: 0.5;
}

.item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.name {
  font-weight: bold;
}

.sale-badge {
  background: #e74c3c;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.7em;
}

.item-info {
  display: flex;
  gap: 10px;
  font-size: 0.85em;
  color: #7f8c8d;
  margin-bottom: 5px;
}

.price {
  color: #27ae60;
  font-weight: bold;
}

.item-nutrition {
  display: flex;
  gap: 5px;
  font-size: 0.75em;
  color: #95a5a6;
  margin-bottom: 8px;
}

.item-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: center;
}

.item-actions button {
  width: 30px;
  height: 30px;
  border: 1px solid #3498db;
  background: white;
  color: #3498db;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.2em;
}

.item-actions button:disabled {
  border-color: #bdc3c7;
  color: #bdc3c7;
  cursor: not-allowed;
}

.qty {
  min-width: 30px;
  text-align: center;
  font-weight: bold;
}

.cart {
  margin-top: 20px;
  padding: 15px;
  background: #ebf5fb;
  border-radius: 8px;
}

.cart-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.cart-item {
  background: white;
  padding: 4px 8px;
  border-radius: 4px;
}

.cart-total {
  font-size: 1.2em;
  font-weight: bold;
  margin-bottom: 10px;
}

.checkout-btn {
  width: 100%;
  padding: 12px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
}

.checkout-btn:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.done-btn {
  display: block;
  width: 100%;
  margin-top: 20px;
  padding: 15px;
  background: #27ae60;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.1em;
  transition: all 0.2s;
}

.done-btn:hover:not(:disabled) {
  background: #219a52;
}

.done-btn:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}
</style>
