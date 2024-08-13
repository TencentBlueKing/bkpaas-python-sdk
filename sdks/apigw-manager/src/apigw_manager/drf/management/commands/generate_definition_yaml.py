# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-蓝鲸 PaaS 平台(BlueKing-PaaS) available.
# Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://opensource.org/licenses/MIT
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

"""
this command will generate the definition.yaml

it will copy a template definition.yaml from apigw_manager into the project. And if the version of apigw_manager changes,
the template definition.yaml will be updated.
"""

import shutil

from django.conf import settings
from django.core.management.base import BaseCommand
from pathlib import Path


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        current_dir = Path(__file__).resolve().parent
        source_file = current_dir / "data" / "definition.yaml"

        define_dir = Path(settings.BASE_DIR)
        definition_path = define_dir / "definition.yaml"

        self.stdout.write(f"will generate {definition_path} from {source_file}")
        shutil.copyfile(source_file, definition_path)

        self.stdout.write(f"generated {definition_path} from {source_file} success")
