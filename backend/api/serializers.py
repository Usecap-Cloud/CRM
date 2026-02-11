from rest_framework import serializers
from .models import (
    Rol, Ejecutivo, Cliente, Coordinador, Servicio,
    Proveedor, Curso, Contrato, ContratoCurso,
    ContratoServicio, ContratoProveedor,
    Seguimiento, ImportHistory
)

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'

class EjecutivoSerializer(serializers.ModelSerializer):
    rol_nombre = serializers.ReadOnlyField(source='rol.nombre')
    class Meta:
        model = Ejecutivo
        fields = '__all__'

class ClienteSerializer(serializers.ModelSerializer):
    ejecutivo_nombre = serializers.ReadOnlyField(source='ejecutivo.nombre')
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

class ContratoCursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContratoCurso
        exclude = ['contrato']

class ContratoServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContratoServicio
        exclude = ['contrato']

class ContratoSerializer(serializers.ModelSerializer):
    cursos_asociados = ContratoCursoSerializer(many=True, required=False, write_only=True)
    servicios_asociados = ContratoServicioSerializer(many=True, required=False, write_only=True)
    empresa_nombre = serializers.ReadOnlyField(source='cliente.razon_social')
    ejecutivo_nombre = serializers.ReadOnlyField(source='ejecutivo.nombre')

    class Meta:
        model = Contrato
        fields = '__all__'

    def create(self, validated_data):
        cursos_data = validated_data.pop('cursos_asociados', [])
        servicios_data = validated_data.pop('servicios_asociados', [])
        
        contrato = Contrato.objects.create(**validated_data)
        
        for curso_item in cursos_data:
            ContratoCurso.objects.create(contrato=contrato, **curso_item)
            
        for servicio_item in servicios_data:
            ContratoServicio.objects.create(contrato=contrato, **servicio_item)
            
        return contrato


class ContratoProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContratoProveedor
        fields = '__all__'

class SeguimientoSerializer(serializers.ModelSerializer):
    empresa_nombre = serializers.ReadOnlyField(source='contrato.cliente.razon_social')
    ejecutivo_nombre = serializers.ReadOnlyField(source='ejecutivo.nombre')
    coordinador_nombre = serializers.ReadOnlyField(source='coordinador.nombre')

    class Meta:
        model = Seguimiento
        fields = '__all__'

class ImportHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportHistory
        fields = '__all__'