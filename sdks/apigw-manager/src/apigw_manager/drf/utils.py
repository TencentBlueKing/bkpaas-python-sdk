# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 蓝鲸 PaaS 平台 (BlueKing-PaaS) available.
# Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://opensource.org/licenses/MIT
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import os
import random
import string
import sys

from typing import Dict, List, Optional


def gen_apigateway_resource_config(
    is_public: bool = True,
    allow_apply_permission: bool = True,
    user_verified_required: bool = False,
    app_verified_required: bool = True,
    resource_permission_required: bool = True,
    description_en: str = "",
    plugin_configs: Optional[List[Dict]] = None,
    match_subpath: bool = False,
) -> Dict[str, Dict[str, any]]:
    """用于辅助生成 bk-apigateway 的资源配置
    Args:
        is_public (bool, optional): 是否公开，不公开在文档中心/应用申请网关权限资源列表中不可见。默认 True
        allow_apply_permission (bool, optional):  是否允许申请权限，不允许的话在应用申请网关权限资源列表中不可见。默认 True
        user_verified_required (bool, optional): 是否开启用户认证 默认 False
        app_verified_required (bool, optional): 是否开启应用认证。默认 True
        resource_permission_required (bool, optional): 是否校验资源权限，是的话将会校验应用是否有调用这个资源的权限，前置条件：开启应用认证。默认 True
        description_en (str, optional): 资源的英文描述。默认 ""
        plugin_configs (Optional[List[Dict]], optional): 插件配置，类型为 List[Dict], 用于声明作用在这个资源上的插件，可以参考官方文档。默认 None.
        match_subpath (bool, optional): 匹配所有子路径，默认为 False. 默认 False
    Returns:
        Dict[str, Dict[str, any]]: _description_
    """

    # resource_permission_required  need app_verified_required
    if not app_verified_required:
        resource_permission_required = False

    if not plugin_configs:
        plugin_configs = []

    return {
        "x-bk-apigateway-resource": {
            "isPublic": is_public,
            "matchSubpath": match_subpath,
            "backend": {
                "name": "default",
                # filled by post process
                "method": "",
                # filled by post process
                "path": "",
                "matchSubpath": match_subpath,
                "timeout": 0,
            },
            "pluginConfigs": plugin_configs,
            "allowApplyPermission": allow_apply_permission,
            "authConfig": {
                "userVerifiedRequired": user_verified_required,
                "appVerifiedRequired": app_verified_required,
                "resourcePermissionRequired": resource_permission_required,
            },
            "descriptionEn": description_en,
        }
    }


