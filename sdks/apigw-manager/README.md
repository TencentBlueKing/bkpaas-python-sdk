# apigw-manager

蓝鲸 API 网关管理 SDK 是一个用于管理 API 网关的工具，它提供了一套完整的工具和功能，可以帮助您更轻松地管理 API 网关，提高系统的安全性和可靠性。

1. Django Command：SDK 提供了 Django Command，支持网关注册、同步、发布等功能。您可以根据需要编排指令，以满足您的特定需求，并集成到您的项目自动执行 API 网关同步过程，以便更轻松地管理 API 网关。

2. Docker 镜像：对于非 Django 项目，提供了 Docker 基础镜像，封装了 SDK 同步网关的相关功能，以便非 Django 项目轻松管理 API 网关。

3. Django 中间件：SDK 还提供了 Django 中间件，用于解析 API 网关请求后端接口时添加的请求头 X-Bkapi-JWT，以方便后端服务校验请求是否来自 API 网关。这个中间件可以确保只有来自蓝鲸 API 网关的请求才能访问您的后端服务，从而提高系统的安全性。

## 安装
基础安装：

```shell
pip install apigw-manager
```

如果需要使用 apigw-manager 提供的 Django 中间件解析来自 API 网关的 X-Bkapi-JWT，可以安装：

```shell
pip install "apigw-manager[cryptography]"
```

## 功能

- 通过预定义的 YAML 文件，您可以轻松地执行网关创建、更新、发布和资源同步操作，从而简化 API 网关管理过程。
- 使用 Django 中间件，您可以解析蓝鲸 API 网关的 X-Bkapi-JWT 请求头，确保只有来自 API 网关的请求才能访问您的后端服务，提升系统安全性。

## 根据 YAML 同步网关配置

SDK 同步网关配置到 API 网关，支持多种方案:
- 直接使用 Django Command 同步：此方案适用于 Django 项目；Django 项目，可直接执行 SDK 提供的 Django Command 指令
- 通过镜像方式同步：此方案适用于非 Django 项目；非 Django 项目，无法直接执行 SDK 提供的 Django Command 指令

### 准备工作

同步网关配置到 API 网关，需要准备网关配置、资源配置、资源文档、自定义同步脚本等数据，可参考目录：
```
support-files
├── definition.yaml         # 维护网关、环境、资源文档路径、主动授权、发布等配置，但不包含资源配置
├── resources.yaml          # 维护资源配置；资源配置可通过 API 网关管理端直接导出，数据量较大，因此单独管理
├── bin
│   └── sync-apigateway.sh  # 自定义同步脚本，Django 项目也可以自定义 Django Command
├── bk_apigw_docs_demo.tgz  # 资源文档归档文件，可选；可通过 API 网关管理端导出；与资源文档目录 apidocs 二选一
└── apidocs                 # 资源文档目录，可选；可通过 API 网关管理端导出并解压，或者直接维护 markdown 格式文档文件
    ├── zh                  # 中文文档目录
    │   └── anything.md
    └── en                  # 英文文档目录
        └── anything.md
```

#### 1. definition.yaml

用于定义网关、环境等配置，为了简化使用，使用以下模型进行处理：

```
  Template(definition.yaml)                     YAML
+--------------------------+        +----------------------------+
|                          |        |                            |       +--------------------------------------+
| ns1:                     |        | ns1:                       |       |                                      |
|   key: {{environ.KEY1}}  |        |   key: value_from_environ  |------>| api1({"key": "value_from_environ"})  |
|                          | Render |                            |       |                                      |
|                          +------->+                            | Load  |                                      |
| ns2:                     |        | ns2:                       |       |                                      |
|   key: {{settings.KEY2}} |        |   key: value_from_settings |------>| api2({"key": "value_from_settings"}) |
|                          |        |                            |       |                                      |
|                          |        |                            |       +--------------------------------------+
+--------------------------+        +----------------------------+
```

definition.yaml 中可以使用 Django 模版语法引用和渲染变量，内置以下变量：
- `settings`：Django 提供的配置对象，优先适合用于使用 Django Command 同步
- `environ`：环境变量，推荐镜像同步方式使用

