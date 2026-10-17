<script setup>
import { ref, reactive, onMounted } from 'vue'
import { listarIncidencias, crearIncidencia, cambiarEstado } from './services/api'
import { useTheme } from './composables/useTheme'
import AyudaModal from './components/AyudaModal.vue'

// Opciones (deben coincidir con los TextChoices del modelo en Django)
const PRIORIDADES = [
  { valor: 'baja', texto: 'Baja' },
  { valor: 'media', texto: 'Media' },
  { valor: 'alta', texto: 'Alta' },
]
const ESTADOS = [
  { valor: 'nuevo', texto: 'Nuevo' },
  { valor: 'en_proceso', texto: 'En proceso' },
  { valor: 'resuelto', texto: 'Resuelto' },
]

const { isDark, toggle: cambiarTema } = useTheme()

// La ayuda se muestra cada vez que se entra a la app
const mostrarAyuda = ref(true)

// Estado de la pantalla
const incidencias = ref([])
const cargando = ref(false)
const errorGeneral = ref('')
const mensajeExito = ref('')

const formulario = reactive({ titulo: '', descripcion: '', prioridad: '' })
const erroresForm = reactive({})

const filtros = reactive({ estado: '', prioridad: '' })

// Cargar lista (con filtros)
async function cargar() {
  cargando.value = true
  errorGeneral.value = ''
  try {
    // Solo mando los filtros que tienen valor
    const params = {}
    if (filtros.estado) params.estado = filtros.estado
    if (filtros.prioridad) params.prioridad = filtros.prioridad

    // api.js ya devuelve response.data
    incidencias.value = await listarIncidencias(params)
  } catch (e) {
    errorGeneral.value = 'No se pudieron cargar las incidencias. ¿Está corriendo el backend?'
  } finally {
    cargando.value = false
  }
}

// Validación en el cliente (el backend vuelve a validar)
function validar() {
  Object.keys(erroresForm).forEach((k) => delete erroresForm[k])

  if (!formulario.titulo.trim()) erroresForm.titulo = 'El título es obligatorio.'
  else if (formulario.titulo.length > 150) erroresForm.titulo = 'Máximo 150 caracteres.'

  if (!formulario.descripcion.trim()) erroresForm.descripcion = 'La descripción es obligatoria.'

  if (!formulario.prioridad) erroresForm.prioridad = 'Selecciona una prioridad.'

  return Object.keys(erroresForm).length === 0
}

async function registrar() {
  mensajeExito.value = ''
  if (!validar()) return

  try {
    await crearIncidencia({
      titulo: formulario.titulo.trim(),
      descripcion: formulario.descripcion.trim(),
      prioridad: formulario.prioridad,
    })
    formulario.titulo = ''
    formulario.descripcion = ''
    formulario.prioridad = ''
    mensajeExito.value = 'Incidencia registrada.'
    await cargar()
  } catch (e) {
    // Si Django responde 400, muestro los errores que manda por campo
    if (e.response?.status === 400) {
      Object.entries(e.response.data).forEach(([campo, msgs]) => {
        erroresForm[campo] = Array.isArray(msgs) ? msgs.join(' ') : msgs
      })
    } else {
      errorGeneral.value = 'Error al registrar la incidencia.'
    }
  }
}

async function actualizarEstado(incidencia, nuevoEstado) {
  const anterior = incidencia.estado
  incidencia.estado = nuevoEstado // actualizo la vista de inmediato
  try {
    await cambiarEstado(incidencia.id, nuevoEstado)
    // Si hay filtro por estado, la incidencia puede dejar de aplicar
    if (filtros.estado) await cargar()
  } catch (e) {
    incidencia.estado = anterior // si falla, regreso al valor anterior
    errorGeneral.value = 'No se pudo cambiar el estado.'
  }
}

function limpiarFiltros() {
  filtros.estado = ''
  filtros.prioridad = ''
  cargar()
}

function textoDe(lista, valor) {
  return lista.find((o) => o.valor === valor)?.texto ?? valor
}

function formatearFecha(fecha) {
  return new Date(fecha).toLocaleString('es-MX', { dateStyle: 'medium', timeStyle: 'short' })
}

function folio(id) {
  return `#${String(id).padStart(4, '0')}`
}

