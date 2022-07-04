# 蓝鲸云 API 客户端
本项目基于 requests，提供了一种基于配置构建 SDK 的方案。

## Features
- 同时支持网关 API 与组件 API，使用体验一致
- 支持丰富的请求参数，包括魔法参数 data，requests.request 全部参数(除 data)、路径参数
  - 魔法参数 data，对于 GET/HEAD/OPTIONS 请求，参数将转换为 QueryString，其它请求方法，则转换为 json 格式的 Body
  - 支持从 django settings，Cookies 获取认证数据
  - verify 默认值为 True，请求 HTTPS 接口更安全
- 支持对 session 进行更新细粒度的控制，支持复用 session 的连接
- 灵活的响应处理方式
  - 支持校验响应状态码，获取响应的 json 数据
  - 支持获取原始的 requests Response 对象，进行更细粒度的控制
- 统一采用异常方案，出错时触发异常，如用户认证失败，请求状态码错误，请求网关超频，请求结果非 JSON 等
- 详细的错误日志，触发异常时，将打印请求的 curl 语句
- 支持数据懒加载，减小内存消耗
- 对 IDE 开发友好，SDK 支持常见 IDE 智能提示及补全；
- 兼容 Python2 及 Python3 的类型补全；

## SDK 使用样例

### 1. 使用 Client

#### 1.1 直接调用 Client，并解析响应
该方式下，SDK 会根据配置自动做请求和响应的转换和解析，隐藏文档已描述的通用细节（如参数位置，响应格式等），用户仅需关注具体字段传递，以减轻使用成本。

```python
from demo.client import Client

# 需提供网关地址 endpoint，环境 stage 默认为 prod
client = Client(stage="prod", endpoint="http://bkapi.example.com/api/test/")
# 根据需求，提供应用认证、用户认证信息
client.update_bkapi_authorization(
    bk_app_code="xxx",
    bk_app_secret="yyy",
    bk_username="admin",
)

# 发起请求，检查 response.raise_for_status()，返回 response.json() 数据
result = client.api.test({"key": "value"})
print(result["ok"])
```

#### 1.2 直接调用 Client，不解析响应
该方式下，SDK 不会有过多的封装，仅做参数传递，调用 requests 进行请求后返回响应，用户对请求流程有更细粒度的控制。

```python
from demo.client import Client

# 需提供网关地址 endpoint，环境 stage 默认为 prod
client = Client(stage="prod", endpoint="http://bkapi.example.com/api/test/")
# 根据需求，提供应用认证、用户认证信息
client.update_bkapi_authorization(
    bk_app_code="xxx",
    bk_app_secret="yyy",
    bk_username="admin",
)

# 发起请求，但不对响应进行解析，直接返回 requests Response 对象，用户可对响应进行更细粒度的控制
response = client.api.test.request({"key": "value"})
result = response.json()
print(result["ok"])
```

### 2. 使用 shortcuts，简化 Client 创建
为降低使用成本，SDK 提供了更简单地创建 Client 的方式：get_client_by_request、get_client_by_username

#### 2.1 使用 get_client_by_request
此方式需提供 django request 对象

get_client_by_request
```python
from demo.shortcuts import get_client_by_request

# 需提供 django request，client 可从 request 中获取当前用户名或从 Cookies 中获取用户登录态
# 并且，支持从 django settings 获取默认的 bk_app_code、bk_app_secret、endpoint，也可通过参数指定
client = get_client_by_request(request)
result = client.api.test({"key": "value"})
print(result["ok])
```

#### 2.2 使用 get_client_by_username
get_client_by_username
```python
from demo.shortcuts import get_client_by_username

# 支持从 django settings 获取默认的 bk_app_code、bk_app_secret、endpoint，也可通过参数指定
client = get_client_by_username("admin")
result = client.api.test({"key": "value"})
print(result["ok])
```

### 3. 复用 session

支持复用 session 连接，提高请求效率

```python
from demo.shortcuts import get_client_by_username

client = get_client_by_username("admin")
with client:
    result = client.api.test({"key": "value"})
    print(result["ok])
```

## SDK 配置说明
SDK 支持通过配置更改一些默认的行为，Django settings 配置优先级高于环境变量。

| 变量名                               | 描述                                   | 类型   | 格式                              | 默认值                     | Django 配置 | 环境变量 | 别名              |
| ------------------------------------ | -------------------------------------- | ------ | --------------------------------- | -------------------------- | ----------- | -------- | ----------------- |
| BK_APP_CODE                          | 应用代号                               | string | `"my_app"`                        |                            | 支持        | 支持     | BKPAAS_APP_ID     |
| BK_APP_SECRET                        | 应用密钥                               | string | `"my_secret"`                     |                            | 支持        | 支持     | BKPAAS_APP_SECRET |
| DEFAULT_STAGE_MAPPINGS               | 指定对应网关的默认环境                 | dict   | `{"my_gateway": "prod"}`          |                            | 支持        |          |                   |
| BK_API_CLIENT_ENABLE_SSL_VERIFY      | 是否开启 SSL 证书验证                  | bool   | `True`                            |                            | 支持        |          |                   |
| BK_API_AUTHORIZATION_COOKIES_MAPPING | 指定 Cookie 和认证参数的映射关系       | dict   | `{"key": "cookie"}`               | `{"bk_token": "bk_token"}` | 支持        |          |                   |
| BK_API_URL_TMPL                      | 网关地址模板，支持 `{api_name}` 占位符 | string | `"http://{api_name}.example.com"` |                            | 支持        | 支持     |                   |
| BK_COMPONENT_API_URL                 | 组件 API 网关地址                      | string | `"http://esb.example.com"`        |                            | 支持        | 支持     |                   |
| DEFAULT_BK_API_VER                   | 默认组件版本号                         | string | `"v1"`                            | `"v2"`                     | 支持        | 支持     |                   |
| BK_API_USE_TEST_ENV                  | 是否使用组件测试环境                   | bool   | `False`                           | `False`                    | 支持        |          |                   |


