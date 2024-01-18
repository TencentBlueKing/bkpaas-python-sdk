# 蓝鲸 PaaS 平台 Python 工具集

![](docs/images/bk_paas_zh.png)
---
[![license](https://img.shields.io/badge/license-mit-brightgreen.svg?style=flat)](LICENSE)
[![blue-krill Release](https://img.shields.io/badge/blue--krill-1.0.5-brightgreen)](https://github.com/TencentBlueKing/bkpaas-python-sdk/releases)
[![bkstorages Release](https://img.shields.io/badge/bkstorages-1.0.1-brightgreen)](https://github.com/TencentBlueKing/bkpaas-python-sdk/releases)
[![bkapi-client-core Release](https://img.shields.io/badge/bkapi--client--core-1.1.0-brightgreen)](https://github.com/TencentBlueKing/bkpaas-python-sdk/releases)
[![bkapi-component-open Release](https://img.shields.io/badge/bkapi--component--open-2.0.0-brightgreen)](https://github.com/TencentBlueKing/bkpaas-python-sdk/releases)
[![apigw-manager Release](https://img.shields.io/badge/apigw--manager-1.0.0-brightgreen)](https://github.com/TencentBlueKing/bkpaas-python-sdk/releases)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/TencentBlueKing/bkpaas-python-sdkpulls)

[English](readme_en.md) | 简体中文

## 总览

该工具集是一个包含了蓝鲸 PaaS/SaaS 开发通用的 Python SDK 合集，旨在为常见的开发场景提供最佳实践，避免无必要的重复设计、开发，提高代码复用性。

## SDKs

- [blue-krill](sdks/blue-krill/README.md) 常用 Python 工具包
- [bkstorages](sdks/bkstorages/README.md) 帮助你在蓝鲸 Django 应用中轻松使用 ***蓝鲸制品库***
  和 [S3 对象存储](https://docs.ceph.com/en/latest/radosgw/s3/) ，支持加速静态资源，管理用户上传文件
- [bkapi-client-core](sdks/bkapi-client-core/README.md) 蓝鲸云 API 客户端
- [bkapi-component-open](sdks/bkapi-component-open/README.md) 蓝鲸组件 API 客户端
- [apigw-manager](sdks/apigw-manager/README.md) 网关管理工具包
- [bkpaas-auth](sdks/bkpaas-auth/README.md) 蓝鲸 PaaS 平台内部服务使用的用户鉴权模块
- [paas-service](sdks/paas-service/README.md) 蓝鲸 PaaS 平台增强服务框架

当前 SDK 均只支持 **Python 3.6+**

## 蓝鲸社区

- [BK-CMDB](https://github.com/Tencent/bk-cmdb): 蓝鲸配置平台（蓝鲸 CMDB）是一个面向资产及应用的企业级配置管理平台。
- [BK-CI](https://github.com/Tencent/bk-ci): 蓝鲸持续集成平台是一个开源的持续集成和持续交付系统，可以轻松将你的研发流程呈现到你面前。
- [BK-BCS](https://github.com/Tencent/bk-bcs): 蓝鲸容器管理平台是以容器技术为基础，为微服务业务提供编排管理的基础服务平台。
- [BK-PaaS](https://github.com/Tencent/bk-PaaS): 蓝鲸 PaaS 平台是一个开放式的开发平台，让开发者可以方便快捷地创建、开发、部署和管理
  SaaS 应用。
- [BK-SOPS](https://github.com/Tencent/bk-sops): 标准运维（SOPS）是通过可视化的图形界面进行任务流程编排和执行的系统，是蓝鲸体系中一款轻量级的调度编排类
  SaaS 产品。

## 贡献

- 对于项目感兴趣，想一起贡献并完善项目请参阅[Contributing Guide](docs/CONTRIBUTING.md)。
- [腾讯开源激励计划](https://opensource.tencent.com/contribution) 鼓励开发者的参与和贡献，期待你的加入。

## 协议

基于 MIT 协议， 详细请参考 [LICENSE](LICENSE)
