# apigw-manager

蓝鲸 API 网关管理 SDK，提供了基本的网关注册，同步，发布等功能。

## 安装
基础安装：

```shell
pip install apigw-manager
```

如果需要使用 apigw-manager 提供的 django 中间件解析来自 API 网关的 X-Bkapi-JWT，可以安装：

```shell
pip install "apigw-manager[cryptography]"
```

## 功能

- 根据预定义的 YAML 文件进行网关创建，更新，发布及资源同步操作
- 解析蓝鲸 API 网关 X-Bkapi-JWT 的 django 中间件，校验接口请求来自 API 网关

## 根据 YAML 同步网关配置

SDK 同步网关配置到 API 网关，支持多种方案:
- 直接使用 django command 同步
- 通过独立镜像方式同步
- 通过外部挂载方式同步

### 准备工作

同步网关配置到 API 网关，需要准备网关配置、资源配置、资源文档等数据：
- definition.yaml: 维护网关、环境、资源文档地址、主动授权、发布等配置，但不包含资源配置
- resources.yaml: 维护资源配置；资源配置可通过 API 网关管理端直接导出，且数据量较大，因此单独管理
- apidocs：资源文档，可选，可通过 API 网关管理端直接导出，或者手工维护 markdown 格式文档文件

网关配置及文档文件目录样例如下：
```
support-files
├── definition.yaml
├── resources.yaml
└── apidocs
    ├── zh
    │   └── get_user.md
    └── en
        └── get_user.md
```

#### 1. definition.yaml

用于定义网关、环境等配置，为了简化使用，使用以下模型进行处理：

```
   Template(definition.yaml)                          YAML
+----------------------------+            +----------------------------+
|                            |            |                            |           +--------------------------------------+
|  ns1:                      |            | ns1:                       |           |                                      |
|    key: {{environ.KEY1}}   |            |   key: value_from_environ  |---------->| api1({"key": "value_from_environ"})  |
|                            |   Render   |                            |           |                                      |
|                            +----------->+                            |   Load    |                                      |
|  ns2:                      |            | ns2:                       |           |                                      |
|    key: {{settings.KEY2}}  |            |   key: value_from_settings |---------->| api2({"key": "value_from_settings"}) |
|                            |            |                            |           |                                      |
|                            |            |                            |           +--------------------------------------+
+----------------------------+            +----------------------------+
```

definition.yaml 中可以使用 Django 模版语法引用和渲染变量，内置以下变量：
- `settings`：django 提供的配置对象
- `environ`：环境变量

推荐在一个文件中统一进行定义，用命名空间来区分不同配置间的定义，[definition.yaml 样例](definition.yaml)：
- `apigateway`：定义网关基本信息，用于命令 `sync_apigw_config`；
- `stage`：定义环境信息，用于命令 `sync_apigw_stage`；
- `grant_permissions`：应用主动授权，用于命令 `grant_apigw_permissions`；
- `apply_permissions`：申请网关权限，用于命令 `apply_apigw_permissions`；
- `resource_docs`：定义资源文档，用于命令 `sync_resource_docs_by_archive`；
- `release`：定义发布内容，用于命令 `create_version_and_release_apigw`；

**注意，同步资源后需要发布后才生效，发布内容定义于 `release`，请及时更新对应的版本信息，否则可能会导致资源漏发或 SDK 版本异常的情况**

#### 2. resources.yaml

用于定义资源配置，推荐在一个文件中统一进行定义，建议通过网关管理端导出资源配置。为了方便用户直接使用网关导出的资源文件，资源定义默认没有命名空间。

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

参考 [definition.yaml 样例](definition.yaml) `resource_docs` 部分，在项目 definition.yaml 文件中，配置资源文档在项目中的位置。
```yaml
resource_docs:
  # 资源文档的归档文件，可为 tar.gz，zip 格式文件
  # archivefile: "{{ settings.BK_APIGW_RESOURCE_DOCS_ARCHIVE_FILE }}"
  # 资源文档目录，basedir 与 archivefile 二者至少一个有效，若同时存在，则 archivefile 优先
  # basedir: "{{ settings.BK_APIGW_RESOURCE_DOCS_BASE_DIR }}"
  basedir: "{{ settings.BASE_DIR }}/support-files/apidocs/"
```

### 直接使用 django command 同步

此方案适用于 django 项目，项目安装 apigw-manager SDK 后，可以直接执行 SDK 提供的 django command。
- 准备文件的样例 [python-script example](examples/python-script)

#### 1. 添加 SDK apigw-manager

