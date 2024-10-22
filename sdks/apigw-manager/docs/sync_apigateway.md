
# 根据 YAML 同步网关配置

SDK 同步网关配置到 API 网关，支持多种方案:

- [直接使用 Django Command 同步](./sync-apigateway-with-django.md)：此方案适用于 Django 项目；Django 项目，可直接执行 SDK 提供的 Django Command 指令
- [通过镜像方式同步](./sync-apigateway-with-docker.md)：此方案适用于非 Django 项目；非 Django 项目，无法直接执行 SDK 提供的 Django Command 指令

## 准备工作

同步网关配置到 API 网关，需要准备网关配置、资源配置、资源文档、自定义同步脚本等数据，可参考目录：

```shell
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

## 1. definition.yaml

用于定义网关、环境等配置，为了简化使用，使用以下模型进行处理：

```shell
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
新接入系统请使用 spec_version=2， 旧有系统如果需要配置多个stage/配置多个backend， 建议也升级到spec_version=2并变更相关yaml配置。
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
> 📢 注意：如果之前接入过的，建议将 sepc_version改成 2，并将原先 `stage:{}`改成 `stages: []`


整体的样例：

```yaml
# definition.yaml 配置文件版本号，必填，固定值 1/2
spec_version: 2  # 如果之前接入过的，建议将 sepc_version改成 2，并将原先 stage:改成 stages: []

# 定义发布内容，用于命令 `create_version_and_release_apigw`，具体生效的环境取决于参数 --stage prod test 等方式来指定
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
  - bk_app_code: "{{ settings.BK_APP_CODE }}" # 环境变量方式："{{ environ.BK_APP_CODE }}"
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
#   - gateway_name: "{{ settings.BK_APIGW_NAME }}" # 环境变量方式："{{ environ.BK_APIGW_NAME }}"
#     # 权限维度，可选值：gateway，按网关授权，包括网关下所有资源，以及未来新创建的资源
#     grant_dimension: "gateway"

# 为网关添加关联应用，关联应用可以通过网关 bk-apigateway 的接口操作网关数据；每个网关最多可有 10 个关联应用；
# 用于命令 `add_related_apps`
related_apps:
  - "{{ settings.BK_APP_CODE }}" # 环境变量方式："{{ environ.BK_APP_CODE }}"

# 定义资源文档路径，用于命令 `sync_resource_docs_by_archive`；
# 资源文档的目录格式样例如下，en 为英文文档，zh 为中文文档，创建归档文件可使用指令 `tar czvf xxx.tgz en zh`：
# ./
# - en
#   - get_user.md
# - zh
#   - get_user.md
resource_docs:
  # 资源文档的归档文件，可为 tar.gz，zip 格式文件
  archivefile: "{{ settings.BK_APIGW_RESOURCE_DOCS_ARCHIVE_FILE }}" # 环境变量方式："{{ environ.BK_APIGW_RESOURCE_DOCS_ARCHIVE_FILE }}"
  # 资源文档目录，basedir 与 archivefile 二者至少一个有效，若同时存在，则 archivefile 优先
  basedir: "{{ settings.BK_APIGW_RESOURCE_DOCS_BASE_DIR }}" # 环境变量方式："{{ environ.BK_APIGW_RESOURCE_DOCS_BASE_DIR }}"
```

**注意：**
- 同步资源或者环境相关配置后，需要创建版本并发布才能生效，发布数据定义于 definition.yaml `release`
- 资源配置 resources.yaml 变更时，需要更新 definition.yaml `release` 中的版本号 version，以便正确创建资源版本及 SDK
- 详细的插件配置见：[插件配置说明](./plugin-use-guide.md)
## 2. resources.yaml

用于定义资源配置，建议通过网关管理端导出。为了方便用户直接使用网关导出的资源文件，资源定义默认没有命名空间。

样例可参考：[resources.yaml](../examples/django/use-custom-script/support-files/resources.yaml)

> 详细的插件配置见：[插件配置说明](./plugin-use-guide.md)

## 3. apidocs（可选）

资源文档，资源文档为 markdown 格式。资源文档的文件名，应为 `资源名称` + `.md` 格式，假如资源名称为 get_user，则文档文件名应为 get_user.md。
将资源的中文文档放到目录 `zh` 下，英文文档放到目录 `en` 下，如果某语言文档不存在，可忽略对应目录。

### 文档目录及命名
资源文档为 markdown 格式，文件名，应为 资源名称 + .md 格式，例如：资源名称为 get_user 时，则其文档文件名应为 get_user.md

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
### 在资源文档中引用公共文档片段

使用jinja2 include 复用公共部分

- 网关采用 Jinja 模板 支持文档文件的引用。对于需采用 Jinja 模板渲染的资源文档，需将文件名后缀设置为 .md.j2
- 对于被引用的公共文档片段，文件名可以以下划线（_）开头。

> 网关导入文档时，将分别进入 zh、en 目录，处理中文、英文文档，不同类型的文档，处理方式不同：
> - .md 为后缀的文档，将直接读取文档内容
> - .md.j2 为后缀的文档，将以文档所在目录为基准，采用 Jinja 模板进行渲染
> - 下划线 (_) 开头的文档，将跳过解析，此类文档为公共文档片段，非具体资源的文档

例如资源 get_user，采用 Jinja 模板渲染时，其文档文件名应为 get_user.md.j2，其引用其它文档示例如下：

```shell
{# 引用公共文档片段 _user_model.md.j2 #}
{% include '_user_model.md.j2' %}
```
资源文档中包含 Jinja 模板文件时，文档的目录结构示例如下：

```shell
.
├── en
│   ├── create_user.md
│   ├── get_user.md.j2
│   └── _user_model.md.j2
└── zh
    ├── create_user.md
    ├── get_user.md.j2
    └── _user_model.md.j2
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

## 4. 国际化支持

### 网关描述国际化
在 definition.yaml 中利用字段 description_en 指定英文描述。样例：

```yaml
apigateway:
  description: "xxxx"
  description_en: "This is the English description"
  is_public: true
  maintainers:
    - "admin"
```
### 环境描述国际化
在 definition.yaml 中利用字段 description_en 指定英文描述。样例：

```yaml
stage:
  name: "prod"
  description: "xxx"
  description_en: "This is the English description"
```
### 资源描述国际化
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
## 同步方案

### 方案一：直接使用 Django Command 同步

此方案适用于 Django 项目，具体请参考 [sync-apigateway-with-django.md](./sync-apigateway-with-django.md)

### 方案二：通过镜像方式同步

此方案适用于非 Django 项目，具体请参考 [sync-apigateway-with-docker.md](./sync-apigateway-with-docker.md)
