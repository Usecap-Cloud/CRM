# api/models.py

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
import re

# Abreviaciones que permanecen en MAYÚSCULAS
_UPPERCASE_ABBR = {
    'S.A.', 'SPA', 'S.P.A.', 'LTDA.', 'LTDA', 'EIRL', 'E.I.R.L.',
    'S.A.C.', 'SRL', 'SAC', 'SA', 'AG', 'LLC', 'INC', 'S.A.S.',
    'RRHH', 'TI', 'RM', 'OTEC', 'SENCE', 'OTECH',
}

def normalize_text(value):
    """
    Convierte texto a Title Case inteligente, preservando abreviaciones
    comunes como S.A., LTDA., SpA, etc.
    """
    if not value or not isinstance(value, str):
        return value
    value = value.strip()
    if not value:
        return value
    words = value.split()
    result = []
    for word in words:
        if word.upper() in _UPPERCASE_ABBR or word.upper().rstrip('.,') in _UPPERCASE_ABBR:
            result.append(word.upper())
        else:
            result.append(word.capitalize())
    return ' '.join(result)

def normalize_estado(value):
    """Normaliza estados a Title Case consistente, manejando ruidos de datos."""
    if not value or not isinstance(value, str):
        return "Activo" # Default sensible
    
    val_clean = value.strip().lower()
    if val_clean in ['nan', 'none', '', 'null', 'n/a']:
        return "Activo" # Asumimos Activo para data ruidosa
        
    mapping = {
        'activo': 'Activo', 'inactivo': 'Inactivo',
        'finalizado': 'Finalizado', 'firmado': 'Firmado',
        'en proceso': 'En Proceso', 'por cerrar': 'Por Cerrar',
        'pendiente': 'Pendiente', 'completado': 'Completado',
        'particular': 'Particular', 'sence': 'SENCE', 'otic': 'OTIC', 'otech': 'OTIC', 'otec': 'OTIC',
    }
    return mapping.get(val_clean, value.strip().capitalize())


def normalize_rut_str(value):
    """
    Normaliza un RUT al formato 12.345.678-9
    """
    if not value:
        return value
    clean = str(value).upper().replace(".", "").replace("-", "").replace(" ", "").strip()
    if len(clean) < 2:
        return clean
    cuerpo = clean[:-1]
    dv = clean[-1]
    try:

        # Formato con puntos: 12.345.678
        cuerpo_fmt = f"{int(cuerpo):,}".replace(",", ".")
        return f"{cuerpo_fmt}-{dv}"
    except:
        return f"{cuerpo}-{dv}"

def validate_rut(value):
    """
    Valida un RUT chileno.
    """
    rut_clean = value.replace(".", "").replace("-", "").replace(" ", "").upper()
    
    if len(rut_clean) < 2:
        raise ValidationError("Ingrese su RUT con dígito verificador.")

    cuerpo = rut_clean[:-1]
    dv = rut_clean[-1]
    
    if not cuerpo.isdigit():
         raise ValidationError("Ingrese su RUT con dígito verificador.")

    suma = 0
    multiplo = 2
    
    for c in reversed(cuerpo):
        suma += int(c) * multiplo
        multiplo += 1
        if multiplo == 8:
            multiplo = 2
            
    dv_esperado = 11 - (suma % 11)
    if dv_esperado == 11:
        dv_calc = "0"
    elif dv_esperado == 10:
        dv_calc = "K"
    else:
        dv_calc = str(dv_esperado)
        
    if dv_calc != dv:
        raise ValidationError("Ingrese su RUT con dígito verificador.")
    return value

# --- UTILIDADES DE TELÉFONO ---

def normalize_phone(value):
    """
    Normaliza números chilenos a formato +56 9 XXXX XXXX
    Si no tiene código de país, asume +56.
    """
    if not value or not isinstance(value, str):
        return value
    
    # Limpiar todo lo que no sea dígito
    clean = re.sub(r'\D', '', value)
    
    if not clean:
        return value

    # Si empieza con 56, quitarlo temporalmente para estandarizar
    if clean.startswith('56') and len(clean) > 9:
        clean = clean[2:]
    
    # Si tiene menos de 9 dígitos (ej: 91234567), le falta el 9 o el código de área
    if len(clean) < 9:
        return value

    # Tomar los últimos 9 dígitos
    clean = clean[-9:]
    
    # Formatear: +56 9 1234 5678
    return f"+56 {clean[0]} {clean[1:5]} {clean[5:]}"

def validate_phone(value):
    """
    Valida que el teléfono tenga el largo corregido de un número chileno (9 dígitos sin contar +56)
    """
    if not value:
        return value
    clean = re.sub(r'\D', '', str(value))
    if clean.startswith('56') and len(clean) > 9:
        clean = clean[2:]
    
    if len(clean) != 9:
        raise ValidationError("El número telefónico debe tener 9 dígitos (ej: 9 1234 5678).")
    return value

