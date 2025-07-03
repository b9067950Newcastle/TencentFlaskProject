# 主机管理系统

## 数据库设计
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
- city_id：外键关联 tblCities.id

**关系**：
- 多对一关联 tblCities
- 一对多关联 tblHost (一个机房有多台主机)

**关键方法：**
- create()：创建新机房（验证城市存在）
- update_by_id()：更新机房名称/所属城市
- delete_by_id/delete_by_name()：删除机房

### tblHost 用于存放服务器信息
**字段：**
- id：主键 (自增整数)
- host_name：主机名 (非空)
- ip_address：IP地址 (唯一，非空)
- IDC_id：外键关联 tblIDC.id
- root_password：加密后的root密码 (bcrypt哈希)
- encryption_key：加密密钥 (Fernet生成)
- last_update_password：密码最后更新时间

**关系**
- 多对一关联 tblIDC

**关键方法**
- create()：创建主机（IP唯一性检查）
- update_by_id()：更新主机信息（含密码更新逻辑）
- get_by_ip()：通过IP查询主机

### tblHostState 用于存放每天主机统计信息
**字段：**
- id：主键
- date：统计日期
- city_id：外键关联 tblCities.id
- IDC_id：外键关联 tblIDC.id
- host_count：主机数量

## api接口

提供了一个api接口用来查询主机是否可ping

使用 ping?ip=0.0.0.0(或其它ip地址)来获取主机

## 定时任务
使用celery创建了两个定时任务，在flask应用与redis服务器均启动后，使用以下命令

celery -A run_celery.celery worker --loglevel=info

## 计时中间件
设计了一个中间件

临时启动celery
redis-server

后台自启动
brew services start redis  # 开机自启

手动启动
redis-server /usr/local/etc/redis.conf --daemonize yes

验证是否运行
redis-cli ping