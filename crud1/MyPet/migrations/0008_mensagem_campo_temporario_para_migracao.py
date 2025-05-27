# Seu novo arquivo de migração (ex: 0008_add_campo_temporario.py)

import datetime
from django.db import migrations, models
from django.utils import timezone # IMPORTE ISTO

class Migration(migrations.Migration):

    dependencies = [
        ('MyPet', '0007_conversa_mensagem'), # Deve ser a migração que você "fakou" no Passo 2
    ]

    operations = [
        migrations.AddField(
            model_name='mensagem',
            name='data_envio',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now), # Usamos default temporariamente para preencher linhas existentes
            preserve_default=False,
        ),
        # Se houver uma operação para adicionar/remover 'campo_temporario_para_migracao',
        # ela pode vir logo depois desta.
    ]