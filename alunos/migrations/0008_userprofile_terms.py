from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alunos', '0007_presenca'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='accepted_terms_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='accepted_terms_version',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
    ]


