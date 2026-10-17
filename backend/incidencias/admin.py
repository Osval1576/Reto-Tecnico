from django.contrib import admin

from .models import Incidencia


@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'prioridad', 'estado', 'creada_en']
    list_filter = ['estado', 'prioridad']
    search_fields = ['titulo', 'descripcion']
