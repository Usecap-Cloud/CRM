# api/models.py

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
import re

# Abreviaciones que permanecen en MAYÚSCULAS
_UPPERCASE_ABBR = {
    'S.A.', 'SPA', 'S.P.A.', 'LTDA.', 'LTDA', 'EIRL', 'E.I.R.L.',
    'S.A.C.', 'SRL', 'SAC', 'SA', 'AG', 'LLC', 'INC', 'S.A.S.',
    'RRHH', 'TI', 'RM',
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
    """Normaliza estados a Title Case consistente."""
    if not value or not isinstance(value, str):
        return value
    mapping = {
        'activo': 'Activo', 'inactivo': 'Inactivo',
        'finalizado': 'Finalizado', 'firmado': 'Firmado',
        'en proceso': 'En Proceso', 'por cerrar': 'Por Cerrar',
        'pendiente': 'Pendiente', 'completado': 'Completado',
    }
    return mapping.get(value.strip().lower(), value.strip().capitalize())


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

# =========================
# Tabla Roles
# =========================
class Rol(models.Model):
    nombre = models.CharField(max_length=50)
    estado = models.CharField(max_length=10)
    descripcion = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

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
    telefono = models.CharField(max_length=20, blank=True, null=True)
    estado = models.CharField(
        max_length=10,
        choices=[("activo", "Activo"), ("inactivo", "Inactivo")]
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
    region = models.CharField(max_length=50, blank=True, null=True)
    comuna = models.CharField(max_length=50, blank=True, null=True)
    especialidad_tipo_clientes = models.CharField(max_length=50, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    # Relaciones
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.rut_ejecutivo = normalize_rut_str(self.rut_ejecutivo)
        self.nombre = normalize_text(self.nombre)
        if self.email:
            self.email = self.email.strip().lower()
        self.region = normalize_text(self.region)
        self.comuna = normalize_text(self.comuna)
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
        choices=[("activo", "Activo"), ("inactivo", "Inactivo")]
    )
    sector_industria = models.CharField(max_length=50, blank=True, null=True)
    direccion = models.CharField(max_length=150, blank=True, null=True)
    region = models.CharField(max_length=50, blank=True, null=True)
    comuna = models.CharField(max_length=50, blank=True, null=True)
    origen_referencia = models.CharField(max_length=50, blank=True, null=True)
    telefono_empresarial = models.CharField(max_length=20, blank=True, null=True)
    fecha_creacion = models.DateField(blank=True, null=True)
    numero_colaboradores = models.IntegerField(default=0)
    tipo_convenio = models.CharField(
        max_length=20, 
        choices=[("otech", "OTEC"), ("sence", "SENCE"), ("particular", "Particular")],
        default="particular"
    )
    cantidad_sucursales = models.IntegerField(default=1)
    observaciones = models.TextField(blank=True, null=True)
    
    # Relaciones (Esenciales para el funcionamiento)
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
        self.sector_industria = normalize_text(self.sector_industria)
        self.direccion = normalize_text(self.direccion)
        self.region = normalize_text(self.region)
        self.comuna = normalize_text(self.comuna)
        self.origen_referencia = normalize_text(self.origen_referencia)
        self.nombre = normalize_text(self.nombre)
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
    telefono = models.CharField(max_length=20, blank=True, null=True)
    cargo = models.CharField(max_length=50, blank=True, null=True)
    fecha_cumpleanos = models.DateField(blank=True, null=True)
    area = models.CharField(max_length=100, blank=True, null=True)
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
        self.cargo = normalize_text(self.cargo)
        self.area = normalize_text(self.area)
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
    rubro = models.CharField(max_length=50, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.nombre = normalize_text(self.nombre)
        self.tipo = normalize_text(self.tipo)
        self.rubro = normalize_text(self.rubro)
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
    telefono = models.CharField(max_length=20, blank=True, null=True)
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
        self.region = normalize_text(self.region)
        self.comuna = normalize_text(self.comuna)
        self.rubro = normalize_text(self.rubro)
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
    tipo_registro = models.CharField(max_length=20)
    empresa = models.CharField(max_length=100)
    fecha_recepcion = models.DateField(blank=True, null=True)
    fecha_emision = models.DateField(blank=True, null=True)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.CharField(
        max_length=20,
        choices=[("activo", "Activo"), ("inactivo", "Inactivo"), ("finalizado", "Finalizado")]
    )
    detalle = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    
    # Relaciones
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    ejecutivo = models.ForeignKey(Ejecutivo, on_delete=models.CASCADE)
    coordinador = models.ForeignKey(Coordinador, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"Contrato {self.id} - {self.empresa}"


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

    def __str__(self):
        return f"{self.tipo_curso} - Contrato {self.contrato.id}"


# =========================
# Tabla Contratos_Servicios
# =========================
class ContratoServicio(models.Model):
    cantidad = models.IntegerField(blank=True, null=True)
    precio_unidad = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    detalle = models.TextField(blank=True, null=True)
    duracion_horas = models.IntegerField(blank=True, null=True)
    costo_negociado = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    # fechas y horas
    fecha_inicio = models.DateField(blank=True, null=True)
    hora_inicio = models.TimeField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    hora_fin = models.TimeField(blank=True, null=True)

    # Relaciones
    contrato = models.ForeignKey("Contrato", on_delete=models.CASCADE)
    servicio = models.ForeignKey("Servicio", on_delete=models.CASCADE)

    def __str__(self):
        return f"Servicio {self.servicio} en Contrato {self.contrato_id}"


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
    contrato = models.ForeignKey("Contrato", on_delete=models.CASCADE)
    coordinador = models.ForeignKey("Coordinador", on_delete=models.CASCADE)
    ejecutivo = models.ForeignKey("Ejecutivo", on_delete=models.CASCADE)
    cliente = models.ForeignKey("Cliente", on_delete=models.CASCADE, null=True)

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
