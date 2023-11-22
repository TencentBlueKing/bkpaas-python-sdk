### 描述

这是一个描述

### 输入参数
| 参数名称 | 参数类型 | 必选 | 描述          |
| -------- | -------- | ---- | ------------- |
| foo      | string   | No   | This is a foo |


### 调用示例
```python
from bkapi.bk_demo.shortcuts import get_client_by_request

client = get_client_by_request(request)
result = client.api.anything({"foo": "bar"}, path_params={}, headers=None, verify=True)
```

### 响应示例
```python
{
    "method": "GET"
}
```

### 响应参数说明
| 参数名称 | 参数类型 | 描述           |
| -------- | -------- | -------------- |
| method   | string   | request method |