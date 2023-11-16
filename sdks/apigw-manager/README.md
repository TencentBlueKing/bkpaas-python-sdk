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
  - 此方案适用于 django 项目；django 项目，可直接执行 SDK 提供的 django command 指令
- 通过镜像方式同步
  - 此方案适用于非 django 项目；非 django 项目，无法直接执行 django command 指令

### 准备工作

同步网关配置到 API 网关，需要准备网关配置、资源配置、资源文档、自定义同步脚本等数据，可参考目录：
```
support-files
├── definition.yaml         # 维护网关、环境、资源文档地址、主动授权、发布等配置，但不包含资源配置
├── resources.yaml          # 维护资源配置；资源配置可通过 API 网关管理端直接导出，且数据量较大，因此单独管理
├── bin
│   └── sync-apigateway     # 自定义同步脚本，django 项目也可使用自定义 django command；利用 SDK 提供的 django command 组装同步任务
├── bk_apigw_docs_demo.tgz  # 资源文档归档文件，可选；与资源文档目录 apidocs 二选一即可
└── apidocs                 # 资源文档，可选；可通过 API 网关管理端直接导出，或者手工维护 markdown 格式文档文件
    ├── zh                  # 中文文档目录
    │   └── anything.md
    └── en                  # 英文文档目录
        └── anything.md
```

#### 1. definition.yaml

用于定义网关、环境等配置，为了简化使用，使用以下模型进行处理：

```
  Template(definition.yaml)                           YAML
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
- `settings`：django 提供的配置对象
- `environ`：环境变量

推荐在一个文件中统一进行定义，用命名空间来区分不同配置间的定义，[definition.yaml 样例](definition.yaml)：
- `apigateway`：定义网关基本信息，用于命令 `sync_apigw_config`；
- `stage`：定义环境信息，用于命令 `sync_apigw_stage`；
- `grant_permissions`：应用主动授权，用于命令 `grant_apigw_permissions`；
- `apply_permissions`：申请网关权限，用于命令 `apply_apigw_permissions`；
- `resource_docs`：定义资源文档路径，用于命令 `sync_resource_docs_by_archive`；
- `release`：定义发布内容，用于命令 `create_version_and_release_apigw`；

**注意，同步资源后需要发布后才生效，发布内容定义于 `release`，请及时更新对应的版本信息，否则可能会导致资源漏发或 SDK 版本异常的情况**

#### 2. resources.yaml

用于定义资源配置，建议通过网关管理端导出资源配置。为了方便用户直接使用网关导出的资源文件，资源定义默认没有命名空间。

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

导入资源文档时，可以直接使用资源文档归档文件，也可以使用资源文档目录。参考 [definition.yaml 样例](definition.yaml)，
在项目 definition.yaml 文件中，修改资源文档相关配置 resource_docs：
```yaml
resource_docs:
  # 资源文档的归档文件，可为 tar.gz，zip 格式文件；创建归档文件可使用指令 `tar czvf xxx.tgz en zh`
  # archivefile: "{{ settings.BK_APIGW_RESOURCE_DOCS_ARCHIVE_FILE }}"
  # 资源文档目录，basedir 与 archivefile 二者至少一个有效，若同时存在，则 archivefile 优先
  # basedir: "{{ settings.BK_APIGW_RESOURCE_DOCS_BASE_DIR }}"
  basedir: "{{ settings.BASE_DIR }}/support-files/apidocs/"
```

### 方案一：直接使用 django command 同步

此方案适用于 django 项目，项目安装 SDK apigw-manager 后，可以直接执行 SDK 提供的 django command。
- 准备文件的样例 [django-custom-script example](examples/django-custom-script)

#### 步骤1. 准备自定义同步脚本

创建一个 bash 脚本，如 `sync-apigateway`，使用 SDK 提供的 django command 定义网关配置的同步脚本，样例如下：
```shell
#!/bin/bash

# 如果任何命令返回一个非零退出状态（错误），脚本将会立即终止执行
set -e

