# -*- coding: utf-8 -*-
"""
 * TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-蓝鲸 PaaS 平台(BlueKing-PaaS) available.
 * Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
"""
from bkapi_client_core.esb import ESBClient, Operation, OperationGroup, bind_property


class BkLoginGroup(OperationGroup):
    # 获取用户信息
    get_user = bind_property(
        Operation,
        name="get_user",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/bk_login/get_user/",
    )

    # 用户登录态验证
    is_login = bind_property(
        Operation,
        name="is_login",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/bk_login/is_login/",
    )


class CcGroup(OperationGroup):
    # 新加主机锁
    add_host_lock = bind_property(
        Operation,
        name="add_host_lock",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/add_host_lock/",
    )

    # 添加主机到业务空闲机
    add_host_to_business_idle = bind_property(
        Operation,
        name="add_host_to_business_idle",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/add_host_to_business_idle/",
    )

    # 新增主机到资源池
    add_host_to_resource = bind_property(
        Operation,
        name="add_host_to_resource",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/add_host_to_resource/",
    )

    # 添加主机到资源池
    add_host_to_resource_pool = bind_property(
        Operation,
        name="add_host_to_resource_pool",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/add_host_to_resource_pool/",
    )

    # 新建模型实例之间的关联关系
    add_instance_association = bind_property(
        Operation,
        name="add_instance_association",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/add_instance_association/",
    )

    # 为服务实例添加标签
    add_label_for_service_instance = bind_property(
        Operation,
        name="add_label_for_service_instance",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/add_label_for_service_instance/",
    )

    # 批量创建通用模型实例
    batch_create_inst = bind_property(
        Operation,
        name="batch_create_inst",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/batch_create_inst/",
    )

    # 批量创建模型实例关联关系
    batch_create_instance_association = bind_property(
        Operation,
        name="batch_create_instance_association",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/batch_create_instance_association/",
    )

    # 批量创建进程模板
    batch_create_proc_template = bind_property(
        Operation,
        name="batch_create_proc_template",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/batch_create_proc_template/",
    )

    # 批量创建项目
    batch_create_project = bind_property(
        Operation,
        name="batch_create_project",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/batch_create_project/",
    )

    # 批量删除业务集
    batch_delete_business_set = bind_property(
        Operation,
        name="batch_delete_business_set",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/batch_delete_business_set/",
    )

    # 批量删除实例
    batch_delete_inst = bind_property(
        Operation,
        name="batch_delete_inst",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/batch_delete_inst/",
    )

    # 批量删除项目
    batch_delete_project = bind_property(
        Operation,
        name="batch_delete_project",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/batch_delete_project/",
    )

    # 批量删除集群
    batch_delete_set = bind_property(
        Operation,
        name="batch_delete_set",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/batch_delete_set/",
    )

    # 批量更新业务集信息
    batch_update_business_set = bind_property(
        Operation,
        name="batch_update_business_set",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/batch_update_business_set/",
    )

    # 批量更新主机属性
    batch_update_host = bind_property(
        Operation,
        name="batch_update_host",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/batch_update_host/",
    )

    # 批量更新对象实例
    batch_update_inst = bind_property(
        Operation,
        name="batch_update_inst",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/batch_update_inst/",
    )

    # 批量更新项目
    batch_update_project = bind_property(
        Operation,
        name="batch_update_project",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/batch_update_project/",
    )

    # 将agent绑定到主机上
    bind_host_agent = bind_property(
        Operation,
        name="bind_host_agent",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/bind_host_agent/",
    )

    # 绑定角色权限
    bind_role_privilege = bind_property(
        Operation,
        name="bind_role_privilege",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/bind_role_privilege/",
    )

    # 克隆主机属性
    clone_host_property = bind_property(
        Operation,
        name="clone_host_property",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/clone_host_property/",
    )

    # 查询模型实例关系数量
    count_instance_associations = bind_property(
        Operation,
        name="count_instance_associations",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/count_instance_associations/",
    )

    # 查询模型实例数量
    count_object_instances = bind_property(
        Operation,
        name="count_object_instances",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/count_object_instances/",
    )

    # 创建业务自定义模型属性
    create_biz_custom_field = bind_property(
        Operation,
        name="create_biz_custom_field",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/create_biz_custom_field/",
    )

    # 新建业务
    create_business = bind_property(
        Operation,
        name="create_business",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/create_business/",
    )

    # 创建业务集
    create_business_set = bind_property(
        Operation,
        name="create_business_set",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/create_business_set/",
    )

    # 添加模型分类
    create_classification = bind_property(
        Operation,
        name="create_classification",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/create_classification/",
    )

    # 创建管控区域
    create_cloud_area = bind_property(
        Operation,
        name="create_cloud_area",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/create_cloud_area/",
    )

    # 添加自定义查询
    create_custom_query = bind_property(
        Operation,
        name="create_custom_query",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/create_custom_query/",
    )

    # 创建动态分组
    create_dynamic_group = bind_property(
        Operation,
        name="create_dynamic_group",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/create_dynamic_group/",
    )

    # 创建实例
    create_inst = bind_property(
        Operation,
        name="create_inst",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/create_inst/",
    )

    # 创建模块
    create_module = bind_property(
        Operation,
        name="create_module",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/create_module/",
    )

    # 创建模型
    create_object = bind_property(
        Operation,
        name="create_object",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/create_object/",
    )

    # 创建模型属性
    create_object_attribute = bind_property(
        Operation,
        name="create_object_attribute",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/create_object_attribute/",
    )

    # 创建进程实例
    create_process_instance = bind_property(
        Operation,
        name="create_process_instance",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/create_process_instance/",
    )

    # 新建服务分类
    create_service_category = bind_property(
        Operation,
        name="create_service_category",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/create_service_category/",
    )

    # 创建服务实例
    create_service_instance = bind_property(
        Operation,
        name="create_service_instance",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/create_service_instance/",
    )

    # 新建服务模板
    create_service_template = bind_property(
        Operation,
        name="create_service_template",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/create_service_template/",
    )

    # 创建集群
    create_set = bind_property(
        Operation,
        name="create_set",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/create_set/",
    )

    # 新建集群模板
    create_set_template = bind_property(
        Operation,
        name="create_set_template",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/create_set_template/",
    )

    # 删除业务
    delete_business = bind_property(
        Operation,
        name="delete_business",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/delete_business/",
    )

    # 删除模型分类
    delete_classification = bind_property(
        Operation,
        name="delete_classification",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/delete_classification/",
    )

    # 删除管控区域
    delete_cloud_area = bind_property(
        Operation,
        name="delete_cloud_area",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/delete_cloud_area/",
    )

    # 删除自定义查询
    delete_custom_query = bind_property(
        Operation,
        name="delete_custom_query",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/delete_custom_query/",
    )

    # 删除动态分组
    delete_dynamic_group = bind_property(
        Operation,
        name="delete_dynamic_group",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/delete_dynamic_group/",
    )

    # 删除主机
    delete_host = bind_property(
        Operation,
        name="delete_host",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/delete_host/",
    )

    # 删除主机锁
    delete_host_lock = bind_property(
        Operation,
        name="delete_host_lock",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/delete_host_lock/",
    )

    # 删除实例
    delete_inst = bind_property(
        Operation,
        name="delete_inst",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/delete_inst/",
    )

    # 删除模型实例之间的关联关系
    delete_instance_association = bind_property(
        Operation,
        name="delete_instance_association",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/delete_instance_association/",
    )

    # 删除模块
    delete_module = bind_property(
        Operation,
        name="delete_module",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/delete_module/",
    )

    # 删除模型
    delete_object = bind_property(
        Operation,
        name="delete_object",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/delete_object/",
    )

    # 删除对象模型属性
    delete_object_attribute = bind_property(
        Operation,
        name="delete_object_attribute",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/delete_object_attribute/",
    )

    # 删除进程模板
    delete_proc_template = bind_property(
        Operation,
        name="delete_proc_template",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/delete_proc_template/",
    )

    # 删除进程实例
    delete_process_instance = bind_property(
        Operation,
        name="delete_process_instance",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/delete_process_instance/",
    )

    # 删除某实例所有的关联关系（包含其作为关联关系原模型和关联关系目标模型的情况）
    delete_related_inst_asso = bind_property(
        Operation,
        name="delete_related_inst_asso",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/delete_related_inst_asso/",
    )

    # 删除服务分类
    delete_service_category = bind_property(
        Operation,
        name="delete_service_category",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/delete_service_category/",
    )

    # 删除服务实例
    delete_service_instance = bind_property(
        Operation,
        name="delete_service_instance",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/delete_service_instance/",
    )

    # 删除服务模板
    delete_service_template = bind_property(
        Operation,
        name="delete_service_template",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/delete_service_template/",
    )

    # 删除集群
    delete_set = bind_property(
        Operation,
        name="delete_set",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/delete_set/",
    )

    # 删除集群模板
    delete_set_template = bind_property(
        Operation,
        name="delete_set_template",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/delete_set_template/",
    )

    # 执行动态分组
    execute_dynamic_group = bind_property(
        Operation,
        name="execute_dynamic_group",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/execute_dynamic_group/",
    )

    # 查询业务主线实例拓扑源与目标节点的关系信息
    find_brief_biz_topo_node_relation = bind_property(
        Operation,
        name="find_brief_biz_topo_node_relation",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/find_brief_biz_topo_node_relation/",
    )

    # 查询主机业务关系信息
    find_host_biz_relations = bind_property(
        Operation,
        name="find_host_biz_relations",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/find_host_biz_relations/",
    )

    # 查询服务模板下的主机
    find_host_by_service_template = bind_property(
        Operation,
        name="find_host_by_service_template",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/find_host_by_service_template/",
    )

    # 查询集群模板下的主机
    find_host_by_set_template = bind_property(
        Operation,
        name="find_host_by_set_template",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/find_host_by_set_template/",
    )

    # 查询拓扑节点下的主机
    find_host_by_topo = bind_property(
        Operation,
        name="find_host_by_topo",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/find_host_by_topo/",
    )

    # 根据业务拓扑中的实例节点查询其下的主机关系信息
    find_host_relations_with_topo = bind_property(
        Operation,
        name="find_host_relations_with_topo",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/find_host_relations_with_topo/",
    )

    # 获取主机与拓扑的关系
    find_host_topo_relation = bind_property(
        Operation,
        name="find_host_topo_relation",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/find_host_topo_relation/",
    )

    # 查询模型实例之间的关联关系
    find_instance_association = bind_property(
        Operation,
        name="find_instance_association",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/find_instance_association/",
    )

    # 查询模型实例的关联关系及可选返回原模型或目标模型的实例详情
    find_instassociation_with_inst = bind_property(
        Operation,
        name="find_instassociation_with_inst",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/find_instassociation_with_inst/",
    )

    # 批量查询某业务的模块详情
    find_module_batch = bind_property(
        Operation,
        name="find_module_batch",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/find_module_batch/",
    )

    # 根据模块ID查询主机和模块的关系
    find_module_host_relation = bind_property(
        Operation,
        name="find_module_host_relation",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/find_module_host_relation/",
    )

    # 根据条件查询业务下的模块
    find_module_with_relation = bind_property(
        Operation,
        name="find_module_with_relation",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/find_module_with_relation/",
    )

    # 查询模型之间的关联关系
    find_object_association = bind_property(
        Operation,
        name="find_object_association",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/find_object_association/",
    )

    # 批量查询某业务的集群详情
    find_set_batch = bind_property(
        Operation,
        name="find_set_batch",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/find_set_batch/",
    )

    # 查询业务拓扑节点的拓扑路径
    find_topo_node_paths = bind_property(
        Operation,
        name="find_topo_node_paths",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/find_topo_node_paths/",
    )

    # 查询业务的空闲机/故障机/待回收模块
    get_biz_internal_module = bind_property(
        Operation,
        name="get_biz_internal_module",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/cc/get_biz_internal_module/",
    )

    # 根据自定义查询获取数据
    get_custom_query_data = bind_property(
        Operation,
        name="get_custom_query_data",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/cc/get_custom_query_data/",
    )

    # 获取自定义查询详情
    get_custom_query_detail = bind_property(
        Operation,
        name="get_custom_query_detail",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/cc/get_custom_query_detail/",
    )

    # 查询指定动态分组
    get_dynamic_group = bind_property(
        Operation,
        name="get_dynamic_group",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/get_dynamic_group/",
    )

    # 获取主机详情
    get_host_base_info = bind_property(
        Operation,
        name="get_host_base_info",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/cc/get_host_base_info/",
    )

    # 查询主线模型的业务拓扑
    get_mainline_object_topo = bind_property(
        Operation,
        name="get_mainline_object_topo",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/get_mainline_object_topo/",
    )

    # 获取进程模板
    get_proc_template = bind_property(
        Operation,
        name="get_proc_template",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/get_proc_template/",
    )

    # 获取服务模板
    get_service_template = bind_property(
        Operation,
        name="get_service_template",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/cc/get_service_template/",
    )

    # 查询业务下的主机
    list_biz_hosts = bind_property(
        Operation,
        name="list_biz_hosts",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/list_biz_hosts/",
    )

    # 查询业务下的主机和拓扑信息
    list_biz_hosts_topo = bind_property(
        Operation,
        name="list_biz_hosts_topo",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/list_biz_hosts_topo/",
    )

    # 查询业务集中的业务列表
    list_business_in_business_set = bind_property(
        Operation,
        name="list_business_in_business_set",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/list_business_in_business_set/",
    )

    # 查询业务集
    list_business_set = bind_property(
        Operation,
        name="list_business_set",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/list_business_set/",
    )

    # 查询业务集拓扑
    list_business_set_topo = bind_property(
        Operation,
        name="list_business_set_topo",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/list_business_set_topo/",
    )

    # 查询主机及其对应topo
    list_host_total_mainline_topo = bind_property(
        Operation,
        name="list_host_total_mainline_topo",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/list_host_total_mainline_topo/",
    )

    # 没有业务ID的主机查询
    list_hosts_without_biz = bind_property(
        Operation,
        name="list_hosts_without_biz",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/list_hosts_without_biz/",
    )

    # 查询进程模板列表
    list_proc_template = bind_property(
        Operation,
        name="list_proc_template",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/list_proc_template/",
    )

    # 查询某业务下进程ID对应的进程详情
    list_process_detail_by_ids = bind_property(
        Operation,
        name="list_process_detail_by_ids",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/list_process_detail_by_ids/",
    )

    # 查询进程实例列表
    list_process_instance = bind_property(
        Operation,
        name="list_process_instance",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/list_process_instance/",
    )

    # 查询项目
    list_project = bind_property(
        Operation,
        name="list_project",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/list_project/",
    )

    # 查询资源池中的主机
    list_resource_pool_hosts = bind_property(
        Operation,
        name="list_resource_pool_hosts",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/list_resource_pool_hosts/",
    )

    # 查询服务分类列表
    list_service_category = bind_property(
        Operation,
        name="list_service_category",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/list_service_category/",
    )

    # 查询服务实例列表
    list_service_instance = bind_property(
        Operation,
        name="list_service_instance",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/list_service_instance/",
    )

    # 通过主机查询关联的服务实例列表
    list_service_instance_by_host = bind_property(
        Operation,
        name="list_service_instance_by_host",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/list_service_instance_by_host/",
    )

    # 通过集群模版查询关联的服务实例列表
    list_service_instance_by_set_template = bind_property(
        Operation,
        name="list_service_instance_by_set_template",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/list_service_instance_by_set_template/",
    )

    # 获取服务实例详细信息
    list_service_instance_detail = bind_property(
        Operation,
        name="list_service_instance_detail",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/list_service_instance_detail/",
    )

    # 服务模板列表查询
    list_service_template = bind_property(
        Operation,
        name="list_service_template",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/list_service_template/",
    )

    # 查询集群模板
    list_set_template = bind_property(
        Operation,
        name="list_set_template",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/list_set_template/",
    )

    # 获取某集群模版下的服务模版列表
    list_set_template_related_service_template = bind_property(
        Operation,
        name="list_set_template_related_service_template",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/cc/list_set_template_related_service_template/",
    )

    # 从服务实例移除标签
    remove_label_from_service_instance = bind_property(
        Operation,
        name="remove_label_from_service_instance",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/remove_label_from_service_instance/",
    )

    # 监听资源变化事件
    resource_watch = bind_property(
        Operation,
        name="resource_watch",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/resource_watch/",
    )

    # 查询业务实例拓扑
    search_biz_inst_topo = bind_property(
        Operation,
        name="search_biz_inst_topo",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/cc/search_biz_inst_topo/",
    )

    # 查询业务
    search_business = bind_property(
        Operation,
        name="search_business",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/search_business/",
    )

    # 查询模型分类
    search_classifications = bind_property(
        Operation,
        name="search_classifications",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/search_classifications/",
    )

    # 查询管控区域
    search_cloud_area = bind_property(
        Operation,
        name="search_cloud_area",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/search_cloud_area/",
    )

    # 查询自定义查询
    search_custom_query = bind_property(
        Operation,
        name="search_custom_query",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/search_custom_query/",
    )

    # 搜索动态分组
    search_dynamic_group = bind_property(
        Operation,
        name="search_dynamic_group",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/search_dynamic_group/",
    )

    # 查询主机锁
    search_host_lock = bind_property(
        Operation,
        name="search_host_lock",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/search_host_lock/",
    )

    # 根据关联关系实例查询模型实例
    search_inst = bind_property(
        Operation,
        name="search_inst",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/search_inst/",
    )

    # 查询实例关联拓扑
    search_inst_association_topo = bind_property(
        Operation,
        name="search_inst_association_topo",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/search_inst_association_topo/",
    )

    # 查询实例关联模型实例基本信息
    search_inst_asst_object_inst_base_info = bind_property(
        Operation,
        name="search_inst_asst_object_inst_base_info",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/search_inst_asst_object_inst_base_info/",
    )

    # 查询实例详情
    search_inst_by_object = bind_property(
        Operation,
        name="search_inst_by_object",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/search_inst_by_object/",
    )

    # 查询模型实例关系
    search_instance_associations = bind_property(
        Operation,
        name="search_instance_associations",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/search_instance_associations/",
    )

    # 查询模块
    search_module = bind_property(
        Operation,
        name="search_module",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/search_module/",
    )

    # 查询对象模型属性
    search_object_attribute = bind_property(
        Operation,
        name="search_object_attribute",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/search_object_attribute/",
    )

    # 查询模型实例
    search_object_instances = bind_property(
        Operation,
        name="search_object_instances",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/search_object_instances/",
    )

    # 查询普通模型拓扑
    search_object_topo = bind_property(
        Operation,
        name="search_object_topo",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/search_object_topo/",
    )

    # 查询模型
    search_objects = bind_property(
        Operation,
        name="search_objects",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/search_objects/",
    )

    # 查询某实例所有的关联关系（包含其作为关联关系原模型和关联关系目标模型的情况）
    search_related_inst_asso = bind_property(
        Operation,
        name="search_related_inst_asso",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/search_related_inst_asso/",
    )

    # 查询集群
    search_set = bind_property(
        Operation,
        name="search_set",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/search_set/",
    )

    # 集群模板同步
    sync_set_template_to_set = bind_property(
        Operation,
        name="sync_set_template_to_set",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/sync_set_template_to_set/",
    )

    # 跨业务转移主机
    transfer_host_across_biz = bind_property(
        Operation,
        name="transfer_host_across_biz",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/transfer_host_across_biz/",
    )

    # 业务内主机转移模块
    transfer_host_module = bind_property(
        Operation,
        name="transfer_host_module",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/transfer_host_module/",
    )

    # 上交主机到业务的故障机模块
    transfer_host_to_faultmodule = bind_property(
        Operation,
        name="transfer_host_to_faultmodule",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/transfer_host_to_faultmodule/",
    )

    # 上交主机到业务的空闲机模块
    transfer_host_to_idlemodule = bind_property(
        Operation,
        name="transfer_host_to_idlemodule",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/transfer_host_to_idlemodule/",
    )

    # 上交主机到业务的待回收模块
    transfer_host_to_recyclemodule = bind_property(
        Operation,
        name="transfer_host_to_recyclemodule",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/transfer_host_to_recyclemodule/",
    )

    # 上交主机至资源池
    transfer_host_to_resourcemodule = bind_property(
        Operation,
        name="transfer_host_to_resourcemodule",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/transfer_host_to_resourcemodule/",
    )

    # 资源池主机分配至业务的空闲机模块
    transfer_resourcehost_to_idlemodule = bind_property(
        Operation,
        name="transfer_resourcehost_to_idlemodule",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/transfer_resourcehost_to_idlemodule/",
    )

    # 清空业务下集群/模块中主机
    transfer_sethost_to_idle_module = bind_property(
        Operation,
        name="transfer_sethost_to_idle_module",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/transfer_sethost_to_idle_module/",
    )

    # 将agent和主机解绑
    unbind_host_agent = bind_property(
        Operation,
        name="unbind_host_agent",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/unbind_host_agent/",
    )

    # 更新业务自定义模型属性
    update_biz_custom_field = bind_property(
        Operation,
        name="update_biz_custom_field",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/update_biz_custom_field/",
    )

    # 修改业务
    update_business = bind_property(
        Operation,
        name="update_business",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/update_business/",
    )

    # 修改业务启用状态
    update_business_enable_status = bind_property(
        Operation,
        name="update_business_enable_status",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/update_business_enable_status/",
    )

    # 更新模型分类
    update_classification = bind_property(
        Operation,
        name="update_classification",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/update_classification/",
    )

    # 更新管控区域
    update_cloud_area = bind_property(
        Operation,
        name="update_cloud_area",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/update_cloud_area/",
    )

    # 更新自定义查询
    update_custom_query = bind_property(
        Operation,
        name="update_custom_query",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/update_custom_query/",
    )

    # 更新动态分组
    update_dynamic_group = bind_property(
        Operation,
        name="update_dynamic_group",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/update_dynamic_group/",
    )

    # 更新主机属性
    update_host = bind_property(
        Operation,
        name="update_host",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/update_host/",
    )

    # 更新主机的管控区域字段
    update_host_cloud_area_field = bind_property(
        Operation,
        name="update_host_cloud_area_field",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/update_host_cloud_area_field/",
    )

    # 更新对象实例
    update_inst = bind_property(
        Operation,
        name="update_inst",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/update_inst/",
    )

    # 更新模块
    update_module = bind_property(
        Operation,
        name="update_module",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/update_module/",
    )

    # 更新定义
    update_object = bind_property(
        Operation,
        name="update_object",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/update_object/",
    )

    # 更新对象模型属性
    update_object_attribute = bind_property(
        Operation,
        name="update_object_attribute",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/update_object_attribute/",
    )

    # 更新拓扑图
    update_object_topo_graphics = bind_property(
        Operation,
        name="update_object_topo_graphics",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/update_object_topo_graphics/",
    )

    # 更新进程模板
    update_proc_template = bind_property(
        Operation,
        name="update_proc_template",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/update_proc_template/",
    )

    # 更新进程实例
    update_process_instance = bind_property(
        Operation,
        name="update_process_instance",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/update_process_instance/",
    )

    # 更新服务分类
    update_service_category = bind_property(
        Operation,
        name="update_service_category",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/update_service_category/",
    )

    # 更新服务模板
    update_service_template = bind_property(
        Operation,
        name="update_service_template",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/update_service_template/",
    )

    # 更新集群
    update_set = bind_property(
        Operation,
        name="update_set",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/update_set/",
    )

    # 编辑集群模板
    update_set_template = bind_property(
        Operation,
        name="update_set_template",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/update_set_template/",
    )

    # 批量创建被引用的模型的实例
    batch_create_quoted_inst = bind_property(
        Operation,
        name="batch_create_quoted_inst",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/batch_create_quoted_inst/",
    )

    # 批量删除被引用的模型的实例
    batch_delete_quoted_inst = bind_property(
        Operation,
        name="batch_delete_quoted_inst",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/batch_delete_quoted_inst/",
    )

    # 批量更新被引用的模型的实例
    batch_update_quoted_inst = bind_property(
        Operation,
        name="batch_update_quoted_inst",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/batch_update_quoted_inst/",
    )

    # 查询容器集群
    list_kube_cluster = bind_property(
        Operation,
        name="list_kube_cluster",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/list_kube_cluster/",
    )

    # 查询Container列表
    list_kube_container = bind_property(
        Operation,
        name="list_kube_container",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/list_kube_container/",
    )

    # 查询namespace
    list_kube_namespace = bind_property(
        Operation,
        name="list_kube_namespace",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/list_kube_namespace/",
    )

    # 查询容器节点
    list_kube_node = bind_property(
        Operation,
        name="list_kube_node",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/list_kube_node/",
    )

    # 查询Pod列表
    list_kube_pod = bind_property(
        Operation,
        name="list_kube_pod",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/list_kube_pod/",
    )

    # 查询workload
    list_kube_workload = bind_property(
        Operation,
        name="list_kube_workload",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/list_kube_workload/",
    )

    # 查询被引用的模型的实例列表
    list_quoted_inst = bind_property(
        Operation,
        name="list_quoted_inst",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/list_quoted_inst/",
    )

    # --- 以下api只在te上云版可用 ---
    # 批量查询业务敏感信息
    find_biz_sensitive_batch = bind_property(
        Operation,
        name="find_biz_sensitive_batch",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/find_biz_sensitive_batch/",
    )

    # 批量查询主机快照
    find_host_snapshot_batch = bind_property(
        Operation,
        name="find_host_snapshot_batch",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/find_host_snapshot_batch/",
    )

    # 查询业务在cc1.0还是在cc3.0
    get_biz_location = bind_property(
        Operation,
        name="get_biz_location",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/get_biz_location/",
    )

    # 根据主机IP及云区域ID查询该主机所属业务是在cc1.0还是在cc3.0
    get_host_location = bind_property(
        Operation,
        name="get_host_location",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/get_host_location/",
    )

    # 查询业务、obs产品和规划产品三者之间的关系
    search_cost_info_relation = bind_property(
        Operation,
        name="search_cost_info_relation",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/search_cost_info_relation/",
    )

    # 根据条件查询业务下的进程实例详情
    search_process_instances = bind_property(
        Operation,
        name="search_process_instances",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/search_process_instances/",
    )

    # 查询订阅
    search_subscription = bind_property(
        Operation,
        name="search_subscription",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/search_subscription/",
    )

    # 订阅事件
    subscribe_event = bind_property(
        Operation,
        name="subscribe_event",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/subscribe_event/",
    )

    # 退订事件
    unsubcribe_event = bind_property(
        Operation,
        name="unsubcribe_event",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/unsubcribe_event/",
    )

    # 更新业务敏感信息
    update_biz_sensitive = bind_property(
        Operation,
        name="update_biz_sensitive",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/update_biz_sensitive/",
    )

    # 修改订阅
    update_event_subscribe = bind_property(
        Operation,
        name="update_event_subscribe",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cc/update_event_subscribe/",
    )
    # --- 以上api只在te上云版可用 ---


