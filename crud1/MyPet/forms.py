from django import forms

class CadastroUsarioForm(forms.Form):
    cpf = forms.CharField()
    nome = forms.CharField()





