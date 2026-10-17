import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

import App from '../App.vue'
import { listarIncidencias, crearIncidencia, cambiarEstado } from '../services/api'

vi.mock('../services/api', () => ({
  listarIncidencias: vi.fn(),
  crearIncidencia: vi.fn(),
  cambiarEstado: vi.fn(),
}))

const INCIDENCIA = {
  id: 1,
  titulo: 'No carga el login',
  descripcion: 'Pantalla en blanco',
  prioridad: 'alta',
  estado: 'nuevo',
  creada_en: '2026-10-17T12:00:00Z',
}

async function montar() {
  const wrapper = mount(App)
  await flushPromises()
  return wrapper
}

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Copia nueva en cada llamada: App.vue muta el estado de la incidencia
    listarIncidencias.mockImplementation(async () => [{ ...INCIDENCIA }])
  })

  it('muestra las incidencias que devuelve la API', async () => {
    const wrapper = await montar()

    expect(listarIncidencias).toHaveBeenCalledWith({})
    expect(wrapper.text()).toContain('No carga el login')
    expect(wrapper.text()).toContain('Alta')
  })

  it('muestra un error si la API no responde', async () => {
    listarIncidencias.mockRejectedValue(new Error('Network Error'))

    const wrapper = await montar()

    expect(wrapper.text()).toContain('No se pudieron cargar las incidencias')
  })

  it('valida los campos obligatorios antes de llamar a la API', async () => {
    const wrapper = await montar()

    await wrapper.find('form').trigger('submit')

    expect(crearIncidencia).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain('El título es obligatorio.')
    expect(wrapper.text()).toContain('La descripción es obligatoria.')
    expect(wrapper.text()).toContain('Selecciona una prioridad.')
  })

  it('registra una incidencia válida y recarga la lista', async () => {
    crearIncidencia.mockResolvedValue({ ...INCIDENCIA, id: 2 })
    const wrapper = await montar()

    await wrapper.find('input[type="text"]').setValue('  Error 500  ')
    await wrapper.find('textarea').setValue('Al guardar')
    await wrapper.find('form select').setValue('media')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(crearIncidencia).toHaveBeenCalledWith({
      titulo: 'Error 500',
      descripcion: 'Al guardar',
      prioridad: 'media',
    })
    expect(listarIncidencias).toHaveBeenCalledTimes(2)
    expect(wrapper.text()).toContain('Incidencia registrada.')
  })

  it('muestra los errores por campo que devuelve el backend', async () => {
    crearIncidencia.mockRejectedValue({
      response: { status: 400, data: { prioridad: ['Prioridad no válida.'] } },
    })
    const wrapper = await montar()

    await wrapper.find('input[type="text"]').setValue('X')
    await wrapper.find('textarea').setValue('Y')
    await wrapper.find('form select').setValue('baja')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('Prioridad no válida.')
  })

  it('filtra por estado', async () => {
    const wrapper = await montar()

    await wrapper.find('.filtros select').setValue('en_proceso')
    await flushPromises()

    expect(listarIncidencias).toHaveBeenLastCalledWith({ estado: 'en_proceso' })
  })

  it('cambia el estado de una incidencia', async () => {
    cambiarEstado.mockResolvedValue({ ...INCIDENCIA, estado: 'resuelto' })
    const wrapper = await montar()

    await wrapper.find('.incidencia select').setValue('resuelto')
    await flushPromises()

    expect(cambiarEstado).toHaveBeenCalledWith(1, 'resuelto')
  })

  it('revierte el estado si la API falla', async () => {
    cambiarEstado.mockRejectedValue(new Error('500'))
    const wrapper = await montar()

    await wrapper.find('.incidencia select').setValue('resuelto')
    await flushPromises()

    expect(wrapper.find('.incidencia select').element.value).toBe('nuevo')
    expect(wrapper.text()).toContain('No se pudo cambiar el estado.')
  })
})