将 SDK apigw-manager 添加到项目依赖中，如 pyproject.toml 或 requirements.txt。

#### 2. 将准备的网关配置文件，添加到项目

将准备的网关配置文件：definition.yaml, resources.yaml, apidocs (可选)，添加到项目

#### 3. 更新 django settings 配置

在 django settings.py 中定义网关名称和接口地址模板：

```python
# 待同步网关配置的网关名
BK_APIGW_NAME = "my-apigateway-name"

# 需将 bkapi.example.com 替换为真实的云 API 域名；
# 在 PaaS 3.0 部署的应用，可从环境变量中获取 BK_API_URL_TMPL，不需要额外配置；
# 实际上，SDK 将调用网关 bk-apigateway 的接口将数据同步到 API 网关
BK_API_URL_TMPL = "http://bkapi.example.com/api/{api_name}/"
```

在 INSTALLED_APPS 中加入以下配置，SDK 将创建表 `apigw_manager_context` 用于存储一些中间数据：

```python
INSTALLED_APPS += [
    "apigw_manager.apigw",
]
```

#### 4. 同步命令

创建一个 bash 脚本，如 `sync-apigateway`，使用 SDK 提供的 django command 定义网关配置的同步脚本，样例如下：
```shell
#!/bin/bash

# 如果任何命令返回一个非零退出状态（错误），脚本将会立即终止执行
set -e

# 待同步网关、资源定义文件，需调整为实际的配置文件地址
definition_file="support-files/definition.yaml"
resources_file="support-files/resources.yaml"

echo "gateway sync definition start ..."
python manage.py sync_apigw_config -f "${definition_file}"  # 同步网关基本信息
python manage.py sync_apigw_stage -f "${definition_file}"  # 同步网关环境信息
python manage.py sync_apigw_resources --delete -f "${resources_file}"  # 同步网关资源
python manage.py sync_resource_docs_by_archive -f "${definition_file}"  # 同步资源文档
python manage.py create_version_and_release_apigw -f "${definition_file}" # 创建资源版本并发布
python manage.py grant_apigw_permissions -f "${definition_file}"  # 为应用主动授权，如无可跳过
python manage.py apply_apigw_permissions -f "${definition_file}"  # 申请网关权限，如无可跳过
python manage.py fetch_apigw_public_key  # 获取网关公钥
python manage.py fetch_esb_public_key  # 获取 ESB 公钥（专用于同时接入 ESB 和网关的系统），如无可跳过
echo "gateway sync definition end"
```

#### 6. 同步网关数据到 API 网关

如项目以二进制方案部署，可在部署阶段执行 sync-apigateway 脚本，进行同步。

如项目以 chart 方案部署，可将 sync-apigateway 添加到一个 K8S Job 进行同步。

### 通过独立镜像方式同步

#### 1. 准备网关 yaml 配置：definition.yaml

#### 2. 准备资源 yaml 配置：resources.yaml

#### 3. 准备资源文档（可选）

#### 4. 准备同步命令（可选）

#### 5. 同步网关数据到 API 网关

### 通过外部挂载方式同步



## 校验请求来自 API 网关

如果应用需要认证 API 网关传递过来的 JWT 信息，在 MIDDLEWARE 中加入：

```python
MIDDLEWARE += [
    'apigw_manager.apigw.authentication.ApiGatewayJWTGenericMiddleware',  # JWT 认证
    'apigw_manager.apigw.authentication.ApiGatewayJWTAppMiddleware',  # JWT 透传的应用信息
    'apigw_manager.apigw.authentication.ApiGatewayJWTUserMiddleware',  # JWT 透传的用户信息
]
```

> **请确保应用进程在启动前执行了 python manage.py fetch_apigw_public_key 命令，否则中间件可能无法正常工作**
> 如果因某些因素不方便使用命令自动获取网关公钥，可以在网关页面中手动获取公钥，配置到 `settings.APIGW_PUBLIC_KEY` 中。

注意中间件的优先级，请加到其他中间件之前。

apigw_manager 默认提供了一个基于 User Model 实现的 authentication backend，如需使用，在 AUTHENTICATION_BACKENDS 中加入：
```python
AUTHENTICATION_BACKENDS += [
    'apigw_manager.apigw.authentication.UserModelBackend',
]
```

### django 中间件

#### ApiGatewayJWTGenericMiddleware
认证 JWT 信息，在 `request` 中注入 `jwt` 对象，有以下属性：
- `api_name`：传入的网关名称；

