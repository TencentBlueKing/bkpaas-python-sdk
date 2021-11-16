from bkapi_client_core.esb import ESBClient, Operation, OperationGroup


class BkLoginGroup(OperationGroup):

    @property
    def get_user(self) -> Operation:
        """获取用户信息"""


class CcGroup(OperationGroup):

    @property
    def add_host_lock(self) -> Operation:
        """新加主机锁"""

    @property
    def add_host_to_resource(self) -> Operation:
        """新增主机到资源池"""

    @property
    def add_instance_association(self) -> Operation:
        """新建模型实例之间的关联关系"""

    @property
    def add_label_for_service_instance(self) -> Operation:
        """为服务实例添加标签"""

    @property
    def batch_create_proc_template(self) -> Operation:
        """批量创建进程模板"""

    @property
    def batch_delete_inst(self) -> Operation:
        """批量删除实例"""

    @property
    def batch_delete_set(self) -> Operation:
        """批量删除集群"""

    @property
    def batch_update_host(self) -> Operation:
        """批量更新主机属性"""

    @property
    def batch_update_inst(self) -> Operation:
        """批量更新对象实例"""

    @property
    def bind_role_privilege(self) -> Operation:
        """绑定角色权限"""

    @property
    def clone_host_property(self) -> Operation:
        """克隆主机属性"""

    @property
    def count_instance_associations(self) -> Operation:
        """查询模型实例关系数量"""

    @property
    def count_object_instances(self) -> Operation:
        """查询模型实例数量"""

    @property
    def create_biz_custom_field(self) -> Operation:
        """创建业务自定义模型属性"""

    @property
    def create_business(self) -> Operation:
        """新建业务"""

    @property
    def create_classification(self) -> Operation:
        """添加模型分类"""

    @property
    def create_cloud_area(self) -> Operation:
        """创建云区域"""

    @property
    def create_custom_query(self) -> Operation:
        """添加自定义查询"""

    @property
    def create_dynamic_group(self) -> Operation:
        """创建动态分组"""

    @property
    def create_inst(self) -> Operation:
        """创建实例"""

    @property
    def create_module(self) -> Operation:
        """创建模块"""

    @property
    def create_object(self) -> Operation:
        """创建模型"""

    @property
    def create_object_attribute(self) -> Operation:
        """创建模型属性"""

    @property
    def create_process_instance(self) -> Operation:
        """创建进程实例"""

    @property
    def create_service_category(self) -> Operation:
        """新建服务分类"""

    @property
    def create_service_instance(self) -> Operation:
        """创建服务实例"""

    @property
    def create_service_template(self) -> Operation:
        """新建服务模板"""

    @property
    def create_set(self) -> Operation:
        """创建集群"""

    @property
    def create_set_template(self) -> Operation:
        """新建集群模板"""

    @property
    def delete_business(self) -> Operation:
        """删除业务"""

    @property
    def delete_classification(self) -> Operation:
        """删除模型分类"""

    @property
    def delete_cloud_area(self) -> Operation:
        """删除云区域"""

    @property
    def delete_custom_query(self) -> Operation:
        """删除自定义查询"""

    @property
    def delete_dynamic_group(self) -> Operation:
        """删除动态分组"""

    @property
    def delete_host(self) -> Operation:
        """删除主机"""

    @property
    def delete_host_lock(self) -> Operation:
        """删除主机锁"""

    @property
    def delete_inst(self) -> Operation:
        """删除实例"""

    @property
    def delete_instance_association(self) -> Operation:
        """删除模型实例之间的关联关系"""

    @property
    def delete_module(self) -> Operation:
        """删除模块"""

    @property
    def delete_object(self) -> Operation:
        """删除模型"""

    @property
    def delete_object_attribute(self) -> Operation:
        """删除对象模型属性"""

    @property
    def delete_proc_template(self) -> Operation:
        """删除进程模板"""

    @property
    def delete_process_instance(self) -> Operation:
        """删除进程实例"""

    @property
    def delete_related_inst_asso(self) -> Operation:
        """删除某实例所有的关联关系（包含其作为关联关系原模型和关联关系目标模型的情况）"""

    @property
    def delete_service_category(self) -> Operation:
        """删除服务分类"""

    @property
    def delete_service_instance(self) -> Operation:
        """删除服务实例"""

    @property
    def delete_service_template(self) -> Operation:
        """删除服务模板"""

    @property
    def delete_set(self) -> Operation:
        """删除集群"""

    @property
    def delete_set_template(self) -> Operation:
        """删除集群模板"""

    @property
    def execute_dynamic_group(self) -> Operation:
        """执行动态分组"""

    @property
    def find_brief_biz_topo_node_relation(self) -> Operation:
        """查询业务主线实例拓扑源与目标节点的关系信息"""

    @property
    def find_host_biz_relations(self) -> Operation:
        """查询主机业务关系信息"""

    @property
    def find_host_by_service_template(self) -> Operation:
        """查询服务模板下的主机"""

    @property
    def find_host_by_set_template(self) -> Operation:
        """查询集群模板下的主机"""

    @property
    def find_host_by_topo(self) -> Operation:
        """查询拓扑节点下的主机"""

    @property
    def find_host_relations_with_topo(self) -> Operation:
        """根据业务拓扑中的实例节点查询其下的主机关系信息"""

    @property
    def find_host_topo_relation(self) -> Operation:
        """获取主机与拓扑的关系"""

    @property
    def find_instance_association(self) -> Operation:
        """查询模型实例之间的关联关系"""

    @property
    def find_module_batch(self) -> Operation:
        """批量查询某业务的模块详情"""

    @property
    def find_module_host_relation(self) -> Operation:
        """根据模块ID查询主机和模块的关系"""

    @property
    def find_module_with_relation(self) -> Operation:
        """根据条件查询业务下的模块"""

    @property
    def find_object_association(self) -> Operation:
        """查询模型之间的关联关系"""

    @property
    def find_set_batch(self) -> Operation:
        """批量查询某业务的集群详情"""

    @property
    def find_topo_node_paths(self) -> Operation:
        """查询业务拓扑节点的拓扑路径"""

    @property
    def get_biz_internal_module(self) -> Operation:
        """查询业务的空闲机/故障机/待回收模块"""

    @property
    def get_custom_query_data(self) -> Operation:
        """根据自定义查询获取数据"""

    @property
    def get_custom_query_detail(self) -> Operation:
        """获取自定义查询详情"""

    @property
    def get_dynamic_group(self) -> Operation:
        """查询指定动态分组"""

    @property
    def get_host_base_info(self) -> Operation:
        """获取主机详情"""

    @property
    def get_mainline_object_topo(self) -> Operation:
        """查询主线模型的业务拓扑"""

    @property
    def get_proc_template(self) -> Operation:
        """获取进程模板"""

    @property
    def get_service_template(self) -> Operation:
        """获取服务模板"""

    @property
    def list_biz_hosts(self) -> Operation:
        """查询业务下的主机"""

    @property
    def list_biz_hosts_topo(self) -> Operation:
        """查询业务下的主机和拓扑信息"""

    @property
    def list_hosts_without_biz(self) -> Operation:
        """没有业务ID的主机查询"""

    @property
    def list_proc_template(self) -> Operation:
        """查询进程模板列表"""

    @property
    def list_process_detail_by_ids(self) -> Operation:
        """查询某业务下进程ID对应的进程详情"""

    @property
    def list_process_instance(self) -> Operation:
        """查询进程实例列表"""

    @property
    def list_resource_pool_hosts(self) -> Operation:
        """查询资源池中的主机"""

    @property
    def list_service_category(self) -> Operation:
        """查询服务分类列表"""

    @property
    def list_service_instance(self) -> Operation:
        """查询服务实例列表"""

    @property
    def list_service_instance_by_host(self) -> Operation:
        """通过主机查询关联的服务实例列表"""

    @property
    def list_service_instance_by_set_template(self) -> Operation:
        """通过集群模版查询关联的服务实例列表"""

    @property
    def list_service_instance_detail(self) -> Operation:
        """获取服务实例详细信息"""

    @property
    def list_service_template(self) -> Operation:
        """服务模板列表查询"""

    @property
    def list_set_template(self) -> Operation:
        """查询集群模板"""

    @property
    def list_set_template_related_service_template(self) -> Operation:
        """获取某集群模版下的服务模版列表"""

    @property
    def remove_label_from_service_instance(self) -> Operation:
        """从服务实例移除标签"""

    @property
    def resource_watch(self) -> Operation:
        """监听资源变化事件"""

    @property
    def search_biz_inst_topo(self) -> Operation:
        """查询业务实例拓扑"""

    @property
    def search_business(self) -> Operation:
        """查询业务"""

    @property
    def search_classifications(self) -> Operation:
        """查询模型分类"""

    @property
    def search_cloud_area(self) -> Operation:
        """查询云区域"""

    @property
    def search_custom_query(self) -> Operation:
        """查询自定义查询"""

    @property
    def search_dynamic_group(self) -> Operation:
        """搜索动态分组"""

    @property
    def search_host_lock(self) -> Operation:
        """查询主机锁"""

    @property
    def search_inst(self) -> Operation:
        """根据关联关系实例查询模型实例"""

    @property
    def search_inst_association_topo(self) -> Operation:
        """查询实例关联拓扑"""

    @property
    def search_inst_asst_object_inst_base_info(self) -> Operation:
        """查询实例关联模型实例基本信息"""

    @property
    def search_inst_by_object(self) -> Operation:
        """查询实例详情"""

    @property
    def search_instance_associations(self) -> Operation:
        """查询模型实例关系"""

    @property
    def search_module(self) -> Operation:
        """查询模块"""

    @property
    def search_object_attribute(self) -> Operation:
        """查询对象模型属性"""

    @property
    def search_object_instances(self) -> Operation:
        """查询模型实例"""

    @property
    def search_object_topo(self) -> Operation:
        """查询普通模型拓扑"""

    @property
    def search_objects(self) -> Operation:
        """查询模型"""

    @property
    def search_related_inst_asso(self) -> Operation:
        """查询某实例所有的关联关系（包含其作为关联关系原模型和关联关系目标模型的情况）"""

    @property
    def search_set(self) -> Operation:
        """查询集群"""

    @property
    def sync_set_template_to_set(self) -> Operation:
        """集群模板同步"""

    @property
    def transfer_host_module(self) -> Operation:
        """业务内主机转移模块"""

    @property
    def transfer_host_to_faultmodule(self) -> Operation:
        """上交主机到业务的故障机模块"""

    @property
    def transfer_host_to_idlemodule(self) -> Operation:
        """上交主机到业务的空闲机模块"""

    @property
    def transfer_host_to_recyclemodule(self) -> Operation:
        """上交主机到业务的待回收模块"""

    @property
    def transfer_host_to_resourcemodule(self) -> Operation:
        """上交主机至资源池"""

    @property
    def transfer_resourcehost_to_idlemodule(self) -> Operation:
        """资源池主机分配至业务的空闲机模块"""

    @property
    def transfer_sethost_to_idle_module(self) -> Operation:
        """清空业务下集群/模块中主机"""

    @property
    def update_biz_custom_field(self) -> Operation:
        """更新业务自定义模型属性"""

    @property
    def update_business(self) -> Operation:
        """修改业务"""

    @property
    def update_business_enable_status(self) -> Operation:
        """修改业务启用状态"""

    @property
    def update_classification(self) -> Operation:
        """更新模型分类"""

    @property
    def update_cloud_area(self) -> Operation:
        """更新云区域"""

    @property
    def update_custom_query(self) -> Operation:
        """更新自定义查询"""

    @property
    def update_dynamic_group(self) -> Operation:
        """更新动态分组"""

    @property
    def update_host(self) -> Operation:
        """更新主机属性"""

    @property
    def update_host_cloud_area_field(self) -> Operation:
        """更新主机的云区域字段"""

    @property
    def update_inst(self) -> Operation:
        """更新对象实例"""

    @property
    def update_module(self) -> Operation:
        """更新模块"""

    @property
    def update_object(self) -> Operation:
        """更新定义"""

    @property
    def update_object_attribute(self) -> Operation:
        """更新对象模型属性"""

    @property
    def update_object_topo_graphics(self) -> Operation:
        """更新拓扑图"""

    @property
    def update_proc_template(self) -> Operation:
        """更新进程模板"""

    @property
    def update_process_instance(self) -> Operation:
        """更新进程实例"""

    @property
    def update_service_category(self) -> Operation:
        """更新服务分类"""

    @property
    def update_service_template(self) -> Operation:
        """更新服务模板"""

    @property
    def update_set(self) -> Operation:
        """更新集群"""

    @property
    def update_set_template(self) -> Operation:
        """编辑集群模板"""


