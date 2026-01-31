# FastAPI Backend

基于 FastAPI + MySQL + JWT 的后端项目

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # 应用入口
│   ├── api/                 # API路由
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py      # 认证路由
│   │       ├── users.py     # 用户路由
│   │       └── items.py     # 物品路由
│   ├── core/                # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py        # 配置文件
│   │   ├── database.py      # 数据库连接
│   │   ├── security.py      # 密码加密
│   │   └── auth.py          # JWT认证
│   ├── crud/                # 数据库操作
│   │   ├── __init__.py
│   │   └── user.py          # 用户CRUD
│   ├── models/              # 数据库模型
│   │   ├── __init__.py
│   │   ├── user.py          # 用户模型
│   │   └── item.py          # 物品模型
│   └── schemas/             # Pydantic模型
│       ├── __init__.py
│       ├── user.py          # 用户schema
│       └── item.py          # 物品schema
├── init_sample_users.py     # 初始化示例用户
├── requirements.txt         # 依赖包
├── .env.example            # 环境变量示例
└── README.md               # 项目说明
```

## 快速开始

### 方式 1：一键启动（推荐）

```powershell
# Windows
.\start.ps1
```

```bash
# Linux/Mac
./start.sh  # 需要创建对应的脚本
```

这将自动完成：
- ✅ 启动 MySQL 容器
- ✅ 安装 Python 依赖
- ✅ 初始化示例用户
- ✅ 启动 FastAPI 服务

### 方式 2：手动启动

#### 1. 启动 MySQL
```bash
docker-compose up -d
```

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 配置环境变量
```bash
# 复制模板（如果还没有 .env 文件）
cp .env.example .env
```

#### 4. 初始化数据库（使用Alembic迁移）
```bash
# 应用数据库迁移
alembic upgrade head

# 可选：初始化示例用户数据
python init_sample_users.py
```

#### 5. 启动服务
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 访问服务
- 🌐 API: http://localhost:8000
- 📚 Swagger 文档: http://localhost:8000/docs
- 📖 ReDoc 文档: http://localhost:8000/redoc

### 停止服务
```powershell
# 停止 MySQL 容器
.\stop.ps1

# 或手动停止
docker-compose down
```

## API 接口

### 认证 API (`/api/v1/auth`)

- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/me` - 获取当前用户信息（需要认证）

### 用户 API (`/api/v1/users`)

- `GET /api/v1/users/` - 获取所有用户（需要认证）
- `GET /api/v1/users/{user_id}` - 获取指定用户（需要认证）

### Items API (`/api/v1/items`)

- `GET /api/v1/items/` - 获取所有items（需要认证）
- `GET /api/v1/items/{item_id}` - 获取指定item（需要认证）
- `POST /api/v1/items/` - 创建新item（需要认证）
- `PUT /api/v1/items/{item_id}` - 更新item（需要认证）
- `DELETE /api/v1/items/{item_id}` - 删除item（需要认证）

### 使用示例

**注册用户：**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"testuser","password":"password123"}'
```

**登录获取令牌：**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

**使用令牌访问受保护接口：**
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 技术栈

- **FastAPI**: 现代、快速的 Web 框架
- **SQLAlchemy**: ORM 数据库操作
- **Alembic**: 数据库迁移工具
- **MySQL**: 关系型数据库
- **PyMySQL**: MySQL 数据库驱动
- **JWT**: JSON Web Token 认证
- **Pydantic**: 数据验证
- **Bcrypt**: 密码加密

## 开发说明

- 所有需要认证的接口都需要在请求头中携带 `Authorization: Bearer <token>`
- JWT Token 默认有效期为 30 分钟（可在 `.env` 中配置）
- 数据库使用 MySQL 8.0
- 示例用户账号：`admin/admin123` 和 `user/user123`

## 数据库迁移

本项目使用 Alembic 管理数据库迁移。**所有数据库表结构的变更都必须通过迁移来完成。**

### 常用命令

```bash
# 应用所有迁移
alembic upgrade head

# 创建新迁移（自动检测模型变化）
alembic revision --autogenerate -m "描述你的变更"

# 回滚一个版本
alembic downgrade -1

# 查看当前版本
alembic current

# 查看迁移历史
alembic history
```

### 详细文档

完整的数据库迁移指南请参考：[MIGRATIONS.md](./MIGRATIONS.md)

