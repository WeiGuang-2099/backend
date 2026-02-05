# 数据库迁移指南

本项目使用 [Alembic](https://alembic.sqlalchemy.org/) 进行数据库迁移管理。所有数据库表结构的变更都应该通过 Alembic 迁移来完成，而不是手动创建或修改表。

## 目录结构

```
backend/
├── alembic/                    # Alembic配置目录
│   ├── versions/               # 迁移脚本目录
│   │   └── eac8d99d29e5_create_users_table.py  # 初始迁移
│   ├── env.py                  # Alembic环境配置
│   ├── script.py.mako          # 迁移脚本模板
│   └── README                  # Alembic说明
├── alembic.ini                 # Alembic配置文件
└── app/
    ├── models/                 # SQLAlchemy模型定义
    │   └── user.py             # User模型
    └── core/
        └── database.py         # 数据库连接配置
```

## 快速开始

### 1. 初始化数据库（首次使用）

当你第一次部署项目或需要重建数据库时：

```bash
# 1. 启动MySQL数据库
docker-compose up -d

# 2. 应用所有迁移
alembic upgrade head
```

### 2. 创建新的迁移

当你修改了模型（添加/删除字段、表等）后，需要创建新的迁移：

#### 方法一：自动生成迁移（推荐）

```bash
# Alembic会自动检测模型变化并生成迁移脚本
alembic revision --autogenerate -m "描述你的变更"

# 例如：
alembic revision --autogenerate -m "add phone field to users"
alembic revision --autogenerate -m "create posts table"
```

#### 方法二：手动创建迁移

```bash
# 创建一个空的迁移脚本，手动编写升级/降级逻辑
alembic revision -m "描述你的变更"
```

### 3. 应用迁移

```bash
# 应用所有未应用的迁移
alembic upgrade head

# 应用到特定版本
alembic upgrade <revision_id>

# 应用下一个迁移
alembic upgrade +1
```

### 4. 回滚迁移

```bash
# 回滚一个版本
alembic downgrade -1

# 回滚到特定版本
alembic downgrade <revision_id>

# 回滚所有迁移（清空数据库）
alembic downgrade base
```

### 5. 查看迁移状态

```bash
# 查看当前数据库版本
alembic current

# 查看迁移历史
alembic history

# 查看详细历史（包括完整的修订ID）
alembic history --verbose
```

## 常见场景

### 场景1: 添加新字段到现有表

1. 修改模型文件（例如 `app/models/user.py`）：
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)  # 新增字段
```

2. 生成迁移脚本：
```bash
alembic revision --autogenerate -m "add phone field to users"
```

3. 检查生成的迁移脚本（位于 `alembic/versions/`），确认无误后应用：
```bash
alembic upgrade head
```

### 场景2: 创建新表

1. 创建新模型文件（例如 `app/models/post.py`）：
```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(String(1000), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
```

2. 在 `alembic/env.py` 中导入新模型（如果需要自动检测）：
```python
# 导入所有模型
from app.models.user import Base
from app.models.post import Post  # 添加新模型
```

3. 生成迁移脚本：
```bash
alembic revision --autogenerate -m "create posts table"
```

4. 应用迁移：
```bash
alembic upgrade head
```

### 场景3: 删除字段

1. 从模型中删除字段

2. 生成迁移脚本：
```bash
alembic revision --autogenerate -m "remove phone field from users"
```

3. **重要**：检查生成的迁移脚本，确认不会误删重要数据

4. 应用迁移：
```bash
alembic upgrade head
```

### 场景4: 重命名字段

**注意**：Alembic 无法自动检测重命名，会将其识别为"删除旧字段+添加新字段"，这会导致数据丢失！

正确做法是手动创建迁移：

```bash
alembic revision -m "rename username to user_name"
```

然后在生成的脚本中使用 `op.alter_column()`：

```python
def upgrade():
    op.alter_column('users', 'username', new_column_name='user_name')

def downgrade():
    op.alter_column('users', 'user_name', new_column_name='username')
```

## 最佳实践

### 1. 开发流程

```
修改模型 → 生成迁移 → 检查迁移脚本 → 应用迁移 → 测试 → 提交代码
```

### 2. 代码审查

- ✅ **始终检查自动生成的迁移脚本**，确保变更符合预期
- ✅ **为每个迁移添加清晰的描述信息**
- ✅ **测试 upgrade 和 downgrade** 功能
- ✅ **提交迁移脚本到版本控制**

### 3. 生产环境部署

```bash
# 1. 备份数据库
mysqldump -u root -p jwt_auth_db > backup.sql

# 2. 查看将要应用的迁移
alembic history

# 3. 应用迁移
alembic upgrade head

# 4. 验证迁移结果
alembic current
```

### 4. 多人协作

- 在 git pull 后，检查是否有新的迁移脚本
- 如果有，先应用迁移再运行应用
- 避免多人同时修改同一个表的结构

### 5. 迁移冲突处理

如果出现多个分支都创建了迁移，导致迁移历史冲突：

```bash
# 1. 查看当前迁移状态
alembic current
alembic history

# 2. 手动合并迁移
# 编辑迁移文件的 down_revision 字段，建立正确的依赖关系
```

## 注意事项

### ⚠️ 重要警告

1. **不要手动修改数据库结构**
   - 所有表结构变更必须通过 Alembic 迁移
   - 手动修改会导致迁移历史不一致

2. **不要删除已应用的迁移脚本**
   - 已经应用到生产环境的迁移脚本不能删除
   - 如果需要撤销，使用 `alembic downgrade`

3. **不要修改已应用的迁移脚本**
   - 如果迁移已经被其他人应用，不要修改
   - 创建新的迁移来修正错误

4. **数据迁移需要特别小心**
   - 涉及数据转换的迁移需要仔细测试
   - 考虑大数据量的性能影响
   - 提供回滚方案

### 🔍 常见问题

**Q: 自动生成的迁移为空？**

A: 可能原因：
- 模型没有被正确导入到 `alembic/env.py`
- 模型定义的 Base 与配置的不一致
- 数据库已经包含这些更改

**Q: 迁移失败怎么办？**

A: 
```bash
# 1. 查看错误信息
alembic upgrade head

# 2. 如果是部分应用，回滚到之前的版本
alembic downgrade -1

# 3. 修复迁移脚本后重新应用
alembic upgrade head
```

**Q: 如何重置整个数据库？**

A:
```bash
# 方法1: 通过Alembic回滚
alembic downgrade base
alembic upgrade head

# 方法2: 删除数据库并重建
docker-compose down -v
docker-compose up -d
alembic upgrade head
```

## 配置说明

### alembic.ini

主配置文件，包含：
- 脚本位置配置
- 日志配置
- 输出编码设置

**注意**：数据库URL不在此文件配置，而是在 `alembic/env.py` 中从项目配置读取。

### alembic/env.py

环境配置文件，负责：
- 导入项目配置和模型
- 设置数据库连接
- 配置 target_metadata（用于自动检测）

当前配置会自动从 `app.core.config.settings` 读取数据库 URL。

## 迁移脚本结构

每个迁移脚本包含两个主要函数：

```python
def upgrade() -> None:
    """应用迁移（升级）"""
    # 在这里定义向前迁移的操作
    pass

def downgrade() -> None:
    """回滚迁移（降级）"""
    # 在这里定义回滚操作
    pass
```

### 常用操作示例

```python
# 创建表
op.create_table(
    'users',
    sa.Column('id', sa.Integer(), primary_key=True),
    sa.Column('name', sa.String(50), nullable=False)
)

# 删除表
op.drop_table('users')

# 添加列
op.add_column('users', sa.Column('age', sa.Integer()))

# 删除列
op.drop_column('users', 'age')

# 创建索引
op.create_index('ix_users_name', 'users', ['name'])

# 删除索引
op.drop_index('ix_users_name', table_name='users')

# 修改列
op.alter_column('users', 'name', new_column_name='username')
```

## 相关资源

- [Alembic 官方文档](https://alembic.sqlalchemy.org/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [FastAPI 数据库教程](https://fastapi.tiangolo.com/tutorial/sql-databases/)

## 技术支持

如有问题，请查阅：
1. Alembic 官方文档
2. 项目 Issue 跟踪
3. 团队技术文档
