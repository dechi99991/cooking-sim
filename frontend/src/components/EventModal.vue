<script setup lang="ts">
import type { EventInfo, PendingDeliveryItem } from '../types'

defineProps<{
  events: EventInfo[]
  deliveries: PendingDeliveryItem[]
  salaryInfo: { gross: number; rent: number; net: number } | null
  bonusInfo: { amount: number } | null
}>()

const emit = defineEmits<{
  close: []
}>()
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal">
      <h3>フェーズ終了</h3>

      <!-- 給料情報 -->
      <div v-if="salaryInfo" class="info-box salary">
        <h4>💰 給料日</h4>
        <div class="salary-details">
          <div class="row">
            <span>総支給額</span>
            <span>¥{{ salaryInfo.gross.toLocaleString() }}</span>
          </div>
          <div class="row deduction">
            <span>家賃</span>
            <span>-¥{{ salaryInfo.rent.toLocaleString() }}</span>
          </div>
          <div class="row total">
            <span>手取り</span>
            <span>¥{{ salaryInfo.net.toLocaleString() }}</span>
          </div>
        </div>
      </div>

      <!-- ボーナス情報 -->
      <div v-if="bonusInfo" class="info-box bonus">
        <h4>🎉 ボーナス</h4>
        <div class="bonus-amount">
          ¥{{ bonusInfo.amount.toLocaleString() }}
        </div>
      </div>

      <!-- 配達情報 -->
      <div v-if="deliveries.length > 0" class="info-box deliveries">
        <h4>📦 配達</h4>
        <div class="delivery-list">
          <div v-for="(item, idx) in deliveries" :key="idx" class="delivery-item">
            <span class="type">{{ item.item_type }}</span>
            <span class="name">{{ item.name }}</span>
            <span class="qty">x{{ item.quantity }}</span>
          </div>
        </div>
      </div>

      <!-- イベント -->
      <div v-if="events.length > 0" class="info-box events">
        <h4>イベント</h4>
        <div class="event-list">
          <div v-for="event in events" :key="event.id" class="event-item">
            {{ event.description }}
          </div>
        </div>
      </div>

      <button class="close-btn" @click="emit('close')">
        閉じる
      </button>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 12px;
  padding: 20px;
  max-width: 450px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

h3 {
  margin: 0 0 20px 0;
  text-align: center;
  color: #2c3e50;
}

h4 {
  margin: 0 0 10px 0;
  color: #7f8c8d;
}

.info-box {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
}

.info-box.salary {
  background: #eafaf1;
}

.info-box.bonus {
  background: #fef9e7;
}

.info-box.deliveries {
  background: #ebf5fb;
}

.salary-details {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.row {
  display: flex;
  justify-content: space-between;
}

.row.deduction {
  color: #e74c3c;
}

.row.total {
  font-weight: bold;
  font-size: 1.1em;
  border-top: 1px solid #ddd;
  padding-top: 5px;
  margin-top: 5px;
}

.bonus-amount {
  font-size: 1.5em;
  font-weight: bold;
  color: #f39c12;
  text-align: center;
}

.delivery-list, .event-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.delivery-item {
  display: flex;
  gap: 10px;
  padding: 8px;
  background: white;
  border-radius: 4px;
}

.delivery-item .type {
  color: #95a5a6;
  font-size: 0.85em;
}

.delivery-item .name {
  font-weight: bold;
}

.delivery-item .qty {
  margin-left: auto;
  color: #3498db;
}

.event-item {
  padding: 10px;
  background: white;
  border-radius: 4px;
  border-left: 3px solid #9b59b6;
}

.close-btn {
  width: 100%;
  padding: 12px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
  margin-top: 10px;
}
</style>
