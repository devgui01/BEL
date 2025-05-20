from django.db import models
from django.utils import timezone

class Aluno(models.Model):
    nome = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    telefone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    endereco = models.CharField(max_length=200)
    data_cadastro = models.DateField(auto_now_add=True)
    faixa = models.CharField(max_length=20, choices=[
        ('BRANCA', 'Branca'),
        ('AZUL', 'Azul'),
        ('ROXA', 'Roxa'),
        ('MARROM', 'Marrom'),
        ('PRETA', 'Preta'),
    ])
    bolsista = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nome

class Mensalidade(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    data_vencimento = models.DateField()
    valor = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('PENDENTE', 'Pendente'),
        ('PAGO', 'Pago'),
        ('ATIVO', 'Ativo'),
    ], default='ATIVO')
    data_pagamento = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"Mensalidade de {self.aluno.nome} ({self.data_vencimento})"

    def save(self, *args, **kwargs):
        if not self.valor:
            self.valor = 100.00 if self.aluno.bolsista else 150.00
        super().save(*args, **kwargs)

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