# 待同步网关名，需修改为实际网关名；直接指定网关名，则不需要配置 django settings BK_APIGW_NAME
gateway_name="bk-demo"

# 待同步网关、资源定义文件，需调整为实际的配置文件地址
definition_file="support-files/definition.yaml"
resources_file="support-files/resources.yaml"

echo "gateway sync definition start ..."
python manage.py sync_apigw_config --api-name=${gateway_name} -f "${definition_file}"  # 同步网关基本信息
python manage.py sync_apigw_stage --api-name=${gateway_name} -f "${definition_file}"  # 同步网关环境信息
python manage.py sync_apigw_resources --delete --api-name=${gateway_name} -f "${resources_file}"  # 同步网关资源；--delete 将删除网关中未在 resources.yaml 存在的资源
python manage.py sync_resource_docs_by_archive --api-name=${gateway_name} -f "${definition_file}"  # 同步资源文档
python manage.py create_version_and_release_apigw --api-name=${gateway_name} -f "${definition_file}" # 创建资源版本并发布
python manage.py grant_apigw_permissions --api-name=${gateway_name} -f "${definition_file}"  # 为应用主动授权，如无可跳过
python manage.py apply_apigw_permissions --api-name=${gateway_name} -f "${definition_file}"  # 申请网关权限，如无可跳过
python manage.py fetch_apigw_public_key --api-name=${gateway_name}  # 获取网关公钥
python manage.py fetch_esb_public_key  # 可选，获取 ESB 公钥（专用于同时接入 ESB 和网关的系统）
echo "gateway sync definition end"
```

如果需要更灵活的控制，也可以采用自定义 django command 的方案，例如：
```
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        if not settings.SYNC_APIGATEWAY_ENABLED:
            return
        
        gateway_name = "bk-demo"

        definition_path = os.path.join(settings.BASE_DIR, "support-files/definition.yaml")
        resources_path = os.path.join(settings.BASE_DIR, "support-files/resources.yaml")

        call_command("sync_apigw_config", f"--api-name={gateway_name}", f"--file={definition_path}")
        call_command("sync_apigw_stage", f"--api-name={gateway_name}", f"--file={definition_path}")
        call_command("sync_apigw_resources", f"--api-name={gateway_name}", "--delete", f"--file={resources_path}")
        call_command("sync_resource_docs_by_archive", f"--api-name={gateway_name}", f"--file={definition_path}")
        call_command("create_version_and_release_apigw", f"--api-name={gateway_name}", f"--file={definition_path}")
        call_command("grant_apigw_permissions", f"--api-name={gateway_name}", f"--file={definition_path}")
        call_command("fetch_apigw_public_key", f"--api-name={gateway_name}", f"--file={definition_path}")
```

#### 步骤2. 添加 SDK apigw-manager

将 SDK apigw-manager 添加到项目依赖中，如 pyproject.toml 或 requirements.txt。

#### 步骤3. 将准备的网关配置文件，添加到项目

将准备的网关配置文件：definition.yaml, resources.yaml, apidocs (可选)，添加到项目

#### 步骤4. 更新 django settings 配置

在 django settings.py 中定义网关名称和接口地址模板：

```python
# 蓝鲸应用账号，用于访问网关 bk-apigateway 接口
BK_APP_CODE = "my-app"
BK_APP_SECRET = "my-app-secret"

# 待同步网关配置的网关名（如果需同步多个网关，可在同步命令中指定）
BK_APIGW_NAME = "my-apigateway-name"

# 需将 bkapi.example.com 替换为真实的云 API 域名；
# 在 PaaS 3.0 部署的应用，可从环境变量中获取 BK_API_URL_TMPL，不需要额外配置；
# 实际上，SDK 将调用网关 bk-apigateway 接口将数据同步到 API 网关
BK_API_URL_TMPL = "http://bkapi.example.com/api/{api_name}/"
```

在 INSTALLED_APPS 中加入以下配置，SDK 将创建表 `apigw_manager_context` 用于存储一些中间数据：

```python
INSTALLED_APPS += [
    "apigw_manager.apigw",
]
```

#### 步骤5. 同步网关数据到 API 网关

chart 部署方案，可采用 K8S Job 同步，样例如下：
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: "bk-demo-sync-apigateway-1"
spec:
  template:
    spec:
      containers:
      - command:
        - bash
        args:
        - sync-apigateway
        image: "mirrors.example.com/blueking/my-image:1.0.0"
        imagePullPolicy: "IfNotPresent"
        name: sync-apigateway
```

