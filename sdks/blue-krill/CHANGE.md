## Change logs

### 1.2.8

- Loosen the version restriction on sub-dep `dataclasses`

### 1.2.7

- Fix：支持不配置加密算法类型，使用默认类型 Fernet

### 1.2.6

- Loosen the version restriction on sub-dep `cryptography`

### 1.2.5

- Feature: MySQLProbe support both pymysql and mysqlclient

### 1.2.4

- Fix: 限制 bkrepo 创建项目管理员的权限

### 1.2.3

- Feature: `blue_krill.aysnc_utils.django_utils` provides some helper functions related to Django + Celery.

### 1.2.2

- Feature: `blue_krill.redis_tools.sentinel.SentinelBackend` to support redis sentinel client
- Feature: `blue_krill.monitoring.probe.redis.RedisSentinelProbe` to support redis sentinel liveness probe

### 1.2.1

- Feature: the pkg version of pyjwt updated from 1.7.0 to 2.4.0

### 1.2.0

- Enhance: Multiple updates and bugfixes on `connections.ha_endpoint_poll` module, it's
  APIs are easier to use now.

### 1.1.2
- 移除 HAEndpointPool 拦截 exempt_exceptions 的冗余日志

### 1.1.1
- Feature: add `MutableURL` to obscure password field in url

### 1.1.0

- Feature: add more JWT utilities in blue_krill.auth
- Feature: add .set_data() hook for APIError type (#51)
- Feature: (web std error) support lazy str, such as Django's i18n gettext (#54)
- Feature: Make blue-krill supports PEP-561 by adding "py.typed" file
- Chore(pkg): update django-environ pkg version to 0.8.1 (#53)
- Fix type checking issues for `StructuredEnum.EnumField`, `ErrorCode`

### 1.0.15

- `blue_krill.models.better_loaddata` 支持 django>=3

### 1.0.14

- `blue_krill.models.fields.EncryptField` 支持 django>=3

### 1.0.13

- `blue_krill.web.drf_util` 增加依赖注入工具
- `blue_krill` 支持 Python 3.8/3.9/3.10
- `blue_krill` 支持 3.8/3.9/3.10 版本

### 1.0.12

- `blue_krill.cubing_case` 兼容 python3.6 正则对驼峰命名解析的 bug.

### 1.0.11
- `blue_krill.storages.blobstore` 增加 `DownloadFailedError` 和 `UploadFailedError` 异常

### 1.0.10

- 增加 `blue_krill.termcolors` 模块, 提供了往终端输出彩色文本的工具库.

### 1.0.9

- `blue_krill.storages.blobstore.bkrepo` 模块增加超时机制

### 1.0.8

- `blue_krill.cubing_case` 增加各个命名方法互相转换的工具库.

### 1.0.7

- `blue_krill.storages.blobstore.base.BlobStore` 增加 delete_file 的函数签名.

### 1.0.6

- `blue_krill.storages.blobstore.bkrepo` 模块增加错误重试机制

### 1.0.5

- `StructuredEnum` 中新增 `get_choices`、`get_labels` 和 `get_values` 方法
- 重构 `StructuredEnum` 的 `get_choice_label` 方法，支持 unhashable 的枚举

### 1.0.4

- 对象存储模块支持签发上传链接

### 1.0.3

- 增加健康探针功能

### 1.0.2

- 允许 SecureEnv 设置自定义解密方法

### 1.0.1

- 增加 better-loaddata 命令

### 1.0.0

- 重新格式化，去除敏感信息
- 调整 encrypt.legacy 模块

### 0.0.17

- 增加 `blue_krill.web` 模块，包含标准错误码 `std_error` 与 DRF 工具模块 `drf_utils`
- 增加 `blue_krill.async_utils` 模块，包含异步轮询工具包 `poll_task`

### 0.0.14

- 增加 blobstore 模块
  - 支持 上传/下载/签发分享链接 三个基础功能
  - 对接 `s3对象存储` 和 `蓝鲸二进制仓库` 两个后端服务 

### 0.0.13

- 增加 data_types.enum 模块
  - 增加 FeatureFlag、FeatureFlagField 用于定义功能标记(FeatureFlag)
  - 增加 StructuredEnum 用于定义带有额外属性的枚举类

### 0.0.12

- 增加 toml 模块依赖

### 0.0.11

- 增加多版本管理工具 editionctl

### 0.0.10

- 增加 `blue_krill.secure.dj_environ` 模块，支持 Django 框架读取加密环境变量
- 增加 `bk-secure` 命令，辅助环境变量加密时使用

### 0.0.9

- 添加 `blue_krill.auth.jwt` 模块，供访问基于 JWT 鉴权的服务时使用

### 0.0.8

- `PrometheusExposeHandler` 增加 `extra_registries` 参数
