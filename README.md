# 主机管理系统

# 数据库设计
数据库存在一下四个表单： tblCities、tblIDC、tblHost、tblHostStat

### tblCities 用于存放城市城市信息

**字段：**
- id：主键 (自增整数)
- city_name：城市名称 (唯一，非空)

**关系：**
- 一对多关联 tblIDC 表 (一个城市有多个机房)

**关键方法：**
- create()：创建新城市（名称唯一性检查）
- delete_by_id/delete_by_name()：删除城市（需要改城市下没有机房）
- update()：更新城市名称（唯一性检查）
- get_by_id/get_by_name()：查询城市

### tblIDC 用于存储机房信息

**字段：**
- id：主键 (自增整数)
- IDC_name：机房名称 (唯一，非空)
- city_id：外键，关联 tblCities.id

**关系**：
- 多对一关联 tblCities
- 一对多关联 tblHost (一个机房有多台主机)

**关键方法：**
- create()：创建新机房（验证城市存在）
- update_by_id()：更新机房名称/所属城市
- delete_by_id/delete_by_name()：删除机房

### tbkHost 用于存放服务器信息
**字段：**
- id：主键 (自增整数)
- host_name：主机名 (非空)
- ip_address：IP地址 (唯一，非空)
- IDC_id：外键，关联 tblIDC.id
- root_password：加密后的root密码 (bcrypt哈希)
- encryption_key：加密密钥 (Fernet生成)
- last_update_password：密码最后更新时间

**关系**
- 多对一关联 tblIDC

**关键方法**
- create()：创建主机（IP唯一性检查）
- update_by_id()：更新主机信息（含密码更新逻辑）
- get_by_ip()：通过IP查询主机

