from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RolViewSet, EjecutivoViewSet, ClienteViewSet, CoordinadorViewSet,
    ServicioViewSet, ProveedorViewSet, CursoViewSet, ContratoViewSet,
    ContratoCursoViewSet, ContratoServicioViewSet, ContratoProveedorViewSet, SeguimientoViewSet
)

router = DefaultRouter()
router.register(r'roles', RolViewSet)
router.register(r'ejecutivos', EjecutivoViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'coordinadores', CoordinadorViewSet)
router.register(r'servicios', ServicioViewSet)
router.register(r'proveedores', ProveedorViewSet)
router.register(r'cursos', CursoViewSet)
router.register(r'contratos', ContratoViewSet)
router.register(r'contratos-cursos', ContratoCursoViewSet)
router.register(r'contratos-servicios', ContratoServicioViewSet)
router.register(r'contratos-proveedores', ContratoProveedorViewSet)
router.register(r'seguimientos', SeguimientoViewSet)

from .views import DashboardStatsView, dashboard_view, PortfolioAPIView, portfolio_view, estadisticas_view, clientes_view, cursos_view, contratos_view

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard-stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('portfolio-data/', PortfolioAPIView.as_view(), name='portfolio-data'),
    path('portfolio/', portfolio_view, name='portfolio'),
    path('estadisticas/', estadisticas_view, name='estadisticas'),
    path('clientes-page/', clientes_view, name='clientes-page'),
    path('cursos-page/', cursos_view, name='cursos-page'),
    path('contratos-page/', contratos_view, name='contratos-page'),
]