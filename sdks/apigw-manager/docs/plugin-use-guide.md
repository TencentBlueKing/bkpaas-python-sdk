# 插件配置说明
插件配置支持主要在 `stage`(definition.yaml) 和 `resource`(resource.yaml) 两个维度上，资源配置的插件优先级最高。
> 注意：所有配置均以 yaml 配置同步为主，举例来说： 如果通过yaml配置的插件配置则会覆盖掉用户在网关管理页面创建的插件配置，如果 yaml 没有配置该插件，则也不会移除
> 用户之前在页面创建的插件配置，不过 yaml 如果没有配置上一次yaml配置的插件，则会移除上一次 yaml 配置的插件。
> `CORS` 插件和 `IP 访问保护插件` 不推荐在yaml配置绑定在环境上。

## 跨域资源共享（CORS）插件

| 参数             | 类型   | 默认值 | 描述                                                         |
| ---------------- | ------ | ------ | ------------------------------------------------------------ |
| allow_origins    | 字符串 | ""     | 允许跨域访问的 Origin，可以使用 * 表示允许所有 Origin 通过。 |
| allow_methods    | 字符串 | "**"   | 允许跨域访问的 Method，可以使用 * 表示允许所有 Method 通过。 |
| allow_headers    | 字符串 | "**"   | 允许跨域访问时请求方携带的 Header，可以使用 * 表示允许所有 Header 通过。 |
| expose_headers   | 字符串 | ""     | 允许跨域访问时响应方携带的 Header，可以使用 * 表示允许任意 Header。 |
| max_age          | 整数   | 86400  | 浏览器缓存 CORS 结果的最大时间，单位为秒。                   |
| allow_credential | 布尔值 | true   | 是否允许跨域访问的请求方携带凭据（如 Cookie 等）。           |

### 配置例子

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

## Header 转换插件

| 参数   | 类型 | 默认值 | 描述                         |
| ------ | ---- | ------ | ---------------------------- |
| set    | 数组 | []     | 设置的请求头，包括键和值。   |
| remove | 数组 | []     | 删除的请求头，只需要提供键。 |

### 配置例子

```yaml
- type: bk-header-rewrite
  yaml: |-
    set:
      - key: test
        value: '2'
    remove: []
```

## IP 访问保护插件

| 参数      | 类型   | 默认值 | 描述                                   |
| --------- | ------ | ------ | -------------------------------------- |
| whitelist | 字符串 | ""     | 白名单中的 IP 地址，支持 CIDR 表示法。 |
| blacklist | 字符串 | ""     | 黑名单中的 IP 地址，支持 CIDR 表示法。 |
| message   | 字符串 | ""     | 当 IP 地址不被允许时显示的消息。       |

### 配置例子

```yaml
- type: bk-ip-restriction
  yaml: |-
    whitelist: '1.1.1.1'
    blacklist: '2.2.2.2'
    message: 'Your IP is not allowed'
```

## 频率控制插件

| 参数        | 类型   | 默认值 | 描述                                             |
| ----------- | ------ | ------ | ------------------------------------------------ |
| rates       | 对象   | {}     | 包含默认频率限制和特殊应用频率限制的对象。       |
| default     | 对象   | {}     | 单个应用的默认频率限制，包括次数和时间范围。     |
| specials    | 数组   | []     | 特殊应用频率限制，对指定应用设置单独的频率限制。 |
| bk_app_code | 字符串 | ""     | 蓝鲸应用ID，用于特殊应用频率限制。               |

### 配置例子

```yaml
- type: bk-rate-limit
  yaml: |-
    rates:
      __default:
      - period: 1
          tokens: 100
```
