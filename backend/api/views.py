from django.shortcuts import render
from rest_framework import viewsets
from .models import (
    Rol, Ejecutivo, Cliente, Coordinador, Servicio,
    Proveedor, Curso, Contrato, ContratoCurso,
    ContratoServicio, ContratoProveedor,Seguimiento
)
from .serializers import (
    RolSerializer, EjecutivoSerializer, ClienteSerializer, CoordinadorSerializer,
    ServicioSerializer, ProveedorSerializer, CursoSerializer, ContratoSerializer,
    ContratoCursoSerializer, ContratoServicioSerializer, ContratoProveedorSerializer, SeguimientoSerializer
)

# Create your views here.

class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer

class EjecutivoViewSet(viewsets.ModelViewSet):
    queryset = Ejecutivo.objects.all()
    serializer_class = EjecutivoSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

class CoordinadorViewSet(viewsets.ModelViewSet):
    queryset = Coordinador.objects.all()
    serializer_class = CoordinadorSerializer

class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer

class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer

class CursoViewSet(viewsets.ModelViewSet):
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer

class ContratoViewSet(viewsets.ModelViewSet):
    queryset = Contrato.objects.all()
    serializer_class = ContratoSerializer

class ContratoCursoViewSet(viewsets.ModelViewSet):
    queryset = ContratoCurso.objects.all()
    serializer_class = ContratoCursoSerializer

class ContratoServicioViewSet(viewsets.ModelViewSet):
    queryset = ContratoServicio.objects.all()
    serializer_class = ContratoServicioSerializer

class ContratoProveedorViewSet(viewsets.ModelViewSet):
    queryset = ContratoProveedor.objects.all()
    serializer_class = ContratoProveedorSerializer

class SeguimientoViewSet(viewsets.ModelViewSet):
    queryset = Seguimiento.objects.all()
    serializer_class = SeguimientoSerializer

from rest_framework.views import APIView
from rest_framework.response import Response

class DashboardStatsView(APIView):
    def get(self, request):
        stats = {
            "empresas_activas": Cliente.objects.count(),
            "cursos_proceso": Curso.objects.filter(estado='En Proceso').count(),
            "contratos_cerrar": Contrato.objects.filter(estado='Por Cerrar').count(),
        }
        return Response(stats)

def dashboard_view(request):
    from django.shortcuts import render
    return render(request, 'dashboard.html')

def home_view(request):
    from django.shortcuts import render
    return render(request, 'home.html')

class PortfolioAPIView(APIView):
    def get(self, request):
        ejecutivos = Ejecutivo.objects.all()
        data = []
        for ej in ejecutivos:
            clientes = Cliente.objects.filter(ejecutivo=ej)
            data.append({
                'ejecutivo_id': ej.id,
                'ejecutivo_nombre': ej.nombre,
                'ejecutivo_email': ej.email,
                'total_clientes': clientes.count(),
                'clientes': [
                    {
                        'id': c.id,
                        'rut': c.rut,
                        'razon_social': c.razon_social,
                        'estado': c.estado
                    } for c in clientes
                ]
            })
        return Response(data)

def portfolio_view(request):
    from django.shortcuts import render
    return render(request, 'portfolio.html')



