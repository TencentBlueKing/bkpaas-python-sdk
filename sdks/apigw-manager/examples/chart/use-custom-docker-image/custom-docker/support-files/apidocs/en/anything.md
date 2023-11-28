### Description

This is a description

### Parameters

| Name | Type   | Required | Description   |
| ---- | ------ | -------- | ------------- |
| foo  | string | No       | This is a foo |

### Request Example
```python
from bkapi.bk_demo.shortcuts import get_client_by_request

client = get_client_by_request(request)
result = client.api.anything({"foo": "bar"}, path_params={}, headers=None, verify=True)
```

### Response Example
```python
{
    "method": "GET"
}
```

### Response Parameters
| Name   | Type   | Description    |
| ------ | ------ | -------------- |
| method | string | request method |