class CmsiGroup(OperationGroup):

    @property
    def get_msg_type(self) -> Operation:
        """查询消息发送类型"""

    @property
    def send_mail(self) -> Operation:
        """发送邮件"""

    @property
    def send_msg(self) -> Operation:
        """通用消息发送"""

    @property
    def send_sms(self) -> Operation:
        """发送短信"""

    @property
    def send_voice_msg(self) -> Operation:
        """公共语音通知"""

    @property
    def send_weixin(self) -> Operation:
        """发送微信消息"""


class GseGroup(OperationGroup):

    @property
    def get_agent_info(self) -> Operation:
        """Agent心跳信息查询"""

    @property
    def get_agent_status(self) -> Operation:
        """Agent在线状态查询"""


class ItsmGroup(OperationGroup):

    @property
    def callback_failed_ticket(self) -> Operation:
        """回调失败的单据"""

    @property
    def create_ticket(self) -> Operation:
        """创建单据"""

    @property
    def get_service_catalogs(self) -> Operation:
        """服务目录查询"""

    @property
    def get_service_detail(self) -> Operation:
        """服务详情查询"""

    @property
    def get_service_roles(self) -> Operation:
        """服务角色查询"""

    @property
    def get_services(self) -> Operation:
        """服务列表查询"""

    @property
    def get_ticket_info(self) -> Operation:
        """单据详情查询"""

    @property
    def get_ticket_logs(self) -> Operation:
        """单据日志查询"""

    @property
    def get_ticket_status(self) -> Operation:
        """单据状态查询"""

    @property
    def get_tickets(self) -> Operation:
        """获取单据列表"""

    @property
    def operate_node(self) -> Operation:
        """处理单据节点"""

    @property
    def operate_ticket(self) -> Operation:
        """处理单据"""

    @property
    def ticket_approval_result(self) -> Operation:
        """审批结果查询"""

    @property
    def token_verify(self) -> Operation:
        """token校验"""


