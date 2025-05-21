from django import forms
from .models import Aluno, Mensalidade
from django.contrib.auth.forms import UserCreationForm

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

class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ['nome', 'data_nascimento', 'telefone', 'email', 'endereco', 'faixa', 'bolsista']
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'id': 'id_data_nascimento', 'class': 'form-control', 'type': 'text'}),
            'telefone': forms.TextInput(attrs={'id': 'id_telefone', 'class': 'form-control'}),
        }

class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",) 