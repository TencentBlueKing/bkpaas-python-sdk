# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-蓝鲸 PaaS 平台(BlueKing-PaaS) available.
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
    app_verified_required: bool = False,
    resource_permission_required: bool = False,
    description_en: str = "",
    plugin_configs: Optional[List[Dict]] = None,
    match_subpath: bool = False,
) -> Dict[str, Dict[str, any]]:
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


# reference: https://github.com/TencentBlueKing/blueapps/blob/master/blueapps/conf/log.py
# changed
def get_logging_config_dict(
    log_level: str,
    is_local: bool,
    log_dir: str,
    app_code: str,
):
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
            # FIXME: remove this when move drf into apigw_manager
            "drf": {
                "handlers": ["apigw_manager"],
                "level": log_level,
                "propagate": True,
            },
        },
    }


# reference: https://github.com/TencentBlueKing/blueapps/blob/master/blueapps/conf/database.py
def get_default_database_config_dict(settings_module):
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
