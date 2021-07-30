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
import logging
from dataclasses import asdict, dataclass
from typing import Dict, List

from blue_krill.monitoring.probe.base import Issue, VirtualProbe

try:
    import pymysql
except ImportError as _e:
    raise ImportError('Error loading mysql module: %s.\n' 'Did you install pymysql?' % _e) from _e


logger = logging.getLogger(__name__)


@dataclass
class MySQLConfig:
    host: str
    port: int
    user: str
    password: str
    database: str


class MySQLProbe(VirtualProbe):
    """
    Usage:
        class SomeMySQLProbe(MySQLProbe):
            name: str = "some"
            config = MySQLConfig(...)
    """

    config: MySQLConfig

    def diagnose(self) -> List[Issue]:
        try:
            connection = pymysql.connect(**asdict(self.config))
        except pymysql.err.OperationalError:
            logger.exception("Can't connect to MySQL server on %s", self.config.host)
            return [Issue(fatal=True, description=f"Can't connect to MySQL server on {self.config.host}")]
        except Exception:  # pylint: disable=broad-except
            logger.exception("Unexpect exception occur when connecting to MySQL server on %s", self.config.host)
            return [Issue(fatal=True, description=f"Can't connect to MySQL server on {self.config.host}")]

        try:
            with connection.cursor() as cursor:
                sql = "SELECT 1"
                cursor.execute(sql)

            connection.commit()
        except Exception as e:  # pylint: disable=broad-except
            return [Issue(fatal=True, description=f"connection to mysql<{self.name}> failed: {e}")]
        finally:
            connection.close()
        return []


def transfer_django_db_settings(django_db_settings: Dict) -> MySQLConfig:
    """transfer django db settings to MySQLConfig"""

    return MySQLConfig(
        **{
            "host": django_db_settings['HOST'],
            "port": int(django_db_settings['PORT']),
            "user": django_db_settings['USER'],
            "password": django_db_settings['PASSWORD'],
            "database": django_db_settings['NAME'],
        }
    )