class Jobv3Group(OperationGroup):

    @property
    def execute_job_plan(self) -> Operation:
        """执行作业执行方案"""

    @property
    def fast_execute_script(self) -> Operation:
        """快速执行脚本"""

    @property
    def fast_execute_sql(self) -> Operation:
        """快速执行SQL"""

    @property
    def fast_transfer_file(self) -> Operation:
        """快速分发文件"""

    @property
    def get_account_list(self) -> Operation:
        """查询业务下的执行账号"""

    @property
    def get_cron_detail(self) -> Operation:
        """查询定时作业详情"""

    @property
    def get_cron_list(self) -> Operation:
        """查询业务下定时作业信息"""

    @property
    def get_job_instance_global_var_value(self) -> Operation:
        """获取作业实例全局变量值"""

    @property
    def get_job_instance_ip_log(self) -> Operation:
        """根据作业实例ID查询作业执行日志"""

    @property
    def get_job_instance_list(self) -> Operation:
        """查询作业实例列表(执行历史)"""

    @property
    def get_job_instance_status(self) -> Operation:
        """根据作业实例 ID 查询作业执行状态"""

    @property
    def get_job_plan_detail(self) -> Operation:
        """查询执行方案详情"""

    @property
    def get_job_plan_list(self) -> Operation:
        """查询执行方案列表"""

    @property
    def get_job_template_list(self) -> Operation:
        """查询作业模版列表"""

    @property
    def get_public_script_list(self) -> Operation:
        """查询公共脚本列表"""

    @property
    def get_public_script_version_detail(self) -> Operation:
        """查询公共脚本详情"""

    @property
    def get_public_script_version_list(self) -> Operation:
        """查询公共脚本版本列表"""

    @property
    def get_script_list(self) -> Operation:
        """查询脚本列表"""

    @property
    def get_script_version_detail(self) -> Operation:
        """查询脚本详情"""

    @property
    def get_script_version_list(self) -> Operation:
        """查询脚本版本列表"""

    @property
    def operate_job_instance(self) -> Operation:
        """作业实例操作"""

    @property
    def operate_step_instance(self) -> Operation:
        """步骤实例操作"""

    @property
    def save_cron(self) -> Operation:
        """新建或保存定时作业"""

    @property
    def update_cron_status(self) -> Operation:
        """更新定时作业状态，如启动或暂停"""


