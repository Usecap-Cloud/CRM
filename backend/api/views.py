from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser
import pandas as pd
import datetime
from .models import (
    Rol, Ejecutivo, Cliente, Coordinador, Servicio,
    Proveedor, Curso, Contrato, ContratoCurso,
    ContratoServicio, ContratoProveedor,Seguimiento, ImportHistory
)
from django.http import HttpResponse
import io
from .serializers import (
    RolSerializer, EjecutivoSerializer, ClienteSerializer, CoordinadorSerializer,
    ServicioSerializer, ProveedorSerializer, CursoSerializer, ContratoSerializer,
    ContratoCursoSerializer, ContratoServicioSerializer, ContratoProveedorSerializer, SeguimientoSerializer
)
from django.contrib.auth.models import User

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
            "cursos_proceso": Curso.objects.filter(estado__iexact='en proceso').count(),
            "contratos_cerrar": Contrato.objects.filter(estado__iexact='por cerrar').count(),
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
            contratos = Contrato.objects.filter(ejecutivo=ej)
            contratos_firmados = contratos.filter(estado='Firmado').count()
            
            data.append({
                'ejecutivo_id': ej.id,
                'ejecutivo_nombre': ej.nombre,
                'ejecutivo_email': ej.email,
                'total_clientes': clientes.count(),
                'total_contratos': contratos.count(),
                'contratos_firmados': contratos_firmados,
                'clientes': [
                    {
                        'id': c.id,
                        'rut': c.rut_empresa,
                        'razon_social': c.razon_social,
                        'estado': c.estado
                    } for c in clientes
                ]
            })
        return Response(data)

def normalize_col(text):
    import unicodedata
    if not text: return ""
    text = str(text).lower().strip()
    text = "".join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    return text.replace(".", "").replace("_", "").replace(" ", "").replace("-", "")