class CmsiGroup(OperationGroup):
    # 查询消息发送类型
    get_msg_type = bind_property(
        Operation,
        name="get_msg_type",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/cmsi/get_msg_type/",
    )

    # 发送邮件
    send_mail = bind_property(
        Operation,
        name="send_mail",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cmsi/send_mail/",
    )

    # 通用消息发送
    send_msg = bind_property(
        Operation,
        name="send_msg",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cmsi/send_msg/",
    )

    # 发送短信
    send_sms = bind_property(
        Operation,
        name="send_sms",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cmsi/send_sms/",
    )

    # 公共语音通知
    send_voice_msg = bind_property(
        Operation,
        name="send_voice_msg",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cmsi/send_voice_msg/",
    )

    # 发送微信消息
    send_weixin = bind_property(
        Operation,
        name="send_weixin",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cmsi/send_weixin/",
    )

    # --- 以下api只在te上云版可用 ---
    # 添加企业微信发件人
    new_wecom_sender = bind_property(
        Operation,
        name="new_wecom_sender",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cmsi/new_wecom_sender/",
    )

    # 查询企业微信发件人
    query_wecom_sender = bind_property(
        Operation,
        name="query_wecom_sender",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/cmsi/query_wecom_sender/",
    )

    # 发送企业微信
    send_rtx = bind_property(
        Operation,
        name="send_rtx",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cmsi/send_rtx/",
    )

    # 发送企业微信应用号消息
    send_wecom_app = bind_property(
        Operation,
        name="send_wecom_app",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cmsi/send_wecom_app/",
    )

    # 发送企业微信机器人消息
    send_wecom_robot = bind_property(
        Operation,
        name="send_wecom_robot",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/cmsi/send_wecom_robot/",
    )
    # --- 以上api只在te上云版可用 ---