二进制部署方案，在部署阶段直接执行 sync-apigateway 脚本：
```shell
bash sync-apigateway
```

### 方案二：通过镜像方式同步

网关提供基础镜像 apigw-manager，用于同步网关数据到 API 网关。基础镜像通过 [Dockerfile](Dockerfile) 进行构建，该镜像封装了 [demo](demo) 项目，可读取 /data/ 目录，直接进行网关注册和同步操作，目录约定：
- */data/definition.yaml*：网关定义文件，用于注册网关；
- */data/resources.yaml*：资源定义文件，用于同步网关资源，可通过网关导出；
- */data/apidocs*：文档目录，可通过网关导出后解压；
- */data/bin/sync-apigateway*：自定义同步脚本；镜像提供默认同步脚本：[sync-apigateway](demo/bin/sync-apigateway)，如不满足需求，可自定义同步脚本

镜像执行同步时，需要额外的环境变量支持：
- `BK_APIGW_NAME`：网关名称；
- `BK_API_URL_TMPL`：云网关 API 地址模板；
- `BK_APP_CODE`：应用名称；
- `BK_APP_SECRET`：应用密钥；
- `DATABASE_URL`：数据库连接地址，可选，格式：`mysql://{username}:{password}@{host}:{port}/{dbname}`；
- `APIGW_PUBLIC_KEY_PATH`：网关公钥保存路径，可选，默认为当前目录下 `apigateway.pub`；

通过镜像进行同步时，镜像需访问用户自定义的数据，在 chart 和二进制两种不同的部署方案中，镜像加载用户自定义数据的方式有所不同：
- chart：
  - 单文件大小 < 1MB 时，可使用 ConfigMap 挂载
  - 单文件大小 >= 1MB 时，可创建自定义镜像
- 二进制：可直接通过外部文件挂载

#### 准备工作

网关配置，资源配置，资源文档等数据，可参考上文 `根据  YAML 同步网关配置` -> `准备工作` 进行准备。

同步脚本，可选择使用默认同步脚本 [sync-apigateway](demo/bin/sync-apigateway)，如果不满足需求，可以自定义同步脚本。

##### 1. 使用默认同步脚本

默认同步脚本 [sync-apigateway](demo/bin/sync-apigateway)，允许通过额外的环境变量设置命令参数：
- `SYNC_APIGW_CONFIG_ARGS`: 用于命令 `sync_apigw_config`
- `SYNC_APIGW_STAGE_ARGS`: 用于命令 `sync_apigw_stage`
- `APPLY_APIGW_PERMISSIONS_ARGS`: 用于命令 `apply_apigw_permissions`
- `GRANT_APIGW_PERMISSIONS_ARGS`: 用于命令 `grant_apigw_permissions`
- `SYNC_APIGW_RESOURCES_ARGS`: 默认值："--delete"，用于命令 `sync_apigw_resources`
- `SYNC_RESOURCE_DOCS_BY_ARCHIVE_ARGS`: 默认值: "--safe-mode"，用于命令 `sync_resource_docs_by_archive`
- `CREATE_VERSION_AND_RELEASE_APIGW_ARGS`: 默认值："--generate-sdks"，用于命令 `create_version_and_release_apigw`
- `APIGW_PUBLIC_KEY_PATH`: 网关公钥保存路径，默认为当前目录下 `apigateway.pub`，用于命令 `fetch_apigw_public_key`

##### 2. 自定义同步脚本

