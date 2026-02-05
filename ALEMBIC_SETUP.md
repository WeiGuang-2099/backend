# Alembic 迁移系统设置完成

## ✅ 已完成的配置

本项目已成功配置 Alembic 数据库迁移系统。以下是所有已完成的工作：

### 1. 安装和配置
- ✅ 添加 `alembic==1.13.1` 到 `requirements.txt`
- ✅ 初始化 Alembic 配置目录和文件
- ✅ 配置 `alembic.ini` 
- ✅ 配置 `alembic/env.py` 以使用项目的数据库设置和模型

### 2. 初始迁移
- ✅ 创建初始迁移脚本：`eac8d99d29e5_create_users_table.py`
- ✅ 迁移包含完整的 users 表定义（包括所有字段、索引和约束）

### 3. 代码修改
- ✅ 从 `app/core/database.py` 移除手动创建表的 `init_db()` 函数
- ✅ 从 `app/main.py` 移除启动时调用 `init_db()` 的代码
- ✅ 添加说明注释，指引使用 Alembic 进行数据库管理

### 4. 文档
- ✅ 创建详细的迁移指南：`MIGRATIONS.md`
- ✅ 更新 `README.md` 添加 Alembic 使用说明

## 🚀 如何使用

### 首次部署（新环境）

```bash
# 1. 启动数据库
docker-compose up -d

# 2. 安装依赖（包括 Alembic）
pip install -r requirements.txt

# 3. 应用所有迁移（创建 users 表）
alembic upgrade head

# 4. 可选：初始化示例用户
python init_sample_users.py

# 5. 启动应用
uvicorn app.main:app --reload
```

### 日常开发流程

当你需要修改数据库结构时：

```bash
# 1. 修改模型文件（例如 app/models/user.py）
# 2. 生成迁移脚本
alembic revision --autogenerate -m "add phone field to users"

# 3. 检查生成的迁移脚本
# 4. 应用迁移
alembic upgrade head
```

## 📂 新增的文件

```
backend/
├── alembic/                                      # Alembic 配置目录
│   ├── versions/                                # 迁移脚本目录
│   │   └── eac8d99d29e5_create_users_table.py  # 初始迁移
│   ├── env.py                                   # 已配置：使用项目设置
│   ├── script.py.mako                           # 迁移脚本模板
│   └── README                                   # Alembic 说明
├── alembic.ini                                  # Alembic 配置文件
├── MIGRATIONS.md                                # 迁移详细指南（新增）
└── ALEMBIC_SETUP.md                             # 本文件（新增）
```

## 🔄 迁移内容

### 初始迁移：eac8d99d29e5_create_users_table.py

创建 `users` 表，包含：

**字段：**
- `id` (Integer, 主键) - 用户唯一标识ID
- `username` (String(50), 唯一, 非空) - 用户名
- `email` (String(100), 唯一, 非空) - 邮箱地址
- `password` (String(255), 非空) - 加密密码

**索引：**
- `ix_users_id` - id 字段索引
- `ix_users_username` - username 唯一索引
- `ix_users_email` - email 唯一索引

**约束：**
- PRIMARY KEY on `id`
- UNIQUE on `username`
- UNIQUE on `email`

## ⚠️ 重要提醒

### 从手动创建迁移到 Alembic

如果你的数据库中已经存在 `users` 表（通过之前的 `Base.metadata.create_all()` 创建）：

#### 选项 1：保留现有数据

```bash
# 1. 标记迁移为已应用（不实际执行）
alembic stamp head

# 这会在数据库中创建 alembic_version 表，
# 并标记当前迁移为已应用，而不会尝试重新创建表
```

#### 选项 2：重建数据库（测试环境）

```bash
# 1. 删除数据库和容器
docker-compose down -v

# 2. 重新启动
docker-compose up -d

# 3. 应用迁移
alembic upgrade head
```

### 多人协作注意事项

1. **拉取代码后**：检查是否有新的迁移脚本
   ```bash
   git pull
   alembic upgrade head
   ```

2. **提交代码前**：确保迁移脚本已测试
   ```bash
   alembic upgrade head    # 测试升级
   alembic downgrade -1    # 测试回滚
   alembic upgrade head    # 恢复
   ```

3. **避免冲突**：
   - 不要同时修改同一个表的结构
   - 发现迁移冲突时及时沟通解决

## 📚 更多信息

- 完整迁移指南：[MIGRATIONS.md](./MIGRATIONS.md)
- Alembic 官方文档：https://alembic.sqlalchemy.org/
- 项目 README：[README.md](./README.md)

## ✨ 优势

使用 Alembic 后，你将获得：

1. **版本控制**：所有数据库变更都有历史记录
2. **可回滚**：可以轻松回滚到之前的版本
3. **团队协作**：团队成员可以同步数据库结构
4. **自动化部署**：可以在 CI/CD 中自动应用迁移
5. **安全性**：避免手动 SQL 操作导致的错误

---

**配置完成时间**: 2026-01-30
**初始迁移版本**: eac8d99d29e5
