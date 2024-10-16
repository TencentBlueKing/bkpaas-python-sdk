# 版本历史

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