onMounted(cargar)
</script>

<template>
  <div class="page">
    <header class="topbar">
      <div class="topbar-left">
        <span class="brand-mark">IN</span>
        <span class="brand-name">Incidencias</span>
        <span class="sep">›</span>
        <h1 class="page-title">Seguimiento de incidencias</h1>
      </div>
      <div class="topbar-right">
        <button type="button" class="tb-theme btn-ayuda" aria-label="Ver ayuda" @click="mostrarAyuda = true">
          <i class="ti ti-help" aria-hidden="true"></i>
        </button>
        <button
          type="button"
          class="tb-theme"
          :aria-label="isDark ? 'Modo claro' : 'Modo oscuro'"
          @click="cambiarTema"
        >
          <i :class="isDark ? 'ti ti-sun' : 'ti ti-moon'" aria-hidden="true"></i>
        </button>
      </div>
    </header>

    <AyudaModal :abierta="mostrarAyuda" @cerrar="mostrarAyuda = false" />

    <main class="content">
      <p v-if="errorGeneral" class="alerta alerta--error" role="alert">
        <i class="ti ti-alert-circle" aria-hidden="true"></i>{{ errorGeneral }}
      </p>
      <p v-if="mensajeExito" class="alerta alerta--exito" role="status">
        <i class="ti ti-circle-check" aria-hidden="true"></i>{{ mensajeExito }}
      </p>

      <div class="main-area">
        <!-- Formulario -->
        <section class="panel">
          <header class="panel-header">
            <h2 class="panel-title">Registrar incidencia</h2>
          </header>
          <form class="form" novalidate @submit.prevent="registrar">
            <label class="field">
              <span class="label">Título</span>
              <input
                v-model="formulario.titulo"
                type="text"
                maxlength="150"
                placeholder="Ej. No carga el inicio de sesión"
                :class="['input', { 'input--error': erroresForm.titulo }]"
              />
              <span v-if="erroresForm.titulo" class="error-campo">{{ erroresForm.titulo }}</span>
            </label>

            <label class="field">
              <span class="label">Descripción</span>
              <textarea
                v-model="formulario.descripcion"
                rows="4"
                placeholder="¿Qué pasó y cómo reproducirlo?"
                :class="['input', 'textarea', { 'input--error': erroresForm.descripcion }]"
              ></textarea>
              <span v-if="erroresForm.descripcion" class="error-campo">{{ erroresForm.descripcion }}</span>
            </label>

            <label class="field">
              <span class="label">Prioridad</span>
              <select
                v-model="formulario.prioridad"
                :class="['input', { 'input--error': erroresForm.prioridad }]"
              >
                <option value="">Selecciona…</option>
                <option v-for="p in PRIORIDADES" :key="p.valor" :value="p.valor">{{ p.texto }}</option>
              </select>
              <span v-if="erroresForm.prioridad" class="error-campo">{{ erroresForm.prioridad }}</span>
            </label>

            <button type="submit" class="btn-submit">
              <i class="ti ti-plus" aria-hidden="true"></i>Registrar
            </button>
          </form>
        </section>

        <!-- Lista con filtros -->
        <section class="panel">
          <div class="list-toolbar filtros">
            <label class="field field--inline">
              <span class="label">Estado</span>
              <select v-model="filtros.estado" class="input" @change="cargar">
                <option value="">Todos</option>
                <option v-for="e in ESTADOS" :key="e.valor" :value="e.valor">{{ e.texto }}</option>
              </select>
            </label>
            <label class="field field--inline">
              <span class="label">Prioridad</span>
              <select v-model="filtros.prioridad" class="input" @change="cargar">
                <option value="">Todas</option>
                <option v-for="p in PRIORIDADES" :key="p.valor" :value="p.valor">{{ p.texto }}</option>
              </select>
            </label>
            <button type="button" class="btn-secundario" @click="limpiarFiltros">Limpiar</button>
            <span class="contador">{{ incidencias.length }} {{ incidencias.length === 1 ? 'incidencia' : 'incidencias' }}</span>
          </div>

          <p v-if="cargando" class="list-state">Cargando…</p>
          <div v-else-if="incidencias.length === 0" class="list-state">
            <i class="ti ti-inbox empty-icon" aria-hidden="true"></i>
            <p>No hay incidencias con esos filtros.</p>
          </div>

          <article v-for="inc in incidencias" :key="inc.id" class="incidencia">
            <div class="incidencia-top">
              <span :class="['dot', `dot--${inc.prioridad}`]" aria-hidden="true"></span>
              <span class="folio">{{ folio(inc.id) }}</span>
              <span :class="['prioridad', `prioridad--${inc.prioridad}`]">{{ textoDe(PRIORIDADES, inc.prioridad) }}</span>
              <time class="fecha" :datetime="inc.creada_en">{{ formatearFecha(inc.creada_en) }}</time>
            </div>
            <h3 class="incidencia-titulo">{{ inc.titulo }}</h3>
            <p class="incidencia-desc">{{ inc.descripcion }}</p>
            <div class="incidencia-pie">
              <span class="estado-wrap">
                <select
                  :value="inc.estado"
                  :class="['estado', `estado--${inc.estado}`]"
                  aria-label="Cambiar estado"
                  @change="actualizarEstado(inc, $event.target.value)"
                >
                  <option v-for="e in ESTADOS" :key="e.valor" :value="e.valor">{{ e.texto }}</option>
                </select>
                <i class="ti ti-chevron-down" aria-hidden="true"></i>
              </span>
            </div>
          </article>
        </section>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* Layout y componentes basados en AllSafe (AppTopBar, ClientDashboard, StatusBadge, PriorityDot) */