# =========================
# Tabla Roles
# =========================
class Rol(models.Model):
    nombre = models.CharField(max_length=50)
    estado = models.CharField(max_length=10)
    descripcion = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.nombre = normalize_text(self.nombre)
        self.estado = normalize_estado(self.estado)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


# =========================
# Tabla Ejecutivos
# =========================
class Ejecutivo(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    rut_ejecutivo = models.CharField(max_length=12, unique=True, validators=[validate_rut])
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True, validators=[validate_phone])
    estado = models.CharField(
        max_length=10,
        choices=[("Activo", "Activo"), ("Inactivo", "Inactivo")]
    )
    area_departamento = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=[
            ("ventas", "Ventas"),
            ("marketing", "Marketing"),
            ("operaciones", "Operaciones"),
            ("finanzas", "Finanzas"),
            ("rrhh", "Recursos Humanos"),
            ("ti", "Tecnología e Informática"),
            ("administracion", "Administración"),
            ("comercial", "Comercial"),
            ("logistica", "Logística"),
            ("atencion_cliente", "Atención al Cliente"),
            ("otro", "Otro")
        ]
    )
    especialidad_tipo_clientes = models.CharField(max_length=50, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    # Relaciones
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.rut_ejecutivo = normalize_rut_str(self.rut_ejecutivo)
        self.nombre = normalize_text(self.nombre)
        if self.email:
            self.email = self.email.strip().lower()
        if self.telefono:
            self.telefono = normalize_phone(self.telefono)
        self.estado = normalize_estado(self.estado)
        self.area_departamento = normalize_text(self.area_departamento)
        self.especialidad_tipo_clientes = normalize_text(self.especialidad_tipo_clientes)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


# =========================
# Tabla Clientes
# =========================
class Cliente(models.Model):
    rut_empresa = models.CharField(max_length=12, unique=True, validators=[validate_rut])
    razon_social = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(
        max_length=10,
        choices=[("Activo", "Activo"), ("Inactivo", "Inactivo")]
    )
    sector_industria = models.CharField(max_length=50, blank=True, null=True)
    direccion = models.CharField(max_length=150, blank=True, null=True)
    region = models.CharField(max_length=50, blank=True, null=True)
    comuna = models.CharField(max_length=50, blank=True, null=True)
    telefono_empresarial = models.CharField(max_length=20, blank=True, null=True, validators=[validate_phone])
    email_empresa = models.EmailField(max_length=254, blank=True, null=True)
    origen_referencia = models.CharField(max_length=50, blank=True, null=True)
    fecha_creacion = models.DateField(blank=True, null=True)
    numero_colaboradores = models.IntegerField(default=0)
    tipo_convenio = models.CharField(
        max_length=20, 
        choices=[("OTIC", "OTIC"), ("SENCE", "SENCE"), ("Particular", "Particular")],
        default="Particular"
    )
    cantidad_sucursales = models.IntegerField(default=1)
    observaciones = models.TextField(blank=True, null=True)
    
    # Relaciones
    ejecutivo = models.ForeignKey(Ejecutivo, on_delete=models.CASCADE)
    cliente_padre = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True)
    contacto_principal = models.ForeignKey(
        "Coordinador",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="es_principal_de"
    )

    def save(self, *args, **kwargs):
        self.rut_empresa = normalize_rut_str(self.rut_empresa)
        self.razon_social = normalize_text(self.razon_social)
        self.nombre = normalize_text(self.nombre)
        self.estado = normalize_estado(self.estado)
        self.sector_industria = normalize_text(self.sector_industria)
        self.direccion = normalize_text(self.direccion)
        self.region = normalize_text(self.region)
        self.comuna = normalize_text(self.comuna)
        self.origen_referencia = normalize_text(self.origen_referencia)
        self.tipo_convenio = normalize_estado(self.tipo_convenio)
        if self.email_empresa:
            self.email_empresa = self.email_empresa.strip().lower()
        if self.telefono_empresarial:
            self.telefono_empresarial = normalize_phone(self.telefono_empresarial)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.razon_social


