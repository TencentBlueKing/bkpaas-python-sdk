# -*- coding: utf-8 -*-
"""
 * TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-蓝鲸 PaaS 平台(BlueKing-PaaS) available.
 * Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
"""
import os
from contextlib import contextmanager

from django.core.management.commands.loaddata import Command as OriginCommand
from django.core.serializers import base
from django.core.serializers import python as _origin_module
from django.core.serializers.python import _get_model
from django.db import DEFAULT_DB_ALIAS, models

SKIP_ENV_VAR_RENDER_TERM = "SKIP_ENV_VAR_RENDER"


def Deserializer(object_list, *, using=DEFAULT_DB_ALIAS, ignorenonexistent=False, **options):
    """
    Deserialize simple Python objects back into Django ORM instances.

    It's expected that you pass the Python objects themselves (instead of a
    stream or a string) to the constructor
    """
    handle_forward_references = options.pop("handle_forward_references", False)
    field_names_cache = {}  # Model: <list of field_names>

    for d in object_list:
        # Look up the model and starting build a dict of data for it.
        try:
            Model = _get_model(d["model"])
        except base.DeserializationError:
            if ignorenonexistent:
                continue
            else:
                raise
        data = {}
        if "pk" in d:
            try:
                data[Model._meta.pk.attname] = Model._meta.pk.to_python(d.get("pk"))
            except Exception as e:
                raise base.DeserializationError.WithData(e, d["model"], d.get("pk"), None)
        m2m_data = {}
        deferred_fields = {}

        if Model not in field_names_cache:
            field_names_cache[Model] = {f.name for f in Model._meta.get_fields()}
        field_names = field_names_cache[Model]

        # Handle each field
        for (field_name, field_value) in d["fields"].items():

            if ignorenonexistent and field_name not in field_names:
                # skip fields no longer on model
                continue

            field = Model._meta.get_field(field_name)

            # Handle M2M relations
            if field.remote_field and isinstance(field.remote_field, models.ManyToManyRel):
                try:
                    values = base.deserialize_m2m_values(field, field_value, using, handle_forward_references)
                except base.M2MDeserializationError as e:
                    raise base.DeserializationError.WithData(e.original_exc, d["model"], d.get("pk"), e.pk)
                if values == base.DEFER_FIELD:
                    deferred_fields[field] = field_value
                else:
                    m2m_data[field.name] = values
            # Handle FK fields
            elif field.remote_field and isinstance(field.remote_field, models.ManyToOneRel):
                try:
                    value = base.deserialize_fk_value(field, field_value, using, handle_forward_references)
                except Exception as e:
                    raise base.DeserializationError.WithData(e, d["model"], d.get("pk"), field_value)
                if value == base.DEFER_FIELD:
                    deferred_fields[field] = field_value
                else:
                    data[field.attname] = value
            # Handle all other fields
            else:
                try:
                    if isinstance(field_value, (str, bytes)) and _should_render_by_env_vars():
                        field_value = os.path.expandvars(field_value)
                    data[field.name] = field.to_python(field_value)
                except Exception as e:
                    raise base.DeserializationError.WithData(e, d["model"], d.get("pk"), field_value)

        obj = base.build_instance(Model, data, using)
        yield base.DeserializedObject(obj, m2m_data, deferred_fields)


def _should_render_by_env_vars():
    return not os.environ.get(SKIP_ENV_VAR_RENDER_TERM, False)


@contextmanager
def patch(owner, attr, value):
    """Monkey patch context manager.

    with patch(os, 'open', myopen):
        ...
    """
    old = getattr(owner, attr)
    setattr(owner, attr, value)
    try:
        yield getattr(owner, attr)
    finally:
        setattr(owner, attr, old)


class Command(OriginCommand):
    def handle(self, *fixture_labels, **options):
        with patch(_origin_module, "Deserializer", Deserializer):
            super().handle(*fixture_labels, **options)
