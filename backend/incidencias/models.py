from django.db import models

class Incidencia(models.Models):
    class Prioridad(models.TextChoices):
        BAJA = "baja", "Baja"
        MEDIA = "media", "Media"
        ALTA = "alta", "Alta"

    class Estado(models.TextChoices):
        NUEVO ="nuevo","Nuevo"
        EN_PROCESO = "media", "Media"
        RESUELTO = "resuelto", "Resuelto"


    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    prioridad = models.CharField(max_length=10, choices= Prioridad.choices)
    estado = models.CharField(max_length=15, choices=Estado.choices, default= Estado.NUEVO)
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [-creada_en]

    def __str__(self):
        return self.titulo