class GseGroup(OperationGroup):
    # Agent心跳信息查询
    get_agent_info = bind_property(
        Operation,
        name="get_agent_info",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/gse/get_agent_info/",
    )

    # Agent在线状态查询
    get_agent_status = bind_property(
        Operation,
        name="get_agent_status",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/gse/get_agent_status/",
    )


class ItsmGroup(OperationGroup):
    # 回调失败的单据
    callback_failed_ticket = bind_property(
        Operation,
        name="callback_failed_ticket",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/itsm/callback_failed_ticket/",
    )

    # 评论单据
    comment_ticket = bind_property(
        Operation,
        name="comment_ticket",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/itsm/comment_ticket/",
    )

    # 创建服务目录
    create_service_catalog = bind_property(
        Operation,
        name="create_service_catalog",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/itsm/create_service_catalog/",
    )

    # 创建单据
    create_ticket = bind_property(
        Operation,
        name="create_ticket",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/itsm/create_ticket/",
    )

    # 服务目录查询
    get_service_catalogs = bind_property(
        Operation,
        name="get_service_catalogs",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/itsm/get_service_catalogs/",
    )

    # 服务详情查询
    get_service_detail = bind_property(
        Operation,
        name="get_service_detail",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/itsm/get_service_detail/",
    )

    # 服务角色查询
    get_service_roles = bind_property(
        Operation,
        name="get_service_roles",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/itsm/get_service_roles/",
    )

    # 服务列表查询
    get_services = bind_property(
        Operation,
        name="get_services",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/itsm/get_services/",
    )

    # 单据详情查询
    get_ticket_info = bind_property(
        Operation,
        name="get_ticket_info",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/itsm/get_ticket_info/",
    )

    # 单据日志查询
    get_ticket_logs = bind_property(
        Operation,
        name="get_ticket_logs",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/itsm/get_ticket_logs/",
    )

    # 单据状态查询
    get_ticket_status = bind_property(
        Operation,
        name="get_ticket_status",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/itsm/get_ticket_status/",
    )

    # 获取单据列表
    get_tickets = bind_property(
        Operation,
        name="get_tickets",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/itsm/get_tickets/",
    )

    # 单据详情查询
    get_workflow_detail = bind_property(
        Operation,
        name="get_workflow_detail",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/itsm/get_workflow_detail/",
    )

    # 导入服务
    import_service = bind_property(
        Operation,
        name="import_service",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/itsm/import_service/",
    )

    # 处理单据节点
    operate_node = bind_property(
        Operation,
        name="operate_node",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/itsm/operate_node/",
    )

    # 处理单据
    operate_ticket = bind_property(
        Operation,
        name="operate_ticket",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/itsm/operate_ticket/",
    )

    # 审批结果查询
    ticket_approval_result = bind_property(
        Operation,
        name="ticket_approval_result",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/itsm/ticket_approval_result/",
    )

    # token校验
    token_verify = bind_property(
        Operation,
        name="token_verify",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/itsm/token/verify/",
    )

    # 更新服务
    update_service = bind_property(
        Operation,
        name="update_service",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/itsm/update_service/",
    )