class MonitorV3Group(OperationGroup):

    @property
    def add_shield(self) -> Operation:
        """新增告警屏蔽"""

    @property
    def batch_retry_config(self) -> Operation:
        """批量重试采集配置的失败实例"""

    @property
    def batch_retry_instance_step(self) -> Operation:
        """重试失败的节点步骤"""

    @property
    def collect_running_status(self) -> Operation:
        """获取采集配置主机的运行状态"""

    @property
    def create_custom_event_group(self) -> Operation:
        """创建自定义事件"""

    @property
    def create_custom_time_series(self) -> Operation:
        """创建自定义指标"""

    @property
    def custom_time_series(self) -> Operation:
        """自定义指标列表"""

    @property
    def custom_time_series_detail(self) -> Operation:
        """自定义指标详情"""

    @property
    def delete_alarm_strategy(self) -> Operation:
        """删除告警策略"""

    @property
    def delete_collect_config(self) -> Operation:
        """删除采集配置"""

    @property
    def delete_custom_event_group(self) -> Operation:
        """删除自定义事件"""

    @property
    def delete_custom_time_series(self) -> Operation:
        """删除自定义指标"""

    @property
    def delete_notice_group(self) -> Operation:
        """删除通知组"""

    @property
    def disable_shield(self) -> Operation:
        """解除告警屏蔽"""

    @property
    def edit_shield(self) -> Operation:
        """编辑告警屏蔽"""

    @property
    def export_uptime_check_task(self) -> Operation:
        """导出拨测任务配置"""

    @property
    def get_collect_config_list(self) -> Operation:
        """采集配置列表"""

    @property
    def get_collect_log_detail(self) -> Operation:
        """获取采集下发详细日志"""

    @property
    def get_collect_status(self) -> Operation:
        """查询采集配置节点状态"""

    @property
    def get_custom_event_group(self) -> Operation:
        """获取自定义事件详情"""

    @property
    def get_es_data(self) -> Operation:
        """获取监控链路时序数据"""

    @property
    def get_event_log(self) -> Operation:
        """查询事件流转记录"""

    @property
    def get_shield(self) -> Operation:
        """获取告警屏蔽"""

    @property
    def get_ts_data(self) -> Operation:
        """获取时序数据"""

    @property
    def get_uptime_check_node_list(self) -> Operation:
        """拨测节点列表"""

    @property
    def get_uptime_check_task_list(self) -> Operation:
        """拨测任务列表"""

    @property
    def import_uptime_check_node(self) -> Operation:
        """导入拨测节点配置"""

    @property
    def import_uptime_check_task(self) -> Operation:
        """导入拨测任务配置"""

    @property
    def list_shield(self) -> Operation:
        """获取告警屏蔽列表"""

    @property
    def metadata_create_cluster_info(self) -> Operation:
        """创建存储集群信息"""

    @property
    def metadata_create_data_id(self) -> Operation:
        """创建监控数据源"""

    @property
    def metadata_create_event_group(self) -> Operation:
        """创建事件分组"""

    @property
    def metadata_create_result_table(self) -> Operation:
        """创建监控结果表"""

    @property
    def metadata_create_result_table_metric_split(self) -> Operation:
        """创建结果表的维度拆分配置"""

    @property
    def metadata_create_time_series_group(self) -> Operation:
        """创建自定义时序分组"""

    @property
    def metadata_delete_event_group(self) -> Operation:
        """删除事件分组"""

    @property
    def metadata_delete_time_series_group(self) -> Operation:
        """删除自定义时序分组"""

    @property
    def metadata_get_cluster_info(self) -> Operation:
        """查询指定存储集群信息"""

    @property
    def metadata_get_data_id(self) -> Operation:
        """获取监控数据源具体信息"""

    @property
    def metadata_get_event_group(self) -> Operation:
        """查询事件分组具体内容"""

    @property
    def metadata_get_result_table(self) -> Operation:
        """获取监控结果表具体信息"""

    @property
    def metadata_get_result_table_storage(self) -> Operation:
        """查询指定结果表的指定存储信息"""

    @property
    def metadata_get_time_series_group(self) -> Operation:
        """获取自定义时序分组具体内容"""

    @property
    def metadata_get_time_series_metrics(self) -> Operation:
        """获取自定义时序结果表的metrics信息"""

    @property
    def metadata_list_label(self) -> Operation:
        """查询当前已有的标签信息"""

    @property
    def metadata_list_result_table(self) -> Operation:
        """查询监控结果表"""

    @property
    def metadata_list_transfer_cluster(self) -> Operation:
        """获取所有transfer集群信息"""

    @property
    def metadata_modify_cluster_info(self) -> Operation:
        """修改存储集群信息"""

    @property
    def metadata_modify_data_id(self) -> Operation:
        """修改指定数据源的配置信息"""

    @property
    def metadata_modify_event_group(self) -> Operation:
        """修改事件分组"""

    @property
    def metadata_modify_result_table(self) -> Operation:
        """修改监控结果表"""

    @property
    def metadata_modify_time_series_group(self) -> Operation:
        """修改自定义时序分组"""

    @property
    def metadata_query_event_group(self) -> Operation:
        """创建事件分组"""

    @property
    def metadata_query_tag_values(self) -> Operation:
        """获取自定义时序分组具体内容"""

    @property
    def metadata_query_time_series_group(self) -> Operation:
        """查询事件分组"""

    @property
    def metadata_upgrade_result_table(self) -> Operation:
        """将指定的监控单业务结果表升级为全业务结果表"""

    @property
    def modify_custom_event_group(self) -> Operation:
        """修改自定义事件"""

    @property
    def modify_custom_time_series(self) -> Operation:
        """修改自定义指标"""

    @property
    def proxy_host_info(self) -> Operation:
        """获取自定义上报的proxy主机信息"""

    @property
    def query_collect_config(self) -> Operation:
        """查询采集配置"""

    @property
    def query_custom_event_group(self) -> Operation:
        """获取业务下自定义事件列表"""

    @property
    def retry_target_nodes(self) -> Operation:
        """重试部分实例或主机"""

    @property
    def rollback_deployment_config(self) -> Operation:
        """采集配置回滚"""

    @property
    def save_alarm_strategy(self) -> Operation:
        """保存告警策略"""

    @property
    def save_collect_config(self) -> Operation:
        """创建/保存采集配置"""

    @property
    def save_notice_group(self) -> Operation:
        """保存通知组"""

    @property
    def search_alarm_strategy(self) -> Operation:
        """查询告警策略"""

    @property
    def search_event(self) -> Operation:
        """查询事件"""

    @property
    def search_notice_group(self) -> Operation:
        """查询通知组"""

    @property
    def switch_alarm_strategy(self) -> Operation:
        """启停告警策略"""

    @property
    def toggle_collect_config_status(self) -> Operation:
        """启停采集配置"""

    @property
    def upgrade_collect_plugin(self) -> Operation:
        """采集配置插件升级"""

    @property
    def validate_custom_event_group_name(self) -> Operation:
        """校验自定义事件名称是否合法"""

    @property
    def validate_custom_ts_group_name(self) -> Operation:
        """校验自定义指标名称是否合法"""


