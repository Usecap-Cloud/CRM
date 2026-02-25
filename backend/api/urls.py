from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RolViewSet, EjecutivoViewSet, ClienteViewSet, CoordinadorViewSet,
    ServicioViewSet, ProveedorViewSet, CursoViewSet, ContratoViewSet,
    ContratoCursoViewSet, ContratoProveedorViewSet, SeguimientoViewSet, ImportHistoryViewSet, AuditLogViewSet
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
router.register(r'contratos-proveedores', ContratoProveedorViewSet)
router.register(r'seguimientos', SeguimientoViewSet, basename='seguimiento')
router.register(r'import-history', ImportHistoryViewSet)
router.register(r'audit-logs', AuditLogViewSet)

from .views import (
    DashboardStatsView, dashboard_view, PortfolioAPIView, portfolio_view, 
    estadisticas_view, clientes_view, coordinadores_view,
    cursos_view, contratos_view, proveedores_view, servicios_view,
    importar_view, AnalyzeHeadersView, ProcessMappedImportView, UniversalImportView,
    ejecutivos_view, CreateEjecutivoAPIView, seguimiento_view, audit_log_view,
    SidebarAlertsView, ForceDataSyncView
)

urlpatterns = [
    path('force-data-sync/', ForceDataSyncView.as_view(), name='force-data-sync'),
    path('sidebar-alerts/', SidebarAlertsView.as_view(), name='sidebar-alerts'),
    path('importar-universal/', UniversalImportView.as_view(), name='importar-universal'),
    path('dashboard-stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('', include(router.urls)),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('portfolio-data/', PortfolioAPIView.as_view(), name='portfolio-data'),
    path('portfolio/', portfolio_view, name='portfolio'),
    path('estadisticas-page/', estadisticas_view, name='estadisticas'),
    path('estadisticas/', estadisticas_view, name='estadisticas-alias'),
    path('clientes-page/', clientes_view, name='clientes-page'),
    path('coordinadores-page/', coordinadores_view, name='coordinadores-page'),
    path('cursos-page/', cursos_view, name='cursos-page'),
    path('contratos-page/', contratos_view, name='contratos-page'),
    path('proveedores-page/', proveedores_view, name='proveedores-page'),
    path('servicios-page/', servicios_view, name='servicios-page'),
    path('seguimiento-page/', seguimiento_view, name='seguimiento-page'),
    path('importar-page/', importar_view, name='importar-page'),
    path('ejecutivos-page/', ejecutivos_view, name='ejecutivos-page'),
    path('ejecutivos-create/', CreateEjecutivoAPIView.as_view(), name='ejecutivos-create'),
    path('importar-analizar/', AnalyzeHeadersView.as_view(), name='importar-analizar'),
    path('importar-procesar/', ProcessMappedImportView.as_view(), name='importar-procesar'),
    path('audit-log-page/', audit_log_view, name='audit-log-page'),
]