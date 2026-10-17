from rest_framework import status
from rest_framework.test import APITestCase

from .models import Incidencia

URL_LISTA = '/api/incidencias/'


def url_detalle(pk):
    return f'{URL_LISTA}{pk}/'


class CrearIncidenciaTests(APITestCase):
    def test_crea_incidencia_valida_con_estado_nuevo(self):
        datos = {'titulo': 'No carga el login', 'descripcion': 'Pantalla en blanco', 'prioridad': 'alta'}

        respuesta = self.client.post(URL_LISTA, datos, format='json')

        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(respuesta.data['estado'], 'nuevo')
        self.assertEqual(Incidencia.objects.count(), 1)

    def test_ignora_estado_enviado_al_crear(self):
        datos = {'titulo': 'X', 'descripcion': 'Y', 'prioridad': 'baja', 'estado': 'resuelto'}

        respuesta = self.client.post(URL_LISTA, datos, format='json')

        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(respuesta.data['estado'], 'nuevo')

    def test_rechaza_campos_obligatorios_faltantes(self):
        respuesta = self.client.post(URL_LISTA, {}, format='json')

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(set(respuesta.data), {'titulo', 'descripcion', 'prioridad'})

    def test_rechaza_campos_en_blanco(self):
        datos = {'titulo': '   ', 'descripcion': '', 'prioridad': 'media'}

        respuesta = self.client.post(URL_LISTA, datos, format='json')

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('titulo', respuesta.data)
        self.assertIn('descripcion', respuesta.data)

    def test_rechaza_prioridad_invalida(self):
        datos = {'titulo': 'X', 'descripcion': 'Y', 'prioridad': 'urgente'}

        respuesta = self.client.post(URL_LISTA, datos, format='json')

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('prioridad', respuesta.data)

    def test_rechaza_titulo_demasiado_largo(self):
        datos = {'titulo': 'a' * 151, 'descripcion': 'Y', 'prioridad': 'baja'}

        respuesta = self.client.post(URL_LISTA, datos, format='json')

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('titulo', respuesta.data)


class ListarYFiltrarTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        Incidencia.objects.create(titulo='A', descripcion='a', prioridad='alta', estado='nuevo')
        Incidencia.objects.create(titulo='B', descripcion='b', prioridad='baja', estado='en_proceso')
        Incidencia.objects.create(titulo='C', descripcion='c', prioridad='alta', estado='resuelto')

    def titulos(self, respuesta):
        return sorted(i['titulo'] for i in respuesta.data)

    def test_lista_todas(self):
        respuesta = self.client.get(URL_LISTA)

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(self.titulos(respuesta), ['A', 'B', 'C'])

    def test_filtra_por_estado(self):
        respuesta = self.client.get(URL_LISTA, {'estado': 'en_proceso'})

        self.assertEqual(self.titulos(respuesta), ['B'])

    def test_filtra_por_prioridad(self):
        respuesta = self.client.get(URL_LISTA, {'prioridad': 'alta'})

        self.assertEqual(self.titulos(respuesta), ['A', 'C'])

    def test_combina_filtros(self):
        respuesta = self.client.get(URL_LISTA, {'prioridad': 'alta', 'estado': 'resuelto'})

        self.assertEqual(self.titulos(respuesta), ['C'])

    def test_filtro_invalido_responde_400(self):
        respuesta = self.client.get(URL_LISTA, {'estado': 'cerrado'})

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('estado', respuesta.data)


class CambiarEstadoTests(APITestCase):
    def setUp(self):
        self.incidencia = Incidencia.objects.create(titulo='A', descripcion='a', prioridad='media')

    def test_cambia_estado(self):
        respuesta = self.client.patch(url_detalle(self.incidencia.pk), {'estado': 'en_proceso'}, format='json')

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.incidencia.refresh_from_db()
        self.assertEqual(self.incidencia.estado, 'en_proceso')

    def test_rechaza_estado_invalido(self):
        respuesta = self.client.patch(url_detalle(self.incidencia.pk), {'estado': 'cerrado'}, format='json')

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.incidencia.refresh_from_db()
        self.assertEqual(self.incidencia.estado, 'nuevo')

    def test_incidencia_inexistente_responde_404(self):
        respuesta = self.client.patch(url_detalle(9999), {'estado': 'resuelto'}, format='json')

        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_permite_borrar(self):
        respuesta = self.client.delete(url_detalle(self.incidencia.pk))

        self.assertEqual(respuesta.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
