# Generated by Django 3.2.4 on 2022-02-27 14:20

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('esocial', '0023_auto_20210809_2056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='arquivos',
            name='arquivo',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(location='/Users/marcelovasconcellos/PycharmProjects/emensageria/arquivos'), upload_to='', verbose_name='Arquivo'),
        ),
        migrations.AlterField(
            model_name='certificados',
            name='certificado',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(location='/Users/marcelovasconcellos/PycharmProjects/emensageria/certificados'), upload_to='', verbose_name='Arquivo'),
        ),
        migrations.AlterField(
            model_name='eventos',
            name='verproc',
            field=models.CharField(default='1.3.0', max_length=20, null=True, verbose_name='Versão do processo'),
        ),
        migrations.AlterField(
            model_name='transmissor',
            name='tpinsc',
            field=models.IntegerField(choices=[(1, '1 - CNPJ'), (2, '2 - CPF')], verbose_name='Tipo de inscrição do empregador'),
        ),
        migrations.AlterField(
            model_name='transmissor',
            name='transmissor_tpinsc',
            field=models.IntegerField(choices=[(1, '1 - CNPJ'), (2, '2 - CPF')], verbose_name='Tipo de inscrição do transmissor'),
        ),
        migrations.AlterField(
            model_name='transmissoreventos',
            name='empregador_tpinsc',
            field=models.IntegerField(choices=[(1, '1 - CNPJ'), (2, '2 - CPF')], verbose_name='Tipo de inscrição do empregador'),
        ),
    ]
