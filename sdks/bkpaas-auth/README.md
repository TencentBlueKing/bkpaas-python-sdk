# bkpaas-auth

蓝鲸 PaaS 平台内部服务使用的用户鉴权模块。

## 版本历史

详见 `CHANGES.md`。

## 开发指南

### 发布包

- 在 `bkpaas_auth/__init__.py`  文件中更新 `__version__`
- 在 `pyproject.toml` 中更新 `version`
- 在 `CHANGES.md` 中添加对应的版本日志
- 执行 `poetry build` 命令在 dist 目录下生成当前版本的包。然后执行 `twine upload dist/* --repository-url {pypi_address} --username {your_name} --password {your_token}` 将其上传到 pypi 服务器上。

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

启用多租户模式时, 需要更新上面的 settings
```python
# 启用多租户模式
BKAUTH_ENABLE_MULTI_TENANT_MODE = True

# 用户登录态认证类型
BKAUTH_BACKEND_TYPE = "bk_token" # 只能选择：bk_token

# 验证用户信息的网关 API(租户版本)
# 如 BK_API_URL_TMPL.format(api_name="bk-login") + "/prod/login/api/v3/open/bk-tokens/userinfo/"
BKAUTH_USER_INFO_APIGW_URL = ""

# [可选]`BKAUTH_DEFAULT_PROVIDER_TYPE` 的值用于 JWT 校验时获取默认的用户认证类型。
BKAUTH_DEFAULT_PROVIDER_TYPE = 'BK'  # 只能选择：BK
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

> 说明: 启用多租户模式后, user 会增加 tenant_id 和 display_name 两个字段，可以通过 `request.user.tenant_id` 获取租户 ID, 通过 `request.user.display_name` 获取用户展示名。

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

### UserTimezoneMiddleware 用户时区中间件

`UserTimezoneMiddleware` 是一个用于根据用户配置的时区自动设置 Django 时区的中间件。

#### 功能特性

- 自动从用户对象的 `time_zone` 属性读取时区配置
- 时区配置无效时自动回退到默认时区 `settings.TIME_ZONE`
- 响应返回时自动重置时区，避免线程复用导致的时区污染

#### 使用说明

1. **配置要求**：
   - 用户对象必须包含 `time_zone` 属性（字符串类型）
   - 时区名称必须符合 IANA 时区数据库标准（如 "Asia/Shanghai"）

2. **中间件顺序**：
   - 必须放在所有用户认证中间件之后
   - 建议放在 `CookieLoginMiddleware` 之后

3. **执行逻辑**：
   - 未登录用户跳过时区设置
   - 读取用户 `time_zone` 属性并验证有效性
   - 时区无效时记录警告日志并回退到默认时区
   - 响应处理完成后自动重置时区

#### 日志输出示例

```bash
# 时区激活成功
DEBUG: Activated timezone 'Asia/Shanghai' for user 'test_user'

# 时区无效警告
WARNING: Invalid time_zone 'Invalid/Timezone' for user 'test_user', fallback to default. Error: ...
```

#### 注意事项

- 确保用户管理系统正确设置 `time_zone` 属性
- 时区名称必须为有效的 IANA 时区标识符
- 中间件依赖 Django 的时区功能，确保 `USE_TZ = True`
