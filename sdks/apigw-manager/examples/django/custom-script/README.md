# 直接使用 Django Command 同步网关样例

主要步骤：
- 1. 提供一个 Django 项目
- 2. 打包项目镜像时，将 `support-files` 拷贝到该项目根目录
- 3. chart 部署时，采用 K8S Job 同步；在 Job 中，执行 `bash support-files/bin/sync-apigateway.sh`
- 4. 二进制部署，直接执行 `bash support-files/bin/sync-apigateway.sh`