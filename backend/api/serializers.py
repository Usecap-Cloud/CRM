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
    proveedor_nombre = serializers.ReadOnlyField(source='proveedor.nombre')

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

class ContratoProveedorSerializer(serializers.ModelSerializer):
    proveedor_nombre = serializers.ReadOnlyField(source='proveedor.nombre')
    servicio_nombre = serializers.ReadOnlyField(source='servicio.nombre')

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

class ContratoSerializer(serializers.ModelSerializer):
    empresa_nombre = serializers.ReadOnlyField(source='cliente.razon_social')
    ejecutivo_nombre = serializers.ReadOnlyField(source='ejecutivo.nombre')
    coordinador_nombre = serializers.ReadOnlyField(source='coordinador.nombre', default="-")
    curso_nombre = serializers.ReadOnlyField(source='curso.nombre', default="-")
    curso_codigo_sence = serializers.ReadOnlyField(source='curso.codigo_sence', default="-")
    
    # Operational data for reading
    contratocurso_set = ContratoCursoSerializer(many=True, read_only=True)
    contratoproveedor_set = ContratoProveedorSerializer(many=True, read_only=True)
    
    # Writeable field for simple operational update (the "main" operational record)
    operativo_data = serializers.JSONField(write_only=True, required=False)
    # Writeable field for nested provider/cost data
    proveedores_data = serializers.JSONField(write_only=True, required=False)
    otro_servicio = serializers.CharField(write_only=True, required=False, allow_blank=True)

    # Mantener los actuales por compatibilidad mientras migramos el frontend
    servicios_info = ServicioSerializer(source='servicios', many=True, read_only=True)
    seguimientos_info = SeguimientoSerializer(source='seguimientos', many=True, read_only=True)

    class Meta:
        model = Contrato
        fields = '__all__'

    def _handle_operativo(self, instance, op_data):
        if not op_data:
            return
        # We assume the user wants to update/create the main ContratoCurso for this contract
        # If the contract has a curso assigned, we link it.
        from .models import ContratoCurso
        curso_id = op_data.get('curso') or (instance.curso.id if instance.curso else None)
        if not curso_id:
            return
            
        op_obj = ContratoCurso.objects.filter(contrato=instance, curso_id=curso_id).first()
        if op_obj:
            for attr, value in op_data.items():
                if attr not in ['id', 'contrato', 'curso']:
                    setattr(op_obj, attr, value)
            op_obj.save()
        else:
            op_data.pop('contrato', None)
            ContratoCurso.objects.create(contrato=instance, **op_data)

    def _handle_otro_servicio(self, instance, name):
        if not name:
            return
        from .models import Servicio
        name = name.strip()
        # Buscar si ya existe por nombre exacto (insensible a mayúsculas)
        servicio = Servicio.objects.filter(nombre__iexact=name).first()
        if not servicio:
            servicio = Servicio.objects.create(nombre=name, estado='activo')
        instance.servicios.add(servicio)

    def _handle_proveedores(self, instance, proveedores_data):
        if proveedores_data is None:
            return
        
        from .models import ContratoProveedor
        # In a real sync we might want to be more careful, but for now we'll 
        # replace or update based on the servicio_id provided.
        # Clear existing ones for this contract if we want a fresh sync, 
        # OR update by service. Let's clear and recreate for simplicity in this workflow.
        ContratoProveedor.objects.filter(contrato=instance).delete()
        
        for item in proveedores_data:
            proveedor_id = item.get('proveedor')
            servicio_id = item.get('servicio')
            costo = item.get('costo_negociado')
            
            if (proveedor_id or item.get('otro_proveedor')) and servicio_id:
                final_proveedor_id = proveedor_id
                
                # Si es un nuevo proveedor
                if proveedor_id == 'otros' and item.get('otro_proveedor'):
                    from .models import Proveedor
                    nome_prov = item.get('otro_proveedor').strip()
                    # Buscar o crear
                    prov_obj = Proveedor.objects.filter(nombre__iexact=nome_prov).first()
                    if not prov_obj:
                        prov_obj = Proveedor.objects.create(nombre=nome_prov, estado='activo')
                    final_proveedor_id = prov_obj.id

                if final_proveedor_id:
                    ContratoProveedor.objects.create(
                        contrato=instance,
                        proveedor_id=final_proveedor_id,
                        servicio_id=servicio_id,
                        costo_negociado=costo
                    )

    def create(self, validated_data):
        op_data = validated_data.pop('operativo_data', None)
        prov_data = validated_data.pop('proveedores_data', None)
        otro_servicio_name = validated_data.pop('otro_servicio', None)
        instance = super().create(validated_data)
        if op_data:
            self._handle_operativo(instance, op_data)
        if otro_servicio_name:
            self._handle_otro_servicio(instance, otro_servicio_name)
        if prov_data:
            self._handle_proveedores(instance, prov_data)
        return instance

    def update(self, instance, validated_data):
        op_data = validated_data.pop('operativo_data', None)
        prov_data = validated_data.pop('proveedores_data', None)
        otro_servicio_name = validated_data.pop('otro_servicio', None)
        instance = super().update(instance, validated_data)
        if op_data:
            self._handle_operativo(instance, op_data)
        if otro_servicio_name:
            self._handle_otro_servicio(instance, otro_servicio_name)
        if prov_data:
            self._handle_proveedores(instance, prov_data)
        return instance

class ImportHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportHistory
        fields = '__all__'

class AuditLogSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.ReadOnlyField(source='usuario.username')
    class Meta:
        model = AuditLog
        fields = '__all__'