from django import forms
from .models import Aluno, Mensalidade, UserProfile
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
        fields = '__all__'
        # Personaliza a mensagem de erro para datas inválidas
        error_messages = {
            'data_nascimento': {
                'invalid': "Informe uma data válida. Por exemplo, Fevereiro não tem 30 dias.",
                'invalid_date': "Formato de data inválido. Use o formato AAAA-MM-DD ou verifique se a data existe no calendário.", # Mensagem mais detalhada para data inválida
            }
        }

class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'nome_completo', 'telefone', 'endereco']
        widgets = {
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 0 0000-0000'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Endereço completo'}),
            'nome_completo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo'}),
        } 