from django.contrib import admin
from .models import Rol, Ejecutivo, Cliente, Coordinador, Servicio, Proveedor, Curso, Contrato, ContratoCurso, ContratoServicio, ContratoProveedor, Seguimiento

admin.site.register([Rol, Ejecutivo, Cliente, Coordinador, Servicio, Proveedor, Curso, Contrato, ContratoCurso, ContratoServicio, ContratoProveedor, Seguimiento])