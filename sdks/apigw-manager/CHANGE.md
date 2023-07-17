## Change logs

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
