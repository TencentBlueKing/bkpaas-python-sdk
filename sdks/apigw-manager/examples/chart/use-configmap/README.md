# 通过镜像方式同步网关: chart + ConfigMap 样例

主要步骤：
- 1. 修改 values.yaml 中的 `apigatewaySync.extraEnvVars`
- 2. 安装 chart，例如: `helm install bk-demo . -n blueking`