## Change logs

## 1.2.0
- BK_API_CLIENT_ENABLE_SSL_VERIFY 默认值设置为 False
- BaseClient 处理响应内容时优先检查 json，添加辅助方法：check_response_apigateway_error, check_response_status
- ResponseError 添加 response_status_code/response_text/response_json 等辅助方法
- 日志中，curl 信息中不再携带请求头

### 1.1.8
- 使用 `CurlRequest` 封装转换 curl 命令的逻辑以优化性能

### 1.1.2
- 优化缺少路径参数的提示

### 1.1.1
- 增加 DEFAULT_STAGE_MAPPINGS 来允许指定不同网关的默认环境

### 1.1.0
- 添加 Makefile