推荐在一个文件中统一进行定义，用命名空间区分不同配置间的定义，definition.yaml 样例：

目前有两种配置文件版本：spec_version=1/2,主要区别就是stage相关的配置方式上有一些不一样。
新接入系统请使用 spec_version=2， 就有系统如果需要配置多个stage/配置多个backend， 建议也升级到spec_version=2并变更相关yaml配置。
区别如下：
spec_version: 1
```yaml
# definition.yaml 配置文件版本号，必填，固定值 1/2
# 1：key为stage; 只支持单个 stage， 并且 proxy_http只能配置一个后端服务
spec_version: 1
stage:
  name: "prod"
  description: "描述"
  description_en: "English description"
  proxy_http:
    timeout: "65"
    upstreams:
      loadbalance: "roundrobin"
      hosts:
        - host: "http://httpbin.org"
          weight: 100
```

spec_version: 2
```yaml
# definition.yaml 配置文件版本号，必填，固定值 1/2
# 2：key为stages; 支持多个stages，并且每个stage可以配置多个backend后端服务
spec_version: 2
stages:
  - name: "prod"
    description: "描述"
    description_en: "English description"
    vars:
      status_500: "500"
    backends:
      - name: "default"
        config:
          timeout: 60
          loadbalance: "roundrobin"
          hosts:
            - host: "http://httpbin.org"
              weight: 100

      - name: "backend1"
        config:
          timeout: 60
          loadbalance: "roundrobin"
          hosts:
            - host: "http://httpbin.org"
              weight: 100
```
> 📢 注意：如果之前接入过的，建议将 sepc_version改成 2，并将原先 stage:改成 stages: []


整体的样例：

