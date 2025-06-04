# 插件配置说明

插件配置支持主要在 `stage`(definition.yaml) 和 `resource`(resource.yaml) 两个维度上，资源配置的插件优先级最高。
> 注意：所有配置均以 yaml 配置同步为主，举例来说：如果通过 yaml 配置的插件配置则会覆盖掉用户在网关管理页面创建的插件配置，如果 yaml 没有配置该插件，则也不会移除
> 用户之前在页面创建的插件配置，不过 yaml 如果没有配置上一次 yaml 配置的插件，则会移除上一次 yaml 配置的插件。
> `CORS` 插件和 `IP 访问保护插件` 不推荐在 yaml 配置绑定在环境上。

## 1. 跨域资源共享（CORS）插件

### 1.1 参数说明

| 参数             | 类型   | 默认值 | 描述                                                         |
| ---------------- | ------ | ------ | ------------------------------------------------------------ |
| allow_origins    | 字符串 | ""     | 允许跨域访问的 Origin，可以使用 * 表示允许所有 Origin 通过。 |
| allow_methods    | 字符串 | "**"   | 允许跨域访问的 Method，可以使用 * 表示允许所有 Method 通过。 |
| allow_headers    | 字符串 | "**"   | 允许跨域访问时请求方携带的 Header，可以使用 * 表示允许所有 Header 通过。 |
| expose_headers   | 字符串 | ""     | 允许跨域访问时响应方携带的 Header，可以使用 * 表示允许任意 Header。 |
| max_age          | 整数   | 86400  | 浏览器缓存 CORS 结果的最大时间，单位为秒。                   |
| allow_credential | 布尔值 | true   | 是否允许跨域访问的请求方携带凭据（如 Cookie 等）。           |

### 1.2 配置例子

```yaml
- type: bk-cors
  yaml: |-
    allow_origins: '*'
    allow_methods: '*'
    allow_headers: '*'
    expose_headers: '*'
    max_age: 86400
    allow_credential: false
```

## 2. Header 转换插件

### 2.1 参数说明

| 参数   | 类型 | 默认值 | 描述                         |
| ------ | ---- | ------ | ---------------------------- |
| set    | 数组 | []     | 设置的请求头，包括键和值。   |
| remove | 数组 | []     | 删除的请求头，只需要提供键。 |

### 2.2 配置例子

```yaml
- type: bk-header-rewrite
  yaml: |-
    set:
      - key: test
        value: '2'
    remove: []
```

## 3. IP 访问保护插件

### 3.1 参数说明

| 参数      | 类型   | 默认值 | 描述                                   |
| --------- | ------ | ------ | -------------------------------------- |
| whitelist | 字符串 | ""     | 白名单中的 IP 地址，支持 CIDR 表示法。 |
| blacklist | 字符串 | ""     | 黑名单中的 IP 地址，支持 CIDR 表示法。 |
| message   | 字符串 | ""     | 当 IP 地址不被允许时显示的消息。       |

### 3.2 配置例子

```yaml
- type: bk-ip-restriction
  yaml: |-
    whitelist: '1.1.1.1'
    blacklist: '2.2.2.2'
    message: 'Your IP is not allowed'
```

## 4. 频率控制插件

### 4.1 参数说明

| 参数        | 类型   | 默认值 | 描述                                             |
| ----------- | ------ | ------ | ------------------------------------------------ |
| rates       | 对象   | {}     | 包含默认频率限制和特殊应用频率限制的对象。       |
| default     | 对象   | {}     | 单个应用的默认频率限制，包括次数和时间范围。     |
| specials    | 数组   | []     | 特殊应用频率限制，对指定应用设置单独的频率限制。 |
| bk_app_code | 字符串 | ""     | 蓝鲸应用 ID，用于特殊应用频率限制。               |

### 4.2 配置例子

```yaml
- type: bk-rate-limit
  yaml: |-
    rates:
      __default:
      - period: 1
          tokens: 100
```

## 5. mocking 插件

### 5.1 参数说明

| 参数                    | 类型  | 默认值 | 描述     |
|-----------------------|-----|-----|--------|
| response_example      | 字符串 | ""  | 响应体。   |
| response_headers      | 对象  | {}  | 响应头。   |
| response_status       | 整数  | 200 | 响应状态码。 |

### 5.2 配置例子

