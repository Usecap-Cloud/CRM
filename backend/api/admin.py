from django.contrib import admin
from .models import Rol, Ejecutivo, Cliente, Coordinador, Servicio, Proveedor, Curso, Contrato, ContratoCurso, ContratoProveedor, Seguimiento

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('razon_social', 'rut_empresa', 'ejecutivo', 'estado')
    search_fields = ('razon_social', 'rut_empresa')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Si el usuario es un ejecutivo, filtrar solo sus clientes
        if hasattr(request.user, 'ejecutivo'):
            return qs.filter(ejecutivo=request.user.ejecutivo)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "ejecutivo":
            if not request.user.is_superuser and hasattr(request.user, 'ejecutivo'):
                kwargs["queryset"] = Ejecutivo.objects.filter(user=request.user)
                kwargs["initial"] = request.user.ejecutivo.id
                kwargs["disabled"] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register([Rol, Ejecutivo, Coordinador, Servicio, Proveedor, Curso, Contrato, ContratoCurso, ContratoProveedor, Seguimiento])