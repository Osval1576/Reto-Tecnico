from rest_framework.routers import DefaultRouter

from .views import IncidenciaViewSet

router = DefaultRouter()
router.register('incidencias', IncidenciaViewSet, basename='incidencia')

urlpatterns = router.urls
