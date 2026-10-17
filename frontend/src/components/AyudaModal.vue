<script setup>
import { ref, watch, nextTick, onBeforeUnmount } from 'vue'

const props = defineProps({ abierta: { type: Boolean, default: false } })
const emit = defineEmits(['cerrar'])

const PASOS = [
  {
    icono: 'ti-file-plus',
    titulo: 'Registra una incidencia',
    texto: 'Escribe un título, describe el problema, elige la prioridad (alta, media o baja) y presiona Registrar. Toda incidencia empieza en estado Nuevo.',
  },
  {
    icono: 'ti-progress-check',
    titulo: 'Actualiza su estado',
    texto: 'En la lista, toca la etiqueta de estado de cada incidencia para moverla de Nuevo a En proceso y después a Resuelto.',
  },
  {
    icono: 'ti-filter',
    titulo: 'Filtra la lista',
    texto: 'Usa los filtros de Estado y Prioridad para ver solo lo que te interesa. Limpiar vuelve a mostrar todas.',
  },
]

const botonCerrar = ref(null)
let focoPrevio = null

function onKeydown(e) {
  if (e.key === 'Escape') emit('cerrar')
}

watch(
  () => props.abierta,
  async (abierta) => {
    if (abierta) {
      focoPrevio = document.activeElement
      document.addEventListener('keydown', onKeydown)
      await nextTick()
      botonCerrar.value?.focus()
    } else {
      document.removeEventListener('keydown', onKeydown)
      focoPrevio?.focus?.()
    }
  },
  { immediate: true },
)

onBeforeUnmount(() => document.removeEventListener('keydown', onKeydown))
</script>

<template>
  <Transition name="modal">
    <div v-if="abierta" class="modal-backdrop" @click.self="emit('cerrar')">
      <div class="modal ayuda" role="dialog" aria-modal="true" aria-labelledby="ayuda-titulo">
        <header class="modal-header">
          <h2 id="ayuda-titulo" class="modal-title">
            <i class="ti ti-help-circle" aria-hidden="true"></i>Cómo usar la app
          </h2>
          <button type="button" class="modal-close" aria-label="Cerrar ayuda" @click="emit('cerrar')">
            <i class="ti ti-x" aria-hidden="true"></i>
          </button>
        </header>

        <ol class="pasos">
          <li v-for="(paso, i) in PASOS" :key="paso.titulo" class="paso">
            <span class="paso-icono"><i :class="['ti', paso.icono]" aria-hidden="true"></i></span>
            <div>
              <p class="paso-titulo"><span class="paso-num">{{ i + 1 }}.</span> {{ paso.titulo }}</p>
              <p class="paso-texto">{{ paso.texto }}</p>
            </div>
          </li>
        </ol>

        <footer class="modal-actions">
          <p class="nota">
            Vuelve a abrir esta ayuda con el botón <i class="ti ti-help" aria-hidden="true"></i> de arriba.
          </p>
          <button ref="botonCerrar" type="button" class="btn-submit" @click="emit('cerrar')">Entendido</button>
        </footer>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
/* Modal basado en ClientDashboard de AllSafe */
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  background: rgba(0,0,0,.4);
  backdrop-filter: blur(2px);
}
.modal {
  width: 100%;
  max-width: 480px;
  max-height: calc(100vh - 32px);
  overflow-y: auto;
  background: var(--surface);
  border: 0.5px solid var(--border);
  border-radius: var(--r-lg);
  box-shadow: var(--shadow-md);
}
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px 14px;
  border-bottom: 0.5px solid var(--border);
}
.modal-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
}
.modal-title i { font-size: 18px; color: var(--accent); }
.modal-close {
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  border-radius: var(--r-sm);
  color: var(--text-3);
  transition: background .15s, color .15s;
}
.modal-close:hover { background: var(--surface-2); color: var(--text); }

.pasos { list-style: none; padding: 16px 20px; display: flex; flex-direction: column; gap: 14px; }
.paso { display: flex; gap: 12px; align-items: flex-start; }
.paso-icono {
  width: 34px;
  height: 34px;
  flex-shrink: 0;
  display: grid;
  place-items: center;
  border-radius: var(--r-sm);
  background: var(--accent-light);
  color: var(--accent);
  font-size: 17px;
}
.paso-titulo { font-size: 13px; font-weight: 600; color: var(--text); }
.paso-num { font-family: var(--font-mono); color: var(--text-3); }
.paso-texto { font-size: 13px; color: var(--text-2); }

.modal-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
  padding: 14px 20px 18px;
  border-top: 0.5px solid var(--border);
}
.nota { font-size: 12px; color: var(--text-3); }
.nota i { vertical-align: -2px; }
.btn-submit {
  padding: 8px 20px;
  border-radius: var(--r-sm);
  background: var(--accent);
  color: var(--accent-fg);
  font-size: 13px;
  font-weight: 600;
  transition: background .15s;
}
.btn-submit:hover { background: var(--accent-hover); }
.btn-submit:focus-visible,
.modal-close:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

.modal-enter-active, .modal-leave-active { transition: opacity .2s; }
.modal-enter-active .modal, .modal-leave-active .modal { transition: transform .2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal, .modal-leave-to .modal { transform: scale(.96); }
</style>