# =========================
# Tabla Coordinadores
# =========================
class Coordinador(models.Model):
    rut_coordinador = models.CharField(max_length=12, unique=True, validators=[validate_rut])
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True, validators=[validate_phone])
    cargo = models.CharField(max_length=50, blank=True, null=True)
    departamento = models.CharField(max_length=100, blank=True, null=True)
    fecha_cumpleanos = models.DateField(blank=True, null=True)
    estado = models.CharField(
        max_length=10,
        choices=[("activo", "Activo"), ("inactivo", "Inactivo")]
    )
    observaciones = models.TextField(blank=True, null=True)
    
    # Relaciones
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    ejecutivo = models.ForeignKey(Ejecutivo, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.rut_coordinador = normalize_rut_str(self.rut_coordinador)
        self.nombre = normalize_text(self.nombre)
        if self.email:
            self.email = self.email.strip().lower()
        if self.telefono:
            self.telefono = normalize_phone(self.telefono)
        self.cargo = normalize_text(self.cargo)
        self.departamento = normalize_text(self.departamento)
        self.estado = normalize_estado(self.estado)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


# =========================
# Tabla Servicios
# =========================
class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.CharField(
        max_length=10,
        choices=[("activo", "Activo"), ("inactivo", "Inactivo")]
    )
    categoria = models.CharField(max_length=50, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.nombre = normalize_text(self.nombre)
        self.tipo = normalize_text(self.tipo)
        self.categoria = normalize_text(self.categoria)
        self.estado = normalize_estado(self.estado)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


# =========================
# Tabla Proveedores
# =========================
class Proveedor(models.Model):
    rut_proveedor = models.CharField(max_length=12, unique=True, validators=[validate_rut])
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    estado = models.CharField(
        max_length=10,
        choices=[("activo", "Activo"), ("inactivo", "Inactivo")]
    )
    contacto = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True, validators=[validate_phone])
    direccion = models.CharField(max_length=150, blank=True, null=True)
    region = models.CharField(max_length=50, blank=True, null=True)
    comuna = models.CharField(max_length=50, blank=True, null=True)
    rubro = models.CharField(max_length=50, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.rut_proveedor = normalize_rut_str(self.rut_proveedor)
        self.nombre = normalize_text(self.nombre)
        self.tipo = normalize_text(self.tipo)
        self.contacto = normalize_text(self.contacto)
        if self.email:
            self.email = self.email.strip().lower()
        if self.telefono:
            self.telefono = normalize_phone(self.telefono)
        self.direccion = normalize_text(self.direccion)
        self.region = normalize_text(self.region)
        self.comuna = normalize_text(self.comuna)
        self.rubro = normalize_text(self.rubro)
        self.estado = normalize_estado(self.estado)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


# =========================
# Tabla Cursos
# =========================
class Curso(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50, blank=True, null=True)
    estado = models.CharField(
        max_length=10,
        choices=[("activo", "Activo"), ("inactivo", "Inactivo")]
    )
    codigo_sence = models.CharField(max_length=50, blank=True, null=True)
    detalle = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.nombre = normalize_text(self.nombre)
        self.categoria = normalize_text(self.categoria)
        self.estado = normalize_estado(self.estado)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


# =========================
# Tabla Contratos
# =========================
class Contrato(models.Model):
    # Identificación (Requested Order: folio, fecha, empresa, curso, servicio, tipo_convenio, valor_persona, valor_total, pago_otic, pago_empresa, fecha_envio, estado)
    folio = models.CharField(max_length=50, unique=True, blank=True, null=True)
    fecha = models.DateField(blank=True, null=True)
    
    # Relaciones principales
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    empresa = models.CharField(max_length=100) # Nombre descriptivo o razón social
    curso = models.ForeignKey('Curso', on_delete=models.SET_NULL, null=True, blank=True)
    servicios = models.ManyToManyField('Servicio', blank=True)
    
    tipo_convenio = models.CharField(
        max_length=20, 
        choices=[("OTIC", "OTIC"), ("SENCE", "SENCE"), ("Particular", "Particular")],
        default="Particular",
        blank=True, null=True
    )
    fecha_envio = models.DateField(blank=True, null=True)
    
    # Finanzas
    valor_persona = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    estado = models.CharField(
        max_length=30,
        choices=[
            ("nuevo requerimiento", "Nuevo Requerimiento"),
            ("aprobado", "Aprobado"),
            ("rechazado", "Rechazado"),
            ("en proceso", "En Proceso"),
            ("liquidado", "Liquidado"),
            ("finalizado", "Finalizado")
        ],
        default="nuevo requerimiento"
    )

    # Campos técnicos y otros
    detalle = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Otras relaciones existentes
    ejecutivo = models.ForeignKey(Ejecutivo, on_delete=models.CASCADE)
    coordinador = models.ForeignKey(Coordinador, on_delete=models.SET_NULL, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Normalización
        if self.cliente and not self.empresa:
            self.empresa = self.cliente.razon_social
        self.empresa = normalize_text(self.empresa)
        
        # Nota: normalize_estado podría necesitar actualización para los nuevos estados en español
        # pero por ahora lo dejamos así o lo ajustamos si es necesario.
        # self.estado = normalize_estado(self.estado) 

        # Si el cliente está presente y la empresa está vacía, copiar razón social
        if self.cliente and not self.empresa:
            self.empresa = self.cliente.razon_social

        # Generación de Folio (si está vacío)
        super().save(*args, **kwargs)

        if not self.folio:
            year = timezone.now().year
            self.folio = f"CON-{year}-{self.id:04d}"
            super().save(update_fields=['folio'])

    def __str__(self):
        return f"{self.folio or 'S/F'} - {self.empresa}"


# =========================
# Tabla Contratos_Cursos
# =========================
class ContratoCurso(models.Model):
    tipo_curso = models.CharField(max_length=30)
    fecha_contrato = models.DateField(blank=True, null=True)
    fecha_inicio_curso = models.DateField(blank=True, null=True)
    fecha_fin_curso = models.DateField(blank=True, null=True)
    duracion_horas = models.IntegerField(blank=True, null=True)
    relator = models.CharField(max_length=100, blank=True, null=True)
    modalidad = models.CharField(max_length=20, blank=True, null=True)
    acceso_contenido = models.CharField(max_length=100, blank=True, null=True)
    servicios_asociados = models.CharField(max_length=150, blank=True, null=True)
    numero_participantes = models.IntegerField(blank=True, null=True)
    numero_grupos = models.IntegerField(blank=True, null=True)
    costo = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    orden_compra = models.CharField(max_length=50, unique=True, blank=True, null=True)
    numero_factura = models.CharField(max_length=50, unique=True, blank=True, null=True)
    rus = models.CharField(max_length=50, unique=True, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    
    # Relaciones
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.tipo_curso = normalize_text(self.tipo_curso)
        self.relator = normalize_text(self.relator)
        self.modalidad = normalize_text(self.modalidad)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tipo_curso} - Contrato {self.contrato.id}"


# =========================
# Tabla Contratos_Proveedores
# =========================
class ContratoProveedor(models.Model):
    cantidad = models.IntegerField(blank=True, null=True)              # cantidad de servicios o unidades contratadas
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)  
    costo_negociado = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)  
    detalle = models.TextField(blank=True, null=True)                  # detalle del acuerdo
    observaciones = models.TextField(blank=True, null=True)            # notas adicionales

    # Fechas de vigencia del contrato con el proveedor
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)

    # Relaciones
    contrato = models.ForeignKey("Contrato", on_delete=models.CASCADE)
    proveedor = models.ForeignKey("Proveedor", on_delete=models.CASCADE)
    servicio = models.ForeignKey("Servicio", on_delete=models.CASCADE) # qué servicio aporta el proveedor

    def __str__(self):
        return f"Contrato {self.contrato.id} - Proveedor {self.proveedor.nombre} - Servicio {self.servicio.nombre}"


