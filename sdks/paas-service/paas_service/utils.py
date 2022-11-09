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
import os
import random
import string
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

from django.db import transaction
from paas_service.models import ResourceId, ServiceInstance, ServiceInstanceConfig
from paas_service.serializers import InstanceConfigSLZ

try:
    from django.http.request import limited_parse_qsl as parse_qsl
except ImportError:
    from django.http.request import parse_qsl


def gen_unique_id(
    name: str,
    namespace: str = "default",
    reserve_length: int = 12,
    divide_char: str = "-",
):
    """Generate an unique id via given name
    :param name 原字符串
    :param namespace 字符串命名空间，区分不同领域
    :param reserve_length 原字符串保留长度
    :param divide_char 特殊串和原串的连接符
    """
    prefix = name[:reserve_length]

    with transaction.atomic():
        # create a db instance for getting auto increment id
        resource_id = ResourceId.objects.create(namespace=namespace, uid=name)

        # update uid
        uid = prefix + divide_char + str(resource_id.id)
        resource_id.uid = uid
        resource_id.save(update_fields=["uid"])

    return resource_id.uid


def get_paas_app_info(instance: ServiceInstance) -> Optional[Dict]:
    """Get instance's related PaaS app infomations Dict"""
    config, _ = ServiceInstanceConfig.objects.get_or_create(instance=instance)
    if not config.was_initialized():
        return None

    slz = InstanceConfigSLZ(config)
    return slz.data["paas_app_info"]


def parse_redirect_params(redirect_url: str = None, **kwargs) -> Tuple[str, dict]:
    """
    从 redirect_url 构建出重定向指令的参数
    >>> parse_redirect_params(redirect_url="instance.index?a=1&b=1&b=2&c=3")
    ('instance.index', {'a': '1', 'b': '2', 'c': '3'})
    """

    if not redirect_url:
        return "instance.index", kwargs

    result = urlparse(redirect_url)
    params = dict(parse_qsl(qs=result.query))
    params.update(kwargs)
    return result.path, params


def generate_password(length=10):
    """生成随机的由大小写字母和数字组成的且至少包含 1 位 数字的密码."""
    password_chars = [random.choice(string.ascii_letters + string.digits) for _ in range(length)]
    password_chars.append(random.choice(string.digits))
    random.shuffle(password_chars)
    return "".join(password_chars)


# WR Algorithm start


class WRItem:
    """A single weighted-random items"""

    @classmethod
    def from_dict(cls, d):
        return WRItem(values=d["values"], weight=d.get("weight", 0))

    def __init__(self, values, weight=0):
        self.values = values
        self.weight = weight

    def __str__(self):
        return f"values={self.values} weight={self.weight}"


class WRItemList:
    # if the precision was set to 10, then an item which's weight is below 10% of the total weight
    # of all items is considered as zero and will never be choosed.
    precision = 100

    @classmethod
    def from_json(cls, items_list: List[Dict]):
        """Generate a list object from json, an example items_list:

        [
            {"values": ANY_THING, "weight": 10},
            {"values": ANY_THING, "weight": 3},
        ]
        """
        items = []
        for data in items_list:
            items.append(WRItem.from_dict(data))
        return WRItemList(items)

    def __init__(self, items: List[WRItem]):
        self.items = items
        self.initalize()

    def initalize(self):
        """Caculate weight and generate a list of size 100 in order to archive the random choice"""
        total_weight = sum(item.weight for item in self.items)
        if not total_weight:
            raise ValueError("no valid items given")

        self._list_of_choices = []
        for item in self.items:
            repeats = int(self.precision * (item.weight / total_weight))
            self._list_of_choices += [item] * repeats

    def get(self) -> WRItem:
        """Pick a item based on weighted-random algorithm"""
        return random.choice(self._list_of_choices)


# WR Algorithm end


def get_node_ip():
    """获取当前节点IP. 使用 helm 部署时, 在 values.yaml 中注入 NODE_IP 这个环境变量."""
    return os.environ.get("NODE_IP", None)


class Base36Handler:
    # keep lowercase
    BASE36 = "0123456789abcdefghijklmnopqrstuvwxyz"

    @classmethod
    def encode(cls, num: int, alphabet=BASE36):
        """Encode a positive number in Base X

        Arguments:
        - `num`: The number to encode
        - `alphabet`: The alphabet to use for encoding
        """
        if num == 0:
            return alphabet[0]
        arr = []
        base = len(alphabet)
        while num:
            num, rem = divmod(num, base)
            arr.append(alphabet[rem])
        arr.reverse()
        return ''.join(arr)

    @classmethod
    def decode(cls, encoded: str, alphabet=BASE36):
        """Decode a Base X encoded string into the number

        Arguments:
        - `string`: The encoded string
        - `alphabet`: The alphabet to use for encoding
        """
        base = len(alphabet)
        str_len = len(encoded)
        num = 0

        idx = 0
        for char in encoded:
            power = str_len - (idx + 1)
            num += alphabet.index(char) * (base ** power)
            idx += 1

        return num
