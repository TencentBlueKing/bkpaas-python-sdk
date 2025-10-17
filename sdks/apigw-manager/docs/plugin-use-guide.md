# 插件配置说明

插件配置支持主要在 `stage`(definition.yaml) 和 `resource`(resource.yaml) 两个维度上，资源配置的插件优先级最高。
> 注意：所有配置均以 yaml 配置同步为主，举例来说：如果通过 yaml 配置的插件配置则会覆盖掉用户在网关管理页面创建的插件配置，如果 yaml 没有配置该插件，则也不会移除
> 用户之前在页面创建的插件配置，不过 yaml 如果没有配置上一次 yaml 配置的插件，则会移除上一次 yaml 配置的插件。
> `CORS` 插件和 `IP 访问保护插件` 不推荐在 yaml 配置绑定在环境上。

## 1. 跨域资源共享（CORS）插件 （配置支持：资源/环境）

### 1.1 参数说明

| 参数             | 类型    | 是否必填 | 默认值     | 描述                                            |
| ---------------- |-------|------|---------|-----------------------------------------------|
| allow_origins    | 字符串   | 否    | ""      | 允许跨域访问的 Origin，可以使用 * 表示允许所有 Origin 通过。       |
| allow_methods    | 字符串   | 是    | "**"    | 允许跨域访问的 Method，可以使用 * 表示允许所有 Method 通过。       |
| allow_headers    | 字符串   | 是    | "**"    | 允许跨域访问时请求方携带的 Header，可以使用 * 表示允许所有 Header 通过。 |
| expose_headers   | 字符串   | 否    | ""      | 允许跨域访问时响应方携带的 Header，可以使用 * 表示允许任意 Header。    |
| max_age          | 整数    | 是    | 86400   | 浏览器缓存 CORS 结果的最大时间，单位为秒。                      |
| allow_credential | 布尔值   | 否    | true    | 是否允许跨域访问的请求方携带凭据（如 Cookie 等）。                 |

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

## 2. Header 转换插件 （配置支持：资源/环境）

### 2.1 参数说明

| 参数   | 类型 | 是否必填 | 默认值 | 描述                         |
| ------ | ---- |-----| ------ | ---------------------------- |
| set    | 数组 | 否   | []     | 设置的请求头，包括键和值。   |
| remove | 数组 | 否   | []     | 删除的请求头，只需要提供键。 |

### 2.2 配置例子

```yaml
- type: bk-header-rewrite
  yaml: |-
    set:
      - key: test
        value: '2'
    remove:
      - key: X-test
```

## 3. IP 访问保护插件 （配置支持：资源/环境）

### 3.1 参数说明

| 参数      | 类型   | 是否必填 | 默认值 | 描述                                   |
| --------- | ------ |-----| ------ | -------------------------------------- |
| whitelist | 字符串 | 否   | ""     | 白名单中的 IP 地址，支持 CIDR 表示法。 |
| blacklist | 字符串 | 否   | ""     | 黑名单中的 IP 地址，支持 CIDR 表示法。 |
| message   | 字符串 | 否   | ""     | 当 IP 地址不被允许时显示的消息。       |

### 3.2 配置例子

```yaml
- type: bk-ip-restriction
  yaml: |-
    whitelist: |-
      # comment
      1.1.1.1
      2.2.2.2
    message: 'Your IP is not allowed'
```

## 4. 频率控制插件 （配置支持：资源/环境）

### 4.1 参数说明

| 参数        | 类型   | 是否必填 | 默认值 | 描述                                             |
| ----------- | ------ |-----| ------ | ------------------------------------------------ |
| rates       | 对象   | 是   | {}     | 包含默认频率限制和特殊应用频率限制的对象。       |
| default     | 对象   | 是   | {}     | 单个应用的默认频率限制，包括次数和时间范围。     |
| specials    | 数组   | 否   | []     | 特殊应用频率限制，对指定应用设置单独的频率限制。 |
| bk_app_code | 字符串 | 否   | ""     | 蓝鲸应用 ID，用于特殊应用频率限制。               |

### 4.2 配置例子

```yaml
- type: bk-rate-limit
  yaml: |-
    rates:
      __default:
      - period: 1
        tokens: 100
```

## 5. mocking 插件（配置支持：资源）

### 5.1 参数说明

| 参数                    | 类型  | 是否必填 | 默认值 | 描述     |
|-----------------------|-----|-----|-----|--------|
| response_example      | 字符串 | 否   | ""  | 响应体。   |
| response_headers      | 对象  | 否   | {}  | 响应头。   |
| response_status       | 整数  | 否   | 200 | 响应状态码。 |

