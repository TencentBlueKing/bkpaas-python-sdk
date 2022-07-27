# BlueKing PaaS Python SDK 

![](docs/images/bk_paas_en.png)
---

[![license](https://img.shields.io/badge/license-mit-brightgreen.svg?style=flat)](LICENSE)
[![blue-krill Release](https://img.shields.io/badge/blue--krill-1.0.5-brightgreen)](https://github.com/TencentBlueKing/bkpaas-python-sdk/releases)
[![bkstorages Release](https://img.shields.io/badge/bkstorages-1.0.1-brightgreen)](https://github.com/TencentBlueKing/bkpaas-python-sdk/releases)
[![bkapi-client-core Release](https://img.shields.io/badge/bkapi--client--core-1.1.0-brightgreen)](https://github.com/TencentBlueKing/bkpaas-python-sdk/releases)
[![bkapi-component-open Release](https://img.shields.io/badge/bkapi--component--open-1.1.0-brightgreen)](https://github.com/TencentBlueKing/bkpaas-python-sdk/releases)
[![apigw-manager Release](https://img.shields.io/badge/apigw--manager-1.0.0-brightgreen)](https://github.com/TencentBlueKing/bkpaas-python-sdk/releases)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/TencentBlueKing/bkpaas-python-sdkpulls)

English | [简体中文](readme.md)

This toolset is a collection of Python SDKs for BlueKing PaaS/SaaS development, designed to provide best practices for common development scenarios, avoid unnecessary duplication of design and development, and improve code reusability.

## SDKs

- [blue-krill](sdks/blue-krill/README.md) Common Python toolkits
- [bkstorages](sdks/bkstorages/README.md) Helps you to use Bk-Repo or [S3 Object Storage](https://docs.ceph.com/en/latest/radosgw/s3/) in your Django application, including accelerating static resources，managing uploaded files.
- [bkapi-client-core](sdks/bkapi-client-core/README.md) Blueking cloud API Client
- [bkapi-component-open](sdks/bkapi-component-open/README.md) Blueking component API Client
- [apigw-manager](sdks/apigw-manager/README.md) Gateway management toolkits
- [bkpaas-auth](sdks/bkpaas-auth/README.md) User authentication module used by internal services of the BK PaaS platform

All sdks above only support **Python 3.6+**

## BlueKing Community
- [BK-CI](https://github.com/Tencent/bk-ci): BlueKing Continuous Integration is a continuous integration and continuous delivery system that can easily present your R & D process to you.
- [BK-BCS](https://github.com/Tencent/bk-bcs): BlueKing Container Service is an orchestration platform for microservices based on container technology.
- [BK-CMDB](https://github.com/Tencent/bk-cmdb): BlueKing Configuration Management DataBase (BlueKing CMDB) is an enterprise level configuration management platform for assets and applications.
- [BK-PaaS](https://github.com/Tencent/bk-PaaS): BlueKing PaaS is an open development platform that allows developers to create, develop, deploy and manage SaaS applications quickly and easily.
- [BK-SOPS](https://github.com/Tencent/bk-sops): BlueKing Standard OPS (SOPS) is a light-weighted SaaS product in the Tencent BlueKing product system designed for the orchestration and execution of tasks through a graphical interface.

## Contributing
- If you have good comments or suggestions, welcome to give us Issues or Pull Requests to contribute to the BlueKing open source community. For more information about BlueKing node management, branch management, Issue and PR specification. Please read the [Contributing Guide](docs/CONTRIBUTING.md).
- [Tencent Open Source Incentive Program](https://opensource.tencent.com/contribution) encourages developers to participate and contribute, and we look forward to your participation.

## License

Based on MIT, please refer to [LICENSE](LICENSE)
