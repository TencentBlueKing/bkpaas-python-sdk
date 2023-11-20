## Change logs

## 1.2.0
- BK_API_CLIENT_ENABLE_SSL_VERIFY 默认值设置为 False
- Client 添加辅助方法：check_response_apigateway_error
- ResponseError 添加辅助方法：response_status_code, response_text, response_json
- 日志中，curl 信息请求头 X-Bkapi-Authorization 脱敏

### 1.1.8
- 使用 `CurlRequest` 封装转换 curl 命令的逻辑以优化性能

### 1.1.2
- 优化缺少路径参数的提示

### 1.1.1
- 增加 DEFAULT_STAGE_MAPPINGS 来允许指定不同网关的默认环境

### 1.1.0
- 添加 Makefile
