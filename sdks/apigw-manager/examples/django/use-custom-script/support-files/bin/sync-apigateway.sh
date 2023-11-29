#!/bin/bash

# 注意事项：
# - 需将 "apigw_manager.apigw" 添加到 django settings INSTALLED_APPS
# - 需提前执行 "python manage.py migrate"

# 如果任何命令返回一个非零退出状态（错误），脚本将会立即终止执行
set -e

# 待同步网关名，直接指定网关名，则不需要配置 django settings BK_APIGW_NAME
gateway_name="bk-demo"

# 待同步网关、资源定义文件
definition_file="support-files/definition.yaml"
resources_file="support-files/resources.yaml"

# sync gateway
echo "gateway ${gateway_name} sync definition start ..."
python manage.py sync_apigw_config --gateway-name=${gateway_name} --file="${definition_file}"
python manage.py sync_apigw_stage --gateway-name=${gateway_name} --file="${definition_file}"
python manage.py sync_apigw_resources --delete --gateway-name=${gateway_name} --file="${resources_file}"
python manage.py sync_resource_docs_by_archive --gateway-name=${gateway_name} --file="${definition_file}"
python manage.py create_version_and_release_apigw --gateway-name=${gateway_name} --file="${definition_file}"
python manage.py grant_apigw_permissions --gateway-name=${gateway_name} --file="${definition_file}"
python manage.py fetch_apigw_public_key --gateway-name=${gateway_name}
echo "gateway ${gateway_name} sync definition end"