class Jobv3Group(OperationGroup):
    # 根据ip列表批量查询作业执行日志
    batch_get_job_instance_ip_log = bind_property(
        Operation,
        name="batch_get_job_instance_ip_log",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/batch_get_job_instance_ip_log/",
    )

    # 执行作业执行方案
    execute_job_plan = bind_property(
        Operation,
        name="execute_job_plan",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/execute_job_plan/",
    )

    # 快速执行脚本
    fast_execute_script = bind_property(
        Operation,
        name="fast_execute_script",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/fast_execute_script/",
    )

    # 快速执行SQL
    fast_execute_sql = bind_property(
        Operation,
        name="fast_execute_sql",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/fast_execute_sql/",
    )

    # 快速分发文件
    fast_transfer_file = bind_property(
        Operation,
        name="fast_transfer_file",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/fast_transfer_file/",
    )

    # 查询业务下的执行账号
    get_account_list = bind_property(
        Operation,
        name="get_account_list",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/jobv3/get_account_list/",
    )

    # 查询定时作业详情
    get_cron_detail = bind_property(
        Operation,
        name="get_cron_detail",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/jobv3/get_cron_detail/",
    )

    # 查询业务下定时作业信息
    get_cron_list = bind_property(
        Operation,
        name="get_cron_list",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/jobv3/get_cron_list/",
    )

    # 获取作业实例全局变量值
    get_job_instance_global_var_value = bind_property(
        Operation,
        name="get_job_instance_global_var_value",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/jobv3/get_job_instance_global_var_value/",
    )

    # 根据作业实例ID查询作业执行日志
    get_job_instance_ip_log = bind_property(
        Operation,
        name="get_job_instance_ip_log",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/jobv3/get_job_instance_ip_log/",
    )

    # 查询作业实例列表(执行历史)
    get_job_instance_list = bind_property(
        Operation,
        name="get_job_instance_list",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/jobv3/get_job_instance_list/",
    )

    # 根据作业实例 ID 查询作业执行状态
    get_job_instance_status = bind_property(
        Operation,
        name="get_job_instance_status",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/jobv3/get_job_instance_status/",
    )

    # 查询执行方案详情
    get_job_plan_detail = bind_property(
        Operation,
        name="get_job_plan_detail",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/jobv3/get_job_plan_detail/",
    )

    # 查询执行方案列表
    get_job_plan_list = bind_property(
        Operation,
        name="get_job_plan_list",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/jobv3/get_job_plan_list/",
    )

    # 查询作业模版列表
    get_job_template_list = bind_property(
        Operation,
        name="get_job_template_list",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/jobv3/get_job_template_list/",
    )

    # 查询公共脚本列表
    get_public_script_list = bind_property(
        Operation,
        name="get_public_script_list",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/jobv3/get_public_script_list/",
    )

    # 查询公共脚本详情
    get_public_script_version_detail = bind_property(
        Operation,
        name="get_public_script_version_detail",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/jobv3/get_public_script_version_detail/",
    )

    # 查询公共脚本版本列表
    get_public_script_version_list = bind_property(
        Operation,
        name="get_public_script_version_list",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/jobv3/get_public_script_version_list/",
    )

    # 查询脚本列表
    get_script_list = bind_property(
        Operation,
        name="get_script_list",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/jobv3/get_script_list/",
    )

    # 查询脚本详情
    get_script_version_detail = bind_property(
        Operation,
        name="get_script_version_detail",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/jobv3/get_script_version_detail/",
    )

    # 查询脚本版本列表
    get_script_version_list = bind_property(
        Operation,
        name="get_script_version_list",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/jobv3/get_script_version_list/",
    )

    # 作业实例操作
    operate_job_instance = bind_property(
        Operation,
        name="operate_job_instance",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/operate_job_instance/",
    )

    # 步骤实例操作
    operate_step_instance = bind_property(
        Operation,
        name="operate_step_instance",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/operate_step_instance/",
    )

    # 新建或保存定时作业
    save_cron = bind_property(
        Operation,
        name="save_cron",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/save_cron/",
    )

    # 更新定时作业状态，如启动或暂停
    update_cron_status = bind_property(
        Operation,
        name="update_cron_status",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/update_cron_status/",
    )

    # 作业类回调报文描述
    callback_protocol = bind_property(
        Operation,
        name="callback_protocol",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/callback_protocol/",
    )

    # 高危脚本检测
    check_script = bind_property(
        Operation,
        name="check_script",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/check_script/",
    )

    # 创建账号
    create_account = bind_property(
        Operation,
        name="create_account",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/create_account/",
    )

    # 创建高危语句规则
    create_dangerous_rule = bind_property(
        Operation,
        name="create_dangerous_rule",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/create_dangerous_rule/",
    )

    # 创建公共脚本
    create_public_script = bind_property(
        Operation,
        name="create_public_script",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/create_public_script/",
    )

    # 新建公共脚本版本
    create_public_script_version = bind_property(
        Operation,
        name="create_public_script_version",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/create_public_script_version/",
    )

    # 创建脚本
    create_script = bind_property(
        Operation,
        name="create_script",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/create_script/",
    )

    # 新建脚本版本
    create_script_version = bind_property(
        Operation,
        name="create_script_version",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/create_script_version/",
    )

    # 删除账号
    delete_account = bind_property(
        Operation,
        name="delete_account",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/delete_account/",
    )

    # 删除高危语句规则
    delete_dangerous_rule = bind_property(
        Operation,
        name="delete_dangerous_rule",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/delete_dangerous_rule/",
    )

    # 删除公共脚本
    delete_public_script = bind_property(
        Operation,
        name="delete_public_script",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/delete_public_script/",
    )

    # 删除公共脚本版本
    delete_public_script_version = bind_property(
        Operation,
        name="delete_public_script_version",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/delete_public_script_version/",
    )

    # 删除脚本
    delete_script = bind_property(
        Operation,
        name="delete_script",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/delete_script/",
    )

    # 删除脚本版本
    delete_script_version = bind_property(
        Operation,
        name="delete_script_version",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/delete_script_version/",
    )

    # 停用高危语句规则
    disable_dangerous_rule = bind_property(
        Operation,
        name="disable_dangerous_rule",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/disable_dangerous_rule/",
    )

    # 禁用公共脚本版本
    disable_public_script_version = bind_property(
        Operation,
        name="disable_public_script_version",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/disable_public_script_version/",
    )

    # 禁用脚本版本
    disable_script_version = bind_property(
        Operation,
        name="disable_script_version",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/disable_script_version/",
    )

    # 启用高危语句规则
    enable_dangerous_rule = bind_property(
        Operation,
        name="enable_dangerous_rule",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/enable_dangerous_rule/",
    )

    # 查看高危语句规则列表
    get_dangerous_rule_list = bind_property(
        Operation,
        name="get_dangerous_rule_list",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/get_dangerous_rule_list/",
    )

    # 发布公共脚本版本
    publish_public_script_version = bind_property(
        Operation,
        name="publish_public_script_version",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/publish_public_script_version/",
    )

    # 发布脚本版本
    publish_script_version = bind_property(
        Operation,
        name="publish_script_version",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/publish_script_version/",
    )

    # 修改高危语句规则
    update_dangerous_rule = bind_property(
        Operation,
        name="update_dangerous_rule",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/update_dangerous_rule/",
    )

    # 更新公共脚本基础信息
    update_public_script_basic = bind_property(
        Operation,
        name="update_public_script_basic",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/update_public_script_basic/",
    )

    # 修改公共脚本版本
    update_public_script_version = bind_property(
        Operation,
        name="update_public_script_version",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/update_public_script_version/",
    )

    # 更新脚本基础信息
    update_script_basic = bind_property(
        Operation,
        name="update_script_basic",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/update_script_basic/",
    )

    # 修改脚本版本信息
    update_script_version = bind_property(
        Operation,
        name="update_script_version",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/jobv3/update_script_version/",
    )


