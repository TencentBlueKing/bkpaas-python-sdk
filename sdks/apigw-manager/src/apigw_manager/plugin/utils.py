# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 蓝鲸 PaaS 平台 (BlueKing-PaaS) available.
# Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://opensource.org/licenses/MIT
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.


from typing import Any

import yaml

# NOTE:
# not literal_unicode:  yaml: '127.0.0.1\n192.168.1.1'
# with literal_unicode:  yaml: |-
#                          127.0.0.1
#                          192.168.1.1


class literal_unicode(str):
    pass


def literal_unicode_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


yaml.add_representer(literal_unicode, literal_unicode_representer)


def yaml_dump(data: Any) -> str:
    return yaml.dump(data)


def yaml_text_indent(text: str, indent: int) -> str:
    """indent the yaml text, for render yaml text in another `yaml:|-`
        - yaml: |-
            a
    b
    c

        TO:
        - yaml: |-
            a
            b
            c

        Args:
            text (str): the yaml text
            indent (int): the indent number

        Returns:
            str: the indented yaml text
    """
    lines = text.splitlines()
    first_line = lines[0]

    indent_spaces = " " * indent
    other_lines = [f"{indent_spaces}{line}" for line in lines[1:]]
    return "\n".join([first_line] + other_lines)