```yaml
# definition.yaml 配置文件版本号，必填，固定值 1/2
spec_version: 2  # 如果之前接入过的，建议将 sepc_version改成 2，并将原先 stage:改成 stages: []

# 定义发布内容，用于命令 `create_version_and_release_apigw`
release:
  # 发布版本号；
  # 资源配置更新，需更新此版本号才会发布资源版本，此版本号和 sdk 版本号一致，错误设置会影响调用方使用
  version: 1.0.0
  # 版本标题
  title: ""
  # 版本描述
  comment: ""

# 定义网关基本信息，用于命令 `sync_apigw_config`
apigateway:
  description: "描述"
  # 网关的英文描述，蓝鲸官方网关需提供英文描述，以支持国际化
  description_en: "English description"
  # 是否公开；公开，则用户可查看资源文档、申请资源权限；不公开，则网关对用户隐藏
  is_public: true
  # 标记网关为官方网关，网关名需以 `bk-` 开头，可选；非官方网关，可去除此配置
  api_type: 1
  # 网关维护人员，仅维护人员有管理网关的权限
  maintainers:
    - "admin"

# 定义环境信息，用于命令 `sync_apigw_stage`
stages:
  - name: "prod"
    description: "描述"
    # 环境的英文名，蓝鲸官方网关需提供，以支持国际化
    description_en: "English description"
    # 环境变量；如未使用，可去除此配置
    # vars:
    #   key: "value"
    # 代理配置
    # proxy_http 与 backends 二选一， 推荐使用 backends 方式配置
    # 网关版本 <= 1.13.3, 只支持一个后端服务, 默认是 default
    # 网关版本 1.13.3之后引入 backends 配置方式,支持多后端服务
    # 注意: 资源中引用的 backend 一定要配置， 否则会导入失败,不配置则会选  择 default 后端服务
    #      如果 backends 没有配置 default 且 resource 未指定 backend 则会导致版本发布校验失败
    backends:
    - name: "default"
      config:
      timeout: 60
      loadbalance: "roundrobin"
      hosts:
         # 网关调用后端服务的默认域名或IP，不包含Path，比如：      http://api.example.com
        - host: ""
          weight: 100

    - name: "service1"
      config:
        timeout: 60
        loadbalance: "roundrobin"
        hosts:
         - host: ""
           weight: 100

    # 环境插件配置
    # plugin_configs:
    #     - type: bk-rate-limit
    #       yaml: |-
    #         rates:
    #           __default:
    #           - period: 1
    #             tokens: 100
    #     - type: bk-header-rewrite
    #       yaml: |-
    #         set:
    #           - key: test
    #             value: '2'
    #         remove: []
    #     - type: bk-cors
    #       yaml: |-
    #         allow_origins: '*'
    #         allow_methods: '*'
    #         allow_headers: '*'
    #         expose_headers: '*'
    #         max_age: 86400
    #         allow_credential: false



# 主动授权，网关主动给应用，添加访问网关所有资源或者具体某个资源的权限；
# 用于命令 `grant_apigw_permissions`
grant_permissions:
  - bk_app_code: "{{ settings.BK_APP_CODE }}" ## 环境变量方式："{{ environ.BK_APP_CODE }}"
    # 授权维度，可选值：
    # gateway: 按网关授权，包括网关下所有资源，以及未来新创建的资源
    # resource: 按资源维度授权
    grant_dimension: "gateway"
    # 如果是按照 resource 维度授权,需要提供如下的具体resource_name
    # resource_names:
    #   - resource_name_1 
    #   - resource_name_2   

# 应用申请指定网关所有资源的权限，待网关管理员审批后，应用才可访问网关资源；
# 用于命令 `apply_apigw_permissions`
# apply_permissions:
#   - gateway_name: "{{ settings.BK_APIGW_NAME }}" ## 环境变量方式："{{ environ.BK_APIGW_NAME }}"
#     # 权限维度，可选值：gateway，按网关授权，包括网关下所有资源，以及未来新创建的资源
#     grant_dimension: "gateway"

# 为网关添加关联应用，关联应用可以通过网关 bk-apigateway 的接口操作网关数据；每个网关最多可有 10 个关联应用；
# 用于命令 `add_related_apps`
related_apps:
  - "{{ settings.BK_APP_CODE }}" ## 环境变量方式："{{ environ.BK_APP_CODE }}"

# 定义资源文档路径，用于命令 `sync_resource_docs_by_archive`；
# 资源文档的目录格式样例如下，en 为英文文档，zh 为中文文档，创建归档文件可使用指令 `tar czvf xxx.tgz en zh`：
# ./
# - en
#   - get_user.md
# - zh
#   - get_user.md
resource_docs:
  # 资源文档的归档文件，可为 tar.gz，zip 格式文件
  archivefile: "{{ settings.BK_APIGW_RESOURCE_DOCS_ARCHIVE_FILE }}" ## 环境变量方式："{{ environ.BK_APIGW_RESOURCE_DOCS_ARCHIVE_FILE }}"
  # 资源文档目录，basedir 与 archivefile 二者至少一个有效，若同时存在，则 archivefile 优先
  basedir: "{{ settings.BK_APIGW_RESOURCE_DOCS_BASE_DIR }}" ## 环境变量方式："{{ environ.BK_APIGW_RESOURCE_DOCS_BASE_DIR }}"
```

**注意：**
- 同步资源或者环境相关配置后，需要创建版本并发布才能生效，发布数据定义于 definition.yaml `release`
- 资源配置 resources.yaml 变更时，需要更新 definition.yaml `release` 中的版本号 version，以便正确创建资源版本及 SDK
- 详细的插件配置见：[插件配置说明](docs/plugin-use-guide.md)
#### 2. resources.yaml

用于定义资源配置，建议通过网关管理端导出。为了方便用户直接使用网关导出的资源文件，资源定义默认没有命名空间。

样例可参考：[resources.yaml](examples/django/use-custom-script/support-files/resources.yaml)

> 详细的插件配置见：[插件配置说明](docs/plugin-use-guide.md)

#### 3. apidocs（可选）

资源文档，资源文档为 markdown 格式。资源文档的文件名，应为 `资源名称` + `.md` 格式，假如资源名称为 get_user，则文档文件名应为 get_user.md。
将资源的中文文档放到目录 `zh` 下，英文文档放到目录 `en` 下，如果某语言文档不存在，可忽略对应目录。