```yaml
- type: bk-mock
  yaml: |-
    response_example: ''
    response_headers:
      - key: key1
        value: value1
    response_status: 200
```

## 6. API 熔断插件

### 6.1 参数说明

| 参数                      | 类型  | 默认值  | 描述                               |
|-------------------------|-----|------|----------------------------------|
| break_response_body     | 字符串 | ""   | 当上游服务处于不健康状态时返回的 HTTP 响应体信息。     |
| break_response_headers  | 对象  | {}   | 当上游服务处于不健康状态时返回的 HTTP 响应头信息。     |
| unhealthy               | 对象  | {}   | 当上游服务处于不健康状态时的 HTTP 的状态码和异常请求次数。 |
| healthy                 | 对象  | {}   | 上游服务处于健康状态时的 HTTP 状态码和连续正常请求次数。  |
| break_response_code     | 整数  | 502  | 当上游服务处于不健康状态时返回的 HTTP 错误码。       |
| max_breaker_sec         | 整数  | 300  | 上游服务熔断的最大持续时间，以秒为单位，最小 3 秒。      |

### 6.2 配置例子

```yaml
- type: bk-mock
  yaml: |-
    break_response_body: ''
    break_response_headers:
      - key: key1
        value: value1
    unhealthy:
      http_statuses: 
      - 500
      successes: 3
    healthy:
      http_statuses: 
      - 200
      failures: 3
    break_response_code: 502
    max_breaker_sec: 300
```


## 7. 故障注入插件

### 7.1 参数说明

| 参数       | 类型  | 默认值  | 描述                    |
|----------|-----|------|-----------------------|
| abort    | 对象  | {}   | 中断状态。                 |
| delay    | 对象  | {}   | 延迟状态。                 |

### 7.2 配置例子

```yaml
- type: fault-injection
  yaml: |-
    abort:
      http_status: 503
      body: ''
      percentage: 50
      vars: ''
    unhealthy:
      duration: 3 
      percentage: 30
      vars: ''
```

## 8. 请求校验插件

### 8.1 参数说明

| 参数             | 类型  | 默认值  | 描述                                |
|----------------|-----|------|-----------------------------------|
| body_schema    | 字符串 | ""   | request body 数据的 JSON Schema。     |
| header_schema  | 字符串 | ""   | request header 数据的 JSON Schema。   |
| rejected_msg   | 字符串 | ""   | 拒绝信息。                             |
| rejected_code  | 整数  | 400  | 拒绝状态码。                            |

### 8.2 配置例子

```yaml
- type: request-validation
  yaml: |-
    body_schema: \'{"type": "object"}\'
    body_schema: \'{"type": "object"}\'
    rejected_msg: ''
    rejected_code: 400
```

## 9. Response 转换插件

### 9.1 参数说明

| 参数            | 类型  | 默认值   | 描述                                                                 |
|---------------|-----|-------|--------------------------------------------------------------------|
| status_code   | 整数  |       | 修改上游返回状态码，默认保留原始响应代码。                                              |
| body          | 字符串 | ""    | 修改上游返回的 body 内容，如果设置了新内容，header 里面的 content-length 字段也会被去掉。        |
| vars          | 字符串 | ""    | vars 是一个表达式列表，只有满足条件的请求和响应才会修改 body 和 header 信息，来自 lua-resty-expr。 |
| body_base64   | 布尔值 | false | 当设置时，在写给客户端之前，在body中传递的主体将被解码，这在一些图像和 Protobuffer 场景中使用。           |
| headers       | 对象  | {}    | 处理响应头。                                                             |

### 9.2 配置例子

```yaml
- type: response-rewrite
  yaml: |-
    status_code: 200
    body: ''
    vars: ''
    body_base64: false
    headers:
      add:
      - key: 'key1: value1'
      remove:
      - key: key1
      set:
      - key: key1
        value: value1
```


## 10. 重定向插件

### 10.1 参数说明

| 参数          | 类型   | 默认值     | 描述                        |
|-------------|------|---------|---------------------------|
| uri         | 字符串  | ""      | 要重定向到的 URI，可以包含 NGINX 变量。 |
| ret_code    | 整数   | 302     | HTTP 响应码。                 |

### 10.2 配置例子

```yaml
- type: redirect
  yaml: |-
    uri: ''
    ret_code: 302
```

