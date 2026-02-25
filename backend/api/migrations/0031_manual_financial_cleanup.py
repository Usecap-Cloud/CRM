from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0030_contrato_fecha_envio_contrato_valor_empresa_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contrato',
            name='subtotal',
        ),
        migrations.RemoveField(
            model_name='contrato',
            name='iva',
        ),
        migrations.RemoveField(
            model_name='contrato',
            name='total',
        ),
        migrations.RenameField(
            model_name='contrato',
            old_name='valor_otic',
            new_name='a_pagar_otic',
        ),
        migrations.RenameField(
            model_name='contrato',
            old_name='valor_empresa',
            new_name='a_pagar_empresa',
        ),
    ]