#### ApiGatewayJWTAppMiddleware
解析 JWT 中的应用信息，在 `request` 中注入 `app` 对象，有以下属性：
- `bk_app_code`：调用接口的应用；
- `verified`：应用是否经过认证；

#### ApiGatewayJWTUserMiddleware
解析 JWT 中的用户信息，在 `request` 中注入 `user` 对象，该对象通过以下调用获取：
```python
auth.authenticate(request, username=username, verified=verified)
```

因此，请选择或实现合适的 authentication backend。
如果该中间件认证逻辑不符合应用预期，可继承此中间件，重载 `get_user` 方法进行调整；

### 用户认证后端
#### UserModelBackend
- 已认证的用户名，通过 `UserModel` 根据 `username` 获取用户，不存在时返回 `None`；
- 未认证的用户名，返回 `AnonymousUser`，可通过继承后修改 `make_anonymous_user` 的实现来定制具体字段；

## 本地开发测试

如果使用了 `ApiGatewayJWTGenericMiddleware` 中间件，在本地开发测试时在请求中带上合法的 JWT 是相对来说较困难的，这个时候我们可以通过使用测试用的 `JWTProvider` 来解决这个问题

在项目根目录下创建 `local_provider.py` 文件，并提供测试用 `JWTProvider`

在 Django settings 中提供如下配置

```python
BK_APIGW_JWT_PROVIDER_CLS = "apigw-manager.apigw.providers.DummyEnvPayloadJWTProvider"
```

同时提供以下环境变量

```
APIGW_MANAGER_DUMMY_API_NAME # JWT 中的 API name
APIGW_MANAGER_DUMMY_PAYLOAD_APP_CODE # JWT payload 中的 app_code
APIGW_MANAGER_DUMMY_PAYLOAD_USERNAME # JWT payload 中的 username
```


## 镜像
### 基础镜像
基础镜像通过 [Dockerfile](Dockerfile) 进行构建，该镜像封装了 [demo](demo) 项目，可读取 /data/ 目录，直接进行网关注册和同步操作，目录约定：
- */data/definition.yaml*：网关定义文件，用于注册网关；
- */data/resources.yaml*：资源定义文件，用于同步网关资源，可通过网关导出；
- */data/docs*：文档目录，可通过网关导出后解压；

镜像执行同步时，需要额外的环境变量支持：
- `BK_APIGW_NAME`：网关名称；
- `BK_API_URL_TMPL`：云网关 API 地址模板；
- `BK_APP_CODE`：应用名称；
- `BK_APP_SECRET`：应用密钥；
- `DATABASE_URL`：数据库连接地址，格式：`mysql://username:password@host:port/dbname`；
- `APIGW_PUBLIC_KEY_PATH`：网关公钥保存路径，默认为当前目录下 `apigateway.pub`；

#### 如何获得网关公钥
1. 如果设置了环境变量 `APIGW_PUBLIC_KEY_PATH`，同步后可读取该文件获取；
2. 如果通过 `DATABASE_URL` 设置了外部数据库，可通过执行以下 SQL 查询：
    ```sql
    select value from apigw_manager_context where scope="public_key" and key="<BK_APIGW_NAME>";
    ```

### 通过外部挂载方式同步
通过外部文件挂载的方式，将对应的目录挂载到 `/data/` 目录下，可通过以下类似的命令进行同步：
```shell
docker run --rm \
    -v /<MY_PATH>/:/data/ \
    -e BK_APIGW_NAME=<BK_APIGW_NAME> \
    -e BK_API_URL_TMPL=<BK_API_URL_TMPL> \
    -e BK_APP_CODE=<BK_APP_CODE> \
    -e BK_APP_SECRET=<BK_APP_SECRET> \
    -e DATABASE_URL=<DATABASE_URL> \
    apigw-manager
```

同步后，会在 *<MY_PATH>* 目录下获得网关公钥文件 *apigateway.pub*。

### 通过镜像方式同步
可将 apigw-manager 作为基础镜像，将配置文件和文档一并构建成一个新镜像，然后通过如 K8S Job 方式进行同步，构建 Dockerfile 参考：
```Dockerfile
FROM apigw-manager

COPY <MY_PATH> /data/
```

环境变量可通过运行时传入，也可以通过构建参数提前设置（仅支持 `BK_APIGW_NAME` 和 `BK_APP_CODE`）：
```shell
docker build \
    -t my-apigw-manager \
    --build-arg BK_APIGW_NAME=<BK_APIGW_NAME> \
    --build-arg BK_APP_CODE=<BK_APP_CODE> \
    -f Dockerfile .
```
