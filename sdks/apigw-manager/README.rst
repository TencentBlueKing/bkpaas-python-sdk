
apigw-manager
=============

蓝鲸 API 网关管理 SDK，提供了基本的注册，同步，发布等功能。

功能
----


* 根据预定义的 YAML 文件进行网关创建，更新，发布及资源同步操作
* 蓝鲸 APIGateway jwt 解析中间件，校验接口请求来自 APIGateway

根据 YAML 同步网关配置
----------------------

更新 django settings 配置
^^^^^^^^^^^^^^^^^^^^^^^^^

在 django settings.py 中定义网关名称和接口地址模板：

.. code-block:: python

   # 待同步网关配置的网关名
   BK_APIGW_NAME = "my-apigateway-name"

   # 需将 bkapi.example.com 替换为真实的云 API 域名，在 PaaS 3.0 部署的应用，可从环境变量中获取 BK_API_URL_TMPL
   BK_API_URL_TMPL = "http://bkapi.example.com/api/{api_name}/"

在 INSTALLED_APPS 中加入以下配置，SDK 将创建表 ``apigw_manager_context`` 用于存储一些中间数据：

.. code-block:: python

   INSTALLED_APPS += [
       'apigw_manager.apigw',
   ]

definition.yaml
^^^^^^^^^^^^^^^

用于定义网关资源，为了简化使用，使用以下模型进行处理：

.. code-block::

   +---------------------------------+                +--------------------------------+
   |                                 |                |                                |
   |                                 |                |  +----------------------+      |
   |   ns1:                          |                |  |ns1:                  |      |
   |     key: {{data.key}}           |                |  |  key: value_from_data+--+   |             +------------------------------+
   |                                 |     Render     |  |                      |  |   |    Load     |                              |
   |                                 +--------------->+  +----------------------+  +---------------->+  api(key="value_from_data")  |
   |   ns2:                          |                |   ns2:                         |             |                              |
   |     key: {{settings.THE_KEY}}   |                |     key: value_from_settings   |             +------------------------------+
   |                                 |                |                                |
   |                                 |                |                                |
   |           Template              |                |              YAML              |
   +---------------------------------+                +--------------------------------+

definition.yaml 中可以使用 Django 模块语法引用和渲染变量，内置以下变量：


* ``settings``\ ：django 提供的配置对象；
* ``environ``\ ：环境变量；
* ``data``\ ：命令行自定义变量；

推荐在一个文件中统一进行定义，用命名空间来区分不同资源间的定义，\ `definition.yaml 样例 <./definition.yaml>`_\ ：


* ``apigateway``\ ：定义网关基本信息，用于命令 ``sync_apigw_config``\ ；
* ``stage``\ ：定义环境信息，用于命令 ``sync_apigw_stage``\ ；
* ``strategies``\ ：定义网关策略，用于命令 ``sync_apigw_strategies``\ ；
* ``apply_permissions``\ ：申请网关权限，用于命令 ``apply_apigw_permissions``\ ；
* ``grant_permissions``\ ：应用主动授权，用于命令 ``grant_apigw_permissions``\ ；
* ``release``\ ：定义发布内容，用于命令 ``create_version_and_release_apigw``\ ；
* ``resource_docs``\ ：定义资源文档，用于命令 ``sync_resource_docs_by_archive``\ ；

特别的，为了方便用户直接使用网关导出的资源文件，资源定义默认没有命名空间。

同步命令
^^^^^^^^

约定：definition.yaml 用于维护网关基本定义，不包含资源定义，资源定义使用 resources.yaml 单独定义，基本的网关同步命令顺序如下，可参考使用：

.. code-block:: shell

   python manage.py sync_apigw_config -f definition.yaml  # 同步网关基本信息
   python manage.py sync_apigw_stage -f definition.yaml  # 同步网关环境信息
   python manage.py sync_apigw_strategies -f definition.yaml  # 同步网关策略
   python manage.py apply_apigw_permissions -f definition.yaml  # 申请网关权限，如无可跳过
   python manage.py grant_apigw_permissions -f definition.yaml  # 为应用主动授权，如无可跳过
   python manage.py sync_apigw_resources -f resources.yaml  # 同步网关资源
   python manage.py sync_resource_docs_by_archive -f definition.yaml  # 同步资源文档
   python manage.py create_version_and_release_apigw -f definition.yaml  # 创建资源版本并发布
   python manage.py fetch_apigw_public_key  # 获取网关公钥

校验请求来自 APIGateway
-----------------------

如果应用需要认证 API 网关传递过来的 JWT 信息，在 MIDDLEWARE 中加入：

.. code-block:: python

   MIDDLEWARE += [
       'apigw_manager.apigw.authentication.ApiGatewayJWTGenericMiddleware',  # JWT 认证
       'apigw_manager.apigw.authentication.ApiGatewayJWTAppMiddleware',  # JWT 透传的应用信息
       'apigw_manager.apigw.authentication.ApiGatewayJWTUserMiddleware',  # JWT 透传的用户信息
   ]

..

   **请确保应用进程在启动前执行了 python manage.py fetch_apigw_public_key 命令，否则中间件可能无法正常工作**


注意中间件的优先级，请加到其他中间件之前。

apigw_manager 默认提供了一个基于 User Model 实现的 authentication backend，如需使用，在 AUTHENTICATION_BACKENDS 中加入：

.. code-block:: python

   AUTHENTICATION_BACKENDS += [
       'apigw_manager.apigw.authentication.UserModelBackend',
   ]

中间件
^^^^^^

ApiGatewayJWTGenericMiddleware
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

认证 JWT 信息，在 ``request`` 中注入 ``jwt`` 对象，有以下属性：


* ``api_name``\ ：传入的网关名称；

ApiGatewayJWTAppMiddleware
~~~~~~~~~~~~~~~~~~~~~~~~~~

解析 JWT 中的应用信息，在 ``request`` 中注入 ``app`` 对象，有以下属性：


* ``bk_app_code``\ ：调用接口的应用；
* ``verified``\ ：应用是否经过认证；

ApiGatewayJWTUserMiddleware
~~~~~~~~~~~~~~~~~~~~~~~~~~~

解析 JWT 中的用户信息，在 ``request`` 中注入 ``user`` 对象，该对象通过以下调用获取：

.. code-block:: python

   auth.authenticate(request, username=username, verified=verified)

因此，请选择或实现合适的 authentication backend。
如果该中间件认证逻辑不符合应用预期，可继承此中间件，重载 ``get_user`` 方法进行调整；

用户认证后端
^^^^^^^^^^^^

UserModelBackend
~~~~~~~~~~~~~~~~


* 已认证的用户名，通过 ``UserModel`` 根据 ``username`` 获取用户，不存在时返回 ``None``\ ；
* 未认证的用户名，返回 ``AnonymousUser``\ ；
