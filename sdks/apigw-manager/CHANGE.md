## Change logs

### 3.0.0
- 添加指令 add_related_apps，支持为网关添加关联应用
- definition.yaml 添加 spec_version 字段，指定配置文件版本号
- Django Command 中，通过参数 --gateway-name 指定网关
- 基础镜像 apigw-manager 中，sync-apigateway.sh 中去除指令 apply_apigw_permissions
- 优化请求 bk-apigateway 接口失败时，打印的错误消息
- 优化 README.md，提供 examples

Breaking changes:
- 基础镜像 apigw-manager 中，调整指令名称
  - sync-apigateway 改为 sync-apigateway.sh
  - apigw-manager 改为 apigw-manager.sh
  - call_command 改为 call_command_or_warning
  - call_definition_command 改为 call_definition_command_or_warning
  - must_call_definition_command 改为 call_definition_command_or_exit
- 以下函数中的参数名 api_name 改为 gateway_name
  - ApiGatewayJWTUserMiddleware.get_user
  - UserModelBackend.authenticate
  - PublicKeyProvider.provide
  - SettingsPublicKeyProvider.provide
  - CachePublicKeyProvider.provide
- 以下函数中参数名 default_api_name 改为 default_gateway_name
  - CachePublicKeyProvider.__init__
  - DefaultJWTProvider.__init__
  - DummyEnvPayloadJWTProvider.__init__
  - JWTProvider.__init__
  - PublicKeyProvider.__init__
  - SettingsPublicKeyProvider.__init__

如果项目添加了自定义镜像，或自定义 Django 中间件，需要按照新的规则进行调整，或者锁定版本号
- 自定义镜像锁定基础镜像 apigw-manager 版本，版本号 < 3.0.0
- SDK 锁定版本号 < 3.0.0，如 poetry 可设置 `apigw-manager = "<3.0.0"`

### 2.0.1
- 修复镜像 sync-apigateway 中，同步任务失败时，脚本退出码为 0 的问题

### 2.0.0
- 恢复指令 sync_apigw_strategies，但其中仅打印告警日志

### 1.2.0
- 优化资源版本是否存在的校验
- 删除指令 sync_apigw_strategies，不再支持同步访问策略

### 1.1.7

- 修复 packaging 缺少 LegacyVersion 的问题

### 1.1.5

- 修复 JWT 解析时算法参数类型问题

### 1.1.4

- 修复 `PublicKeyProvider` 缺少 `default_api_name` 属性导致的问题

### 1.1.3

- 增加 `JWTProvider` 机制以方便本地开发调试
- 当网关管理员为空时，默认使用 admin
- 修复创建 SDK 的顺序问题

### 1.1.2

- 优化错误提示消息

### 1.1.1

- 完善创建网关版本命令默认参数

### 1.0.11

- 修复语义化版本(alpha/beta)转换导致的同步问题

### 1.0.2

- 兼容 Django 3.X 版本
- 优化错误提示消息

### 1.0.1

- Makefile 支持 publish 到 pypi 源
