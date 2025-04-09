from django import forms

class CadastroUsarioForm(forms.Form):
    cpf = forms.CharField(label = 'Cpf', max_length=100)
    nome = forms.CharField(label = 'Nome', max_length=100)
    data_de_nasc = forms.DateField(label = 'Data de nascimento')
    genero = forms.ChoiceField(label = 'Gênero')
    endereco = forms.CharField(label = 'Endereço', max_length=100)
    tipo_residencia = forms.ChoiceField(label = 'Tipo de residência')
    email = forms.EmailField(label = 'E-mail', max_length=100)
    telefone = forms.CharField(label = 'Telefone', max_length=100)
    senha = forms.CharField(label = 'Senha', max_length=100)

class CadastroAnimalForm(forms.Form):
    especie = forms.ChoiceField(label = 'Espécie')
    raca = forms.ChoiceField(label = 'Raça')
    porte = forms.ChoiceField(label = 'Porte do animal')
    sexo = forms.ChoiceField(label = 'Sexo')
    dt_nascimento = forms.DateField(label = 'Data de nascimento' )


class CadastroMonitorForm(forms.Form):
    cpf = forms.CharField(label = 'Cpf', max_length=100)
    nome = forms.CharField(label = 'Nome', max_length=100)
    data_de_nasc = forms.DateField(label = 'Data de nascimento')
    genero = forms.ChoiceField(label = 'Gênero')
    endereco = forms.CharField(label = 'Endereço', max_length=100)
    tipo_residencia = forms.ChoiceField(label = 'Tipo de residência')
    email = forms.EmailField(label = 'E-mail', max_length=100)
    telefone = forms.CharField(label = 'Telefone', max_length=100)
    senha = forms.CharField(label = 'Senha', max_length=100)



