# 版本历史

## 2.0.4
- 新增幂等分配实例的接口：POST `services/<service_id>/instances/`，幂等键默认为 `engine_app_name`
和老分配接口 POST `services/<service_id>/instances/<instance_id>/` 不同：
    a. 一个幂等键（engine_app_name）只会分配一个增强服务实例，请求会尝试复用已分配的同幂等键下的实例
    b. 无需传递路径参数 `<instance_id>`, 调用方需使用响应中的实例 uuid

## 2.0.3
- service list 接口返回增加 `plan_schema` 字段，以指导服务方案配置 

## 2.0.2
- Support multi tenant 

## 2.0.1
- Support querying service instance with parameter to_be_deleted 

## 2.0.0
- 支持 Python 3.11，移除对 Python 3.6, 3.7 的支持

## 1.1.6
- Loosen the version restriction on sub-dep `pyjwt`

## 1.1.5
- 支持通过 name 查询 service instance

## 1.1.4
- 版权申明格式修改

## 1.1.3
- 升级 django3.2 并支持 i18n