如果默认同步脚本不满足需求，可以自定义同步脚本，样例如下：
```bash
#!/bin/bash

# 加载 apigw-manager 原始镜像中的通用函数
source /apigw-manager/demo/bin/functions

# 待同步网关名，需修改为实际网关名；直接指定网关名，则不需要配置环境变量 BK_APIGW_NAME
gateway_name="bk-demo"

# 待同步网关、资源定义文件
definition_file="/data/definition.yaml"
resources_file="/data/resources.yaml"

title "begin to db migrate"
call_command migrate apigw

title "syncing apigateway"
must_call_definition_command sync_apigw_config "${definition_file}" --api-name=${gateway_name}
must_call_definition_command sync_apigw_stage "${definition_file}" --api-name=${gateway_name}
must_call_definition_command sync_apigw_resources "${resources_file}" --api-name=${gateway_name} --delete
must_call_definition_command sync_resource_docs_by_archive "${definition_file}" --api-name=${gateway_name} --safe-mode
must_call_definition_command grant_apigw_permissions "${definition_file}" --api-name=${gateway_name}

title "fetch apigateway public key"
apigw-manager fetch_apigw_public_key --api-name=${gateway_name} --print > "apigateway.pub"

title "releasing"
must_call_definition_command create_version_and_release_apigw "${definition_file}" --api-name=${gateway_name}

title "done"
```

样例脚本中：
- `/apigw-manager/demo/bin/functions`，定义一些常用 bash 函数，如 title, call_command 等，源码 [functions](demo/bin/functions)
- `call_command`: 执行一个 django command 指令，出错返回非 0 错误码，不退出脚本
- `must_call_definition_command`: 执行一个 django command 指令，出错退出脚本执行
- `apigw-manager`: 单纯执行一个 django command 指令，出错返回非 0 错误码，不退出脚本，源码 [apigw-manager](demo/bin/apigw-manager)
- `title`: 打印一行日志

#### 使用方式一：chart + ConfigMap

使用基础镜像 apigw-manager，并为网关配置、资源文档创建 ConfigMap 对象，将这些 ConfigMap 挂载到基础镜像中，如此镜像就可以读取到网关数据，但是 chart 本身限制单文件不能超过 1MB。
- 准备文件的样例 [chart-configmap example](examples/chart-configmap)

操作步骤如下：

步骤1：将网关配置、资源文档、自定义同步命令，放到 chart 项目的 files 文件夹下，可参考目录：
```
.
├── Chart.yaml
├── files
│   └── support-files
│       ├── apidocs
│       │   ├── en
│       │   │   └── anything.md
│       │   └── zh
│       │       └── anything.md
│       ├── bin
│       │   └── sync-apigateway
│       ├── definition.yaml
│       └── resources.yaml
```

步骤2：在 chart values.yaml 中添加配置
```yaml
apigatewaySync:
  ## 默认为 false 不同步网关配置
  enabled: false
  image:
    registry: mirrors.example.com
    repository: blueking/apigw-manager
    tag: "latest"
    pullPolicy: "Always"
  mounts:
    - name: "sync-apigw-base"
      filePath: "files/support-files/*"
      mountPath: "/data/"
    - name: "sync-apigw-bin"
      filePath: "files/support-files/bin/*"
      mountPath: "/data/bin/"
    - name: "sync-apigw-apidocs-zh"
      filePath: "files/support-files/apidocs/zh/*"
      mountPath: "/data/apidocs/zh/"
    - name: "sync-apigw-apidocs-en"
      filePath: "files/support-files/apidocs/en/*"
      mountPath: "/data/apidocs/en/"
```

步骤2：在 chart templates 下创建 ConfigMap 模板文件，样例如下：
```yaml
{{- if .Values.apigatewaySync.enabled }}
{{- range $item := .Values.apigatewaySync.configMaps }}
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: bk-demo-{{ $item.name }}
data:
{{ (.Files.Glob "$item.filePath").AsConfig | indent 2 }}
{{- end }}
```

