# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - PaaS 平台 (BlueKing - PaaS System) available.
# Copyright (C) Tencent. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
from apigw_manager.plugin.utils import literal_unicode, yaml_dump, yaml_text_indent


class TestYamlDump:
    def test_yaml_dump(self):
        data = {"yaml": ["a", "b"]}
        result = yaml_dump(data)
        assert "yaml:\n- a\n- b\n" == result

    def test_yaml_dump_str(self):
        data = {"yaml": "127.0.0.1\n192.168.1.1"}
        result = yaml_dump(data)
        expected = """yaml: '127.0.0.1

  192.168.1.1'
"""
        assert expected == result

    def test_yaml_dump_literal_unicode(self):
        data = {"yaml": literal_unicode("127.0.0.1\n192.168.1.1")}

        result = yaml_dump(data)
        expected = """yaml: |-
  127.0.0.1
  192.168.1.1
"""
        assert expected == result


class TestYamlTextIndent:
    def test_yaml_text_indent(self):
        yaml_text = """a
b
c
"""
        result = yaml_text_indent(yaml_text, 2)
        expected = """a
  b
  c"""
        assert expected == result
