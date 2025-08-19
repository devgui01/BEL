from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('alunos', '0006_grouped_faixas'),
    ]

    operations = [
        migrations.CreateModel(
            name='Presenca',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField()),
                ('presente', models.BooleanField(default=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('aluno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='alunos.aluno')),
            ],
            options={
                'ordering': ['-data', 'aluno__nome'],
                'unique_together': {('aluno', 'data')},
            },
        ),
    ]