文档文件目录样例如下：
```
.
├── en
│   ├── create_user.md
│   └── get_user.md
└── zh
    ├── create_user.md
    └── get_user.md
```

导入资源文档时，可以直接使用资源文档归档文件，也可以使用资源文档目录。参考上文 definition.yaml 样例，
在项目 definition.yaml 文件中，修改资源文档相关配置 resource_docs：
```yaml
resource_docs:
  # 资源文档的归档文件，可为 tar.gz，zip 格式文件；创建归档文件可使用指令 `tar czvf xxx.tgz en zh`
  # archivefile: "{{ settings.BK_APIGW_RESOURCE_DOCS_ARCHIVE_FILE }}"
  # 资源文档目录，basedir 与 archivefile 二者至少一个有效，若同时存在，则 archivefile 优先
  # basedir: "{{ settings.BK_APIGW_RESOURCE_DOCS_BASE_DIR }}"
  basedir: "support-files/apidocs/"
```

#### 4. 国际化支持

##### 网关描述国际化
在 definition.yaml 中利用字段 description_en 指定英文描述。样例：

```yaml
apigateway:
  description: "xxxx"
  description_en: "This is the English description"
  is_public: true
  maintainers:
    - "admin"
```
##### 环境描述国际化
在 definition.yaml 中利用字段 description_en 指定英文描述。样例：

```yaml
stage:
  name: "prod"
  description: "xxx"
  description_en: "This is the English description"
```
##### 资源描述国际化
可以在resources.yaml对应的 `x-bk-apigateway-resource` 的 `descriptionEn` 指定英文描述
```yaml
x-bk-apigateway-resource:
isPublic: false
allowApplyPermission: false
matchSubpath: false
backend:
  type: HTTP
  method: get
  path: /anything
  matchSubpath: false
  timeout: 0
  upstreams: {}
  transformHeaders: {}
authConfig:
  appVerifiedRequired: true
  userVerifiedRequired: false
  resourcePermissionRequired: false
descriptionEn: anything

```
### 方案一：直接使用 Django Command 同步

此方案适用于 Django 项目，具体请参考 [sync-apigateway-with-django.md](docs/sync-apigateway-with-django.md)

### 方案二：通过镜像方式同步

此方案适用于非 Django 项目，具体请参考 [sync-apigateway-with-docker.md](docs/sync-apigateway-with-docker.md)


## 如何获取网关公钥

后端服务如需解析 API 网关发送的请求头 X-Bkapi-JWT，需要提前获取该网关的公钥。获取网关公钥，有以下方案。

### 1. 根据 SDK 提供的 Django Command 拉取

在同步网关数据时，直接添加以下 Command 拉取网关公钥。网关公钥将保存在 model Context 对应的库表 apigw_manager_context 中，SDK 提供的 Django 中间件将从表中读取网关公钥。

```bash
# 默认拉取 settings.BK_APIGW_NAME 对应网关的公钥
python manage.py fetch_apigw_public_key

# 拉取指定网关的公钥
python manage.py fetch_apigw_public_key --gateway-name my-gateway
```

### 2. 直接获取网关公钥，配置到项目配置文件

服务仅需接入一些固定的网关部署环境时，可在网关管理端，网关基本信息中查询网关公钥，并配置到项目配置文件。

蓝鲸官方网关，需要自动注册并获取网关公钥，可联系蓝鲸官方运营同学，在服务部署前，由官方提前创建网关，并设置网关公钥、私钥，同时将网关公钥同步给后端服务。
具体可参考 helm-charts 仓库的 README。

### 3. 通过网关公开接口，拉取网关公钥

