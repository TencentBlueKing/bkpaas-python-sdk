# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making
蓝鲸智云 - PaaS 平台 (BlueKing - PaaS System) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except
in compliance with the License. You may obtain a copy of the License at

    http://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software distributed under
the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the License for the specific language governing permissions and
limitations under the License.

We undertake not to change the open source license (MIT license) applicable
to the current version of the project delivered to anyone in the future.
"""
# Generated by Django 3.2.12 on 2022-04-26 04:29
from django.apps.registry import Apps
from django.db import migrations, models
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


def copy_field(app_label, model_name, from_field, to_field):
    def migrate(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
        updated = []
        model = apps.get_model(app_label, model_name)
        for item in model.objects.all():
            value = getattr(item, from_field)
            setattr(item, to_field, value)
            updated.append(item)
        if hasattr(model, "bulk_update"):
            model.objects.bulk_update(updated, fields=[to_field])
        else:
            for item in updated:
                item.save(update_fields=[to_field])

    return migrate


class Migration(migrations.Migration):

    dependencies = [
        ('paas_service', '0007_auto_20220426_0225'),
    ]

    operations = [
        migrations.RenameField(
            model_name='service',
            old_name='description',
            new_name='description_zh_cn',
        ),
        migrations.RenameField(
            model_name='service',
            old_name='display_name',
            new_name='display_name_zh_cn',
        ),
        migrations.RenameField(
            model_name='service',
            old_name='instance_tutorial',
            new_name='instance_tutorial_zh_cn',
        ),
        migrations.RenameField(
            model_name='service',
            old_name='long_description',
            new_name='long_description_zh_cn',
        ),
        migrations.RenameField(
            model_name='specdefinition',
            old_name='display_name',
            new_name='display_name_zh_cn',
        ),
        migrations.RenameField(
            model_name='specification',
            old_name='display_name',
            new_name='display_name_zh_cn',
        ),
        migrations.AddField(
            model_name='service',
            name='description_en',
            field=models.CharField(blank=True, max_length=1024, verbose_name='简介'),
        ),
        migrations.AddField(
            model_name='service',
            name='display_name_en',
            field=models.CharField(default='', max_length=128, verbose_name='服务全称'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='service',
            name='instance_tutorial_en',
            field=models.TextField(blank=True, verbose_name='实例内页介绍'),
        ),
        migrations.AddField(
            model_name='service',
            name='long_description_en',
            field=models.TextField(blank=True, verbose_name='详细介绍'),
        ),
        migrations.AddField(
            model_name='specdefinition',
            name='display_name_en',
            field=models.CharField(blank=True, max_length=128, verbose_name='展示名称'),
        ),
        migrations.AddField(
            model_name='specification',
            name='display_name_en',
            field=models.CharField(blank=True, max_length=64, verbose_name='展示名称'),
        ),
        migrations.RunPython(code=copy_field('paas_service', 'service', 'description_zh_cn', 'description_en')),
        migrations.RunPython(code=copy_field('paas_service', 'service', 'display_name_zh_cn', 'display_name_en')),
        migrations.RunPython(
            code=copy_field('paas_service', 'service', 'instance_tutorial_zh_cn', 'instance_tutorial_en')
        ),
        migrations.RunPython(
            code=copy_field('paas_service', 'service', 'long_description_zh_cn', 'long_description_en')
        ),
        migrations.RunPython(
            code=copy_field('paas_service', 'specdefinition', 'display_name_zh_cn', 'display_name_en')
        ),
        migrations.RunPython(
            code=copy_field('paas_service', 'specification', 'display_name_zh_cn', 'display_name_en')
        ),
    ]
