# -*- coding: utf-8 -*-
from enum import Enum


class Category(int, Enum):
    """Paas service categories"""

    DATA_STORAGE = 1
    MONITORING_HEALTHY = 2


# Login 服务的重定向链接字段名
REDIRECT_FIELD_NAME = "c_url"