API 网关提供了公钥查询接口，后端服务可按需根据接口拉取网关公钥，接口信息如下：
```bash
# 将 bkapi.example.com 替换为网关 API 地址，
# 将 gateway_name 替换为待查询公钥的网关名，
# 提供正确的蓝鲸应用账号
curl -X GET 'https://bkapi.example.com/api/bk-apigateway/prod/api/v1/apis/{gateway_name}/public_key/' \
  -H 'X-Bkapi-Authorization: {"bk_app_code": "my-app", "bk_app_secret": "secret"}'
```

响应样例：

```json
{
    "data": {
        "public_key": "your public key"
    }
}
```

注意事项：
- 拉取公钥时，不能实时拉取，需要添加缓存（实时拉取会导致整体接口性能下降）

## 校验请求来自 API 网关

### 场景一：Django 项目

要在后端服务中认证 API 网关传递过来的请求头 `X-Bkapi-JWT`，可以通过在 settings 中的 MIDDLEWARE 中添加以下 Django 中间件。这样，在请求处理过程中，会自动解析请求头中的 X-Bkapi-JWT，并将相关信息添加到 request 对象中。

```python
MIDDLEWARE += [
    "apigw_manager.apigw.authentication.ApiGatewayJWTGenericMiddleware",  # JWT 认证，解析请求头中的 X-Bkapi-JWT，获取 request.jwt 对象
    "apigw_manager.apigw.authentication.ApiGatewayJWTAppMiddleware",  # 根据 request.jwt，获取 request.app 对象
]
```

添加以上两个中间件后，request 对象中将会添加 `request.jwt` 和 `request.app` 两个对象。这些对象包含了网关名、当前请求的蓝鲸应用 ID 等信息。具体内容可参考下文。

如果需要在 request 对象中获取当前请求用户 `request.user` 对象，除了上面的中间件外，还需要添加一个中间件以及 AUTHENTICATION_BACKENDS：

```python
# 添加中间件
MIDDLEWARE += [
    "apigw_manager.apigw.authentication.ApiGatewayJWTUserMiddleware",  # 根据 request.jwt，获取 request.user 对象
]

# 添加 AUTHENTICATION_BACKENDS
AUTHENTICATION_BACKENDS += [
    "apigw_manager.apigw.authentication.UserModelBackend",
]
```

注意，Django 中间件 ApiGatewayJWTGenericMiddleware 解析 `X-Bkapi-JWT` 时，需要获取网关公钥，SDK 默认从以下两个位置获取网关公钥：
- SDK model Context (库表 apigw_manager_context)，需提前执行 `python manage.py fetch_apigw_public_key` 拉取并保存网关公钥
- settings.APIGW_PUBLIC_KEY，可在网关页面中手动获取公钥，并配置到 settings 中

#### Django 中间件

##### ApiGatewayJWTGenericMiddleware
利用网关公钥，解析请求头中的 X-Bkapi-JWT，在 `request` 中注入 `jwt` 对象，有以下属性：
- `gateway_name`：传入的网关名称；

##### ApiGatewayJWTAppMiddleware
根据 `request.jwt`，在 `request` 中注入 `app` 对象，有以下属性：
- `bk_app_code`：调用接口的应用；
- `verified`：应用是否经过认证；

##### ApiGatewayJWTUserMiddleware
根据 `request.jwt`，在 `request` 中注入 `user` 对象:
- 如果用户通过认证：其为一个 Django User Model 对象，用户名为当前请求用户的用户名
- 如果用户未通过认证，其为一个 Django AnonymousUser 对象，用户名为当前请求用户的用户名

如果中间件 `ApiGatewayJWTUserMiddleware` 中获取用户的逻辑不满足需求，可以继承此中间件并自定义用户获取方法 `get_user`，例如：：

```python
class MyJWTUserMiddleware(ApiGatewayJWTUserMiddleware):
  def get_user(self, request, gateway_name=None, bk_username=None, verified=False, **credentials):
      ...
      return auth.authenticate(
          request, gateway_name=gateway_name, bk_username=bk_username, verified=verified, **credentials
      )
```

注意：在自定义中间件 `ApiGatewayJWTUserMiddleware` 时，如果继续使用 `auth.authenticate` 获取用户，请确保正确设置用户认证后端，以遵循 Django `AUTHENTICATION_BACKENDS` 相关规则。

