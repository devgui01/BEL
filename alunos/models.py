from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Aluno(models.Model):
    nome = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    telefone = models.CharField(max_length=25)
    email = models.EmailField(blank=True, null=True)
    endereco = models.CharField(max_length=200)
    data_cadastro = models.DateField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alunos', null=True, blank=True)
    faixa = models.CharField(max_length=20, choices=[
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
    ])
    bolsista = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nome

class Mensalidade(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('PAGO', 'Pago'),
        ('ATRASADO', 'Atrasado'),
    ]
    
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    data_vencimento = models.DateField()
    valor = models.DecimalField(max_digits=6, decimal_places=2)
    data_pagamento = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDENTE')
    
    def __str__(self):
        return f"Mensalidade de {self.aluno.nome} - {self.data_vencimento}"

    def save(self, *args, **kwargs):
        if not self.valor:
            self.valor = 100.00 if self.aluno.bolsista else 150.00
        super().save(*args, **kwargs)

    @property
    def pago(self):
        return self.status == 'PAGO'

class Pagamento(models.Model):
    METODO_CHOICES = [
        ('DINHEIRO', 'Dinheiro'),
        ('PIX', 'PIX'),
        ('CARTAO', 'Cartão'),
        ('TRANSFERENCIA', 'Transferência'),
    ]
    
    mensalidade = models.ForeignKey(Mensalidade, on_delete=models.CASCADE)
    data_pagamento = models.DateField()
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pagamento = models.CharField(max_length=20, choices=METODO_CHOICES)
    data_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Pagamento de {self.mensalidade.aluno.nome} - {self.data_pagamento}"

class Presenca(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    data = models.DateField()
    presente = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('aluno', 'data'),)
        ordering = ['-data', 'aluno__nome']

    def __str__(self):
        return f"{self.aluno.nome} - {self.data} - {'Presente' if self.presente else 'Ausente'}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)  # Temporariamente comentado
    nome_completo = models.CharField(max_length=100, blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    endereco = models.CharField(max_length=200, blank=True)
    dark_mode = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s profile"

# Signal to create/update user profile
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    # For existing users, create a profile if it doesn't exist
    else:
        # This will get the profile if it exists, or create it if it doesn't
        profile, created = UserProfile.objects.get_or_create(user=instance)
        # If the profile already existed, you might want to save it here if you made other changes elsewhere
        # profile.save()
