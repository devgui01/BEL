from django import forms
from .models import Aluno, Mensalidade

class GerarMensalidadeForm(forms.ModelForm):
    aluno = forms.ModelChoiceField(
        queryset=Aluno.objects.filter(ativo=True),
        label="Aluno",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    valor = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        label="Valor",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    data_vencimento = forms.DateField(
        label="Data de Vencimento",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    class Meta:
        model = Mensalidade
        fields = ['aluno', 'valor', 'data_vencimento'] 