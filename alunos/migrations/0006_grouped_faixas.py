from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alunos', '0005_remove_userprofile_avatar_alter_aluno_faixa'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aluno',
            name='faixa',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('Adulto', [
                        ('BRANCA', 'Branca'),
                        ('AZUL', 'Azul'),
                        ('ROXA', 'Roxa'),
                        ('MARROM', 'Marrom'),
                        ('PRETA', 'Preta'),
                    ]),
                    ('Infantil', [
                        ('BRANCA_KIDS', 'Branca'),
                        ('CINZA_BRANCA', 'Cinza e Branca'),
                        ('CINZA', 'Cinza'),
                        ('CINZA_PRETA', 'Cinza e Preta'),
                        ('AMARELA_BRANCA', 'Amarela e Branca'),
                        ('AMARELA', 'Amarela'),
                        ('AMARELA_PRETA', 'Amarela e Preta'),
                        ('LARANJA_BRANCA', 'Laranja e Branca'),
                        ('LARANJA', 'Laranja'),
                        ('LARANJA_PRETA', 'Laranja e Preta'),
                        ('VERDE_BRANCA', 'Verde e Branca'),
                        ('VERDE', 'Verde'),
                        ('VERDE_PRETA', 'Verde e Preta'),
                    ]),
                ],
            ),
        ),
    ]


