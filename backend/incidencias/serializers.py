from rest_framework import serializers

from .models import Incidencia


class IncidenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incidencia
        fields = ['id', 'titulo', 'descripcion', 'prioridad', 'estado', 'creada_en', 'actualizada']
        read_only_fields = ['id', 'creada_en', 'actualizada']
        extra_kwargs = {
            'titulo': {
                'error_messages': {
                    'required': 'El título es obligatorio.',
                    'blank': 'El título es obligatorio.',
                    'max_length': 'Máximo 150 caracteres.',
                },
            },
            'descripcion': {
                'error_messages': {
                    'required': 'La descripción es obligatoria.',
                    'blank': 'La descripción es obligatoria.',
                },
            },
            'prioridad': {
                'error_messages': {
                    'required': 'Selecciona una prioridad.',
                    'blank': 'Selecciona una prioridad.',
                    'invalid_choice': 'Prioridad no válida.',
                },
            },
            'estado': {
                'error_messages': {
                    'invalid_choice': 'Estado no válido.',
                },
            },
        }

    def validate(self, attrs):
        # Una incidencia nueva siempre arranca en "nuevo"; el estado solo cambia después
        if self.instance is None:
            attrs['estado'] = Incidencia.Estado.NUEVO
        return attrs
