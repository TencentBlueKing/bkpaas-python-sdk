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

## 功能使用

- [根据 YAML 同步网关配置](./docs/sync_apigateway.md)：通过预定义的 YAML 文件，您可以轻松地执行网关创建、更新、发布和资源同步操作，从而简化 API 网关管理过程。主要有以下两种方案：
   - [直接使用 Django Command 同步](./docs/sync-apigateway-with-django.md): 此方案适用于 Django 项目
   - [通过镜像方式同步](./docs/sync-apigateway-with-docker.md): 此方案适用于非 Django 项目

- [解析**JWT**](./docs/jwt-explain.md): 使用 Django 中间件，您可以解析蓝鲸 API 网关的 X-Bkapi-JWT 请求头，确保只有来自 API 网关的请求才能访问您的后端服务，提升系统安全性。


## FAQ

### 1.同步过程中报错：`call_definition_command_or_exit: command not found`

这种大概率是自定义脚本有问题，参照文档，按照对应目录下的 examples 的同步脚本即可。

### 2.执行同步命令时报错：`Error responded by API Gateway, status_code:_code: 404, request_id:, error_code: 1640401, API not found`

网关URL `BK_API_URL_TMPL` 漏配或者配错了(自定义脚本中存在错误)。举例说明: BK_API_URL_TMPL: http://bkapi.example.com/api/{api_name}"l, 注意 {api_name}是占位符需要保留

### 3.同步过程中报错: `校验失败: api_type: api_type 为 1 时，网关名 name 需以 bk- 开头。

这个是因为 `definition.yaml` 定义的 apigateway.api_type为 1，标记网关为官方网关，网关名需以 `bk-` 开头，可选；非官方网关，可去除此配置
当设置为 1 时,则 `sync-apigateway.sh`里面的 `gateway_name` 参数需要以 bk- 开头

### 4.definition.yaml 指定了一个环境，为啥发布时却将其他环境也进行了发布？

definition.yaml 指定的环境配置适用于 `sync_apigw_stage` 命令，而资源发布 `create_version_and_release_apigw` 需要通过指定 --stage prod test 等方式来指定，未指定则
会发布所有该网关存在的环境

### 5. 调用 bk-apigateway 网关的 API，出现 ”应用无操作网关权限“错误

**错误示例：**

```json
{
  "result": false,
  "code": "40403",
  "message": "应用无操作网关权限",
  "data": null
}
```

**错误原因：**

应用调用网关 bk-apigateway 的接口，去操作网关数据时，该应用需要有操作该网关数据的权限（而非调用 bk-apigateway 网关 API 的权限）。比如，应用 app1 操作网关 bk-demo 时，app1 应该有操作网关 bk-demo 数据的权限，以防止误修改其他网关的数据。
则通过管理端页面 `http://apigw.__bk_domain__` 创建网关，此时，没有任何应用可以通过 bk-apigateway 的接口修改该网关数据
通过 bk-apigateway 的接口创建的网关，此时，除创建网关时使用的应用外，其它应用无权限修改此网关数据

**修复方案：**

访问 `http://apigw.__bk_domain__/backend/admin42/core/apirelatedapp/`，添加应用操作网关数据的权限

### 6. 注册网关资源时如果只想注册生成版本，不进行版本发布，该如何操作？

`create_version_and_release_apigw` 是进行网关资源生成版本和发布的命令，可以通过指定 `--no-pub` 只进行版本生成，不进行资源发布。