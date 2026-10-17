<script setup>
import { ref, reactive, onMounted } from 'vue'
import { listarIncidencias, crearIncidencia, cambiarEstado } from './services/api'
 
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
  return new Date(fecha).toLocaleString('es-MX')
}
 
onMounted(cargar)
</script>
 
<template>
  <main class="contenedor">
    <h1>Seguimiento de incidencias</h1>
 
    <p v-if="errorGeneral" class="alerta error">{{ errorGeneral }}</p>
    <p v-if="mensajeExito" class="alerta exito">{{ mensajeExito }}</p>
 
    <!-- Formulario -->
    <section class="tarjeta">
      <h2>Registrar incidencia</h2>
      <form @submit.prevent="registrar" novalidate>
        <label>
          Título
          <input v-model="formulario.titulo" type="text" maxlength="150" />
          <span v-if="erroresForm.titulo" class="error-campo">{{ erroresForm.titulo }}</span>
        </label>
 
        <label>
          Descripción
          <textarea v-model="formulario.descripcion" rows="3"></textarea>
          <span v-if="erroresForm.descripcion" class="error-campo">{{ erroresForm.descripcion }}</span>
        </label>
 
        <label>
          Prioridad
          <select v-model="formulario.prioridad">
            <option value="">Selecciona…</option>
            <option v-for="p in PRIORIDADES" :key="p.valor" :value="p.valor">{{ p.texto }}</option>
          </select>
          <span v-if="erroresForm.prioridad" class="error-campo">{{ erroresForm.prioridad }}</span>
        </label>
 
        <button type="submit">Registrar</button>
      </form>
    </section>
 
    <!-- Filtros -->
    <section class="tarjeta filtros">
      <label>
        Estado
        <select v-model="filtros.estado" @change="cargar">
          <option value="">Todos</option>
          <option v-for="e in ESTADOS" :key="e.valor" :value="e.valor">{{ e.texto }}</option>
        </select>
      </label>
      <label>
        Prioridad
        <select v-model="filtros.prioridad" @change="cargar">
          <option value="">Todas</option>
          <option v-for="p in PRIORIDADES" :key="p.valor" :value="p.valor">{{ p.texto }}</option>
        </select>
      </label>
      <button type="button" class="secundario" @click="limpiarFiltros">Limpiar</button>
    </section>
 
    <!-- Lista -->
    <section>
      <p v-if="cargando">Cargando…</p>
      <p v-else-if="incidencias.length === 0">No hay incidencias con esos filtros.</p>
 
      <article v-for="inc in incidencias" :key="inc.id" class="tarjeta incidencia">
        <div class="encabezado">
          <h3>{{ inc.titulo }}</h3>
          <span :class="['etiqueta', inc.prioridad]">{{ textoDe(PRIORIDADES, inc.prioridad) }}</span>
        </div>
        <p>{{ inc.descripcion }}</p>
        <div class="pie">
          <small>{{ formatearFecha(inc.creada_en) }}</small>
          <select :value="inc.estado" @change="actualizarEstado(inc, $event.target.value)">
            <option v-for="e in ESTADOS" :key="e.valor" :value="e.valor">{{ e.texto }}</option>
          </select>
        </div>
      </article>
    </section>
  </main>
</template>
 
<style scoped>
.contenedor { max-width: 760px; margin: 0 auto; padding: 16px; font-family: system-ui, sans-serif; }
h1 { margin-bottom: 16px; }
.tarjeta { border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin-bottom: 16px; background: #fff; }
form, label { display: flex; flex-direction: column; gap: 6px; }
form { gap: 12px; }
input, textarea, select { padding: 8px; border: 1px solid #ccc; border-radius: 6px; font: inherit; }
button { padding: 8px 14px; border: none; border-radius: 6px; background: #2563eb; color: #fff; cursor: pointer; }
button.secundario { background: #6b7280; }
.filtros { display: flex; gap: 12px; align-items: flex-end; flex-wrap: wrap; }
.error-campo { color: #b91c1c; font-size: 0.85rem; }
.alerta { padding: 10px; border-radius: 6px; }
.alerta.error { background: #fee2e2; color: #991b1b; }
.alerta.exito { background: #dcfce7; color: #166534; }
.encabezado, .pie { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.encabezado h3 { margin: 0; }
.etiqueta { padding: 2px 10px; border-radius: 999px; font-size: 0.8rem; }
.etiqueta.baja { background: #e0f2fe; color: #075985; }
.etiqueta.media { background: #fef9c3; color: #854d0e; }
.etiqueta.alta { background: #fee2e2; color: #991b1b; }
</style>
 