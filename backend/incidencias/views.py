from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from .models import Incidencia
from .serializers import IncidenciaSerializer


class IncidenciaViewSet(viewsets.ModelViewSet):
    """
    GET    /api/incidencias/?estado=&prioridad=  lista (filtros opcionales)
    POST   /api/incidencias/                     registra una incidencia
    GET    /api/incidencias/<id>/                detalle
    PATCH  /api/incidencias/<id>/                cambia el estado (u otros campos)
    """

    serializer_class = IncidenciaSerializer
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    FILTROS = {
        'estado': Incidencia.Estado.values,
        'prioridad': Incidencia.Prioridad.values,
    }

    def get_queryset(self):
        queryset = Incidencia.objects.all()
        if self.action != 'list':
            return queryset

        errores = {}
        for campo, validos in self.FILTROS.items():
            valor = self.request.query_params.get(campo)
            if not valor:
                continue
            if valor not in validos:
                errores[campo] = f'Valor no válido. Opciones: {", ".join(validos)}.'
            else:
                queryset = queryset.filter(**{campo: valor})

        if errores:
            raise ValidationError(errores)
        return queryset
