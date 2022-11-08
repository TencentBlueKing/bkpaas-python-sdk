# Paas Service

蓝鲸 PaaS 平台增强服务框架


## 版本历史

详见 `CHANGES.md`。

## 使用指南

1. 更新 settings：
```python
INSTALLED_APPS = [
    ...
    'paas_service',
    ...
]

MIDDLEWARE = [
    ...
    'paas_service.auth.middleware.VerifiedClientMiddleware',
    ...
]

# 数据库敏感字段加密 Key
BKKRILL_ENCRYPT_SECRET_KEY = base64.b64encode(b'\x01' * 32)

# 与 PaaS 平台通信的 JWT 信息
PAAS_SERVICE_JWT_CLIENTS = [
    {
        "iss": "paas-v3",
        "key": "123..........",
        "algorithm": "HS256",
    },
]

# 增强服务供应商类
PAAS_SERVICE_PROVIDER_CLS = "svc_xxx.vendor.provider.Provider"
# 增强服务实例信息渲染函数
PAAS_SERVICE_SVC_INSTANCE_RENDER_FUNC = "svc_xxx.vendor.render.render_instance_data"

# 设置语言，注意：目前国际化只支持: 简体中文 和 English
LANGUAGE_CODE = 'zh-cn'

LANGUAGES = [("zh-cn", "简体中文"), ("en", "English")]
```

2. 单元测试

首先，安装 pytest、pytest-django。

然后执行 `make test` 运行所有单元测试。