# =========================
# Tabla Seguimiento
# =========================
class Seguimiento(models.Model):
    tipo = models.CharField(max_length=50, default="General")
    fecha = models.DateField(blank=True, null=True)
    requerimiento = models.TextField(blank=True, null=True)
    fecha_envio = models.DateField(blank=True, null=True)
    respuesta = models.TextField(blank=True, null=True)
    fecha_respuesta = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=20)
    cerrado = models.BooleanField(default=False)
    fecha_seguimiento = models.DateField(blank=True, null=True)
    accion = models.CharField(max_length=50, default="Sin Acción")
    respuesta_seguimiento = models.TextField(blank=True, null=True)
    fecha_respuesta_seguimiento = models.DateField(blank=True, null=True)
    detalle = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    # Relaciones
    contrato = models.ForeignKey("Contrato", on_delete=models.CASCADE, related_name="seguimientos")
    coordinador = models.ForeignKey("Coordinador", on_delete=models.CASCADE)
    ejecutivo = models.ForeignKey("Ejecutivo", on_delete=models.CASCADE)
    cliente = models.ForeignKey("Cliente", on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        self.tipo = normalize_text(self.tipo)
        self.accion = normalize_text(self.accion)
        self.estado = normalize_estado(self.estado)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Seguimiento {self.id} - Contrato {self.contrato_id}"


# =========================
# Historial de Importaciones
# =========================
class ImportHistory(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    nombre_archivo = models.CharField(max_length=255)
    filas_procesadas = models.IntegerField(default=0)
    estado = models.CharField(max_length=20) # 'exito', 'importando', 'error'
    mensaje_error = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre_archivo} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"


# =========================
# Auditoría de Cambios
# =========================
class AuditLog(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=20) # 'CREAR', 'EDITAR', 'ELIMINAR'
    modelo = models.CharField(max_length=50)
    objeto_id = models.IntegerField()
    objeto_repr = models.CharField(max_length=255)
    detalle = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.fecha.strftime('%Y-%m-%d %H:%M')} - {self.usuario} - {self.accion} {self.modelo}"
