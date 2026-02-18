# api/models.py

from django.db import models
from django.core.exceptions import ValidationError
import re

def validate_rut(value):
    """
    Valida un RUT chileno.
    Acepta cualquier formato (con/sin puntos, con/sin guion)
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


from django.contrib.auth.models import User

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

    def __str__(self):
        return self.nombre


# =========================
# Tabla Clientes
# =========================

class Cliente(models.Model):
    rut_empresa = models.CharField(max_length=12, unique=True, validators=[validate_rut])
    razon_social = models.CharField(max_length=100)
    estado = models.CharField(
        max_length=10,
        choices=[("activo", "Activo"), ("inactivo", "Inactivo")]
    )
    direccion = models.CharField(max_length=150, blank=True, null=True)
    region = models.CharField(max_length=50, blank=True, null=True)
    comuna = models.CharField(max_length=50, blank=True, null=True)
    sector_industria = models.CharField(max_length=50, blank=True, null=True)
    origen_referencia = models.CharField(max_length=50, blank=True, null=True)
    fecha_creacion = models.DateField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    
    # Relaciones
    ejecutivo = models.ForeignKey(Ejecutivo, on_delete=models.CASCADE)
    cliente_padre = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True)

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
    estado = models.CharField(
        max_length=10,
        choices=[("activo", "Activo"), ("inactivo", "Inactivo")]
    )
    observaciones = models.TextField(blank=True, null=True)
    
    # Relaciones
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

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
    tipo_seguimiento = models.CharField(max_length=50)
    requerimiento = models.TextField(blank=True, null=True)
    fecha = models.DateField(blank=True, null=True)
    respuesta = models.TextField(blank=True, null=True)
    fecha_respuesta = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=20)
    cerrado = models.BooleanField(default=False)
    fecha_proxima_accion = models.DateField(blank=True, null=True)
    detalle = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    # Relaciones
    contrato = models.ForeignKey("Contrato", on_delete=models.CASCADE)
    coordinador = models.ForeignKey("Coordinador", on_delete=models.CASCADE)
    ejecutivo = models.ForeignKey("Ejecutivo", on_delete=models.CASCADE)

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
