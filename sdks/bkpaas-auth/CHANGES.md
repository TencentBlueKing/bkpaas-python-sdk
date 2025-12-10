# 版本历史

## 3.1.3
- feat: 用户模型增加时区支持，新增 time_zone 属性，由认证服务返回时区

## 3.1.2
- fix: 修复通过 APIGatewayAuthBackend 认证无法获取 tenant_id 的问题

## 3.1.1
- fix: 修复 apigw-manager 4.0.1 版本 JWT 中间件新增 tenant_id 参数导致的 JWT 认证失效问题

## 3.1.0
- feat: UniversalAuthBackend 支持获取用户租户身份信息

## 3.0.0
- BreakChange: 不再支持 Python 3.6，3.7
- BreakChange: Django 版本要求 >=4.2，<5.0

## 2.1.0
- fix: 修复 APIGatewayAuthBackend 不兼容 ^3.0.0 以上的 apigw_manager

## 2.0.8
- 将认证信息标准化到请求头 X-Bkapi-Authorization 中

## 2.0.6
- TokenRequestBackend.request_username 支持国际化

## 2.0.5
- TokenRequestBackend 处理蓝鲸统一登录的错误状态码 code=1302403
- CookieLoginMiddleware 根据错误状态码 code=1302403, 限制用户的访问权限

## 2.0.4
- 修复保存用户时，email 字段为 None 的问题

## 2.0.3
- 登录票据验证失败的日志级别调整为 warning

## 2.0.2
- 代码格式规范

## 2.0.1
- 使用 `cryptography` 替换原来的依赖 `pycrypto`
