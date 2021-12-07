# Blue krill

Python 常用工具包模块。

## 使用指南

### 1. blue_krill.secure

加解密、安全相关的工具与模块。

#### 1.1 dj_environ 模块

dj_environ 的主要目的是在 [django-environ](https://github.com/joke2k/django-environ) 之上，增加可以阅读加密环境变量的能力。如需使用，首先需要设置密文环境变量：

```bash
export DATABASE_URL='<使用 bk-secure 加密后的字符串>'
export FOO='<使用 bk-secure 加密后的字符串>'
```

然后在 `settings` 模块中，初始化 `SecureEnv` 对象并使用它读取对应配置：

```python
from blue_krill.secure.dj_environ import SecureEnv

# 初始化并加载 .env 文件内容
sec_env = SecureEnv()
environ.Env.read_env()

# 读取为数据库配置
DATABASES['default'] = sec_env.db()

# 读取为普通配置
FOO = sec_env('FOO')
```

#### 1.2 bk-secure 脚本

bk-secure 主要用于配合 dj_environ 模块生成加密环境变量（或配置文件）。使用前，先将 `BK_FERNET_KEY` 设为你所使用的加密 key。一般情况下，这个值等同于 Django 项目的 `BKKRILL_ENCRYPT_SECRET_KEY` 配置项：

```
export BK_FERNET_KEY='... ...'
```

执行 `encrypt` 加密某段明文：

```console
❯ bk-secure encrypt
Input string: mysql://u:p@localhost/foo
The encrypted token is: gAAAAABfKUtKIBzYc_gyQL-j9TmI35O1d0auLQfYeso6D8Q77ZC9PIuv26ABPFlOQSSPDzT3HcVrhI1K3XwU5Xfs6gP6iAe8RhEAJJhMktp7CKzn7p7imNk=
```

执行 `decrypt` 解密某段密文：

```console
❯ bk-secure decrypt
Input token: gAAAAABfKUtKIBzYc_gyQL-j9TmI35O1d0auLQfYeso6D8Q77ZC9PIuv26ABPFlOQSSPDzT3HcVrhI1K3XwU5Xfs6gP6iAe8RhEAJJhMktp7CKzn7p7imNk=
The decrypted result is: mysql://u:p@localhost/foo
```

使用 `edit` 以明文方式编辑某段密文，并输出新的密文：

```console
❯ bk-secure edit
Input token: gAAAAABfKUtKIBzYc_gyQL-j9TmI35O1d0auLQfYeso6D8Q77ZC9PIuv26ABPFlOQSSPDzT3HcVrhI1K3XwU5Xfs6gP6iAe8RhEAJJhMktp7CKzn7p7imNk=
# 将弹出编辑器界面修改明文，可通过 $EDITOR 环境变量设置编辑器
The new value is: mysql://u:p@localhost/foo2
The encrypted new value is: gAAAAABfKUui5_YUVxoYEYQG61RSRX1Ll3s1dgkZ5nUEJbCxakWHSyo3AKZFv3GuoQ7cH2Hm5LEU2QDK8C3G-_iog0TmqSbVkIYf0WnksH2DGgedldfbwhs=
```

### 2. blue_krill.editions

多版本开发相关工具模块

#### 2.1 editionctl 工具

`editonctl` 是用来帮助开发需要支持多版本 Python 项目的工具，使用该工具前，请先把你的项目目录组织成下面这种结构：

```raw
├── editionctl.toml
├── editions
│   ├── ee
│   │   └── ee.py
│   └── te
│       └── te.py
└── main
    └── main.py
```

其中：

- `editions`：仅保存不同版本所特有的源码文件
- `main`：项目主目录

#### 2.1.1 创建配置文件

要使用 `editonctl`，首先需要在项目内创建配置文件 `editionctl.toml`。比如，针对上面的项目结构，我们可以创建这样的配置文件：

```toml
# 项目主目录
project_root = 'main'
# 项目各版本所在目录
editions_root = 'editions'

[[editions]]
# 版本名称
name = "TE"
# 版本相对路径
rel_directory = 'te'

[[editions]]
name = "EE"
rel_directory = 'ee'
```

> 更多配置文件相关说明，可执行 `editionctl help` 查看。

#### 2.1.2 在版本之间切换

在不同版本间切换，需要使用 `editionctl activate {EDITION_NAME}` 命令。执行该命令后，工具会将指定版本下的所有源码文件，拷贝到 `project_root` 中。

```bash
$ editionctl activate EE
[2020-12-17 16:51:37,312] INFO: Edition EE activated, linker is default
```

> 为了避免由工具拷贝的文件被意外提交到源码仓库，这些文件会被添加到 `{project_root}/.gitignore` 中。

#### 2.1.3 重置多版本

假如你想要清除所有由 `editionctl` 工具创建的源码文件，可以执行 `editionctl reset` 命令。执行该命令将删除所有多版本相关文件，只保留主目录。

#### 2.1.4 进入开发模式

在开发多版本项目时，`editions_root` 目录下的当前版本相关文件会被频繁修改。正常情况下，每次修改版本文件后，我们都要手动重新执行 `activate` 命令重新同步文件。

为了简化这个过程，我们可以使用 `editionctl develop`。

执行 `editionctl develop` 命令后，工具将会持续监听当前 `edition` 目录下的任何改动。如果监听到新改动，则自动触发同步机制。

```
$ editionctl develop
[2020-12-17 16:56:34,385] INFO: Start watching editions/ee directory for edition EE...
```

### 3. blue_krill.data_types.enum

枚举相关的数据类型。

### 3.1 FeatureFlag

功能标记(Feature Flag)用于控制当前用户能否感知到某个功能/特性，只提供**开启(enabled)**和**关闭(disabled)**两个状态, 分别对应于布尔值的 True/Flase。
为了避免各项目重复造轮子, blue_krill 抽象出通用的 FeatureFlag 模型, 同时也提供类似于`枚举(Enum)`的API, 降低使用成本。

#### 3.1.1 如何定义 FeatureFlag

就像定义普通的 Python Class 一样, 定义 FeatureFlag 只需要继承 `blue_krill.data_types.enum::FeatureFlag` 即可。
```python
from blue_krill.data_types.enum import FeatureFlag, FeatureFlagField


class UserFeatureFlag(FeatureFlag):
    # 使用类属性声明 FeatureFlagField 时, name 属性会通过描述符协议自动设置, 无需额外指定.
    WEBCONSOLE = FeatureFlagField(label="使用 WEBConsole")
    CREATE_SMART_APP = FeatureFlagField(label="创建 Smart 应用")
    ...
```

#### 3.1.2 如何添加额外的 FeatureFlag

不同于`枚举值(Enum)`, FeatureFlag 允许在运行过程中动态添加额外的字段或修改已有字段的默认值。

```python
# 添加额外的 FeatureFlag 时, 需要制定对应的名称.
UserFeatureFlag.register_feature_flag(FeatureFlagField(name="CHOOSE_SOURCE_ORIGIN", label="选择源码来源"))
```

### 3.2 StructuredEnum

考虑到我们使用`枚举值(Enum)`时, 往往会给枚举值添加额外的描述字段，为了避免各项目重复造轮子，blue_krill 基于 `Enum` 实现了 StructuredEnum，可以基于配套的 `EnumField` 定义带有额外描述内容的枚举值。

```python
from blue_krill.data_types.enum import EnumField, StructuredEnum


class DiffType(str, StructuredEnum):
    ADDED = EnumField("added", label="新增")
    DELETED = EnumField("deleted", label="删除")
    NOT_MODIFIED = EnumField("not_modified", label="未改动")
```

### 4. blue_krill.storages.blobstore

对象存储服务的简单封装, 目前支持 **上传**, **下载**, **生成预签名URL** 三个接口.

#### 4.1 S3Store

S3 协议的 BlobStore 实现, 使用时需要额外安装 boto3=='^1.4.3', 可参考以下代码进行实例化:
```python
from blue_krill.storages.blobstore.s3 import S3Store


store = S3Store(
    bucket="your-bucket",
    aws_access_key_id='your-access-key',
    aws_secret_access_key='your-secret-key',
    endpoint_url='your-s3-endpoint',
    # Optional
    region_name='your-region, default is `us-east-1`',
    signature_version='your-signature-version, default is s3v4',
)
```

#### 4.2 BKGenericRepo

底层服务是 **蓝鲸通用二进制仓库** 的底层实现, 可参考以下代码进行实例化:

```python
from blue_krill.storages.blobstore.bkrepo import BKGenericRepo


store = BKGenericRepo(
    bucket='your-bucket',
    project='your-project-id',
    endpoint_url='',
)
```

### 5. blue_krill.web

`blue_krill.web` 主要存放与 Web 开发有关的工具集。

#### 5.1 blue_krill.web.std_error

该模块内包含标准的错误码功能。`std_error` 最常见的用法，是通过 `ErrorCode` 定义一套错误码集合：

```python
from blue_krill.web.std_error import ErrorCode

class ErrorCodes:
    CREATE_ERROR = ErrorCode('创建失败')
    DELETE_ERROR = ErrorCode('删除失败')

# 实例化一个全局对象
error_codes = ErrorCodes()
```

当你要抛出某个特定错误时，可以使用下面的语句：

```python
raise error_codes.CREATE_ERROR

# 使用 .f() / .format() 方法追加错误信息
raise error_codes.CREATE_ERROR.f('追加说明')

# 传递 replace=True 替换错误信息
raise error_codes.CREATE_ERROR.f('替换信息', replace=True)
```

> 注意：`APIError` 是不可变类型，调用 `format()` 会克隆并返回一个新对象，而非修改现有对象。

当程序抛出 `APIError` 异常后，为了让用户正常看到错误响应，你必须在 Web 框架里捕获并处理该类异常。

##### 5.1.1 在框架内捕获 APIError 异常

视 Web 框架的不同，捕获与处理 `APIError` 的方式会略有区别，以 `DRF` 框架为例。要捕获 `APIError` 异常，我们首先得创建一个新函数：

```python
# file: my_module.py
from blue_krill.web.std_error import APIError

def custom_exception_handler(exc, context):
    if isinstance(exc, APIError):
        # 你可以随意修改这里的响应数据结构
        data = {
            'code': exc.code,
            'detail': exc.message,
        }
        return Response(data, status=exc.status_code)
    # ... 其他异常处理撮箕
```

创建完函数后，下一步是修改项目配置，将 `EXCEPTION_HANDLER` 调整为该异常捕获函数：

```python
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'my_module.custom_exception_handler'
}
```

配置完成后，每当你在项目里抛出 `error_codes.CREATE_ERROR`，用户便会看到下面的错误信息：

```json
{
    "code": 'CREATE_ERROR',
    "detail": '创建失败'
}
```

##### 5.1.2 ErrorCode API 说明

在创建 `ErrorCode` 对象时，除了可以传入必须的 `message` 参数，还支持传入许多可选的个性化参数：

- `message`: 必选，错误详情信息，可包含字符串模板变量
- `code_num`: 可选，数字错误代码，默认为 -1
- `extra_formatter`：可选，额外的错误信息格式化函数
- `status_code`: 该错误推荐使用的 HTTP 错误代码，默认为 400

这些参数各自有着不同的用途，比如，通过定义 `extra_formatter` 属性，你可以调整 `APIError` 拼装错误信息 `message` 的逻辑。

以下面的代码为例：

```python
# formatter 函数接收两个参数：默认错误信息、当前异常对象
def _format_message(message, exc):
    # 将错误码拼装到错误信息前
    return f'code: {exc.code} - {message}'

class ErrorCodes:
    foo = ErrorCode('foo message', extra_formatter=_format_message)
```

当你抛出 `foo` 错误码时，由于我们使用了自定义的 `message` 格式化函数，错误详情会变成这样：`code: foo - foo message`。

`ErrorCode` 的 `message` 除了能使用普通字符串以外，还支持字符串模板功能。举个例子，假如你定义的 `message` 是 `name={name}`，那么，当你抛出异常时，可以用 `.format()` 方法传入模板变量，对错误信息进行二次渲染。

```python
raise error_codes.FOO # 1
raise error_codes.FOO.format(name='foobar') # 2
```

1. 用户看到的错误信息是 `name={name}`
2. 用户看到的错误信息会变为 `name=foobar`

#### 5.2 blue_krill.web.drf_utils

`drf_utils` 模块内包含许多与 DRF 框架有关的工具。

##### 5.2.1 stringify_validation_error

`stringify_validation_error()` 会将由 DRF 框架抛出的 `ValidationError` 校验错误异常对象，转换为可读性更好的错误提示文字。

比如，下面的异常对象：

```python
ValidationError({'foo': {'bar': [ErrorDetail('err1'), ErrorDetail('err2')]}})
```

可以被转换为：`['foo.bar: err1', 'foo.bar: err2']` 这样的文字内容。

### 6. blue_krill.async_utils

#### 6.1 blue_krill.aysnc_utils.poll_tasks

`poll_tasks` 是一个用来执行长时间轮询任务的异步工具模块。它的工作原理是每隔几秒钟，拉起一个 `celery` 任务进行轮询逻辑。当轮询应该结束时，带着结果回调。

要创建一个新的轮询任务，你首先要编写一个 `TaskPoller` 类。

```python
from blue_krill.async_utils.poll_task import TaskPoller, PollingResult

class MyTaskPoller(TaskPoller):

    # 通过定义下面的属性，修改当前 Poller 类的默认配置
    # max_retries_on_error = 10
    # overall_timeout_seconds = 3600 * 24 * 7
    # default_retry_delay_seconds = 10

    def query(self) -> PollingResult:
        result = request_api()
        if result:
            return PollingResult.done(data={'result': ...})
        else:
            return PollingResult.doing(data={'current_value': ...})
```

`TaskPoller` 的配置属性含义如下：

- `max_retries_on_error`：当轮询抛出异常的总次数，超过该值后，不再继续下次轮询
- `overall_timeout_seconds`：当轮询的总执行时间（从第一次轮询开始后计算）超过该值，结束本次轮询并返回超时结果
- `default_retry_delay_seconds`：两次轮询行为之间相隔的秒数

每个 `TaskPoller` 类都必须重写 `query()` 方法，在其中实现**每次**轮询的真正逻辑。在 `query()` 方法内部，你可以从以下属性读取与本次轮询相关的数据：

- `self.params`：轮询任务启动时的参数，通常为字典 `Dict`
- `self.metadata`：本次轮询任务的元数据，里面包含轮询开始时间、已完成的轮询次数等数据

`query()` 方法需要返回一个 `PollingResult` 结果，来控制接下来的轮询流程。

不同的轮询结果，代表着不同含义：

- `PollingResult.done()`：表示整个轮询任务已结束，不会启动新异步任务
- `PollingResult.doing()`：表示应该继续轮询，会派生新的异步任务

在实例化 `PollingResult` 时，你可以通过 `data` 属性传入额外数据。该数据对于不同状态的轮询结果来说，有着不同含义。

- 当轮询返回 `done()` 结果时，`data` 会通过回调传递到 `CallbackHandler` 的 `result` 参数里
- 当轮询仍在继续，返回 `doing()` 结果时，可在 `TaskPoller` 类中，通过 `self.metadata.last_polling_data` 获取**上次轮询**的 `data` 内容

创建完 TaskPoller 类后，下一步是编写 ResultHandler 结果回调类。

##### 6.1.1 定义 CallbackHandler 类

一个标准的 `CallbackHandler` 如下所示：

```python
from blue_krill.async_utils.poll_task import (
    CallbackHandler,
    CallbackResult,
    TaskPoller
)

class MyHandler(CallbackHandler):

    def handle(self, result: CallbackResult, poller: TaskPoller):
        # 通过 result 和 poller 执行回调逻辑
        pass
```

根据轮询的不同执行结果，`CallbackResult.status` 会有几种不同的状态：

- `CallbackStatus.NORMAL`：轮询正常结束，`Poller` 返回的轮询结果为 `DONE` / '.doing()'
- `CallbackStatus.TIMEOUT`：轮询超过了规定时间（``overall_timeout_seconds``）仍未结束，判定为超时
- `CallbackStatus.EXCEPTION`：轮询时发生了异常，且总异常次数超过最大值：`max_retries_on_error`

为了方便操作，你可以直接调用 `result.is_exception` 属性来获知本次轮询是否正常结束。任何状态不为 `NORMAL` 的结果，`.is_exception` 值都为 `True`。

##### 6.1.2 启动轮询任务

当你定义好 `Poller` 与 `CallbackHandler` 类后，可以用以下方式启动一次轮询任务：

```python
# params = {'some_field': 'value'}
MyTaskPoller.start(params, MyHandler)
```

通过执行 `TaskPoller` 类的 `start()` 方法，程序会派生出一个名为 `poll_task.check_status_until_finished` 的 `celery` 异步任务，之后触发 `TaskPoller` 的 `query()` 方法，不断开始轮询。

### 7. blue_krill.monitoring.probe

`blue_krill.monitoring.probe` 模块提供了常见的健康探针功能。

#### 7.1 blue_krill.monitoring.probe.tcp

`blue_krill.monitoring.probe.tcp` 模块提供了通用的 TCP 健康探针, 可检测是否能建立 TCP 连接。

```python
# Usage:
from blue_krill.monitoring.probe.tcp import TCPProbe, InternetAddress


class SomeTCPProbe(TCPProbe):
    name: str = "some"
    address: InternetAddress = InternetAddress(host="localhost", port=8080)


report = SomeTCPProbe().report()
```

#### 7.2 blue_krill.monitoring.probe.http

`blue_krill.monitoring.probe.http` 模块提供了通用的 HTTP 健康探针, 可检测 HTTP 服务是否正常工作。

```python
# Usage
from blue_krill.monitoring.probe.http import HttpProbe


class SomeHttpProbe(HttpProbe):
    name: str = "some"
    url: str = "http://localhost/ping"


report = SomeHttpProbe().report()


class SomeHttpWithAuth(HttpProbe):
    name: str = "some"
    url: str = "http://localhost/ping"
    params: Dict = {"token": "dummy"}
    headers: Dict = {"Authorization": "Basic YWxhZGRpbjpvcGVuc2VzYW1l"}


report = SomeHttpWithAuth().report()
```

#### 7.3 blue_krill.monitoring.probe.mysql

`blue_krill.monitoring.probe.mysql` 模块提供了通用的 MySQL 健康探针, 可检测 MySQL 服务是否正常工作, 该模块依赖 pymysql。

```python
# Usage:
from blue_krill.monitoring.probe.mysql import MySQLProbe, MySQLConfig


class SomeMySQLProbe(MySQLProbe):
    name: str = "some"
    config = MySQLConfig(host="localhost", port=3306, username="root", password="root", database="information_schema")


report = SomeMySQLProbe().report()
```

#### 7.4 blue_krill.monitoring.probe.redis

`blue_krill.monitoring.probe.redis` 模块提供了通用的 Redis 健康探针, 可检测 Redis 服务是否正常工作, 该模块依赖 redis。

```python
# Usage:
from blue_krill.monitoring.probe.redis import RedisProbe


class SomeRedisProbe(RedisProbe):
    name: str = "some"
    redis_url: str = "redis://localhost:6379/0"


report = SomeRedisProbe().report()
```

### 8 blue_krill.cubing_case
`blue_krill.cubing_case` 增加各个方法互相转换的工具库.

#### 8.1 blue_krill.cubing_case.RegexCubingHelper
基于多种正则将多种模式混合的字符串进行拆分，转换并组合成新的字符串的工具类。

#### 8.2 blue_krill.cubing_case.CommonCaseConvertor
在 `blue_krill.cubing_case.RegexCubingHelper` 之上的一个封装实现，将指定的多种模式的字符串转化成常见的方法，包含：
- 驼峰式：`CubingCase`
- 小写开头的驼峰式：`cubingCase`
- 小写下划线式：`cubing_case`
- 大写下划线式：`CUBING_CASE`
- 小写连字符式：`cubing-case`
- 大写下划线式：`CUBING-CASE`
- 小写点分式：`cubing.case`
- 大写下划线式：`CUBING.CASE`
- 小写空格分隔式：`cubing case`

#### 8.3 blue_krill.cubing_case.shortcuts
`blue_krill.cubing_case.shortcuts` 是 `blue_krill.cubing_case.CommonCaseConvertor` 的一个快捷方式，内置了其转换目标的所有源模式，可以实现所有模式的正反转换。


## 开发指南

首先安装 [poetry](https://github.com/python-poetry/poetry)，之后在项目目录下执行 `poetry env use python3.6` 初始化开发用虚拟环境。然后用 `poetry shell` 命令激活虚拟环境。

- 执行 `poetry install` 安装所有依赖
- 使用 `pytest -s .` 执行所有单元测试

在开发时，如果想让某项目安装本地目录里的 blue-krill 模块，首先切换到对应项目虚拟环境，然后在 blue-krill 目录执行 `pip install -e .` 

### 使用 tox 执行单元测试

为了测试包在不同 Python 版本下的稳定性，我们使用了 tox 工具。在项目目录下执行 `tox` 即可执行所有的单元测试。

### 发布包

首先，执行 `poetry build` 命令在 dist 目录下生成当前版本的包(需要检查 dist 目录中的内容是否符合预期，避免上传其他版本覆盖)。然后执行 `twine upload dist/* --repository-url {pypi_address} --username {your_name} --password {your_token}` 将其上传到 pypi 服务器上。

### 关于 setup.py

虽然在 [PEP 517](https://python-poetry.org/docs/pyproject/#poetry-and-pep-517) 规范里，Python 包不再需要 `setup.py` 文件。但真正少了 `setup.py` 文件后，会发现有些功能就没法正常使用，比如 pip 的可编辑安装模式、tox 等（[相关文档](https://github.com/python-poetry/poetry/issues/761)）。所以我们仍然需要它。

为了避免维护重复的 `pyproject.toml` 和 `setup.py` 文件，我们使用了 [dephell](https://github.com/dephell/dephell) 工具来自动生成 `setup.py` 文件。

- 安装 dephell
- 在根目录执行 `dephell deps convert --from pyproject.toml --to setup.py`