class MonitorV3Group(OperationGroup):
    # 新增告警屏蔽
    add_shield = bind_property(
        Operation,
        name="add_shield",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/add_shield/",
    )

    # 快速创建APM应用
    apm_create_application = bind_property(
        Operation,
        name="apm_create_application",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/apm/create_application/",
    )

    # 删除处理套餐
    delete_action_config = bind_property(
        Operation,
        name="delete_action_config",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/delete_action_config/",
    )

    # 删除告警策略
    delete_alarm_strategy = bind_property(
        Operation,
        name="delete_alarm_strategy",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/delete_alarm_strategy/",
    )

    # 删除告警策略
    delete_alarm_strategy_v2 = bind_property(
        Operation,
        name="delete_alarm_strategy_v2",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/delete_alarm_strategy_v2/",
    )

    # 删除告警策略
    delete_alarm_strategy_v3 = bind_property(
        Operation,
        name="delete_alarm_strategy_v3",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/delete_alarm_strategy_v3/",
    )

    # 删除通知组
    delete_notice_group = bind_property(
        Operation,
        name="delete_notice_group",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/delete_notice_group/",
    )

    # 解除告警屏蔽
    disable_shield = bind_property(
        Operation,
        name="disable_shield",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/disable_shield/",
    )

    # 编辑处理套餐
    edit_action_config = bind_property(
        Operation,
        name="edit_action_config",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/edit_action_config/",
    )

    # 编辑告警屏蔽
    edit_shield = bind_property(
        Operation,
        name="edit_shield",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/edit_shield/",
    )

    # 导出拨测任务配置
    export_uptime_check_task = bind_property(
        Operation,
        name="export_uptime_check_task",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/export_uptime_check_task/",
    )

    # 获取单个处理套餐
    get_action_config = bind_property(
        Operation,
        name="get_action_config",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/get_action_config/",
    )

    # 查询事件流转记录
    get_event_log = bind_property(
        Operation,
        name="get_event_log",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/get_event_log/",
    )

    # 获取告警屏蔽
    get_shield = bind_property(
        Operation,
        name="get_shield",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/get_shield/",
    )

    # 获取时序数据
    get_ts_data = bind_property(
        Operation,
        name="get_ts_data",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/get_ts_data/",
    )

    # 导入拨测节点配置
    import_uptime_check_node = bind_property(
        Operation,
        name="import_uptime_check_node",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/import_uptime_check_node/",
    )

    # 导入拨测任务配置
    import_uptime_check_task = bind_property(
        Operation,
        name="import_uptime_check_task",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/import_uptime_check_task/",
    )

    # 获取告警屏蔽列表
    list_shield = bind_property(
        Operation,
        name="list_shield",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/list_shield/",
    )

    # 创建存储集群信息
    metadata_create_cluster_info = bind_property(
        Operation,
        name="metadata_create_cluster_info",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_create_cluster_info/",
    )

    # 创建监控数据源
    metadata_create_data_id = bind_property(
        Operation,
        name="metadata_create_data_id",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_create_data_id/",
    )

    # 创建事件分组
    metadata_create_event_group = bind_property(
        Operation,
        name="metadata_create_event_group",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_create_event_group/",
    )

    # 创建日志分组
    metadata_create_log_group = bind_property(
        Operation,
        name="metadata_create_log_group",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_create_log_group/",
    )

    # 创建监控结果表
    metadata_create_result_table = bind_property(
        Operation,
        name="metadata_create_result_table",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_create_result_table/",
    )

    # 创建结果表的维度拆分配置
    metadata_create_result_table_metric_split = bind_property(
        Operation,
        name="metadata_create_result_table_metric_split",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_create_result_table_metric_split/",
    )

    # 创建自定义时序分组
    metadata_create_time_series_group = bind_property(
        Operation,
        name="metadata_create_time_series_group",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_create_time_series_group/",
    )

    # 删除事件分组
    metadata_delete_event_group = bind_property(
        Operation,
        name="metadata_delete_event_group",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_delete_event_group/",
    )

    # 删除日志分组
    metadata_delete_log_group = bind_property(
        Operation,
        name="metadata_delete_log_group",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_delete_log_group/",
    )

    # 删除自定义时序分组
    metadata_delete_time_series_group = bind_property(
        Operation,
        name="metadata_delete_time_series_group",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_delete_time_series_group/",
    )

    # 获取监控数据源具体信息
    metadata_get_data_id = bind_property(
        Operation,
        name="metadata_get_data_id",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_get_data_id/",
    )

    # 查询事件分组具体内容
    metadata_get_event_group = bind_property(
        Operation,
        name="metadata_get_event_group",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_get_event_group/",
    )

    # 查询日志分组具体内容
    metadata_get_log_group = bind_property(
        Operation,
        name="metadata_get_log_group",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_get_log_group/",
    )

    # 获取监控结果表具体信息
    metadata_get_result_table = bind_property(
        Operation,
        name="metadata_get_result_table",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_get_result_table/",
    )

    # 查询指定结果表的指定存储信息
    metadata_get_result_table_storage = bind_property(
        Operation,
        name="metadata_get_result_table_storage",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_get_result_table_storage/",
    )

    # 获取自定义时序分组具体内容
    metadata_get_time_series_group = bind_property(
        Operation,
        name="metadata_get_time_series_group",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_get_time_series_group/",
    )

    # 查询当前已有的标签信息
    metadata_list_label = bind_property(
        Operation,
        name="metadata_list_label",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_list_label/",
    )

    # 查询监控结果表
    metadata_list_result_table = bind_property(
        Operation,
        name="metadata_list_result_table",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_list_result_table/",
    )

    # 获取所有transfer集群信息
    metadata_list_transfer_cluster = bind_property(
        Operation,
        name="metadata_list_transfer_cluster",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_list_transfer_cluster/",
    )

    # 修改存储集群信息
    metadata_modify_cluster_info = bind_property(
        Operation,
        name="metadata_modify_cluster_info",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_modify_cluster_info/",
    )

    # 修改指定数据源的配置信息
    metadata_modify_data_id = bind_property(
        Operation,
        name="metadata_modify_data_id",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_modify_data_id/",
    )

    # 修改事件分组
    metadata_modify_event_group = bind_property(
        Operation,
        name="metadata_modify_event_group",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_modify_event_group/",
    )

    # 修改日志分组
    metadata_modify_log_group = bind_property(
        Operation,
        name="metadata_modify_log_group",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_modify_log_group/",
    )

    # 修改监控结果表
    metadata_modify_result_table = bind_property(
        Operation,
        name="metadata_modify_result_table",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_modify_result_table/",
    )

    # 修改自定义时序分组
    metadata_modify_time_series_group = bind_property(
        Operation,
        name="metadata_modify_time_series_group",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_modify_time_series_group/",
    )

    # 查询事件分组
    metadata_query_event_group = bind_property(
        Operation,
        name="metadata_query_event_group",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_query_event_group/",
    )

    # 查询日志分组
    metadata_query_log_group = bind_property(
        Operation,
        name="metadata_query_log_group",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_query_log_group/",
    )

    # 获取自定义时序分组具体内容
    metadata_query_tag_values = bind_property(
        Operation,
        name="metadata_query_tag_values",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_query_tag_values/",
    )

    # 查询事件分组
    metadata_query_time_series_group = bind_property(
        Operation,
        name="metadata_query_time_series_group",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_query_time_series_group/",
    )

    # 将指定的监控单业务结果表升级为全业务结果表
    metadata_upgrade_result_table = bind_property(
        Operation,
        name="metadata_upgrade_result_table",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_upgrade_result_table/",
    )

    # 修改数据源与结果表的关系
    modify_datasource_result_table = bind_property(
        Operation,
        name="modify_datasource_result_table",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_modify_datasource_result_table/",
    )

    # 保存处理套餐
    save_action_config = bind_property(
        Operation,
        name="save_action_config",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/save_action_config/",
    )

    # 保存告警策略
    save_alarm_strategy = bind_property(
        Operation,
        name="save_alarm_strategy",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/save_alarm_strategy/",
    )

    # 保存告警策略
    save_alarm_strategy_v2 = bind_property(
        Operation,
        name="save_alarm_strategy_v2",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/save_alarm_strategy_v2/",
    )

    # 保存告警策略
    save_alarm_strategy_v3 = bind_property(
        Operation,
        name="save_alarm_strategy_v3",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/save_alarm_strategy_v3/",
    )

    # 保存通知组
    save_notice_group = bind_property(
        Operation,
        name="save_notice_group",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/save_notice_group/",
    )

    # 查询处理记录
    search_action = bind_property(
        Operation,
        name="search_action",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/search_action/",
    )

    # 批量获取处理套餐
    search_action_config = bind_property(
        Operation,
        name="search_action_config",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/search_action_config/",
    )

    # 查询告警策略
    search_alarm_strategy = bind_property(
        Operation,
        name="search_alarm_strategy",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/search_alarm_strategy/",
    )

    # 查询告警策略
    search_alarm_strategy_v2 = bind_property(
        Operation,
        name="search_alarm_strategy_v2",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/search_alarm_strategy_v2/",
    )

    # 查询告警策略
    search_alarm_strategy_v3 = bind_property(
        Operation,
        name="search_alarm_strategy_v3",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/search_alarm_strategy_v3/",
    )

    # 查询全业务告警策略
    search_alarm_strategy_without_biz = bind_property(
        Operation,
        name="search_alarm_strategy_without_biz",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/search_alarm_strategy_without_biz/",
    )

    # 查询告警记录
    search_alert = bind_property(
        Operation,
        name="search_alert",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/search_alert/",
    )

    # 查询事件
    search_event = bind_property(
        Operation,
        name="search_event",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/search_event/",
    )

    # 查询通知组
    search_notice_group = bind_property(
        Operation,
        name="search_notice_group",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/search_notice_group/",
    )

    # 启停告警策略
    switch_alarm_strategy = bind_property(
        Operation,
        name="switch_alarm_strategy",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/switch_alarm_strategy/",
    )

    # 视图数据查询
    time_series_unify_query = bind_property(
        Operation,
        name="time_series_unify_query",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/time_series_unify_query/",
    )

    # 批量更新策略局部配置
    update_partial_strategy_v2 = bind_property(
        Operation,
        name="update_partial_strategy_v2",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/update_partial_strategy_v2/",
    )

    # 批量更新策略局部配置
    update_partial_strategy_v3 = bind_property(
        Operation,
        name="update_partial_strategy_v3",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/update_partial_strategy_v3/",
    )

    # 批量删除轮值规则
    delete_duty_rules = bind_property(
        Operation,
        name="delete_duty_rules",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/delete_duty_rules/",
    )

    # 删除分派组
    delete_rule_group = bind_property(
        Operation,
        name="delete_rule_group",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/delete_rule_group/",
    )

    # 批量删除用户组
    delete_user_groups = bind_property(
        Operation,
        name="delete_user_groups",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/delete_user_groups/",
    )

    # 指标通用查询
    get_metric_list = bind_property(
        Operation,
        name="get_metric_list",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/get_metric_list/",
    )

    # 事件检索
    grafana_log_query = bind_property(
        Operation,
        name="grafana_log_query",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/grafana_log_query/",
    )

    # 判断结果表中是否存在指定data_label
    metadata_is_data_label_exist = bind_property(
        Operation,
        name="metadata_is_data_label_exist",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_is_data_label_exist/",
    )

    # 根据space_uid查询data_source
    metadata_query_data_source_by_space_uid = bind_property(
        Operation,
        name="metadata_query_data_source_by_space_uid",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/metadata_query_data_source_by_space_uid/",
    )

    # 预览轮值规则
    preview_duty_rule = bind_property(
        Operation,
        name="preview_duty_rule",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/preview_duty_rule/",
    )

    # 预览一个组的轮值规则
    preview_user_group = bind_property(
        Operation,
        name="preview_user_group",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/preview_user_group/",
    )

    # 保存轮值规则
    save_duty_rule = bind_property(
        Operation,
        name="save_duty_rule",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/save_duty_rule/",
    )

    # 保存分派组
    save_rule_group = bind_property(
        Operation,
        name="save_rule_group",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/save_rule_group/",
    )

    # 保存用户组
    save_user_group = bind_property(
        Operation,
        name="save_user_group",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/save_user_group/",
    )

    # 查询轮值规则组
    search_duty_rules = bind_property(
        Operation,
        name="search_duty_rules",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/search_duty_rules/",
    )

    # 查询单个轮值规则的详情
    search_duty_rule_detail = bind_property(
        Operation,
        name="search_duty_rule_detail",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/search_duty_rule_detail/",
    )

    # 查询分派组
    search_rule_groups = bind_property(
        Operation,
        name="search_rule_groups",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/search_rule_groups/",
    )

    # 查询用户组(新版)
    search_user_groups = bind_property(
        Operation,
        name="search_user_groups",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/search_user_groups/",
    )

    # 查询单个用户组详情
    search_user_group_detail = bind_property(
        Operation,
        name="search_user_group_detail",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/monitor_v3/search_user_group_detail/",
    )