## 模型

主要模型定义的类关系请参考 [class_diagram.md](./class_diagram.md)

### Session
在 `requests.Session` 的基础之上，增加特有业务逻辑封装：
- 公共参数设置
- 超时设置
- 路径参数设置

同时扩展原有 hooks 机制，为后续进阶需求提供扩展。
session 管理状态及完成每一个接口调用。

### Operation
借用 openapi 概念，表示一个路径和方法绑定的操作，相当于网关中的资源及 ESB 中的组件（对应的某个方法），作为配置及调用入口，封装以下属性：
- 方法
- 路径
- 默认配置

Operation 不发起具体的请求，对应的请求会在调用时交给 Manager 完成。

### Manager
管理 Session 和 Operation，作为整体的“门面”，可以扩展实现为一个 Client。
其本身不保存状态，而是提供封装，将状态转换成 Session 的基本属性。
其本身也不完成接口调用，而是管理调用流程，处理好请求创建，响应解析和异常处理等步骤。

### OperationGroup
Operation 的分组，在 ESB 中，可以用系统名作为分组，而在网关中，即使不区分系统，但为了避免资源和 Client 自身属性的冲突，也使用默认分组管理。

### Client
Manager 的子类，管理 OperationGroups 以及其定义的 Operations，针对具体的业务场景中，提供更符合业务流程的封装。

## 易用性设计
在现有的网关文档中，有较大的一类文档基于程序自动生成，其中虽有描述请求方法，认证方式，调用示例，但因为基于模板生成的原因，其内容较为死板和繁琐。如果由人去机械化地拼接接口的每个配置细节，因为这种方式是反人性的，会有较大的出错概率，由此会带来额外的不必要的咨询和反馈。因此希望 SDK 能够自动帮用户去处理这些机械化的配置，只需要关注核心的调用参数即可完成任务。此外，SDK 本身又可看做某个版本的离线文档，通过 SDK 合理的智能提示和补全，也可以免除用户的查找和排除成本。

### 接口定义
在接口的设计上，有以下目标：

- 避免覆盖和重写 `__init__` 方法；
- 使用静态显式的定义方式；
- 为了减轻内存压力，使用懒加载进行初始化；
- 没有具体的业务逻辑；

因此接口定义使用类属性 + property 的方式进行：

```python
class Group(OperationGroup):
    test = bind_property(Operation, name="test", method="GET", path="/test/")
```

如上示例，声明了一个 API 分组 `Group`。`test` 是该分组下注册在网关的一个资源名称，其方法为 `GET`，资源路径为 `/test/`。

```python
class Client(APIGatewayClient):
    api = bind_property(Group)
```

上方示例基于 `Group` 这个 api 分组定义了一个网关客户端，使用 `Client` 可直接调用这个网关下的所有资源接口。
在接口定义中，`bind_property` 方法实现了懒加载属性的功能，在调用时自动初始化对应类型，同时基于类型注解实现了泛型，可以帮助 IDE 建立类型系统。

### IDE 优化
#### 智能补全
得益于 `bind_property` 实现的泛型，IDE 可以完成 `Client -> Group -> Operation` 整个调用链的智能补全。而 `Operation` 自身的补全方式，完全基于 `Operation` 定义，仅需维护本项目即可。

#### 接口文档
为了优化 Python3 的调用逻辑，同时兼容 Python2 的使用，SDK 生成定义的同时，也会生成对应的存根文件（.pyi），将接口文档作为 docstring，在 IDE 中引用即可看到文档：

```python
class Group(OperationGroup):
    @property
    def test(self) -> Operation:
        """test api"""

class Client(APIGatewayClient):
    @property
    def api(self) -> Group:
        """api resources"""
```

存根文件在运行时不会被执行，因此使用等价的 `property` 描述资源定义，通过 docstring 暴露文档（也是唯一方式）。

## 进阶使用
### 统计指标
启用前需安装额外依赖：

```shell
pip install bkapi_client_core[monitor]
```

执行以下代码启用 prometheus 指标统计的功能：

```python
from bkapi_client_core import prometheus

prometheus.enable()
```

开启后，sdk 会对每次请求进行指标的统计，暴露到 */metrics* 接口，指标如下：

| 名称                            | 类型      | 描述         | 维度                    |
| ------------------------------- | --------- | ------------ | ----------------------- |
| bkapi_requests_duration_seconds | Histogram | 请求耗时     | operation,method        |
| bkapi_requests_body_bytes       | Histogram | 请求体大小   | operation,method        |
| bkapi_responses_body_bytes      | Histogram | 响应体大小   | operation,method        |
| bkapi_responses_total           | Counter   | 响应总数     | operation,method,status |
| bkapi_failures_total            | Counter   | 请求失败总数 | operation,method,error  |