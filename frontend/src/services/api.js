import axios from 'axios';

const api = axios.create({ baseURL: '/api' })

export const listarIncidencias = (filtros = {}) => 
    api.get('/incidencias/', { params: filtros }).then(response => response.data);

export const crearIncidencia = (datos) =>
    api.post('/incidencias/', datos).then(response => response.data);

export const cambiarEstado = (id, estado) =>
    api.patch(`/incidencias/${id}/`, { estado }).then(response => response.data);