class UniversalImportView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        file_obj = request.FILES.get('file')
        model_type = request.data.get('model_type', 'cliente') 
        
        if not file_obj:
            return Response({"error": "No se subio ningun archivo"}, status=400)
        
        try:
            df = pd.read_excel(file_obj)
            
            # Map columns fuzzily
            mapping = {}
            for col in df.columns:
                norm = normalize_col(col)
                # Main ID (RUT) logic
                if norm == 'rut': mapping['rut'] = col
                elif model_type == 'cliente' and norm in ['rutempresa', 'empresarut']: mapping['rut'] = col
                elif model_type == 'ejecutivo' and norm in ['rutejecutivo', 'ejecutivorut']: mapping['rut'] = col
                elif norm in ['id', 'cedula'] and 'rut' not in mapping: mapping['rut'] = col
                
                # Relationship logic
                if model_type == 'cliente' and norm in ['rutejecutivo', 'ejecutivorut', 'ejecutivo', 'asignadoa']:
                    mapping['ejecutivo_rut'] = col
                
                # Common fields
                if norm in ['razonsocial', 'empresa', 'razon']: mapping['razon_social'] = col
                elif norm in ['nombre', 'nom', 'nombrecompleto']: mapping['nombre'] = col
                elif norm in ['email', 'correo', 'mail']: mapping['email'] = col
                elif norm in ['telefono', 'fono', 'celular', 'phone', 'tel']: mapping['telefono'] = col
                elif norm in ['estado', 'status', 'estadocliente', 'estadoejecutivo']: mapping['estado'] = col
                elif norm in ['codigo', 'code', 'cod']: mapping['codigo'] = col
                elif norm in ['rubro', 'especialidad', 'sector']: mapping['rubro'] = col
                elif norm in ['contacto', 'personacontacto', 'nombrecontacto']: mapping['nombre_contacto'] = col
                
                # Contract specific mapping
                elif norm in ['tiporegistro', 'tipo']: mapping['tipo_registro'] = col
                elif norm in ['fecharecepcion', 'recepcion']: mapping['fecha_recepcion'] = col
                elif norm in ['fechaemision', 'emision']: mapping['fecha_emision'] = col
                elif norm in ['rutcliente', 'clienterut', 'rutempresa', 'razonsocial']: mapping['cliente_rut'] = col
                elif norm in ['rutcoordinador', 'coordinadorrut', 'coordinador']: mapping['coordinador_rut'] = col
                elif norm in ['fechainicio', 'iniciocontrato', 'fecinicio']: mapping['fecha_inicio'] = col
                elif norm in ['subtotal', 'neto', 'valorneto', 'monto']: mapping['subtotal'] = col
                elif norm in ['direccion', 'dir', 'calle']: mapping['direccion'] = col
                elif norm == 'comuna': mapping['comuna'] = col
                elif norm == 'region': mapping['region'] = col
                elif norm in ['sectorindustria', 'sector']: mapping['sector_industria'] = col
                elif norm in ['origenreferencia', 'origen']: mapping['origen_referencia'] = col
                elif norm in ['areadepartamento', 'area', 'departamento']: mapping['area'] = col
                elif norm in ['especialidadtipoclientes', 'especialidad']: mapping['especialidad'] = col
                elif norm in ['observaciones', 'obs', 'comentarios']: mapping['observaciones'] = col
                elif norm in ['rol', 'idrol', 'rolnombre']: mapping['rol'] = col

            created_count = 0
            errors = []
            
            default_ejecutivo = Ejecutivo.objects.first()
            default_rol = Rol.objects.first()

            # Check for mandatory columns depending on model
            mandatory = []
            if model_type == 'cliente': mandatory = ['rut']
            elif model_type == 'curso': mandatory = ['nombre']
            elif model_type == 'proveedor': mandatory = ['rut']
            elif model_type == 'ejecutivo': mandatory = ['rut']
            
            missing = [m for m in mandatory if m not in mapping]
            if missing:
                return Response({
                    "error": f"Columnas faltantes requeridas: {', '.join(missing)}",
                    "cols_detected": list(df.columns)
                }, status=400)

            for index, row in df.iterrows():
                try:
                    if model_type == 'cliente':
                        rut_val = row.get(mapping.get('rut'))
                        rut = str(rut_val).strip() if rut_val is not None else ""
                        if rut.endswith('.0'): rut = rut[:-2]
                        
                        if not rut or rut == 'nan' or Cliente.objects.filter(rut_empresa=rut).exists():
                            if rut and rut != 'nan':
                                errors.append(f"Fila {index + 2}: ya existe o RUT inválido ({rut})")
                            continue

                        rs_val = row.get(mapping.get('razon_social'))
                        razon_social = str(rs_val).strip() if rs_val is not None else ""
                        
                        nom_val = row.get(mapping.get('nombre'))
                        nombre = str(nom_val).strip() if nom_val is not None else ""
                        
                        if not razon_social or razon_social == 'nan':
                            razon_social = nombre if nombre and nombre != 'nan' else "Sin Razon Social"
                        if not nombre or nombre == 'nan':
                            nombre = razon_social

                        email_val = row.get(mapping.get('email'))
                        email = str(email_val).strip() if email_val is not None else ""
                        if not email or email == 'nan':
                            email = f"import_{rut.replace('.','').replace('-','')}@usecap.cl"
                        
                        ejecutivo_rut = row.get(mapping.get('ejecutivo_rut'))
                        ejecutivo = default_ejecutivo # Default to the first executive
                        if ejecutivo_rut:
                            ej_rut_str = str(ejecutivo_rut).strip()
                            if ej_rut_str.endswith('.0'): ej_rut_str = ej_rut_str[:-2]
                            found_ej = Ejecutivo.objects.filter(rut_ejecutivo=ej_rut_str).first()
                            if found_ej: ejecutivo = found_ej

                        Cliente.objects.create(
                            rut_empresa=rut,
                            razon_social=razon_social,
                            nombre=nombre,
                            email=email,
                            telefono=str(row.get(mapping.get('telefono'), '')).strip(),
                            estado=str(row.get(mapping.get('estado'), 'activo')).lower(),
                            direccion=str(row.get(mapping.get('direccion'), '')).strip(),
                            comuna=str(row.get(mapping.get('comuna'), '')).strip(),
                            region=str(row.get(mapping.get('region'), '')).strip(),
                            sector_industria=str(row.get(mapping.get('sector_industria'), '')).strip(),
                            origen_referencia=str(row.get(mapping.get('origen_referencia'), '')).strip(),
                            observaciones=str(row.get(mapping.get('observaciones'), '')).strip(),
                            ejecutivo=ejecutivo
                        )
                        created_count += 1
                    elif model_type == 'ejecutivo':
                        rut_val = row.get(mapping.get('rut'))
                        rut = str(rut_val).strip() if rut_val is not None else ""
                        if rut.endswith('.0'): rut = rut[:-2]
                        if not rut or rut == 'nan' or Ejecutivo.objects.filter(rut_ejecutivo=rut).exists(): continue

                        rol = default_rol
                        rol_val = row.get(mapping.get('rol'))
                        if rol_val:
                            found_rol = Rol.objects.filter(nombre__iexact=str(rol_val).strip()).first()
                            if found_rol: rol = found_rol

                        # Handle User creation
                        user_email = str(row.get(mapping.get('email'), f"ej_{rut.replace('-','')}@usecap.cl")).strip()
                        username = user_email.split('@')[0]
                        
                        is_admin = rol.nombre.lower() == "administrador"
                        
                        if not User.objects.filter(username=username).exists():
                            new_user = User.objects.create_user(
                                username=username,
                                email=user_email,
                                password=f"USECAP_{rut.split('-')[0]}",
                                is_staff=is_admin,
                                is_superuser=is_admin
                            )
                        else:
                            new_user = User.objects.get(username=username)
                            if is_admin:
                                new_user.is_staff = True
                                new_user.is_superuser = True
                                new_user.save()

                        Ejecutivo.objects.create(
                            user=new_user,
                            rut_ejecutivo=rut,
                            nombre=str(row.get(mapping.get('nombre'), 'Sin Nombre')).strip(),
                            email=user_email,
                            telefono=str(row.get(mapping.get('telefono'), '')).strip(),
                            estado=str(row.get(mapping.get('estado'), 'activo')).lower(),
                            area_departamento=str(row.get(mapping.get('area'), '')).strip(),
                            region=str(row.get(mapping.get('region'), '')).strip(),
                            comuna=str(row.get(mapping.get('comuna'), '')).strip(),
                            especialidad_tipo_clientes=str(row.get(mapping.get('especialidad'), '')).strip(),
                            observaciones=str(row.get(mapping.get('observaciones'), '')).strip(),
                            rol=rol
                        )
                        created_count += 1
                    elif model_type == 'proveedor':
                        rut_val = row.get(mapping.get('rut'))
                        rut = str(rut_val).strip() if rut_val is not None else ""
                        if rut.endswith('.0'): rut = rut[:-2]
                        if not rut or rut == 'nan': continue
                        
                        if Proveedor.objects.filter(rut_proveedor=rut).exists():
                            continue
                            
                        Proveedor.objects.create(
                            rut_proveedor=rut,
                            nombre=str(row.get(mapping.get('nombre'), 'Sin Nombre')).strip(),
                            contacto=str(row.get(mapping.get('nombre_contacto'), '')).strip(),
                            email=str(row.get(mapping.get('email'), '')).strip(),
                            telefono=str(row.get(mapping.get('telefono'), '')).strip(),
                            rubro=str(row.get(mapping.get('rubro'), '')).strip()
                        )
                        created_count += 1
                    elif model_type == 'coordinador':
                        rut_val = row.get(mapping.get('rut'))
                        rut = str(rut_val).strip() if rut_val is not None else ""
                        if rut.endswith('.0'): rut = rut[:-2]
                        if not rut or rut == 'nan': continue
                        
                        if Coordinador.objects.filter(rut_coordinador=rut).exists():
                            continue
                            
                        Coordinador.objects.create(
                            rut_coordinador=rut,
                            nombre=str(row.get(mapping.get('nombre'), 'Sin Nombre')).strip(),
                            email=str(row.get(mapping.get('email'), '')).strip(),
                            telefono=str(row.get(mapping.get('telefono'), '')).strip()
                        )
                        created_count += 1
                    elif model_type == 'curso':
                        nom_val = row.get(mapping.get('nombre'))
                        nombre = str(nom_val).strip() if nom_val is not None else ""
                        if not nombre or nombre == 'nan': continue
                        
                        cod_val = row.get(mapping.get('codigo'))
                        codigo = str(cod_val).strip() if cod_val is not None else f"CUR_{index}_{int(pd.Timestamp.now().timestamp())}"
                        
                        est_val = row.get(mapping.get('estado'))
                        estado = str(est_val).strip().lower() if est_val is not None else "activo"

                        Curso.objects.create(
                            codigo=codigo,
                            nombre=nombre,
                            estado=estado
                        )
                        created_count += 1
                    elif model_type == 'contrato':
                        rut_cli_val = row.get(mapping.get('cliente_rut'))
                        rut_cli = str(rut_cli_val).strip() if rut_cli_val is not None else ""
                        if rut_cli.endswith('.0'): rut_cli = rut_cli[:-2]
                        
                        cliente = Cliente.objects.filter(rut_empresa=rut_cli).first()
                        if not cliente:
                            # Try by razon social if RUT mapping failed or not found
                            rs_val = row.get(mapping.get('razon_social'))
                            if rs_val:
                                cliente = Cliente.objects.filter(razon_social__icontains=str(rs_val).strip()).first()
                        
                        if not cliente:
                            errors.append(f"Fila {index + 2}: Cliente no encontrado ({rut_cli})")
                            continue

                        ejecutivo = cliente.ejecutivo # Default to client's executive
                        ej_rut_val = row.get(mapping.get('ejecutivo_rut'))
                        if ej_rut_val:
                            ej_rut = str(ej_rut_val).strip()
                            if ej_rut.endswith('.0'): ej_rut = ej_rut[:-2]
                            found_ej = Ejecutivo.objects.filter(rut_ejecutivo=ej_rut).first()
                            if found_ej: ejecutivo = found_ej
                        
                        coordinador = None
                        coor_rut_val = row.get(mapping.get('coordinador_rut'))
                        if coor_rut_val:
                            coor_rut = str(coor_rut_val).strip()
                            if coor_rut.endswith('.0'): coor_rut = coor_rut[:-2]
                            coordinador = Coordinador.objects.filter(rut_coordinador=coor_rut).first()

                        # Date parsing
                        def parse_date(val):
                            if pd.isna(val) or not val: return None
                            try:
                                if isinstance(val, (pd.Timestamp, datetime.date)): return val
                                return pd.to_datetime(val).date()
                            except: return None

                        fecha_rec = parse_date(row.get(mapping.get('fecha_recepcion'))) or datetime.date.today()
                        fecha_emi = parse_date(row.get(mapping.get('fecha_emision'))) or datetime.date.today()
                        fecha_ini = parse_date(row.get(mapping.get('fecha_inicio'))) or fecha_rec

                        subtotal_val = row.get(mapping.get('subtotal'))
                        try:
                            subtotal = float(subtotal_val) if not pd.isna(subtotal_val) else 0
                        except:
                            subtotal = 0

                        Contrato.objects.create(
                            tipo_registro=str(row.get(mapping.get('tipo_registro'), 'Servicio')).strip(),
                            empresa=cliente.razon_social,
                            fecha_recepcion=fecha_rec,
                            fecha_emision=fecha_emi,
                            fecha_inicio=fecha_ini,
                            subtotal=subtotal,
                            estado=str(row.get(mapping.get('estado'), 'Por Cerrar')).strip(),
                            detalle=str(row.get(mapping.get('detalle'), '')).strip(),
                            observaciones=str(row.get(mapping.get('observaciones'), '')).strip(),
                            cliente=cliente,
                            ejecutivo=ejecutivo,
                            coordinador=coordinador
                        )
                        created_count += 1
                        # Success case for other models moved created_count here
                    elif model_type in ['cliente', 'ejecutivo', 'proveedor', 'coordinador']:
                         # These already have create logic above, they increment their own created_count
                         # Wait, I should move created_count inside each block to be safe.
                         # Actually I'll do it for all of them in a second pass if needed.
                         pass
                except Exception as e:
                    errors.append(f"Fila {index + 2}: {str(e)}")
            
            return Response({
                "message": f"Se procesaron {created_count} registros de tipo {model_type}",
                "errors": errors if len(errors) < 10 else errors[:10] + ["... y más"]
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
                    
                    if Cliente.objects.filter(rut_empresa=rut).exists():
                        errors.append(f"Fila {index + 2}: El RUT {rut} ya existe.")
                        continue
                    
                    if Cliente.objects.filter(email=email).exists():
                        email = f"import_{index}_{rut.replace('.','').replace('-','')}@usecap.cl"

                    Cliente.objects.create(
                        rut_empresa=rut,
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
    return render(request, 'proveedores.html')

def ejecutivos_view(request):
    from django.shortcuts import render
    return render(request, 'ejecutivos.html')

def seguimiento_view(request):
    from django.shortcuts import render
    return render(request, 'seguimiento.html')

class CreateEjecutivoAPIView(APIView):
    def post(self, request):
        try:
            data = request.data
            rut = data.get('rut')
            nombre = data.get('nombre')
            email = data.get('email')
            rol_id = data.get('rol')
            
            if not rut or not nombre or not email:
                return Response({"error": "Faltan campos obligatorios"}, status=400)
                
            rol = Rol.objects.get(id=rol_id) if rol_id else Rol.objects.first()
            is_admin = rol.nombre.lower() == "administrador" if rol else False

            # Check if executive already exists
            ejecutivo_instance = Ejecutivo.objects.filter(rut_ejecutivo=rut).first()
            
            if ejecutivo_instance:
                # Update existing executive
                user_instance = ejecutivo_instance.user
                if user_instance:
                    user_instance.email = email
                    user_instance.is_staff = is_admin
                    user_instance.is_superuser = is_admin
                    user_instance.save()

                ejecutivo_instance.nombre = nombre
                ejecutivo_instance.email = email
                ejecutivo_instance.telefono = data.get('telefono', ejecutivo_instance.telefono)
                ejecutivo_instance.estado = data.get('estado', ejecutivo_instance.estado)
                ejecutivo_instance.area_departamento = data.get('area', ejecutivo_instance.area_departamento)
                ejecutivo_instance.rol = rol
                ejecutivo_instance.save()
                message = "Ejecutivo actualizado correctamente"
                status_code = 200
            else:
                # Create new executive
                username = email.split('@')[0]
                if User.objects.filter(username=username).exists():
                    username = f"{username}_{rut.split('-')[0]}"
                    
                new_user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=f"USECAP_{rut.split('-')[0]}", # Default password
                    is_staff=is_admin,
                    is_superuser=is_admin
                )
                
                ejecutivo_instance = Ejecutivo.objects.create(
                    user=new_user,
                    rut_ejecutivo=rut,
                    nombre=nombre,
                    email=email,
                    telefono=data.get('telefono', ''),
                    estado=data.get('estado', 'activo'),
                    area_departamento=data.get('area', ''),
                    rol=rol
                )
                message = "Ejecutivo creado correctamente"
                status_code = 201
            
            return Response({"message": message, "username": ejecutivo_instance.user.username if ejecutivo_instance.user else ""}, status=status_code)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
