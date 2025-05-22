from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('alunos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mensalidade',
            name='status',
            field=models.CharField(
                choices=[('PENDENTE', 'Pendente'), ('PAGO', 'Pago'), ('ATRASADO', 'Atrasado')],
                default='PENDENTE',
                max_length=10
            ),
        ),
    ] 