### 直接使用 Django Command 同步网关

项目安装 SDK apigw-manager 后，可以直接执行 SDK 提供的 Django Command。
- 准备文件的样例 [examples/django/use-custom-script](../examples/django/use-custom-script)

#### 步骤1. 准备自定义同步脚本

创建一个 bash 脚本，如 `sync-apigateway.sh`，使用 SDK 提供的 Django Command 定义网关配置的同步脚本，样例如下：
```shell
#!/bin/bash

# 如果任何命令返回一个非零退出状态（错误），脚本将会立即终止执行
set -e

# 待同步网关名，需修改为实际网关名；
# - 如在下面指令的参数中，指定了参数 --gateway-name=${gateway_name}，则使用该参数指定的网关名
# - 如在下面指令的参数中，未指定参数 --gateway-name，则使用 Django settings BK_APIGW_NAME
gateway_name="bk-demo"

# 待同步网关、资源定义文件，需调整为实际的配置文件地址
definition_file="support-files/definition.yaml"
resources_file="support-files/resources.yaml"

echo "gateway sync definition start ..."

# 同步网关基本信息
echo "gateway sync definition start ..."
python manage.py sync_apigw_config --gateway-name=${gateway_name} --file="${definition_file}"

# 同步网关环境信息
python manage.py sync_apigw_stage --gateway-name=${gateway_name} --file="${definition_file}"

# 同步网关资源
# 
# --delete: 当资源在服务端存在，却未出现在资源定义文件中时，指定本参数会强制删除这类资源，以保证服务端资源和文件内容完全一致。
#           如果未指定本参数，将忽略未出现的资源
python manage.py sync_apigw_resources --delete --gateway-name=${gateway_name} --file="${resources_file}"

# 可选，同步资源文档
python manage.py sync_resource_docs_by_archive --gateway-name=${gateway_name} --file="${definition_file}"

# 创建资源版本、发布；指定参数 --generate-sdks 时，会同时生成资源版本对应的网关 SDK  指定 --stage stage1 stage2 时会发布指定环境,不设置则发布所有环境
# 指定参数 --no-pub 则只生成版本，不发布
python manage.py create_version_and_release_apigw --gateway-name=${gateway_name} --file="${definition_file}"

# 可选，为应用主动授权
python manage.py grant_apigw_permissions --gateway-name=${gateway_name} --file="${definition_file}"

# 获取网关公钥
python manage.py fetch_apigw_public_key --gateway-name=${gateway_name}

echo "gateway sync definition end"
```

如果需要更灵活的控制，也可以采用自定义 Django Command 的方案，例如：
```python
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        if not getattr(settings, "SYNC_APIGATEWAY_ENABLED", True):
            return
        
        # 待同步网关名，需修改为实际网关名；直接指定网关名，则不需要配置 Django settings BK_APIGW_NAME
        gateway_name = "bk-demo"

        # 待同步网关、资源定义文件，需调整为实际的配置文件地址
        definition_path = "support-files/definition.yaml"
        resources_path = "support-files/resources.yaml"

        call_command("sync_apigw_config", f"--gateway-name={gateway_name}", f"--file={definition_path}")
        call_command("sync_apigw_stage", f"--gateway-name={gateway_name}", f"--file={definition_path}")
        call_command("sync_apigw_resources", f"--gateway-name={gateway_name}", "--delete", f"--file={resources_path}")
        call_command("sync_resource_docs_by_archive", f"--gateway-name={gateway_name}", f"--file={definition_path}")
        call_command("create_version_and_release_apigw", f"--gateway-name={gateway_name}", f"--file={definition_path}")
        call_command("grant_apigw_permissions", f"--gateway-name={gateway_name}", f"--file={definition_path}")
        call_command("fetch_apigw_public_key", f"--gateway-name={gateway_name}")
```

#### 步骤2. 添加 SDK apigw-manager

将 SDK apigw-manager 添加到项目依赖中，如 pyproject.toml 或 requirements.txt。

#### 步骤3. 将准备的网关配置文件，添加到项目

将准备的网关配置文件：definition.yaml, resources.yaml, apidocs (可选)，添加到项目

#### 步骤4. 更新 Django settings 配置

在 Django settings.py 中定义网关名称和接口地址模板：

```python
# 蓝鲸应用账号，用于访问网关 bk-apigateway 接口
BK_APP_CODE = "my-app"
BK_APP_SECRET = "my-app-secret"

# 待同步网关配置的网关名（如果需同步多个网关，可在同步命令中指定）
BK_APIGW_NAME = "my-gateway-name"

# 需将 bkapi.example.com 替换为真实的云 API 域名；
# 在 PaaS 3.0 部署的应用，可从环境变量中获取 BK_API_URL_TMPL，不需要额外配置；
# 实际上，SDK 将调用网关 bk-apigateway 接口将数据同步到 API 网关
BK_API_URL_TMPL = "http://bkapi.example.com/api/{api_name}/" ## 例如：网关host是：`bkapi.example.com`，则对应的值为：http://bkapi.example.com/api/{api_name} 注意：{api_name} 这个是占位符。
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
  name: "bk-demo-sync-apigateway"
spec:
  template:
    spec:
      containers:
      - command:
        - bash
        args:
        - support-files/bin/sync-apigateway.sh
        ## 自定义 Django Command 时，可直接执行 Command 指令
        # -c
        # "python manage.py sync_apigateway"
        image: "hub.bktencent.com/blueking/my-image:1.0.0"
        imagePullPolicy: "IfNotPresent"
        name: sync-apigateway
```

二进制部署方案，在部署阶段直接执行 sync-apigateway.sh 脚本：
```shell
bash support-files/bin/sync-apigateway.sh
```


### 支持的 Django Command 列表

```bash
# 可选，为网关添加关联应用，关联应用可以通过网关 bk-apigateway 提供的接口管理网关数据
python manage.py add_related_apps --gateway-name=${gateway_name} --file="${definition_file}"

# 可选，申请网关权限
python manage.py apply_apigw_permissions --gateway-name=${gateway_name} --file="${definition_file}"

# 创建资源版本并发布；指定参数 --generate-sdks 时，会同时生成资源版本对应的网关 SDK 指定 --stage stage1 stage2 时会发布指定环境,不设置则发布所有环境
# 指定参数 --no-pub 则只生成版本，不发布
python manage.py create_version_and_release_apigw --gateway-name=${gateway_name} --file="${definition_file}"

# 获取网关公钥
python manage.py fetch_apigw_public_key --gateway-name=${gateway_name}

# 可选，获取 ESB 公钥（专用于同时接入 ESB 和网关的系统）
python manage.py fetch_esb_public_key

# 可选，为应用主动授权
python manage.py grant_apigw_permissions --gateway-name=${gateway_name} --file="${definition_file}"

# 同步网关基本信息
python manage.py sync_apigw_config --gateway-name=${gateway_name} --file="${definition_file}"

# 同步网关资源；--delete 将删除网关中未在 resources.yaml 存在的资源
python manage.py sync_apigw_resources --delete --gateway-name=${gateway_name} --file="${resources_file}"

# 同步网关环境信息
python manage.py sync_apigw_stage --gateway-name=${gateway_name} --file="${definition_file}"

# 可选，同步资源文档
python manage.py sync_resource_docs_by_archive --gateway-name=${gateway_name} --file="${definition_file}"
```
