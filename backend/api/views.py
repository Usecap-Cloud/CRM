from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response

import pandas as pd
import datetime
from .models import (
    Rol, Ejecutivo, Cliente, Coordinador, Servicio,
    Proveedor, Curso, Contrato, ContratoCurso,
    ContratoServicio, ContratoProveedor,Seguimiento, ImportHistory,
    AuditLog, normalize_rut_str
)
from django.http import HttpResponse
import io
from .serializers import (
    RolSerializer, EjecutivoSerializer, ClienteSerializer, CoordinadorSerializer,
    ServicioSerializer, ProveedorSerializer, CursoSerializer, ContratoSerializer,
    ContratoCursoSerializer, ContratoServicioSerializer, ContratoProveedorSerializer, SeguimientoSerializer, AuditLogSerializer
)

# Create your views here.

class AuditMixin:
    def perform_create(self, serializer):
        instance = serializer.save()
        AuditLog.objects.create(
            usuario=self.request.user if not self.request.user.is_anonymous else None,
            accion='CREAR',
            modelo=self.__class__.__name__.replace('ViewSet', ''),
            objeto_id=instance.id,
            objeto_repr=str(instance),
            detalle=f"Creado nuevo registro de {self.__class__.__name__.replace('ViewSet', '')}"
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        AuditLog.objects.create(
            usuario=self.request.user if not self.request.user.is_anonymous else None,
            accion='EDITAR',
            modelo=self.__class__.__name__.replace('ViewSet', ''),
            objeto_id=instance.id,
            objeto_repr=str(instance),
            detalle=f"Actualizado registro de {self.__class__.__name__.replace('ViewSet', '')}"
        )

    def perform_destroy(self, instance):
        AuditLog.objects.create(
            usuario=self.request.user if not self.request.user.is_anonymous else None,
            accion='ELIMINAR',
            modelo=self.__class__.__name__.replace('ViewSet', ''),
            objeto_id=instance.id,
            objeto_repr=str(instance),
            detalle=f"Eliminado registro de {self.__class__.__name__.replace('ViewSet', '')}"
        )
        instance.delete()

class RolViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer

class EjecutivoViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Ejecutivo.objects.all()
    serializer_class = EjecutivoSerializer

class ClienteViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

class CoordinadorViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Coordinador.objects.all()
    serializer_class = CoordinadorSerializer

class ServicioViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer

class ProveedorViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer

class CursoViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer

class ContratoViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Contrato.objects.all()
    serializer_class = ContratoSerializer

class ContratoCursoViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = ContratoCurso.objects.all()
    serializer_class = ContratoCursoSerializer

class ContratoServicioViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = ContratoServicio.objects.all()
    serializer_class = ContratoServicioSerializer

class ContratoProveedorViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = ContratoProveedor.objects.all()
    serializer_class = ContratoProveedorSerializer

class SeguimientoViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Seguimiento.objects.all()
    serializer_class = SeguimientoSerializer

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all().order_by('-fecha')
    serializer_class = AuditLogSerializer

class DashboardStatsView(APIView):
    def get(self, request):
        # Restricted access to Admin or Gerencia
        if not request.user.is_superuser:
            ej = getattr(request.user, 'ejecutivo', None)
            if not ej or ej.rol.nombre not in ['Administrador', 'Gerencia']:
                return Response({"error": "No tiene permisos para ver estadísticas"}, status=403)

        # Recent Activity (Seguimiento)
        recent_activity = []
        seguimientos = Seguimiento.objects.select_related('contrato__cliente').order_by('-fecha')[:5]
        for s in seguimientos:
            recent_activity.append({
                "id": s.id,
                "cliente": s.contrato.cliente.razon_social if s.contrato and s.contrato.cliente else "N/A",
                "tipo": s.tipo_seguimiento,
                "fecha": s.fecha,
                "estado": s.estado
            })

        # Agenda (Contracts expiring soon)
        agenda = []
        today = datetime.date.today()
        # Filter contracts that are active or 'por cerrar' and have a future expiration date
        contratos = Contrato.objects.filter(
            fecha_vencimiento__gte=today
        ).exclude(estado__iexact='finalizado').order_by('fecha_vencimiento')[:5]
        
        for c in contratos:
            agenda.append({
                "id": c.id,
                "titulo": c.empresa, # Using company name as title
                "fecha": c.fecha_vencimiento
            })

        stats = {
            "empresas_activas": Cliente.objects.count(),
            "cursos_proceso": Curso.objects.filter(estado__iexact='en proceso').count(),
            "contratos_cerrar": Contrato.objects.filter(estado__iexact='por cerrar').count(),
            "actividad_reciente": recent_activity,
            "agenda": agenda
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

def clean_val(val, default=""):
    import pandas as pd
    if pd.isna(val) or val is None:
        return default
    s = str(val).strip()
    if s.lower() == 'nan':
        return default
    if s.endswith('.0'):
        s = s[:-2]
    return s

def validate_rut_chile(rut):
    if not rut: return False
    rut_clean = str(rut).upper().replace(".", "").replace("-", "").replace(" ", "").strip()
    if len(rut_clean) < 2: return False
    cuerpo = rut_clean[:-1]
    dv = rut_clean[-1]
    if not cuerpo.isdigit(): return False
    suma = 0
    multiplo = 2
    for c in reversed(cuerpo):
        suma += int(c) * multiplo
        multiplo += 1
        if multiplo == 8: multiplo = 2
    dv_esperado = 11 - (suma % 11)
    if dv_esperado == 11: dv_calc = "0"
    elif dv_esperado == 10: dv_calc = "K"
    else: dv_calc = str(dv_esperado)
    return dv_calc == dv

def format_rut_chile(rut):
    return normalize_rut_str(rut)

class UniversalImportView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        file_obj = request.FILES.get('file')
        model_type = request.data.get('model_type', 'cliente') 
        
        if not file_obj:
            return Response({"error": "No se subio ningun archivo"}, status=400)

        AuditLog.objects.create(
            usuario=request.user if not request.user.is_anonymous else None,
            accion='IMPORTAR',
            modelo=model_type.capitalize(),
            objeto_id=0,
            objeto_repr=file_obj.name,
            detalle=f"Iniciada importación masiva de {model_type} desde archivo {file_obj.name}"
        )
        
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
                if model_type == 'cliente':
                    if norm in ['rutejecutivo', 'ejecutivorut', 'ejecutivo', 'asignadoa']:
                        mapping['ejecutivo_rut'] = col
                    elif norm in ['rutclientepadre', 'clientepadre', 'padre']:
                        mapping['cliente_padre_rut'] = col
                
                # Common fields
                if norm in ['razonsocial', 'empresa', 'razon']: mapping['razon_social'] = col
                elif norm in ['nombre', 'nom', 'nombrecompleto']: mapping['nombre'] = col
                elif norm in ['email', 'correo', 'mail']: mapping['email'] = col
                elif norm in ['telefono', 'fono', 'celular', 'phone', 'tel']: mapping['telefono'] = col
                elif norm in ['estado', 'status', 'estadocliente', 'estadoejecutivo']: mapping['estado'] = col
                elif norm in ['codigo', 'code', 'cod']: mapping['codigo'] = col
                elif norm in ['rubro', 'especialidad', 'sector', 'sectorindustria']: mapping['sector_industria'] = col
                elif norm in ['contacto', 'personacontacto', 'nombrecontacto']: mapping['nombre_contacto'] = col
                elif norm in ['direccion', 'address', 'dir']: mapping['direccion'] = col
                elif norm in ['region']: mapping['region'] = col
                elif norm in ['comuna']: mapping['comuna'] = col
                elif norm in ['origenreferencia', 'origen']: mapping['origen_referencia'] = col
                elif norm in ['fechainscripcion', 'fechacreacion', 'inscripcion', 'creacion']: mapping['fecha_creacion'] = col
                elif norm in ['rutejecutivo', 'ejecutivorut', 'rut_ejecutivo']: mapping['ejecutivo_rut'] = col
                
                # Contract specific mapping
                elif model_type == 'contrato' and norm in ['tiporegistro', 'tipo']: mapping['tipo_registro'] = col
                elif model_type == 'contrato' and norm in ['fecharecepcion', 'recepcion']: mapping['fecha_recepcion'] = col
                elif model_type == 'contrato' and norm in ['fechaemision', 'emision']: mapping['fecha_emision'] = col
                elif (model_type == 'contrato' or model_type == 'coordinador') and norm in ['rutcliente', 'clienterut', 'rutempresa', 'razonsocial']: mapping['cliente_rut'] = col
                elif model_type == 'contrato' and norm in ['rutcoordinador', 'coordinadorrut', 'coordinador']: mapping['coordinador_rut'] = col
                elif model_type == 'contrato' and norm in ['fechainicio', 'iniciocontrato', 'fecinicio']: mapping['fecha_inicio'] = col
                elif model_type == 'contrato' and norm in ['subtotal', 'neto', 'valorneto', 'monto']: mapping['subtotal'] = col
                elif model_type == 'contrato' and norm in ['sectorindustria', 'sector']: mapping['sector_industria'] = col
                elif model_type == 'contrato' and norm in ['origenreferencia', 'origen']: mapping['origen_referencia'] = col
                elif norm in ['areadepartamento', 'area', 'departamento']: mapping['area'] = col
                elif norm in ['especialidadtipoclientes', 'especialidad']: mapping['especialidad'] = col
                elif norm in ['observaciones', 'obs', 'comentarios']: mapping['observaciones'] = col
                elif norm in ['rol', 'idrol', 'rolnombre']: mapping['rol'] = col
                elif norm in ['rutcoordinador', 'rut_coordinador']: mapping['rut'] = col
                elif norm in ['fechacumpleanos', 'cumpleanos', 'fecha_cumpleanos']: mapping['fecha_cumpleanos'] = col
                elif norm in ['cargo', 'puesto', 'position']: mapping['cargo'] = col

            created_count = 0
            errors = []
            
            default_ejecutivo = Ejecutivo.objects.first()
            # Default to 'Ejecutivo Comercial' as requested
            default_rol = Rol.objects.filter(nombre__iexact='Ejecutivo Comercial').first() or \
                         Rol.objects.filter(id=2).first() or \
                         Rol.objects.first()

            # Check for mandatory columns depending on model
            mandatory = []
            if model_type == 'cliente': mandatory = ['rut']
            elif model_type == 'curso': mandatory = ['nombre']
            elif model_type == 'proveedor': mandatory = ['rut']
            elif model_type == 'ejecutivo': mandatory = ['rut']
            elif model_type == 'coordinador': mandatory = ['rut', 'cliente_rut']
            
            missing = [m for m in mandatory if m not in mapping]
            if missing:
                return Response({
                    "error": f"Columnas faltantes requeridas: {', '.join(missing)}",
                    "cols_detected": list(df.columns),
                    "mapping_debug": mapping
                }, status=400)

            for index, row in df.iterrows():
                try:
                    if model_type == 'cliente':
                        rut_raw = clean_val(row.get(mapping.get('rut')))
                        if not rut_raw:
                            continue
                        
                        if not validate_rut_chile(rut_raw):
                            errors.append(f"Fila {index + 2}: Ingrese su RUT con dígito verificador ({rut_raw})")
                            continue
                        
                        rut = format_rut_chile(rut_raw)
                        # Check exist with normalized RUT
                        if Cliente.objects.filter(rut_empresa=rut).exists():
                            errors.append(f"Fila {index + 2}: El cliente ya existe ({rut})")
                            continue

                        razon_social = clean_val(row.get(mapping.get('razon_social')))
                        if not razon_social:
                            nombre = clean_val(row.get(mapping.get('nombre')))
                            razon_social = nombre if nombre else "Sin Razon Social"
                        
                        # Find Ejecutivo
                        ejecutivo = default_ejecutivo
                        rut_ej_val = clean_val(row.get(mapping.get('ejecutivo_rut')))
                        if rut_ej_val:
                            ej_found = Ejecutivo.objects.filter(rut_ejecutivo=rut_ej_val).first()
                            if ej_found: ejecutivo = ej_found

                        # Date parsing for Cliente
                        def parse_date_custom(val):
                            if pd.isna(val) or not val: return None
                            try:
                                if isinstance(val, (pd.Timestamp, datetime.date)): return val
                                return pd.to_datetime(val, dayfirst=True).date()
                            except: return None

                        fecha_creacion = parse_date_custom(row.get(mapping.get('fecha_creacion')))
                        
                        # Find Cliente Padre
                        cliente_padre = None
                        rut_padre_raw = clean_val(row.get(mapping.get('cliente_padre_rut')))
                        if rut_padre_raw:
                            rut_padre_fmt = format_rut_chile(rut_padre_raw)
                            cliente_padre = Cliente.objects.filter(rut_empresa=rut_padre_fmt).first()

                        Cliente.objects.create(
                            rut_empresa=rut,
                            razon_social=razon_social,
                            estado=clean_val(row.get(mapping.get('estado')), 'activo').lower(),
                            sector_industria=clean_val(row.get(mapping.get('sector_industria'))),
                            direccion=clean_val(row.get(mapping.get('direccion')), "Sin Dirección"),
                            comuna=clean_val(row.get(mapping.get('comuna')), "Santiago"),
                            region=clean_val(row.get(mapping.get('region')), "RM"),
                            origen_referencia=clean_val(row.get(mapping.get('origen_referencia'))),
                            fecha_creacion=fecha_creacion,
                            observaciones=clean_val(row.get(mapping.get('observaciones'))),
                            ejecutivo=ejecutivo,
                            cliente_padre=cliente_padre
                        )
                        created_count += 1
                        
                    elif model_type == 'ejecutivo':
                        rut_raw = clean_val(row.get(mapping.get('rut')))
                        if not rut_raw:
                            continue
                            
                        if not validate_rut_chile(rut_raw):
                            errors.append(f"Fila {index + 2}: Ingrese su RUT con dígito verificador ({rut_raw})")
                            continue
                        
                        rut = format_rut_chile(rut_raw)
                        if Ejecutivo.objects.filter(rut_ejecutivo=rut).exists():
                            errors.append(f"Fila {index + 2}: El ejecutivo ya existe ({rut})")
                            continue
                        
                        rol = default_rol
                        rol_val = clean_val(row.get(mapping.get('rol')))
                        if rol_val:
                            found_rol = Rol.objects.filter(nombre__iexact=rol_val).first()
                            if found_rol: rol = found_rol

                        # Handle User creation
                        user_email = clean_val(row.get(mapping.get('email')), f"ej_{rut.replace('.','').replace('-','')}@usecap.cl")
                        username = user_email.split('@')[0]
                        
                        is_admin = rol.nombre.lower() == "administrador"
                        
                        if not User.objects.filter(username=username).exists():
                            # Clean RUT for password (numeric only)
                            pass_prefix = rut.split('-')[0].replace('.', '')
                            new_user = User.objects.create_user(
                                username=username,
                                email=user_email,
                                password=f"USECAP_{pass_prefix}",
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
                            nombre=clean_val(row.get(mapping.get('nombre')), 'Sin Nombre'),
                            email=user_email,
                            telefono=clean_val(row.get(mapping.get('telefono'))),
                            estado=clean_val(row.get(mapping.get('estado')), 'activo').lower(),
                            area_departamento=clean_val(row.get(mapping.get('area'))),
                            region=clean_val(row.get(mapping.get('region'))),
                            comuna=clean_val(row.get(mapping.get('comuna'))),
                            especialidad_tipo_clientes=clean_val(row.get(mapping.get('especialidad'))),
                            observaciones=clean_val(row.get(mapping.get('observaciones'))),
                            rol=rol
                        )
                        created_count += 1
                    elif model_type == 'proveedor':
                        rut_raw = clean_val(row.get(mapping.get('rut')))
                        if not rut_raw:
                            continue
                            
                        if not validate_rut_chile(rut_raw):
                            errors.append(f"Fila {index + 2}: Ingrese su RUT con dígito verificador ({rut_raw})")
                            continue
                        
                        rut = format_rut_chile(rut_raw)
                        if Proveedor.objects.filter(rut_proveedor=rut).exists():
                            errors.append(f"Fila {index + 2}: El proveedor ya existe ({rut})")
                            continue
                            
                        Proveedor.objects.create(
                            rut_proveedor=rut,
                            nombre=clean_val(row.get(mapping.get('nombre')), 'Sin Nombre'),
                            contacto=clean_val(row.get(mapping.get('nombre_contacto'))),
                            email=clean_val(row.get(mapping.get('email'))),
                            telefono=clean_val(row.get(mapping.get('telefono'))),
                            rubro=clean_val(row.get(mapping.get('rubro')))
                        )
                        created_count += 1
                    elif model_type == 'coordinador':
                        rut_val = row.get(mapping.get('rut'))
                        rut_raw = str(rut_val).strip() if rut_val is not None else ""
                        if rut_raw.endswith('.0'): rut_raw = rut_raw[:-2]
                        if not rut_raw or rut_raw == 'nan': 
                            continue
                        
                        if not validate_rut_chile(rut_raw):
                            errors.append(f"Fila {index + 2}: Ingrese su RUT con dígito verificador ({rut_raw})")
                            continue
                        
                        rut = format_rut_chile(rut_raw)
                        if Coordinador.objects.filter(rut_coordinador=rut).exists():
                            errors.append(f"Fila {index + 2}: El coordinador ya existe ({rut})")
                            continue

                        # Find Cliente
                        cliente = None
                        rut_cli_raw = row.get(mapping.get('cliente_rut'))
                        if rut_cli_raw:
                            rut_cli = format_rut_chile(clean_val(rut_cli_raw))
                            cliente = Cliente.objects.filter(rut_empresa=rut_cli).first()
                            
                            if not cliente:
                                # Try fuzzy/cleaner match if formatted failed
                                clean_cli = str(rut_cli_raw).upper().replace(".","").replace("-","").strip()
                                # We check if any existing client matches the clean version
                                for c in Cliente.objects.all():
                                    if c.rut_empresa.replace(".","").replace("-","").upper() == clean_cli:
                                        cliente = c
                                        break

                        # Validate Client Existence (Mandatory)
                        if not cliente:
                             errors.append(f"Fila {index + 2}: Cliente no encontrado (RUT: {rut_cli_raw})")
                             continue
                            
                        # Find Ejecutivo (Optional)
                        ejecutivo = None
                        rut_ej_raw = row.get(mapping.get('ejecutivo_rut'))
                        if rut_ej_raw:
                            rut_ej = format_rut_chile(clean_val(rut_ej_raw))
                            ejecutivo = Ejecutivo.objects.filter(rut_ejecutivo=rut_ej).first()

                        Coordinador.objects.create(
                            rut_coordinador=rut,
                            nombre=str(row.get(mapping.get('nombre'), 'Sin Nombre')).strip(),
                            email=str(row.get(mapping.get('email'), '')).strip(),
                            telefono=str(row.get(mapping.get('telefono'), '')).strip(),
                            cliente=cliente,
                            estado=str(row.get(mapping.get('estado'), 'activo')).lower(),
                            cargo=str(row.get(mapping.get('cargo'), '')).strip(),
                            fecha_cumpleanos=pd.to_datetime(row.get(mapping.get('fecha_cumpleanos'))).date() if not pd.isna(row.get(mapping.get('fecha_cumpleanos'))) else None,
                            ejecutivo=ejecutivo
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
                        rut_cli_raw = clean_val(row.get(mapping.get('cliente_rut')))
                        rut_cli = format_rut_chile(rut_cli_raw)
                        
                        cliente = Cliente.objects.filter(rut_empresa=rut_cli).first()
                        if not cliente:
                            # Try search by clean RUT
                            clean_cli = rut_cli_raw.upper().replace(".","").replace("-","").strip()
                            for c in Cliente.objects.all():
                                if c.rut_empresa.replace(".","").replace("-","").upper() == clean_cli:
                                    cliente = c
                                    break
                            
                        if not cliente:
                            # Try by razon social if RUT mapping failed or not found
                            rs_val = clean_val(row.get(mapping.get('razon_social')))
                            if rs_val:
                                cliente = Cliente.objects.filter(razon_social__icontains=rs_val).first()
                        
                        if not cliente:
                            errors.append(f"Fila {index + 2}: Cliente no encontrado ({rut_cli_raw})")
                            continue

                        ejecutivo = cliente.ejecutivo # Default to client's executive
                        ej_rut = clean_val(row.get(mapping.get('ejecutivo_rut')))
                        if ej_rut:
                            found_ej = Ejecutivo.objects.filter(rut_ejecutivo=ej_rut).first()
                            if found_ej: ejecutivo = found_ej
                        
                        coordinador = None
                        coor_rut = clean_val(row.get(mapping.get('coordinador_rut')))
                        if coor_rut:
                            coordinador = Coordinador.objects.filter(rut_coordinador=coor_rut).first()

                        # Date parsing
                        def parse_date(val):
                            if pd.isna(val) or not val: return None
                            try:
                                if isinstance(val, (pd.Timestamp, datetime.date)): return val
                                return pd.to_datetime(val, dayfirst=True).date()
                            except: return None

                        fecha_rec = parse_date(row.get(mapping.get('fecha_recepcion')))
                        fecha_emi = parse_date(row.get(mapping.get('fecha_emision')))
                        fecha_ini = parse_date(row.get(mapping.get('fecha_inicio')))

                        subtotal_val = row.get(mapping.get('subtotal'))
                        try:
                            subtotal = float(subtotal_val) if not pd.isna(subtotal_val) else 0
                        except:
                            subtotal = 0

                        Contrato.objects.create(
                            tipo_registro=clean_val(row.get(mapping.get('tipo_registro')), 'Servicio'),
                            empresa=cliente.razon_social,
                            fecha_recepcion=fecha_rec,
                            fecha_emision=fecha_emi,
                            fecha_inicio=fecha_ini,
                            subtotal=subtotal,
                            estado=clean_val(row.get(mapping.get('estado')), 'Por Cerrar'),
                            detalle=clean_val(row.get(mapping.get('detalle'))),
                            observaciones=clean_val(row.get(mapping.get('observaciones'))),
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
                "message": f"Proceso finalizado. Creados: {created_count}, Errores: {len(errors)}",
                "created_count": created_count,
                "error_count": len(errors),
                "errors": errors if len(errors) < 20 else errors[:20] + ["... y más errores no mostrados."]
            }, status=200 if (created_count > 0 or not errors) else 400)
        except Exception as e:
            return Response({"error": f"Error fatal en importación: {str(e)}"}, status=500)
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
        
        AuditLog.objects.create(
            usuario=request.user if not request.user.is_anonymous else None,
            accion='IMPORTAR',
            modelo='Cliente',
            objeto_id=0,
            objeto_repr=file_obj.name,
            detalle=f"Iniciada importación mapeada de clientes desde archivo {file_obj.name}"
        )
        
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
                        
                    rut = clean_val(row.get(rut_col))
                    razon_social = clean_val(row.get(razon_social_col))
                    
                    if not rut or not razon_social:
                        continue
                        
                    # Optional fields
                    email_col = mapping.get('email')
                    nombre_col = mapping.get('nombre')
                    estado_col = mapping.get('estado')
                    
                    email = clean_val(row.get(email_col)) if email_col else ""
                    nombre = clean_val(row.get(nombre_col), razon_social) if nombre_col else razon_social
                    estado = clean_val(row.get(estado_col), 'activo').lower() if estado_col else "activo"
                    
                    if not email:
                        email = f"import_{rut.replace('.','').replace('-','')}@usecap.cl"
                    
                    if Cliente.objects.filter(rut_empresa=rut).exists():
                        errors.append(f"Fila {index + 2}: El RUT {rut} ya existe.")
                        continue
                    
                    if Cliente.objects.filter(email=email).exists():
                        email = f"import_{index}_{rut.replace('.','').replace('-','')}@usecap.cl"

                    Cliente.objects.create(
                        rut_empresa=rut,
                        razon_social=razon_social,
                        estado=estado,
                        ejecutivo=default_ejecutivo,
                        direccion="Sin Dirección",
                        comuna="Santiago",
                        region="RM",
                        sector_industria=""
                    )
                    created_count += 1
                except Exception as e:
                    errors.append(f"Fila {index + 2}: {str(e)}")
            
            # Save to history
            ImportHistory.objects.create(
                nombre_archivo=file_obj.name,
                filas_procesadas=created_count,
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
    from django.shortcuts import render, redirect
    if not request.user.is_superuser:
        ej = getattr(request.user, 'ejecutivo', None)
        if not ej or ej.rol.nombre not in ['Administrador', 'Gerencia']:
            return redirect('dashboard')
    return render(request, 'estadisticas.html')

def clientes_view(request):
    from django.shortcuts import render
    return render(request, 'clientes.html')

def coordinadores_view(request):
    return render(request, "coordinadores.html")

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
                # Check duplicates by Email (RUT already checked by unique=True/serializer but we wrap it)
                if Ejecutivo.objects.filter(email=email).exists():
                    return Response({"error": f"El correo {email} ya está registrado"}, status=400)

                username = email.split('@')[0]
                if User.objects.filter(username=username).exists():
                    username = f"{username}_{rut.split('-')[0].replace('.','')}"
                    
                # Clean RUT for password (numeric only)
                pass_prefix = rut.split('-')[0].replace('.', '')
                new_user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=f"USECAP_{pass_prefix}", # Default password
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
            
            AuditLog.objects.create(
                usuario=request.user if not request.user.is_anonymous else None,
                accion='EDITAR' if status_code == 200 else 'CREAR',
                modelo='Ejecutivo',
                objeto_id=ejecutivo_instance.id,
                objeto_repr=str(ejecutivo_instance),
                detalle=f"{message} manualmente vía API"
            )
            return Response({"message": message, "username": ejecutivo_instance.user.username if ejecutivo_instance.user else ""}, status=status_code)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

def servicios_view(request):
    from django.shortcuts import render
    return render(request, 'servicios.html')

def audit_log_view(request):
    from django.shortcuts import render, redirect
    if not request.user.is_superuser:
        ej = getattr(request.user, 'ejecutivo', None)
        if not ej or ej.rol.nombre not in ['Administrador', 'Gerencia']:
            return redirect('dashboard')
    return render(request, 'audit_log.html')
