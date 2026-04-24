# 版本历史

## 2.0.4
- 新增幂等分配实例接口 `POST services/<service_id>/instances/idem_prov/`，默认以 `engine_app_name` 作为幂等键，适用于分配耗时较长、可能超过五分钟的增强服务：
    a. 同一幂等键仅对应一个增强服务实例，重复请求会复用已分配的实例
    b. 无需传递路径参数 `<instance_id>`，调用方应使用响应中的实例 UUID

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