class SopsGroup(OperationGroup):
    # 认领职能化任务
    claim_functionalization_task = bind_property(
        Operation,
        name="claim_functionalization_task",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/sops/claim_functionalization_task/",
    )

    # 创建并开始执行任务
    create_and_start_task = bind_property(
        Operation,
        name="create_and_start_task",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/sops/create_and_start_task/",
    )

    # 通过流程模板新建周期任务
    create_periodic_task = bind_property(
        Operation,
        name="create_periodic_task",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/sops/create_periodic_task/",
    )

    # 通过流程模板新建任务
    create_task = bind_property(
        Operation,
        name="create_task",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/sops/create_task/",
    )

    # 快速新建一次性任务
    fast_create_task = bind_property(
        Operation,
        name="fast_create_task",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/sops/fast_create_task/",
    )

    # 查询单个公共流程模板详情
    get_common_template_info = bind_property(
        Operation,
        name="get_common_template_info",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/sops/get_common_template_info/",
    )

    # 查询公共模板列表
    get_common_template_list = bind_property(
        Operation,
        name="get_common_template_list",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/sops/get_common_template_list/",
    )

    # 获取职能化任务列表
    get_functionalization_task_list = bind_property(
        Operation,
        name="get_functionalization_task_list",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/sops/get_functionalization_task_list/",
    )

    # 查询业务下的某个周期任务详情
    get_periodic_task_info = bind_property(
        Operation,
        name="get_periodic_task_info",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/sops/get_periodic_task_info/",
    )

    # 查询业务下的周期任务列表
    get_periodic_task_list = bind_property(
        Operation,
        name="get_periodic_task_list",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/sops/get_periodic_task_list/",
    )

    # 根据插件code获取某个业务下对应插件信息
    get_plugin_detail = bind_property(
        Operation,
        name="get_plugin_detail",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/sops/get_plugin_detail/",
    )

    # 查询某个业务下的插件列表
    get_plugin_list = bind_property(
        Operation,
        name="get_plugin_list",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/sops/get_plugin_list/",
    )

    # 查询任务执行详情
    get_task_detail = bind_property(
        Operation,
        name="get_task_detail",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/sops/get_task_detail/",
    )

    # 获取业务下的任务列表
    get_task_list = bind_property(
        Operation,
        name="get_task_list",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/sops/get_task_list/",
    )

    # 获取节点执行数据
    get_task_node_data = bind_property(
        Operation,
        name="get_task_node_data",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/sops/get_task_node_data/",
    )

    # 查询任务节点执行详情
    get_task_node_detail = bind_property(
        Operation,
        name="get_task_node_detail",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/sops/get_task_node_detail/",
    )

    # 查询任务或任务节点执行状态
    get_task_status = bind_property(
        Operation,
        name="get_task_status",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/sops/get_task_status/",
    )

    # 获取一批任务的是否需要人工干预的判断状态
    get_tasks_manual_intervention_state = bind_property(
        Operation,
        name="get_tasks_manual_intervention_state",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/sops/get_tasks_manual_intervention_state/",
    )

    # 批量查询任务状态
    get_tasks_status = bind_property(
        Operation,
        name="get_tasks_status",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/sops/get_tasks_status/",
    )

    # 查询单个模板详情
    get_template_info = bind_property(
        Operation,
        name="get_template_info",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/sops/get_template_info/",
    )

    # 查询模板列表
    get_template_list = bind_property(
        Operation,
        name="get_template_list",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/sops/get_template_list/",
    )

    # 获取模板执行方案列表
    get_template_schemes = bind_property(
        Operation,
        name="get_template_schemes",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/sops/get_template_schemes/",
    )

    # 获取项目详情
    get_user_project_detail = bind_property(
        Operation,
        name="get_user_project_detail",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/sops/get_user_project_detail/",
    )

    # 获取用户有权限的项目列表
    get_user_project_list = bind_property(
        Operation,
        name="get_user_project_list",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/sops/get_user_project_list/",
    )

    # 导入公共流程
    import_common_template = bind_property(
        Operation,
        name="import_common_template",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/sops/import_common_template/",
    )

    # 导入业务流程模板
    import_project_template = bind_property(
        Operation,
        name="import_project_template",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/sops/import_project_template/",
    )

    # 修改周期任务的全局参数
    modify_constants_for_periodic_task = bind_property(
        Operation,
        name="modify_constants_for_periodic_task",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/sops/modify_constants_for_periodic_task/",
    )

    # 修改任务的全局参数
    modify_constants_for_task = bind_property(
        Operation,
        name="modify_constants_for_task",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/sops/modify_constants_for_task/",
    )

    # 修改周期任务的调度策略
    modify_cron_for_periodic_task = bind_property(
        Operation,
        name="modify_cron_for_periodic_task",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/sops/modify_cron_for_periodic_task/",
    )

    # 回调任务节点
    node_callback = bind_property(
        Operation,
        name="node_callback",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/sops/node_callback/",
    )

    # 操作任务中的节点
    operate_node = bind_property(
        Operation,
        name="operate_node",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/sops/operate_node/",
    )

    # 操作任务
    operate_task = bind_property(
        Operation,
        name="operate_task",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/sops/operate_task/",
    )

    # 获取节点选择后新的任务树（针对公共流程）
    preview_common_task_tree = bind_property(
        Operation,
        name="preview_common_task_tree",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/sops/preview_common_task_tree/",
    )

    # 获取节点选择后新的任务树
    preview_task_tree = bind_property(
        Operation,
        name="preview_task_tree",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/sops/preview_task_tree/",
    )

    # 查询任务分类统计总数
    query_task_count = bind_property(
        Operation,
        name="query_task_count",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/sops/query_task_count/",
    )

    # 设置周期任务是否激活
    set_periodic_task_enabled = bind_property(
        Operation,
        name="set_periodic_task_enabled",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/sops/set_periodic_task_enabled/",
    )

    # 开始执行任务
    start_task = bind_property(
        Operation,
        name="start_task",
        method="POST",
        path="/api/c/compapi{bk_api_ver}/sops/start_task/",
    )


