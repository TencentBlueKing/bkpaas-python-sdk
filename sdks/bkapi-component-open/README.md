# 蓝鲸组件 API 客户端

使用蓝鲸组件 API 客户端，便于访问蓝鲸组件 API。

## SDK 使用样例

### 1 使用 get_client_by_request
此方式需提供 django request 对象

get_client_by_request
```python
from bkapi_component.open.shortcuts import get_client_by_request

# 需提供 django request，client 可从 request 中获取当前用户名或从 Cookies 中获取用户登录态
# 并且，支持从 django settings 获取默认的 bk_app_code、bk_app_secret、endpoint，也可通过参数指定
client = get_client_by_request(request)
result = client.cc.search_business({"key": "value"})
print(result["ok])
```

### 2 使用 get_client_by_username
get_client_by_username
```python
from bkapi_component.open.shortcuts import get_client_by_username

# 支持从 django settings 获取默认的 bk_app_code、bk_app_secret、endpoint，也可通过参数指定
client = get_client_by_username("admin")
result = client.cc.search_business({"key": "value"})
print(result["ok])
```
