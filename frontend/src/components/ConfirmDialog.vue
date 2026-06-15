<script setup lang="ts">
const props = defineProps<{
  visible: boolean
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  type?: 'danger' | 'warning' | 'info'
}>()

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="visible" class="overlay" @click.self="emit('cancel')">
        <Transition name="scale">
          <div v-if="visible" class="dialog">
            <div class="dialog-icon">
              <span v-if="type === 'danger'">🗑️</span>
              <span v-else-if="type === 'warning'">⚠️</span>
              <span v-else>💬</span>
            </div>
            <h3 class="dialog-title">{{ title }}</h3>
            <p class="dialog-message">{{ message }}</p>
            <div class="dialog-actions">
              <button class="btn-cancel" @click="emit('cancel')">
                {{ cancelText || '取消' }}
              </button>
              <button
                class="btn-confirm"
                :class="{ danger: type === 'danger' }"
                @click="emit('confirm')"
              >
                {{ confirmText || '确认' }}
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(2px);
}

.dialog {
  background: var(--color-surface, #fff);
  border-radius: 1.25rem;
  padding: 2rem;
  max-width: 380px;
  width: 90%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  text-align: center;
}

.dialog-icon {
  font-size: 2.5rem;
  margin-bottom: 0.8rem;
}

.dialog-title {
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 0.6rem;
  color: #1e293b;
}

.dialog-message {
  font-size: 0.95rem;
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.dialog-actions {
  display: flex;
  gap: 0.8rem;
  justify-content: center;
}

.btn-cancel,
.btn-confirm {
  padding: 0.6rem 1.8rem;
  border: none;
  border-radius: 999px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: #f1f5f9;
  color: #64748b;
}

.btn-cancel:hover {
  background: #e2e8f0;
  color: #1e293b;
}

.btn-confirm {
  background: #3b82f6;
  color: #fff;
}

.btn-confirm:hover {
  background: #2563eb;
}

.btn-confirm.danger {
  background: #ef4444;
}

.btn-confirm.danger:hover {
  background: #dc2626;
}

/* 动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.scale-enter-active,
.scale-leave-active {
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.scale-enter-from,
.scale-leave-to {
  transform: scale(0.9);
  opacity: 0;
}
</style>
