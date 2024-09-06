## 通过镜像方式同步网关

#### 镜像说明

网关提供基础镜像 apigw-manager，用于同步网关数据到 API 网关。基础镜像通过 [Dockerfile](../Dockerfile) 进行构建，该镜像封装了 [demo](../demo) 项目，可读取 /data/ 目录，直接进行网关注册和同步操作，目录约定：
- */data/definition.yaml*：网关定义文件，用于注册网关；
- */data/resources.yaml*：资源定义文件，用于同步网关资源，可通过网关导出；
- */data/apidocs*：文档目录，可通过网关导出后解压；
- */data/bin/sync-apigateway.sh*：自定义同步脚本;


镜像执行同步时，需要额外的环境变量支持：
- `BK_APIGW_NAME`：网关名称；
- `BK_API_URL_TMPL`：云网关 API 地址模板，例如：网关host是：`bkapi.example.com`，则对应的值为：http://bkapi.example.com/api/{api_name} 注意：{api_name} 这个是占位符。
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
- `SYNC_RESOURCE_DOCS_BY_ARCHIVE_ARGS`: 默认值: "--safe-mode"，用于命令 `sync_resource_docs_by_archive`，同步网关文档
- `CREATE_VERSION_AND_RELEASE_APIGW_ARGS`: 默认值："--generate-sdks"，用于命令 `create_version_and_release_apigw`,创建资源版本并发布


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


#### 准备工作

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
call_definition_command_or_exit sync_apigw_resources "${resources_file}" --gateway-name=${gateway_name} --delete
call_definition_command_or_exit sync_resource_docs_by_archive "${definition_file}" --gateway-name=${gateway_name} --safe-mode
call_definition_command_or_exit grant_apigw_permissions "${definition_file}" --gateway-name=${gateway_name}

title "fetch apigateway public key"
apigw-manager.sh fetch_apigw_public_key --gateway-name=${gateway_name} --print > "apigateway.pub"

title "releasing"
# 创建资源版本并发布；指定参数 --generate-sdks 时，会同时生成资源版本对应的网关 SDK, 指定 --stage stage1 stage2 时会发布指定环境,不设置则发布所有环境
# 指定参数 --no-pub 则只生成版本，不发布
call_definition_command_or_exit create_version_and_release_apigw "${definition_file}" --gateway-name=${gateway_name}

log_info "done"
```


#### 使用方式一：chart + ConfigMap

使用基础镜像 apigw-manager，并为网关配置、资源文档创建 ConfigMap 对象，将这些 ConfigMap 挂载到基础镜像中，如此镜像就可以读取到网关数据，但是 chart 本身限制单文件不能超过 1MB。
- 准备文件的样例 [examples/chart/use-configmap](../examples/chart/use-configmap)

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
│       │   └── sync-apigateway.sh
│       ├── definition.yaml
│       └── resources.yaml
```

步骤2：在 chart values.yaml 中添加配置
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

步骤2：在 chart templates 下创建 ConfigMap 模板文件，样例如下：
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

步骤3：添加 K8S Job 同步任务，样例如下：
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

#### 使用方式二：chart + 自定义镜像

可将 apigw-manager 作为基础镜像，将配置文件和文档一并构建成一个新镜像，然后通过如 K8S Job 方式进行同步。
- 准备文件的样例 [examples/chart/use-custom-docker-image](../examples/chart/use-custom-docker-image)

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
    │   └── sync-apigateway.sh
    ├── definition.yaml
    └── resources.yaml
```

步骤2. 构建 Dockerfile，参考：
```Dockerfile
FROM hub.bktencent.com/blueking/apigw-manager:3.1.1

COPY support-files /data/
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

#### 使用方式三：二进制 + 外部文件挂载

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


### 支持同步指令

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
call_definition_command_or_exit sync_apigw_resources "${resources_file}" --gateway-name=${gateway_name} --delete
 
# 同步网关环境信息
call_definition_command_or_exit sync_apigw_stage "${definition_file}" --gateway-name=${gateway_name} 
 
# 可选，同步资源文档
call_definition_command_or_exit sync_resource_docs_by_archive "${definition_file}" --gateway-name=${gateway_name} --safe-mode
  
```
