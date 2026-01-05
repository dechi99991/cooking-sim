<script setup lang="ts">
import { watch } from 'vue'
import { useGameStore } from '../stores/game'
import { storeToRefs } from 'pinia'

const store = useGameStore()
const { state, onlineShopData, loading } = storeToRefs(store)

// データ取得
watch(() => state.value?.phase, async (phase) => {
  if (phase === 'ONLINE_SHOPPING') {
    await store.fetchOnlineShop()
  }
}, { immediate: true })

async function buyProvision(name: string) {
  await store.buyFromOnlineShop('provision', name, 1)
  await store.fetchOnlineShop()
}

async function buyRelic(name: string) {
  await store.buyFromOnlineShop('relic', name, 1)
  await store.fetchOnlineShop()
}
</script>

<template>
  <div class="online-shop">
    <h3>通販</h3>

    <div v-if="!onlineShopData" class="loading">読み込み中...</div>

    <template v-else>
      <div class="shop-info">
        <span>所持金: ¥{{ onlineShopData.player_money.toLocaleString() }}</span>
        <span v-if="onlineShopData.card_debt > 0" class="debt">
          カード残高: -¥{{ onlineShopData.card_debt.toLocaleString() }}
        </span>
      </div>

      <!-- 食糧 -->
      <div class="section">
        <h4>食糧・ドリンク</h4>
        <div class="items">
          <div
            v-for="item in onlineShopData.provisions"
            :key="item.name"
            class="item"
            :class="{ sale: item.is_sale }"
          >
            <div class="item-header">
              <span class="name">{{ item.name }}</span>
              <span v-if="item.is_sale" class="sale-badge">SALE</span>
            </div>
            <div class="item-info">
              <span class="price">¥{{ item.price }}</span>
              <span v-if="item.caffeine > 0" class="caffeine">カフェイン: {{ item.caffeine }}</span>
            </div>
            <div class="item-nutrition">
              <span>活{{ item.nutrition.vitality }}</span>
              <span>精{{ item.nutrition.mental }}</span>
              <span>覚{{ item.nutrition.awakening }}</span>
              <span>持{{ item.nutrition.sustain }}</span>
              <span>防{{ item.nutrition.defense }}</span>
              <span>満{{ item.fullness }}</span>
            </div>
            <button
              class="buy-btn"
              :disabled="item.price > onlineShopData.player_money || loading"
              @click="buyProvision(item.name)"
            >
              購入
            </button>
          </div>
        </div>
      </div>

      <!-- レリック -->
      <div class="section">
        <h4>アイテム（レリック）</h4>
        <div class="items relics">
          <div
            v-for="item in onlineShopData.relics"
            :key="item.name"
            class="item relic"
            :class="{
              sale: item.is_sale,
              owned: item.is_owned,
              pending: item.is_pending
            }"
          >
            <div class="item-header">
              <span class="name">{{ item.name }}</span>
              <span v-if="item.is_sale" class="sale-badge">SALE</span>
              <span v-if="item.is_owned" class="owned-badge">所持中</span>
              <span v-if="item.is_pending" class="pending-badge">配送中</span>
            </div>
            <div class="description">{{ item.description }}</div>
            <div class="item-info">
              <span class="price">¥{{ item.price.toLocaleString() }}</span>
              <span class="effect">効果: {{ item.effect_type }} +{{ item.effect_value }}</span>
            </div>
            <button
              class="buy-btn"
              :disabled="item.is_owned || item.is_pending || item.price > onlineShopData.player_money || loading"
              @click="buyRelic(item.name)"
            >
              <template v-if="item.is_owned">購入済み</template>
              <template v-else-if="item.is_pending">配送待ち</template>
              <template v-else>購入</template>
            </button>
          </div>
        </div>
      </div>

      <div class="notice">
        ※通販商品は翌日届きます
      </div>
    </template>
  </div>
</template>

<style scoped>
.online-shop {
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

.debt {
  color: #e74c3c;
}

.section {
  margin-bottom: 20px;
}

.items {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 10px;
}

.items.relics {
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
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

.item.owned {
  opacity: 0.6;
  background: #f8f9fa;
}

.item.pending {
  background: #fef9e7;
  border-color: #f39c12;
}

.item-header {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
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

.owned-badge {
  background: #95a5a6;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.7em;
}

.pending-badge {
  background: #f39c12;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.7em;
}

.description {
  font-size: 0.85em;
  color: #7f8c8d;
  margin-bottom: 8px;
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

.caffeine {
  color: #9b59b6;
}

.effect {
  color: #3498db;
}

.item-nutrition {
  display: flex;
  gap: 5px;
  font-size: 0.75em;
  color: #95a5a6;
  margin-bottom: 8px;
}

.buy-btn {
  width: 100%;
  padding: 8px;
  background: #9b59b6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.buy-btn:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.notice {
  text-align: center;
  color: #95a5a6;
  font-size: 0.85em;
  margin-top: 15px;
}
</style>
