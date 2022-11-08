# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2021-02-23 09:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paas_service', '0005_auto_20210202_1055'),
    ]

    operations = [
        migrations.RenameField(
            model_name='service',
            old_name='logo',
            new_name='logo_url'
        ),
        migrations.AddField(
            model_name='service',
            name='logo',
            field=models.TextField(blank=True, null=True, verbose_name='服务 logo base64'),
        ),
    ]