### 5.2 配置例子

```yaml
- type: bk-mock
  yaml: |-
    response_example: "{\"hello\": \"world\"}"
    response_headers:
      - key: foo
        value: bar
    response_status: 200
```

## 6. API 熔断插件 （配置支持：资源）

### 6.1 参数说明

| 参数                      | 类型  | 是否必填 | 默认值 | 描述                               |
|-------------------------|-----|-----|-----|----------------------------------|
| break_response_body     | 字符串 | 否   | ""  | 当上游服务处于不健康状态时返回的 HTTP 响应体信息。     |
| break_response_headers  | 对象  | 否   | {}  | 当上游服务处于不健康状态时返回的 HTTP 响应头信息。     |
| unhealthy               | 对象  | 否   | {}  | 当上游服务处于不健康状态时的 HTTP 的状态码和异常请求次数。 |
| unhealthy.http_statuses | 数组  | 否   | []  | 不健康状态码列表。 |
| unhealthy.failures      | 整数  | 否   | 3   | 触发不健康状态的异常请求次数。 |
| healthy                 | 对象  | 否   | {}  | 上游服务处于健康状态时的 HTTP 状态码和连续正常请求次数。  |
| healthy.http_statuses   | 数组  | 否   | []  | 健康状态码列表。  |
| healthy.successes       | 整数  | 否   | 3   | 触发健康状态的连续正常请求次数。  |
| break_response_code     | 整数  | 是   | 502 | 当上游服务处于不健康状态时返回的 HTTP 错误码。       |
| max_breaker_sec         | 整数  | 否   | 300 | 上游服务熔断的最大持续时间，以秒为单位，最小 3 秒。      |

### 6.2 配置例子

```yaml
- type: api-breaker
  yaml: |-
    break_response_body: 'test body'
    break_response_headers:
      - key: foo
        value: bar
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


## 7. 故障注入插件 （配置支持：资源）

### 7.1 参数说明

| 参数                | 类型      | 是否必填 | 默认值 | 描述                    |
|-------------------|---------|------|---|-----------------------|
| abort             | 对象      | 否    | {} | 中断状态。                 |
| abort.http_status | 整数      | 是    |   | 返回给客户端的 HTTP 状态码。                 |
| abort.body        | 字符串    | 否    | "" | 返回给客户端的 HTTP 状态码。                 |
| abort.percentage  | 整数      | 否    |   | 将被中断的请求占比。                 |
| abort.vars        | 字符串    | 否    | "" | 执行故障注入的规则，当规则匹配通过后才会执行故障注。                |
| delay             | 对象      | 否    | {} | 延迟状态。                 |
| delay.duration    | 小数      | 是    |   | 延迟时间，可以指定小数。                 |
| delay.percentage  | 整数      | 否    |   | 将被延迟的请求占比。                 |
| delay.vars        | 字符串    | 否    | ""  | 执行请求延迟的规则，当规则匹配通过后才会延迟请求。                 |

### 7.2 配置例子

```yaml
- type: fault-injection
  yaml: |-
    abort:
      http_status: 503
      body: "Fault Injection!"
      percentage: 50
      vars: "[[[\"arg_name\", \"==\", \"jack\"], [\"arg_age\", \"==\", 18]]]"
    delay:
      duration: 3
      percentage: 30
      vars: "[[[\"http_age\", \"==\", 18]]]"
```

## 8. 请求校验插件 （配置支持：资源）

### 8.1 参数说明

| 参数             | 类型  | 是否必填 | 默认值  | 描述                                |
|----------------|-----|-----|------|-----------------------------------|
| body_schema    | 字符串 | 否   | ""   | request body 数据的 JSON Schema。     |
| header_schema  | 字符串 | 否   | ""   | request header 数据的 JSON Schema。   |
| rejected_msg   | 字符串 | 否   | ""   | 拒绝信息。                             |
| rejected_code  | 整数  | 否   | 400  | 拒绝状态码。                            |

### 8.2 配置例子

```yaml
- type: request-validation
  yaml: |-
    body_schema: "{\"type\": \"object\",\"required\": [\"Content-Type\"],\"properties\": {\"Content-Type\": {\"type\": \"string\",\"pattern\": \"^application\\/json$\"}}}"
    header_schema: "{\"type\": \"object\",\"required\": [\"required_payload\"],\"properties\": {\"required_payload\": {\"type\": \"string\"},\"boolean_payload\": {\"type\": \"boolean\"},\"array_payload\": {\"type\": \"array\",\"minItems\": 1,\"items\": {\"type\": \"integer\",\"minimum\": 200,\"maximum\": 599},\"uniqueItems\": true,\"default\": [200]}}}"
    rejected_msg: "Request header validation failed"
    rejected_code: 403