class SopsGroup(OperationGroup):

    @property
    def claim_functionalization_task(self) -> Operation:
        """认领职能化任务"""

    @property
    def create_periodic_task(self) -> Operation:
        """通过流程模板新建周期任务"""

    @property
    def create_task(self) -> Operation:
        """通过流程模板新建任务"""

    @property
    def fast_create_task(self) -> Operation:
        """快速新建一次性任务"""

    @property
    def get_common_template_info(self) -> Operation:
        """查询单个公共流程模板详情"""

    @property
    def get_common_template_list(self) -> Operation:
        """查询公共模板列表"""

    @property
    def get_periodic_task_info(self) -> Operation:
        """查询业务下的某个周期任务详情"""

    @property
    def get_periodic_task_list(self) -> Operation:
        """查询业务下的周期任务列表"""

    @property
    def get_plugin_list(self) -> Operation:
        """查询某个业务下的插件列表"""

    @property
    def get_task_detail(self) -> Operation:
        """查询任务执行详情"""

    @property
    def get_task_list(self) -> Operation:
        """获取业务下的任务列表"""

    @property
    def get_task_node_data(self) -> Operation:
        """获取节点执行数据"""

    @property
    def get_task_node_detail(self) -> Operation:
        """查询任务节点执行详情"""

    @property
    def get_task_status(self) -> Operation:
        """查询任务或任务节点执行状态"""

    @property
    def get_tasks_status(self) -> Operation:
        """批量查询任务状态"""

    @property
    def get_template_info(self) -> Operation:
        """查询单个模板详情"""

    @property
    def get_template_list(self) -> Operation:
        """查询模板列表"""

    @property
    def get_template_schemes(self) -> Operation:
        """获取模板执行方案列表"""

    @property
    def get_user_project_detail(self) -> Operation:
        """获取项目详情"""

    @property
    def get_user_project_list(self) -> Operation:
        """获取用户有权限的项目列表"""

    @property
    def import_common_template(self) -> Operation:
        """导入公共流程"""

    @property
    def import_project_template(self) -> Operation:
        """导入业务流程模板"""

    @property
    def modify_constants_for_periodic_task(self) -> Operation:
        """修改周期任务的全局参数"""

    @property
    def modify_constants_for_task(self) -> Operation:
        """修改任务的全局参数"""

    @property
    def modify_cron_for_periodic_task(self) -> Operation:
        """修改周期任务的调度策略"""

    @property
    def node_callback(self) -> Operation:
        """回调任务节点"""

    @property
    def operate_node(self) -> Operation:
        """操作任务中的节点"""

    @property
    def operate_task(self) -> Operation:
        """操作任务"""

    @property
    def preview_task_tree(self) -> Operation:
        """获取节点选择后新的任务树"""

    @property
    def query_task_count(self) -> Operation:
        """查询任务分类统计总数"""

    @property
    def set_periodic_task_enabled(self) -> Operation:
        """设置周期任务是否激活"""

    @property
    def start_task(self) -> Operation:
        """开始执行任务"""


