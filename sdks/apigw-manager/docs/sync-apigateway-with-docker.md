# 通过镜像方式同步网关

## 镜像说明

网关提供基础镜像 apigw-manager，用于同步网关数据到 API 网关。基础镜像通过 [Dockerfile](../Dockerfile) 进行构建，该镜像封装了 [demo](../demo) 项目，可读取 /data/ 目录，直接进行网关注册和同步操作，目录约定：

- */data/definition.yaml*：网关定义文件，用于注册网关；
- */data/resources.yaml*：资源定义文件，用于同步网关资源，可通过网关导出；
- */data/apidocs*：文档目录，可通过网关导出后解压；
- */data/bin/sync-apigateway.sh*：自定义同步脚本;

镜像默认使用以下环境变量执行同步；开启 KMS 后，应用凭据改由信封读取，见 [KMS 配置说明](#kms-配置说明)：

- `BK_APIGW_NAME`：网关名称；
- `BK_API_URL_TMPL`：云网关 API 地址模板，例如：网关 host 是：`bkapi.example.com`，则对应的值为：http://bkapi.example.com/api/{api_name} 注意：{api_name} 这个是占位符。
- `BK_APP_CODE`：应用名称；
- `BK_APP_SECRET`：应用密钥；

通过镜像进行同步时，镜像需访问用户自定义的数据，在 chart 和二进制两种不同的部署方案中，镜像加载用户自定义数据的方式有所不同：

- chart：
  - 单文件大小 < 1MB 时，可使用 ConfigMap 挂载
  - 单文件大小 >= 1MB 时，可创建自定义镜像
- 二进制：可直接通过外部文件挂载

同步脚本 `sync-apigateway.sh`，脚本允许通过额外的环境变量设置同步脚本当中一些命令参数：

- `SYNC_APIGW_CONFIG_ARGS`: 用于命令 `sync_apigw_config`, 同步网关基础配置
- `SYNC_APIGW_STAGE_ARGS`: 用于命令 `sync_apigw_stage`, 同步环境配置
- `APPLY_APIGW_PERMISSIONS_ARGS`: 用于命令 `apply_apigw_permissions`，申请网关资源权限
- `GRANT_APIGW_PERMISSIONS_ARGS`: 用于命令 `grant_apigw_permissions`，授权网关权限
- `SYNC_APIGW_RESOURCES_ARGS`: 默认值："--delete"，用于命令 `sync_apigw_resources`，同步网关资源
- `SYNC_RESOURCE_DOCS_BY_ARCHIVE_ARGS`: 默认值： "--safe-mode"，用于命令 `sync_resource_docs_by_archive`，同步网关文档
- `CREATE_VERSION_AND_RELEASE_APIGW_ARGS`: 默认值为空，用于命令 `create_version_and_release_apigw`，创建资源版本并发布；如需同时生成资源版本对应的网关 SDK，请显式设置为 `"--generate-sdks"`
- `ENABLE_SYNC_MCP_SERVERS`: 用于命令 `sync_apigw_stage_mcp_servers`, 是否开启同步环境 MCP Server
- `SYNC_APIGW_STAGE_MCP_SERVERS_ARGS`: 用于命令 `sync_apigw_stage_mcp_servers`，同步环境 MCP Server 的额外参数

基础镜像提供了一些自定义同步脚本常用的 bash 函数，以及执行 Django Command 指令的辅助脚本：

- `functions.sh`，定义一些常用 bash 函数，源码 [/apigw-manager/bin/functions.sh](../bin/functions.sh)

functions.sh 中的 bash 函数：

- `call_command_or_warning`: 执行一个 Django Command 指令，出错返回非 0 错误码，不退出脚本
- `call_definition_command_or_warning`: 执行一个 Django Command 指令，出错时打印告警日志，不退出脚本
- `call_definition_command_or_exit`: 执行一个 Django Command 指令，出错退出脚本执行
- `title`: 打印标题
- `log_info`: 打印 info 日志
- `log_warn`: 打印 warning 日志
- `log_error`: 打印 error 日志

## KMS 配置说明

从 **5.0.3** 开始，基础镜像支持在自带 Django 项目初始化时解密应用凭据。镜像已安装 `bk-kms-sdk` 及国密后端，支持 SDK 的 RSA/SM2、AES/SM4 信封。解密在容器内本地完成，不请求远程 KMS 服务。部署方负责准备配套的私钥、加密信封及 Kubernetes Secret，并完成环境变量注入和文件挂载。

`ENABLE_KMS` 未设置或值为 `false` 时，继续使用原有 `BK_APP_CODE` / `BK_APP_SECRET`，不导入 KMS SDK、不读取信封文件。开关仅接受字面值 `true` 或 `True` 开启，其余值均关闭。

开启 KMS 时，配置以下环境变量，原有 `BK_APIGW_NAME`、`BK_API_URL_TMPL` 等非凭据配置仍然需要提供：

| 环境变量 | 说明 | 默认值 |
| --- | --- | --- |
| `ENABLE_KMS` | 是否开启 KMS 应用凭据解密 | 关闭 |
| `BK_APIGW_MANAGER_KMS_PRIVATE_KEY` | Base64 编码的 PEM 私钥内容，不是私钥文件路径；开启时必填 | 无 |
| `BK_APIGW_MANAGER_KMS_ENVELOPE_PATH` | 挂载的信封文件路径；文件内容为 UTF-8 编码的 Base64 信封，开启时必填 | 无 |
| `BK_APIGW_MANAGER_KMS_APP_NAME` | 选择 `bkapp_id_secret` 下的应用条目名称，与条目中的 `app_code` 值可以不同 | `default` |

以下是**待加密的 JSON 明文结构**，不是挂载文件的最终内容。只要求所选条目的 `app_code`、`app_secret` 为非空字符串，其他条目和字段可以省略：

```json
{
  "bkapp_id_secret": {
    "default": {
      "app_code": "<应用代码>",
      "app_secret": "<应用密钥>"
    },
    "bk_apigw_test": {
      "app_code": "<另一应用代码>",
      "app_secret": "<另一应用密钥>"
    }
  }
}
```

例如，`BK_APIGW_MANAGER_KMS_APP_NAME=bk_apigw_test` 会读取 `bkapp_id_secret.bk_apigw_test.app_code` 和 `bkapp_id_secret.bk_apigw_test.app_secret`。开启 KMS 后，信封凭据优先于原有 `BK_APP_CODE` / `BK_APP_SECRET`；私钥或文件不可用、解密失败、JSON 无效、所选条目或字段缺失时，管理命令启动失败，不回退到旧凭据。错误信息不输出私钥、信封或明文。

Kubernetes Job 配置示例（部署方已创建 `my-app-kms` Secret，包含 `privateKey` 和 `envelope` 两个字段）：

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: sync-apigateway
spec:
  template:
    spec:
      containers:
        - name: sync-apigateway
          image: hub.bktencent.com/blueking/apigw-manager:5.0.3
          env:
            - name: BK_APIGW_NAME
              value: "bk-demo"
            - name: BK_API_URL_TMPL
              value: "http://bkapi.example.com/api/{api_name}"
            - name: ENABLE_KMS
              value: "true"
            - name: BK_APIGW_MANAGER_KMS_PRIVATE_KEY
              valueFrom:
                secretKeyRef:
                  name: my-app-kms
                  key: privateKey
            - name: BK_APIGW_MANAGER_KMS_ENVELOPE_PATH
              value: "/etc/secrets/apigw-manager-kms"
            - name: BK_APIGW_MANAGER_KMS_APP_NAME
              value: "default"
          volumeMounts:
            - name: kms-envelope
              mountPath: /etc/secrets/apigw-manager-kms
              subPath: envelope
              readOnly: true
            # 另行挂载网关定义、资源及文档到 /data，见下文的同步方式。
      volumes:
        - name: kms-envelope
          secret:
            secretName: my-app-kms
            items:
              - key: envelope
                path: envelope
      restartPolicy: Never
```

Secret 中 `privateKey` 的业务内容是 SDK 要求的 Base64 编码 PEM。若使用 Secret 的 `stringData`，直接填写该内容；若使用 `data`，还需要 Kubernetes Secret 自身的一层 Base64 编码。

默认同步脚本和通过 `apigw-manager.sh` 执行管理命令的自定义同步脚本共用镜像自带的 `demo.settings` 配置入口，每个管理命令进程解密一次。解密后直接赋值给 Django settings，并同步到**当前 Python 进程**的 `os.environ`，保留凭据中的 `$`、引号和空白等字符，因此已有 `settings.BK_APP_CODE`、`environ.BK_APP_CODE` 等模板写法继续生效。不会回写 Secret 或凭据文件，也不会反向修改父 Bash 进程的环境变量；Bash 自身读取凭据仍读取部署注入的值。使用业务项目自己的 Django settings 时，应由业务项目接入 KMS。

私钥通过环境变量注入、信封通过 `subPath` 挂载时，更新 Secret 不会刷新正在运行的容器。轮换后应重新创建同步 Job / Pod。

## 准备工作

准备自定义同步脚本，镜像执行时指定使用自定义同步脚本即可。自定义同步脚本样例 [sync-apigateway.sh](../examples/chart/use-custom-docker-image/my-apigw-manager/support-files/bin/sync-apigateway.sh) 如下：

```bash
#!/bin/bash

# 加载 apigw-manager 原始镜像中的通用函数
source /apigw-manager/bin/functions.sh

# 待同步网关名，需修改为实际网关名；
# - 如在下面指令的参数中，指定了参数 --gateway-name=${gateway_name}，则使用该参数指定的网关名
# - 如在下面指令的参数中，未指定参数 --gateway-name，则使用 Django settings BK_APIGW_NAME
gateway_name="bk-demo"

# 待同步网关、资源定义文件
definition_file="/data/definition.yaml"
resources_file="/data/resources.yaml"

title "begin to db migrate"
call_command_or_warning migrate apigw

title "syncing apigateway"
call_definition_command_or_exit sync_apigw_config "${definition_file}" --gateway-name=${gateway_name}
call_definition_command_or_exit sync_apigw_stage "${definition_file}" --gateway-name=${gateway_name}

# 可指定 --doc_language=en/zh  是否生成接口文档(中文/英文)
call_definition_command_or_exit sync_apigw_resources "${resources_file}" --gateway-name=${gateway_name} --delete
call_definition_command_or_exit sync_resource_docs_by_archive "${definition_file}" --gateway-name=${gateway_name} --safe-mode
call_definition_command_or_exit grant_apigw_permissions "${definition_file}" --gateway-name=${gateway_name}

title "fetch apigateway public key"
apigw-manager.sh fetch_apigw_public_key --gateway-name=${gateway_name} --print > "apigateway.pub"

title "releasing"
# 创建资源版本并发布；指定参数 --generate-sdks 时，会同时生成资源版本对应的网关 SDK, 指定 --stage stage1 stage2 时会发布指定环境,不设置则发布所有环境
# 指定参数 --no-pub 则只生成版本，不发布
call_definition_command_or_exit create_version_and_release_apigw "${definition_file}" --gateway-name=${gateway_name}

# 可选：需要同步 MCP Server 时调用。
# 注意：前提是该 stage 有生效的版本且声明的 mcp tool 在生效版本的资源列表里且确认过请求参数
# 支持的配置字段详见 sync_apigateway.md「1.4 MCP Server 配置说明」
# call_definition_command_or_exit sync_apigw_stage_mcp_servers "${definition_file}" --gateway-name=${gateway_name}

log_info "done"
```

## 同步方式

### 1. 使用方式一：chart + ConfigMap

使用基础镜像 apigw-manager，并为网关配置、资源文档创建 ConfigMap 对象，将这些 ConfigMap 挂载到基础镜像中，如此镜像就可以读取到网关数据，但是 chart 本身限制单文件不能超过 1MB。

- 准备文件的样例 [examples/chart/use-configmap](../examples/chart/use-configmap)

操作步骤如下：

步骤 1：将网关配置、资源文档、自定义同步命令，放到 chart 项目的 files 文件夹下，可参考目录：

```plain
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
│       │   └── sync-apigateway.sh
│       ├── definition.yaml
│       └── resources.yaml
```

步骤 2：在 chart values.yaml 中添加配置

```yaml
apigatewaySync:
  image: "hub.bktencent.com/blueking/apigw-manager:3.1.1"
  configMapMounts:
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
  extraEnvVars:
    - name: BK_APIGW_NAME
      value: "bk-demo"
    - name: BK_APP_CODE
      value: "bk-demo"
    - name: BK_APP_SECRET
      value: "secret"
    - name: BK_API_URL_TMPL
      value: "http://bkapi.example.com/api/{api_name}"
```

步骤 2：在 chart templates 下创建 ConfigMap 模板文件，样例如下：

```yaml
{{- $files := .Files }}
{{- range $item := .Values.apigatewaySync.configMapMounts }}
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: bk-demo-{{ $item.name }}
data:
{{ ($files.Glob $item.filePath).AsConfig | indent 2 }}
{{- end }}
```

步骤 3：添加 K8S Job 同步任务，样例如下：

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: "bk-demo-sync-apigateway"
spec:
  template:
    spec:
      containers:
      - command:
        - bash
        args:
        - bin/sync-apigateway.sh
        image: "{{ .Values.apigatewaySync.image }}"
        imagePullPolicy: "Always"
        name: sync-apigateway
        env:
        {{- toYaml .Values.apigatewaySync.extraEnvVars | nindent 8 }}
        volumeMounts:
        {{- range $item := .Values.apigatewaySync.configMapMounts }}
        - mountPath: "{{ $item.mountPath }}"
          name: "{{ $item.name }}"
        {{- end }}
      volumes:
      {{- range $item := .Values.apigatewaySync.configMapMounts }}
      - name: "{{ $item.name }}"
        configMap:
          defaultMode: 420
          name: "{{ $item.name }}"
      {{- end }}
      restartPolicy: Never
```

### 2. 使用方式二：chart + 自定义镜像

可将 apigw-manager 作为基础镜像，将配置文件和文档一并构建成一个新镜像，然后通过如 K8S Job 方式进行同步。

- 准备文件的样例 [examples/chart/use-custom-docker-image](../examples/chart/use-custom-docker-image)

操作步骤如下：

步骤 1. 将网关配置，资源文档，自定义同步命令，放到一个文件夹下，可参考目录：

```plain
.
├── Dockerfile
└── support-files
    ├── apidocs
    │   ├── en
    │   │   └── anything.md
    │   └── zh
    │       └── anything.md
    ├── bin
    │   └── sync-apigateway.sh
    ├── definition.yaml
    └── resources.yaml
```

步骤 2. 构建 Dockerfile，参考：

```Dockerfile
FROM hub.bktencent.com/blueking/apigw-manager:3.1.1

COPY support-files /data/
```

步骤 3：构建新镜像

```shell
docker build -t my-apigw-manager -f Dockerfile .
```

步骤 4：添加 K8S Job 同步任务，样例如下

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: "bk-demo-sync-apigateway"
spec:
  template:
    spec:
      containers:
      - command:
        - bash
        args:
        - bin/sync-apigateway.sh
        image: "hub.bktencent.com/blueking/my-apigw-manager:latest"
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
      restartPolicy: Never
```

### 3. 使用方式三：二进制 + 外部文件挂载

使用基础镜像 apigw-manager，通过外部文件挂载的方式，将对应的目录挂载到 /data/ 目录下，可通过以下类似的命令进行同步：

```bash
docker run --rm \
    -v /<MY_PATH>/:/data/ \
    -e BK_APIGW_NAME=<BK_APIGW_NAME> \
    -e BK_API_URL_TMPL=<BK_API_URL_TMPL> \
    -e BK_APP_CODE=<BK_APP_CODE> \
    -e BK_APP_SECRET=<BK_APP_SECRET> \
    hub.bktencent.com/blueking/apigw-manager:3.1.1
```

## 支持同步指令

```bash
# 可选，为网关添加关联应用，关联应用可以通过网关 bk-apigateway 提供的接口管理网关数据
call_definition_command_or_exit add_related_apps "${definition_file}" --gateway-name=${gateway_name}

# 可选，申请网关权限
call_definition_command_or_exit apply_apigw_permissions "${definition_file}" --gateway-name=${gateway_name}

# 创建资源版本并发布；指定参数 --generate-sdks 时，会同时生成资源版本对应的网关 SDK, 指定 --stage stage1 stage2 时会发布指定环境,不设置则发布所有环境
# 指定参数 --no-pub 则只生成版本，不发布
call_definition_command_or_exit create_version_and_release_apigw "${definition_file}" --gateway-name=${gateway_name}

# 获取网关公钥，存放到文件 apigateway.pub
apigw-manager.sh fetch_apigw_public_key --gateway-name=${gateway_name} --print > "apigateway.pub"

# 可选，为应用主动授权
call_definition_command_or_exit grant_apigw_permissions "${definition_file}" --gateway-name=${gateway_name}

# 同步网关基本信息
call_definition_command_or_exit sync_apigw_config "${definition_file}" --gateway-name=${gateway_name}

# 同步网关资源
#
# --delete: 当资源在服务端存在，却未出现在资源定义文件中时，指定本参数会强制删除这类资源，以保证服务端资源和文件内容完全一致。
#           如果未指定本参数，将忽略未出现的资源
# --doc_language: en/zh  是否生成接口文档(中文/英文)
call_definition_command_or_exit sync_apigw_resources "${resources_file}" --gateway-name=${gateway_name} --delete --doc_language=zh

# 同步网关环境信息
call_definition_command_or_exit sync_apigw_stage "${definition_file}" --gateway-name=${gateway_name}

# 可选，同步资源文档
call_definition_command_or_exit sync_resource_docs_by_archive "${definition_file}" --gateway-name=${gateway_name} --safe-mode

# 可选：需要同步 MCP Server 时调用。
# 注意：前提是该 stage 有生效的版本且声明的 mcp tool 在生效版本的资源列表里且确认过请求参数
# 支持的 mcp_servers 字段: name(必选), title, description(必选), labels, resource_names(必选),
# tool_names, is_public, status(必选), protocol_type, target_app_codes, oauth2_public_client_enabled,
# oauth2_personal_client_enabled, raw_response_enabled, category_names
# 详见 sync_apigateway.md「1.4 MCP Server 配置说明」
# call_definition_command_or_exit sync_apigw_stage_mcp_servers "${definition_file}" --gateway-name=${gateway_name}
```
