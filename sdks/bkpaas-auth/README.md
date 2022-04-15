# bkpaas-auth

蓝鲸 PaaS 平台内部服务使用的用户鉴权模块。

## 版本历史

详见 `CHANGES.md`。

## 开发指南

### 发布包

- 在 `bkpaas_auth/__init__.py`  文件中更新 `__version__`
- 在 `setup.py` 文件中更新 `version`
- 在 `pyproject.toml` 中更新 `version`
- 在 `CHANGES.md` 中添加对应的版本日志
- 执行 `poetry build` 命令在 dist 目录下生成当前版本的包。然后执行 `twine upload dist/* --repository-url {pypi_address} --username {your_name} --password {your_token}` 将其上传到 pypi 服务器上。

### 关于 setup.py

虽然在 [PEP 517](https://python-poetry.org/docs/pyproject/#poetry-and-pep-517) 规范里，Python 包不再需要 `setup.py` 文件。但真正少了 `setup.py` 文件后，会发现有些功能就没法正常使用，比如 pip 的可编辑安装模式、tox 等（[相关文档](https://github.com/python-poetry/poetry/issues/761)）。所以我们仍然需要它。

为了避免维护重复的 `pyproject.toml` 和 `setup.py` 文件，我们使用了 [dephell](https://github.com/dephell/dephell) 工具来自动生成 `setup.py` 文件。

- 安装 dephell
- 在根目录执行 `dephell deps convert --from pyproject.toml --to setup.py`

## 使用指南
1. 更新 settings：
```python
INSTALLED_APPS = [
    ...
    'bkpaas_auth',
    ...
]

MIDDLEWARE = [
    ...
    'bkpaas_auth.middlewares.CookieLoginMiddleware',
    ...
]

AUTHENTICATION_BACKENDS = [
    # [推荐] 使用内置的虚拟用户类型，不依赖于数据库表.
    'bkpaas_auth.backends.UniversalAuthBackend',
    # 如果项目需要保留使用数据库表的方式来设计用户模型, 则需要使用 DjangoAuthUserCompatibleBackend
    # 'bkpaas_auth.backends.DjangoAuthUserCompatibleBackend',
]

# 使用 bkpaas_auth 内置的基于内存的用户模型
# 如果项目需要保留使用数据库表的方式来设计用户模型, 可阅读 「关于AUTH_USER_MODEL」的部分说明
AUTH_USER_MODEL = 'bkpaas_auth.User'

# 用户登录态认证类型
BKAUTH_BACKEND_TYPE = "bk_token" # 可选值：bk_token/bk_ticket
# 验证用户登录态的 API，如 蓝鲸统一登录校验登录态的 API
BKAUTH_USER_COOKIE_VERIFY_URL = "http://bk-login-web/api/v3/is_login/"

# [可选]`BKAUTH_DEFAULT_PROVIDER_TYPE` 的值用于 JWT 校验时获取默认的用户认证类型。
BKAUTH_DEFAULT_PROVIDER_TYPE = 'RTX'  # 可选值：RTX/UIN/BK，详见 ProviderType
```

2. 在 app config 中进行 patch：

配置登录模块的 apps.py

```python
from bkpaas_auth.backends import DjangoAuthUserCompatibleBackend
from bkpaas_auth.models import User
from django.apps import AppConfig


class MyAppConfig(AppConfig):
    name = 'my_app'

    def ready(self):
        from bkpaas_auth.monkey import patch_middleware_get_user

        patch_middleware_get_user()
```

更新 `__init__.py`，配置 default_app_config
```
default_app_config = 'xxx.apps.MyAppConfig'
```

3. 配置日志（可选）
在 django settings 的 LOGGING 中，为 sdk 配置 logger，如

```python
LOGGING = {
    "handlers": {
        "root": {
            ...
        },
    },
    "loggers": {
        "bkpaas_auth": {
            "handlers": ["root"],
            "level": "WARNING",
            "propagate": True,
        },
    },
}
```

### 关于 AUTH_USER_MODEL

bkpaas-auth 内置的基于内存的不依赖于数据库表的用户模型, 如果需要复用原有的用户模型, 则需要使用 `DjangoAuthUserCompatibleBackend` 作为用户校验后端.

在默认情况下, `DjangoAuthUserCompatibleBackend` 会从 bkpaas-auth 获取到当前登录的用户信息, 并会根据用户信息尝试创建一个基于数据库的用户模型.
如果你有以下诉求, 则应当继承 `DjangoAuthUserCompatibleBackend`, 自行实现具体的业务逻辑:

1. 不希望自动创建基于数据库的用户模型:
```python


class YourDjangoAuthUserCompatibleBackend(DjangoAuthUserCompatibleBackend):
    create_unknown_user = False
```

2. 用户模型有与 django `auth.User` 不兼容的字段或其他需要初始化的字段:
```python

class YourDjangoAuthUserCompatibleBackend(DjangoAuthUserCompatibleBackend):
    def configure_user(self, db_user, bk_user: User):
        """
        Configure a user after creation and return the updated user.
        """
        ...
        return db_user
```

#### 和 [apigw-manager](../apigw-manager) 集成
该 SDK 可以和 apigw-manager 集成，完成网关 JWT 的校验，在 settings 中配置：
```python
INSTALLED_APPS += ["apigw_manager.apigw"]
AUTHENTICATION_BACKENDS += ["bkpaas_auth.backends.APIGatewayAuthBackend"]
MIDDLEWARE += [
    "apigw_manager.apigw.authentication.ApiGatewayJWTGenericMiddleware",  # JWT 认证
    "apigw_manager.apigw.authentication.ApiGatewayJWTAppMiddleware",  # JWT 透传的应用信息
    "apigw_manager.apigw.authentication.ApiGatewayJWTUserMiddleware",  # JWT 透传的用户信息
]
```

设置之后，通过 JWT 透传的用户态会验证后，会写入到 `request.user` 中。注意，配置了不认证用户的网关资源透传的请求，会生成一个有对应用户名的匿名用户对象（`is_authenticated` 为 `False`）。