class UsermanageGroup(OperationGroup):

    @property
    def list_department_profiles(self) -> Operation:
        """查询部门的用户信息 (v2)"""

    @property
    def list_departments(self) -> Operation:
        """查询部门 (v2)"""

    @property
    def list_profile_departments(self) -> Operation:
        """查询用户的部门信息 (v2)"""

    @property
    def list_users(self) -> Operation:
        """查询用户 (v2)"""

    @property
    def retrieve_department(self) -> Operation:
        """查询单个部门信息 (v2)"""

    @property
    def retrieve_user(self) -> Operation:
        """查询单个用户信息 (v2)"""


class Client(ESBClient):
    """ESB Components"""

    @property
    def bk_login(self) -> Group:
        """bk_login apis"""

    @property
    def cc(self) -> Group:
        """cc apis"""

    @property
    def cmsi(self) -> Group:
        """cmsi apis"""

    @property
    def gse(self) -> Group:
        """gse apis"""

    @property
    def itsm(self) -> Group:
        """itsm apis"""

    @property
    def jobv3(self) -> Group:
        """jobv3 apis"""

    @property
    def monitor_v3(self) -> Group:
        """monitor_v3 apis"""

    @property
    def sops(self) -> Group:
        """sops apis"""

    @property
    def usermanage(self) -> Group:
        """usermanage apis"""
