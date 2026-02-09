from rest_framework import serializers
from .models import (
    Rol, Ejecutivo, Cliente, Coordinador, Servicio,
    Proveedor, Curso, Contrato, ContratoCurso,
    ContratoServicio, ContratoProveedor,
    Seguimiento
)

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'

class EjecutivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ejecutivo
        fields = '__all__'

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class CoordinadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinador
        fields = '__all__'

class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = '__all__'

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'

class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = '__all__'

class ContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        fields = '__all__'

class ContratoCursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContratoCurso
        fields = '__all__'

class ContratoServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContratoServicio
        fields = '__all__'

class ContratoProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContratoProveedor
        fields = '__all__'

class SeguimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seguimiento
        fields = '__all__'