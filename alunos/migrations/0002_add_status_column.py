from django.db import migrations, models
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('alunos', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=(
                        "ALTER TABLE \"alunos_mensalidade\" "
                        "ADD COLUMN IF NOT EXISTS \"status\" varchar(10) NOT NULL DEFAULT 'PENDENTE'"
                    ),
                    reverse_sql=(
                        "ALTER TABLE \"alunos_mensalidade\" DROP COLUMN IF EXISTS \"status\""
                    ),
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='mensalidade',
                    name='status',
                    field=models.CharField(
                        choices=[('PENDENTE', 'Pendente'), ('PAGO', 'Pago'), ('ATRASADO', 'Atrasado')],
                        default='PENDENTE',
                        max_length=10
                    ),
                ),
            ],
        ),
    ]