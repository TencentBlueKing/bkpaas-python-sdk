# 通过镜像方式同步网关：chart + 自定义镜像样例

文件目录：
- my-apigw-manager: 用于生成自定义镜像
- bk-demo-chart: chart 样例，使用生成的自定义镜像同步网关

主要步骤：
- 1. 构建自定义镜像，例如：`docker build -f my-apigw-manager/Dockerfile --tag my-apigw-manager:development my-apigw-manager`
- 2. 修改 bk-demo-chart/values.yaml 中的 `apigatewaySync.image`, `apigatewaySync.extraEnvVars`
- 3. 安装 chart，例如：`helm install bk-demo-chart bk-demo-chart -f bk-demo-chart/values.yaml -n blueking`