class UsermanageGroup(OperationGroup):
    # 查询部门的用户信息 (v2)
    list_department_profiles = bind_property(
        Operation,
        name="list_department_profiles",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/usermanage/list_department_profiles/",
    )

    # 查询部门 (v2)
    list_departments = bind_property(
        Operation,
        name="list_departments",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/usermanage/list_departments/",
    )

    # 查询用户的部门信息 (v2)
    list_profile_departments = bind_property(
        Operation,
        name="list_profile_departments",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/usermanage/list_profile_departments/",
    )

    # 查询用户 (v2)
    list_users = bind_property(
        Operation,
        name="list_users",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/usermanage/list_users/",
    )

    # 查询单个部门信息 (v2)
    retrieve_department = bind_property(
        Operation,
        name="retrieve_department",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/usermanage/retrieve_department/",
    )

    # 查询单个用户信息 (v2)
    retrieve_user = bind_property(
        Operation,
        name="retrieve_user",
        method="GET",
        path="/api/c/compapi{bk_api_ver}/usermanage/retrieve_user/",
    )


class Client(ESBClient):
    """ESB Components"""
    bk_login = bind_property(BkLoginGroup, name="bk_login")
    cc = bind_property(CcGroup, name="cc")
    cmsi = bind_property(CmsiGroup, name="cmsi")
    gse = bind_property(GseGroup, name="gse")
    itsm = bind_property(ItsmGroup, name="itsm")
    jobv3 = bind_property(Jobv3Group, name="jobv3")
    monitor_v3 = bind_property(MonitorV3Group, name="monitor_v3")
    sops = bind_property(SopsGroup, name="sops")
    usermanage = bind_property(UsermanageGroup, name="usermanage")