def get_logging_config_dict(
    log_level: str,
    is_local: bool,
    log_dir: str,
    app_code: str,
):
    """用户生成蓝鲸 PaaS 运行时的 Django Logging 配置
    来源于蓝鲸开发框架，以获取最大的兼容性 reference: https://github.com/TencentBlueKing/blueapps/blob/master/blueapps/conf/log.py

    Args:
        log_level (str): 日志级别
        is_local (bool): 是否是本地开发，本地开发日志格式为文本格式，线上环境为 json 格式
        log_dir (str): 日志文件所在目录
        app_code (str): 应用 app_code

    Returns:
        logging config dict
    """
    log_class = "concurrent_log_handler.ConcurrentRotatingFileHandler"

    if is_local:
        log_name_prefix = os.getenv("BKPAAS_LOG_NAME_PREFIX", app_code)
        logging_format = {
            "format": (
                "%(levelname)s [%(asctime)s] %(pathname)s "
                "%(lineno)d %(funcName)s %(process)d %(thread)d "
                "\n \t %(message)s \n"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    else:
        rand_str = "".join(random.sample(string.ascii_letters + string.digits, 4))
        log_name_prefix = "{}-{}".format(os.getenv("BKPAAS_PROCESS_TYPE", "web"), rand_str)

        logging_format = {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "fmt": (
                "%(levelname)s %(asctime)s %(pathname)s %(lineno)d " "%(funcName)s %(process)d %(thread)d %(message)s"
            ),
        }
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": logging_format,
            "simple": {"format": "%(levelname)s %(message)s"},
        },
        "handlers": {
            "null": {"level": "DEBUG", "class": "logging.NullHandler"},
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "simple",
            },
            "root": {
                "class": log_class,
                "formatter": "verbose",
                "filename": os.path.join(log_dir, "%s-django.log" % log_name_prefix),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 5,
            },
            "component": {
                "class": log_class,
                "formatter": "verbose",
                "filename": os.path.join(log_dir, "%s-component.log" % log_name_prefix),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 5,
            },
            "mysql": {
                "class": log_class,
                "formatter": "verbose",
                "filename": os.path.join(log_dir, "%s-mysql.log" % log_name_prefix),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 5,
            },
            "celery": {
                "class": log_class,
                "formatter": "verbose",
                "filename": os.path.join(log_dir, "%s-celery.log" % log_name_prefix),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 5,
            },
            "apigw_manager": {
                "class": log_class,
                "formatter": "verbose",
                "filename": os.path.join(log_dir, "%s-apigw_manager.log" % log_name_prefix),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 5,
            },
        },
        "loggers": {
            "django": {"handlers": ["null"], "level": "INFO", "propagate": True},
            "django.server": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": True,
            },
            "django.request": {
                "handlers": ["root"],
                "level": "ERROR",
                "propagate": True,
            },
            "django.db.backends": {
                "handlers": ["mysql"],
                "level": log_level,
                "propagate": True,
            },
            # the root logger ,用于整个 project 的 logger
            "root": {"handlers": ["root"], "level": log_level, "propagate": True},
            # 组件调用日志
            "component": {
                "handlers": ["component"],
                "level": log_level,
                "propagate": True,
            },
            "celery": {"handlers": ["celery"], "level": log_level, "propagate": True},
            # other loggers...
            # 普通 app 日志
            "app": {"handlers": ["root"], "level": log_level, "propagate": True},
            # 框架
            "apigw_manager": {
                "handlers": ["apigw_manager"],
                "level": log_level,
                "propagate": True,
            },
        },
    }


def get_default_database_config_dict(settings_module):
    """用户生成蓝鲸 PaaS 运行时的 Django Database 配置
    由于蓝鲸 PaaS 内外版本差异，数据库相关的环境变量有所不同，所以需要通过这个函数做版本差异兼容。
    来源于蓝鲸开发框架，以获取最大的兼容性 reference: https://github.com/TencentBlueKing/blueapps/blob/master/blueapps/conf/database.py

    Args:
        django settings locals() 配置

    Returns:
        database config dict
    """
    if os.getenv("GCS_MYSQL_NAME") and os.getenv("MYSQL_NAME"):
        db_prefix = settings_module.get("DB_PREFIX", "")
        if not db_prefix:
            raise EnvironmentError("no DB_PREFIX config while multiple " "databases found in environment")
    elif os.getenv("GCS_MYSQL_NAME"):
        db_prefix = "GCS_MYSQL"
    elif os.getenv("MYSQL_NAME"):
        db_prefix = "MYSQL"
    else:
        # 对应非 GCS_MYSQL 或 MYSQL 开头的情况，需开发者自行配置
        sys.stderr.write("DB_PREFIX config is not 'GCS_MYSQL' or 'MYSQL_NAME'\n")
        return {}
    return {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ["%s_NAME" % db_prefix],
        "USER": os.environ["%s_USER" % db_prefix],
        "PASSWORD": os.environ["%s_PASSWORD" % db_prefix],
        "HOST": os.environ["%s_HOST" % db_prefix],
        "PORT": os.environ["%s_PORT" % db_prefix],
        "OPTIONS": {"isolation_level": "repeatable read"},
    }
