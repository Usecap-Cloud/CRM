from rest_framework import serializers
from .models import (
    Rol, Ejecutivo, Cliente, Coordinador, Servicio,
    Proveedor, Curso, Contrato, ContratoCurso,
    ContratoProveedor,
    Seguimiento, ImportHistory, AuditLog
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

    def validate_rut_ejecutivo(self, value):
        if Ejecutivo.objects.filter(rut_ejecutivo=value).exists():
            raise serializers.ValidationError("Este RUT ya está registrado como ejecutivo.")
        return value

    def validate_email(self, value):
        if Ejecutivo.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo ya está registrado por otro ejecutivo.")
        return value

class ClienteSerializer(serializers.ModelSerializer):
    ejecutivo_nombre = serializers.ReadOnlyField(source='ejecutivo.nombre')
    cliente_padre_nombre = serializers.ReadOnlyField(source='cliente_padre.razon_social')
    contacto_nombre = serializers.ReadOnlyField(source='contacto_principal.nombre')
    contacto_email = serializers.ReadOnlyField(source='contacto_principal.email')
    contacto_telefono = serializers.ReadOnlyField(source='contacto_principal.telefono')
    filiales_count = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = '__all__'

    def get_filiales_count(self, obj):
        return Cliente.objects.filter(cliente_padre=obj).count()

    def validate_rut_empresa(self, value):
        queryset = Cliente.objects.filter(rut_empresa=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Este RUT ya está registrado como cliente.")
        return value

class CoordinadorSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.ReadOnlyField(source='cliente.razon_social')
    ejecutivo_nombre = serializers.ReadOnlyField(source='ejecutivo.nombre')

    class Meta:
        model = Coordinador
        fields = '__all__'

    def validate_rut_coordinador(self, value):
        # Exclude current instance when editing
        queryset = Coordinador.objects.filter(rut_coordinador=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Este RUT ya está registrado como coordinador.")
        return value

class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = '__all__'

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'

    def validate_rut_proveedor(self, value):
        instance = self.instance
        qs = Proveedor.objects.filter(rut_proveedor=value)
        if instance:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Este RUT ya está registrado como proveedor.")
        return value

class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = '__all__'

class ContratoCursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContratoCurso
        exclude = ['contrato']

class ContratoSerializer(serializers.ModelSerializer):
    cursos_asociados = ContratoCursoSerializer(many=True, required=False, write_only=True)
    empresa_nombre = serializers.ReadOnlyField(source='cliente.razon_social')
    ejecutivo_nombre = serializers.ReadOnlyField(source='ejecutivo.nombre')

    class Meta:
        model = Contrato
        fields = '__all__'

    def create(self, validated_data):
        cursos_data = validated_data.pop('cursos_asociados', [])
        contrato = Contrato.objects.create(**validated_data)
        for curso_item in cursos_data:
            ContratoCurso.objects.create(contrato=contrato, **curso_item)
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

class AuditLogSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.ReadOnlyField(source='usuario.username')
    class Meta:
        model = AuditLog
        fields = '__all__'