```

## 9. Response 转换插件 （配置支持：资源）

### 9.1 参数说明

| 参数          | 类型  | 是否必填 | 默认值   | 描述                                                                 |
|-------------|-----|-----|-------|--------------------------------------------------------------------|
| status_code | 整数  | 否   |       | 修改上游返回状态码，默认保留原始响应代码。                                              |
| body        | 字符串 | 否   | ""    | 修改上游返回的 body 内容，如果设置了新内容，header 里面的 content-length 字段也会被去掉。        |
| vars        | 字符串 | 否   | ""    | vars 是一个表达式列表，只有满足条件的请求和响应才会修改 body 和 header 信息，来自 lua-resty-expr。 |
| body_base64 | 布尔值 | 否   | false | 当设置时，在写给客户端之前，在body中传递的主体将被解码，这在一些图像和 Protobuffer 场景中使用。           |
| headers     | 对象  | 否   | {}    | 处理响应头。                                                             |
| headers.add | 数组   | 否   | []    | 添加新的响应头，只需要提供键。格式为 ["name: value", ...]。                                                    |
| headers.set | 数组   | 否   | []    | 改写响应头，包括键和值。  格式为 {"name": "value", ...}。                                                     |
| headers.remove | 数组   | 否   | []    | 移除响应头，只需要提供键。  格式为 ["name", ...]。                                                          |

### 9.2 配置例子

```yaml
- type: response-rewrite
  yaml: |-
    body: "{\"code\":\"ok\",\"message\":\"new json body\"}"
    body_base64: false
    headers:
      add:
        - key: X-Server-balancer-addr
          value: test
      set:
        - key: X-Server-id
          value: "3"
      remove:
        - key: X-TO-BE-REMOVED
    vars: "[[[\"arg_name\", \"==\", \"jack\"], [\"arg_age\", \"==\", 18]]]"
    status_code: 200
```


## 10. 重定向插件 （配置支持：资源）

### 10.1 参数说明

| 参数          | 类型   | 是否必填 | 默认值     | 描述                        |
|-------------|------|-----|---------|---------------------------|
| uri         | 字符串  | 否   | ""      | 要重定向到的 URI，可以包含 NGINX 变量。 |
| ret_code    | 整数   | 否   | 302     | HTTP 响应码。                 |

### 10.2 配置例子

```yaml
- type: redirect
  yaml: |-
    uri: '/test/default.html'
    ret_code: 302
```


## 11. AccessToken 来源 （配置支持：资源）

### 11.1 参数说明

| 参数         | 类型     | 是否必填 | 默认值     | 描述             |
|------------|--------|------|---------|------------------------|
| source     | 字符串    | 是    | "bearer"      | 认证令牌的来源，默认是 bearer。 |

### 11.2 配置例子

```yaml
- type: bk-access-token-source
  yaml: 'source: bearer'
```

## 12. 限制请求大小 （配置支持：资源/环境）

### 12.1 参数说明

| 参数             | 类型   | 是否必填 | 默认值    | 描述                          |
|----------------|------|------|--------|-----------------------------|
| max_body_size  | 整数   | 是    |     | 最大请求体大小，最大值 33554432（32 M）。 |

### 12.2 配置例子

```yaml
- type: bk-request-body-limit
  yaml: 'max_body_size: 1024'
```


## 13. 用户访问限制 （配置支持：资源）

### 13.1 参数说明

| 参数             | 类型 | 是否必填 | 默认值                        | 描述    |
|----------------|----|------|----------------------------|-------|
| whitelist  | 数组 | 否    |                            | 白名单。  |
| blacklist  | 数组 | 否    |                            | 黑名单。  |
| message  | 字符串  | 否    | The bk-user is not allowed | 错误提示。 |

### 13.2 配置例子

```yaml
- type: bk-user-restriction
  yaml: |-
    whitelist:
      - key: admin
    message: 'The bk-user is not allowed'
```


## 14. 代理缓存 （配置支持：资源）

### 14.1 参数说明

| 参数             | 类型  | 是否必填  | 默认值 | 描述    |
|----------------|-----|-------|-----|-------|
| cache_method  | 数组  | 是     | GET | 缓存方法，仅支持：GET, HEAD。  |
| cache_ttl  | 整数   | 否     | 300 | 缓存时间，最大值 3600 秒。  |

### 14.2 配置例子

```yaml
- type: proxy-cache
  yaml: |-
    cache_method:
      - key: GET
    cache_ttl: 300
```