步骤3：添加 K8S Job 同步任务，样例如下：
```yaml
{{- if .Values.apigatewaySync.enabled }}
apiVersion: batch/v1
kind: Job
metadata:
  name: "bk-demo-sync-apigateway-1"
spec:
  template:
    spec:
      containers:
      - command:
        - bash
        args:
        - sync-apigateway
        image: "mirrors.example.com/blueking/apigw-manager:latest"
        imagePullPolicy: "Always"
        name: sync-apigateway
        env:
        - name: BK_APIGW_NAME
          value: "bk-demo"
        - name: BK_APP_CODE
          value: "bk-demo"
        - name: BK_APP_SECRET
          value: "secret"
        - name: BK_API_URL_TMPL
          value: "http://bkapi.example.com/api/{api_name}"
        volumeMounts: 
        {{- range $item := .Values.apigatewaySync.configMaps }}
        - mountPath: "{{ $item.mountPath }}"
          name: "{{ $item.name }}"
        {{- end }}
      volumes: 
      {{- range $item := .Values.apigatewaySync.configMaps }}
      - name: "{{ $item.name }}"
        configMap:
          defaultMode: 420
          name: "{{ $item.name }}"
      {{- end }}
```

#### 使用方式二：chart + 自定义镜像

可将 apigw-manager 作为基础镜像，将配置文件和文档一并构建成一个新镜像，然后通过如 K8S Job 方式进行同步。
- 准备文件的样例 [chart-custom-docker example](examples/chart-custom-docker)

操作步骤如下：

步骤1. 将网关配置，资源文档，自定义同步命令，放到一个文件夹下，可参考目录：
```
.
├── Dockerfile
└── support-files
    ├── apidocs
    │   ├── en
    │   │   └── anything.md
    │   └── zh
    │       └── anything.md
    ├── bin
    │   └── sync-apigateway
    ├── definition.yaml
    └── resources.yaml
```

步骤2. 构建 Dockerfile，参考：
```Dockerfile
FROM mirrors.example.com/blueking/apigw-manager:latest

COPY <support-files> /data/
```

步骤3：构建新镜像
```shell
docker build -t my-apigw-manager -f Dockerfile .
```

步骤4：添加 K8S Job 同步任务，样例如下
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: "bk-demo-sync-apigateway-1"
spec:
  template:
    spec:
      containers:
      - command:
        - bash
        args:
        - sync-apigateway
        image: "mirrors.example.com/blueking/my-apigw-manager:latest"
        imagePullPolicy: "Always"
        name: sync-apigateway
        env:
        - name: BK_APIGW_NAME
          value: "bk-demo"
        - name: BK_APP_CODE
          value: "bk-demo"
        - name: BK_APP_SECRET
          value: "secret"
        - name: BK_API_URL_TMPL
          value: "http://bkapi.example.com/api/{api_name}"
```

#### 使用方式三：二进制 + 外部文件挂载

使用基础镜像 apigw-manager，通过外部文件挂载的方式，将对应的目录挂载到 /data/ 目录下，可通过以下类似的命令进行同步：
```bash
docker run --rm \
    -v /<MY_PATH>/:/data/ \
    -e BK_APIGW_NAME=<BK_APIGW_NAME> \
    -e BK_API_URL_TMPL=<BK_API_URL_TMPL> \
    -e BK_APP_CODE=<BK_APP_CODE> \
    -e BK_APP_SECRET=<BK_APP_SECRET> \
    -e DATABASE_URL=<DATABASE_URL> \
    mirrors.example.com/blueking/apigw-manager:latest
```

同步后，会在 *<MY_PATH>* 目录下获得网关公钥文件 *apigateway.pub*。

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

### 本地开发测试

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

## FAQ

#### 如何获得网关公钥
1. 如果设置了环境变量 `APIGW_PUBLIC_KEY_PATH`，同步后可读取该文件获取；
2. 如果通过 `DATABASE_URL` 设置了外部数据库，可通过执行以下 SQL 查询：
    ```sql
    select value from apigw_manager_context where scope="public_key" and key="<BK_APIGW_NAME>";
    ```

同步后，会在 *<MY_PATH>* 目录下获得网关公钥文件 *apigateway.pub*。