#### 用户认证后端

##### UserModelBackend
- 已认证的用户名，根据 `UserModel` 创建一个用户对象，不存在时返回 `None`；
- 未认证的用户名，返回 `AnonymousUser`，可通过继承后修改 `make_anonymous_user` 的实现来定制具体字段；

#### 本地开发测试

本地开发测试时，接口可能未接入 API 网关，此时中间件 `ApiGatewayJWTGenericMiddleware` 无法获取请求头中的 X-Bkapi-JWT。
为方便测试，SDK 提供了一个 Dummy JWT Provider，用于根据环境变量直接构造一个 request.jwt 对象。

在项目中添加本地开发配置文件 `local_settings.py`，并将其导入到 settings；然后，在此本地开发配置文件中添加配置：
```python
BK_APIGW_JWT_PROVIDER_CLS = "apigw_manager.apigw.providers.DummyEnvPayloadJWTProvider"
```

同时提供以下环境变量（非 Django settings)
```
APIGW_MANAGER_DUMMY_GATEWAY_NAME      # JWT 中的网关名
APIGW_MANAGER_DUMMY_PAYLOAD_APP_CODE  # JWT payload 中的 app_code
APIGW_MANAGER_DUMMY_PAYLOAD_USERNAME  # JWT payload 中的 username
```

### 场景二：非 Django 项目

非 Django 项目，需要项目获取网关公钥，并解析请求头中的 X-Bkapi-JWT；获取网关公钥的方案请参考上文。

解析 X-Bkapi-JWT 时，可根据 jwt header 中的 kid 获取当前网关名，例如：
```
{
    "iat": 1701399603,
    "typ": "JWT",
    "kid": "my-gateway",   # 网关名称
    "alg": "RS512"         # 加密算法
}
```

可从 jwt 内容中获取网关认证的应用、用户信息，例如：
```
{
  "user": {                  # 用户信息
    "bk_username": "admin",  # 用户名，解析时需同时支持 bk_username、username 两个 key，如 user.get("bk_username") or user.get("username", "")
    "verified": true         # 用户是否通过认证，true 表示通过认证，false 表示未通过认证
  },
  "app": {                    # 蓝鲸应用信息
    "bk_app_code": "my-app",  # 蓝鲸应用ID，解析时需同时支持 bk_app_code、app_code 两个 key，如 app.get("bk_app_code") or app.get("app_code", "")
    "verified": true          # 应用是否通过认证，true 表示通过认证，false 表示未通过认证
  },
  "exp": 1701401103,      # 过期时间
  "nbf": 1701399303,      # Not Before 时间
  "iss": "APIGW"          # 签发者
}
```
## FAQ
### 1.同步过程中报错：`call_definition_command_or_exit: command not found`
这种大概率是自定义脚本有问题，参照文档，按照对应目录下的 examples 的同步脚本即可。

### 2.执行同步命令时报错：`Error responded by API Gateway, status_code:_code: 404, request_id:, error_code: 1640401, API not found`
网关URL `BK_API_URL_TMPL` 漏配或者配错了(自定义脚本中存在错误)。举例说明: BK_API_URL_TMPL: http://bkapi.example.com/api/{api_name}"l, 注意 {api_name}是占位符需要保留

### 3.同步过程中报错: `校验失败: api_type: api_type 为 1 时，网关名 name 需以 bk- 开头。`
这个是因为 `definition.yaml` 定义的 apigateway.api_type为 1，标记网关为官方网关，网关名需以 `bk-` 开头，可选；非官方网关，可去除此配置
当设置为 1 时,则 `sync-apigateway.sh`里面的 `gateway_name` 参数需要以 bk- 开头

### 4.definition.yaml 指定了一个环境，为啥发布时却将其他环境也进行了发布？
definition.yaml 指定的环境配置适用于 `sync_apigw_stage` 命令，而资源发布 `create_version_and_release_apigw` 需要通过指定 --stage prod test 等方式来指定，未指定则
会发布所有该网关存在的环境