from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser
import pandas as pd
from .models import (
    Rol, Ejecutivo, Cliente, Coordinador, Servicio,
    Proveedor, Curso, Contrato, ContratoCurso,
    ContratoServicio, ContratoProveedor,Seguimiento, ImportHistory
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
    from django.shortcuts import render, redirect
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'dashboard.html')

def login_view(request):
    from django.shortcuts import render, redirect
    from django.contrib.auth import authenticate, login
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Usuario o contrasena incorrectos'})
    return render(request, 'login.html')

def logout_view(request):
    from django.shortcuts import redirect
    from django.contrib.auth import logout
    logout(request)
    return redirect('login')

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

class ImportarClientesExcelView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No se subio ningun archivo"}, status=400)
        
        try:
            df = pd.read_excel(file_obj)
            # Normalize column names to lowercase and strip whitespace
            df.columns = [str(col).lower().strip() for col in df.columns]
            
            # Get a default executive
            default_ejecutivo = Ejecutivo.objects.first()
            if not default_ejecutivo:
                return Response({"error": "No hay ejecutivos registrados en el sistema para asignar clientes."}, status=400)

            created_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Look for variations of names if possible
                    rut = str(row.get('rut', '')).strip()
                    razon_social = str(row.get('razon_social', '')).strip()
                    nombre = str(row.get('nombre', razon_social)).strip() # Use razon_social as default nombre
                    email = str(row.get('email', '')).strip()
                    estado = str(row.get('estado', 'activo')).strip().lower()
                    
                    if not rut or rut == 'nan' or not razon_social or razon_social == 'nan':
                        continue # Skip empty rows
                    
                    # Generate a dummy email if empty, as it's required and unique
                    if not email or email == 'nan':
                        email = f"import_{rut.replace('.','').replace('-','')}@usecap.cl"
                    
                    if Cliente.objects.filter(rut=rut).exists():
                        errors.append(f"Fila {index + 2}: Cliente con RUT {rut} ya existe")
                        continue
                    
                    if Cliente.objects.filter(email=email).exists():
                         # If email exists but RUT is different, we must change email or skip
                        email = f"import_{index}_{rut.replace('.','').replace('-','')}@usecap.cl"
                        
                    Cliente.objects.create(
                        rut=rut,
                        razon_social=razon_social,
                        nombre=nombre,
                        email=email,
                        estado=estado,
                        ejecutivo=default_ejecutivo
                    )
                    created_count += 1
                except Exception as e:
                    errors.append(f"Fila {index + 2}: {str(e)}")
            
            return Response({
                "message": f"Se crearon {created_count} clientes exitosamente",
                "errors": errors
            })
            
        except Exception as e:
            return Response({"error": f"Error al procesar el archivo: {str(e)}"}, status=500)

class AnalyzeHeadersView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No se subio ningun archivo"}, status=400)
        
        try:
            # Read first row only for speed
            df = pd.read_excel(file_obj, nrows=0)
            headers = [str(col) for col in df.columns]
            return Response({"headers": headers})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class ProcessMappedImportView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        file_obj = request.FILES.get('file')
        mapping_str = request.data.get('mapping')
        
        if not file_obj or not mapping_str:
            return Response({"error": "Falta el archivo o el mapeo"}, status=400)
        
        try:
            import json
            mapping = json.loads(mapping_str)
            df = pd.read_excel(file_obj)
            
            # Map columns
            # matching: { "rut": "RUT_Empresa", "razon_social": "Nombre_Empresa", ... }
            
            default_ejecutivo = Ejecutivo.objects.first()
            if not default_ejecutivo:
                return Response({"error": "No hay ejecutivos registrados"}, status=400)

            created_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    data = {}
                    # Required fields and their mapping
                    rut_col = mapping.get('rut')
                    razon_social_col = mapping.get('razon_social')
                    
                    if not rut_col or not razon_social_col:
                        continue
                        
                    rut = str(row.get(rut_col, '')).strip()
                    razon_social = str(row.get(razon_social_col, '')).strip()
                    
                    if not rut or rut == 'nan' or not razon_social or razon_social == 'nan':
                        continue
                        
                    # Optional fields
                    email_col = mapping.get('email')
                    nombre_col = mapping.get('nombre')
                    estado_col = mapping.get('estado')
                    
                    email = str(row.get(email_col, '')) if email_col else ""
                    nombre = str(row.get(nombre_col, razon_social)) if nombre_col else razon_social
                    estado = str(row.get(estado_col, 'activo')).lower() if estado_col else "activo"
                    
                    if not email or email == 'nan':
                        email = f"import_{rut.replace('.','').replace('-','')}@usecap.cl"
                    
                    if Cliente.objects.filter(rut=rut).exists():
                        errors.append(f"Fila {index + 2}: duplicado RUT {rut}")
                        continue
                    
                    if Cliente.objects.filter(email=email).exists():
                        email = f"import_{index}_{rut.replace('.','').replace('-','')}@usecap.cl"

                    Cliente.objects.create(
                        rut=rut,
                        razon_social=razon_social,
                        nombre=nombre,
                        email=email,
                        estado=estado,
                        ejecutivo=default_ejecutivo
                    )
                    created_count += 1
                except Exception as e:
                    errors.append(f"Fila {index + 2}: {str(e)}")
            
            # Save to history
            ImportHistory.objects.create(
                nombre_archivo=file_obj.name,
                filas_processed=created_count,
                estado='exito' if created_count > 0 else 'error',
                mensaje_error="; ".join(errors[:5]) if errors else None
            )
            
            return Response({
                "message": f"Se procesaron {created_count} clientes",
                "errors": errors
            })
            
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class ImportHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    from .serializers import ImportHistorySerializer
    queryset = ImportHistory.objects.all().order_by('-fecha')
    serializer_class = ImportHistorySerializer

def importar_view(request):
    from django.shortcuts import render
    return render(request, 'importar.html')

def portfolio_view(request):
    from django.shortcuts import render
    return render(request, 'portfolio.html')

def estadisticas_view(request):
    from django.shortcuts import render
    return render(request, 'estadisticas.html')

def clientes_view(request):
    from django.shortcuts import render
    return render(request, 'clientes.html')

def cursos_view(request):
    from django.shortcuts import render
    return render(request, 'cursos.html')

def contratos_view(request):
    from django.shortcuts import render
    return render(request, 'contratos.html')

def proveedores_view(request):
    from django.shortcuts import render
    return render(request, 'proveedores.html')
