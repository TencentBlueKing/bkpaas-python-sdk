.. role:: raw-html-m2r(raw)
   :format: html


apigw-manager
=============

蓝鲸 API 网关管理 SDK，提供了基本的注册，同步，发布等功能。

安装
----

基础安装：

.. code-block:: shell

   pip install apigw-manager

如果需要使用 apigw-manager 的中间件来解析 JWT，可以安装：

.. code-block:: shell

   pip install "apigw-manager[cryptography]"

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

推荐在一个文件中统一进行定义，用命名空间来区分不同资源间的定义，\ `definition.yaml 样例 <definition.yaml>`_\ ：


* ``apigateway``\ ：定义网关基本信息，用于命令 ``sync_apigw_config``\ ；
* ``stage``\ ：定义环境信息，用于命令 ``sync_apigw_stage``\ ；
* ``strategies``\ ：定义网关策略，用于命令 ``sync_apigw_strategies``\ ；
* ``apply_permissions``\ ：申请网关权限，用于命令 ``apply_apigw_permissions``\ ；
* ``grant_permissions``\ ：应用主动授权，用于命令 ``grant_apigw_permissions``\ ；
* ``release``\ ：定义发布内容，用于命令 ``create_version_and_release_apigw``\ ；
* ``resource_docs``\ ：定义资源文档，用于命令 ``sync_resource_docs_by_archive``\ ；

**注意，同步资源后需要发布后才生效，发布内容定义于 ``release``\ ，请及时更新对应的版本信息，否则可能会导致资源漏发或 SDK 版本异常的情况**

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
   python manage.py create_version_and_release_apigw -f definition.yaml --generate-sdks  # 创建资源版本并发布，同时生成 SDK
   python manage.py fetch_apigw_public_key  # 获取网关公钥
   python manage.py fetch_esb_public_key  # 获取 ESB 公钥（专用于同时接入 ESB 和网关的系统）

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
* 未认证的用户名，返回 ``AnonymousUser``\ ，可通过继承后修改 ``make_anonymous_user`` 的实现来定制具体字段；

镜像
----

基础镜像
^^^^^^^^

基础镜像通过 `Dockerfile <Dockerfile>`_ 进行构建，该镜像封装了 `demo <demo>`_ 项目，可读取 /data/ 目录，直接进行网关注册和同步操作，目录约定：


* */data/definition.yaml*\ ：网关定义文件，用于注册网关；
* */data/resources.yaml*\ ：资源定义文件，用于同步网关资源，可通过网关导出；
* */data/docs*\ ：文档目录，可通过网关导出后解压；

镜像执行同步时，需要额外的环境变量支持：


* ``BK_APIGW_NAME``\ ：网关名称；
* ``BK_API_URL_TMPL``\ ：云网关 API 地址模板；
* ``BK_APP_CODE``\ ：应用名称；
* ``BK_APP_SECRET``\ ：应用密钥；
* ``DATABASE_URL``\ ：数据库连接地址，格式：\ ``mysql://username:password@host:port/dbname``\ ；
* ``APIGW_PUBLIC_KEY_PATH``\ ：网关公钥保存路径，默认为当前目录下 ``apigateway.pub``\ ；

如何获得网关公钥
~~~~~~~~~~~~~~~~


#. 如果设置了环境变量 ``APIGW_PUBLIC_KEY_PATH``\ ，同步后可读取该文件获取；
#. 如果通过 ``DATABASE_URL`` 设置了外部数据库，可通过执行以下 SQL 查询：
   .. code-block:: sql

       select value from apigw_manager_context where scope="public_key" and key="<BK_APIGW_NAME>";

通过外部挂载方式同步
^^^^^^^^^^^^^^^^^^^^

通过外部文件挂载的方式，将对应的目录挂载到 ``/data/`` 目录下，可通过以下类似的命令进行同步：

.. code-block:: shell

   docker run rm \
       -v /<MY_PATH>/:/data/ \
       -e BK_APIGW_NAME=<BK_APIGW_NAME> \
       -e BK_API_URL_TMPL=<BK_API_URL_TMPL> \
       -e BK_APP_CODE=<BK_APP_CODE> \
       -e BK_APP_SECRET=<BK_APP_SECRET> \
       -e DATABASE_URL=<DATABASE_URL> \
       apigw-manager

同步后，会在 *\ :raw-html-m2r:`<MY_PATH>`\ * 目录下获得网关公钥文件 *apigateway.pub*\ 。

通过镜像方式同步
^^^^^^^^^^^^^^^^

可将 apigw-manager 作为基础镜像，将配置文件和文档一并构建成一个新镜像，然后通过如 K8S Job 方式进行同步，构建 Dockerfile 参考：

.. code-block:: Dockerfile

   FROM apigw-manager

   COPY <MY_PATH> /data/

环境变量可通过运行时传入，也可以通过构建参数提前设置（仅支持 ``BK_APIGW_NAME`` 和 ``BK_APP_CODE``\ ）：

.. code-block:: shell

   docker build \
       -t my-apigw-manager \
       --build-arg BK_APIGW_NAME=<BK_APIGW_NAME> \
       --build-arg BK_APP_CODE=<BK_APP_CODE> \
       -f Dockerfile .