.page { min-height: 100vh; display: flex; flex-direction: column; }

/* ─── Top bar ─── */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  height: 56px;
  padding: 0 20px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}
.topbar-left { display: flex; align-items: center; gap: 10px; min-width: 0; }
.brand-mark {
  width: 30px;
  height: 30px;
  flex-shrink: 0;
  display: grid;
  place-items: center;
  border-radius: 8px;
  background: var(--accent);
  color: var(--accent-fg);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .5px;
}
.brand-name { font-weight: 700; font-size: 15px; color: var(--text); }
.sep { color: var(--text-3); font-size: 18px; line-height: 1; }
.page-title {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 500;
  letter-spacing: -0.01em;
  color: var(--text-2);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.topbar-right { display: flex; align-items: center; gap: 8px; }
.tb-theme {
  width: 34px;
  height: 34px;
  flex-shrink: 0;
  display: grid;
  place-items: center;
  border: 0.5px solid var(--border);
  border-radius: var(--r-sm);
  color: var(--text-2);
  transition: background .15s, color .15s, border-color .15s;
}
.tb-theme:hover { background: var(--surface-2); color: var(--text); border-color: var(--text-3); }
.tb-theme i { font-size: 15px; }

/* ─── Contenido ─── */
.content {
  flex: 1;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 20px 32px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.main-area {
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: 12px;
  align-items: start;
}
.panel {
  background: var(--surface);
  border: 0.5px solid var(--border);
  border-radius: var(--r);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}
.panel-header { padding: 16px 20px 12px; border-bottom: 0.5px solid var(--border); }
.panel-title { font-family: var(--font-display); font-size: 15px; font-weight: 600; color: var(--text); }

/* ─── Alertas ─── */
.alerta {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 12px;
  border-radius: var(--r-sm);
  font-size: 13px;
}
.alerta i { font-size: 16px; }
.alerta--error { background: var(--c-urgent-bg); color: var(--c-urgent); }
.alerta--exito { background: var(--c-resolved-bg); color: var(--c-resolved); }

/* ─── Formulario ─── */
.form { padding: 20px; display: flex; flex-direction: column; gap: 14px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.label { font-size: 12px; font-weight: 600; color: var(--text-2); letter-spacing: .3px; }
.input {
  width: 100%;
  padding: 9px 12px;
  border: 0.5px solid var(--border);
  border-radius: var(--r-sm);
  background: var(--surface-2);
  color: var(--text);
  font-size: 13px;
  transition: border-color .15s;
}
.input:focus { border-color: var(--accent); outline: none; }
.input::placeholder { color: var(--text-3); }
.input--error { border-color: var(--c-urgent); }
.textarea { resize: vertical; }
.error-campo { font-size: 12px; color: var(--c-urgent); }
.btn-submit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 9px 20px;
  border-radius: var(--r-sm);
  background: var(--accent);
  color: var(--accent-fg);
  font-size: 13px;
  font-weight: 600;
  transition: background .15s;
}
.btn-submit:hover { background: var(--accent-hover); }
.btn-submit:focus-visible,
.btn-secundario:focus-visible,
.tb-theme:focus-visible,
.estado:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

/* ─── Lista ─── */
.list-toolbar {
  display: flex;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 8px 10px;
  padding: 12px 14px;
  border-bottom: 0.5px solid var(--border);
}
.field--inline { min-width: 140px; }
.field--inline .input { padding: 7px 10px; }
.btn-secundario {
  padding: 7px 14px;
  border-radius: var(--r-sm);
  background: var(--surface-2);
  border: 0.5px solid var(--border);
  color: var(--text-2);
  font-size: 13px;
  font-weight: 500;
  transition: background .15s;
}
.btn-secundario:hover { background: var(--border); }
.contador {
  margin-left: auto;
  align-self: center;
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: .5px;
  text-transform: uppercase;
  color: var(--text-3);
}
.list-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 40px 16px;
  color: var(--text-3);
  font-size: 13px;
  text-align: center;
}
.empty-icon { font-size: 36px; opacity: .4; }

.incidencia {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 14px 16px;
  border-bottom: 0.5px solid var(--border);
  transition: background .1s;
}
.incidencia:last-child { border-bottom: none; }
.incidencia:hover { background: var(--surface-2); }
.incidencia-top { display: flex; align-items: center; gap: 7px; }
.folio { font-family: var(--font-mono); font-size: 11px; font-weight: 600; color: var(--text-2); }
.fecha {
  margin-left: auto;
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: .5px;
  color: var(--text-3);
  white-space: nowrap;
}
.incidencia-titulo { font-size: 14px; font-weight: 600; color: var(--text); padding-left: 15px; overflow-wrap: anywhere; }
.incidencia-desc {
  font-size: 13px;
  color: var(--text-2);
  padding-left: 15px;
  overflow-wrap: anywhere;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.incidencia-pie { padding: 6px 0 0 15px; }

/* Prioridad (PriorityDot de AllSafe) */
.dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.dot--baja  { background: var(--c-low); }
.dot--media { background: var(--c-medium); }
.dot--alta  { background: var(--c-urgent); }
.prioridad {
  padding: 1px 7px;
  border-radius: 100px;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: .4px;
  text-transform: uppercase;
}
.prioridad--baja  { background: var(--c-low-bg);    color: var(--c-low); }
.prioridad--media { background: var(--c-medium-bg); color: var(--c-medium); }
.prioridad--alta  { background: var(--c-urgent-bg); color: var(--c-urgent); }

/* Estado: selector con apariencia de StatusBadge */
.estado-wrap { position: relative; display: inline-flex; align-items: center; }
.estado {
  appearance: none;
  padding: 4px 26px 4px 10px;
  border: 0.5px solid transparent;
  border-radius: 100px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: .4px;
  text-transform: uppercase;
  cursor: pointer;
  transition: border-color .15s;
}
.estado:hover { border-color: currentColor; }
.estado option { background: var(--surface); color: var(--text); text-transform: none; }
.estado-wrap i { position: absolute; right: 9px; font-size: 12px; pointer-events: none; }
.estado--nuevo       { background: var(--c-open-bg);     color: var(--c-open); }
.estado--en_proceso  { background: var(--c-progress-bg); color: var(--c-progress); }
.estado--resuelto    { background: var(--c-resolved-bg); color: var(--c-resolved); }
.estado-wrap:has(.estado--nuevo) i      { color: var(--c-open); }
.estado-wrap:has(.estado--en_proceso) i { color: var(--c-progress); }
.estado-wrap:has(.estado--resuelto) i   { color: var(--c-resolved); }

/* ─── Responsive ─── */
@media (max-width: 860px) {
  .main-area { grid-template-columns: 1fr; }
}
@media (max-width: 520px) {
  .topbar { padding: 0 16px; }
  .brand-name, .sep { display: none; }
  .content { padding: 12px 16px 24px; }
  .field--inline { flex: 1 1 120px; min-width: 0; }
  .contador { width: 100%; margin-left: 0; }
}
</style>
