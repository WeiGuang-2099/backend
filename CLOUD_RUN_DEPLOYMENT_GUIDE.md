# Cloud Run + Cloud SQL 部署完整指南

本文档记录了将 FastAPI 后端部署到 Google Cloud Run 并连接 Cloud SQL MySQL 的完整流程、遇到的问题及解决方案。

---

## 目录

1. [前置准备](#前置准备)
2. [部署步骤](#部署步骤)
3. [遇到的问题与解决方案](#遇到的问题与解决方案)
4. [关键配置说明](#关键配置说明)
5. [未来部署注意事项](#未来部署注意事项)

---

## 前置准备

### 1. GCP 项目设置

```bash
# 初始化 gcloud
gcloud init

# 设置项目
gcloud config set project my-first-backend2099
```

### 2. 启用必要 API

```bash
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    sqladmin.googleapis.com \
    artifactregistry.googleapis.com
```

### 3. 创建 Cloud SQL MySQL 实例

```bash
# 创建实例 (db-f1-micro 是最便宜的配置)
gcloud sql instances create fastapi-mysql \
    --database-version=MYSQL_8_0 \
    --tier=db-f1-micro \
    --region=asia-east1 \
    --storage-auto-increase \
    --storage-size=10GB \
    --availability-type=zonal

# 创建数据库
gcloud sql databases create jwt_auth_db --instance=fastapi-mysql

# 创建用户
gcloud sql users create jwt_user --instance=fastapi-mysql --password=YOUR_PASSWORD
```

### 4. 创建 Artifact Registry 仓库

```bash
gcloud artifacts repositories create fastapi-repo \
    --repository-format=docker \
    --location=asia-east1

# 配置 Docker 认证
gcloud auth configure-docker asia-east1-docker.pkg.dev
```

---

## 部署步骤

### 步骤 1: 准备 Dockerfile

```dockerfile
# FastAPI Backend Dockerfile for Cloud Run

# Stage 1: Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libmariadb3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:approot
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/ || exit 1

# Run the application
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

**关键点**：
- 使用多阶段构建减小镜像大小
- 系统级安装 Python 包（避免用户权限问题）
- 非 root 用户运行（安全最佳实践）
- 支持动态 PORT（Cloud Run 要求）

### 步骤 2: 准备 .dockerignore

```
# Git
.git
.gitignore

# Python
__pycache__
*.py[cod]
*.so
.pytest_cache

# Virtual Environment
venv
env

# Environment files (重要!)
.env
.env.*

# Database files
*.db
*.sqlite

# Documentation
README.md
docs

# Scripts
deploy.sh
```

### 步骤 3: 配置环境变量

**关键配置 - DATABASE_URL 格式**：

```bash
# 错误格式 (会连接到 localhost)
DATABASE_URL=mysql+pymysql://user:pass@/cloudsql/project:region:instance/database

# 正确格式 (Cloud SQL Unix socket)
DATABASE_URL=mysql+pymysql://user:pass@/database?unix_socket=/cloudsql/project:region:instance
```

### 步骤 4: 构建并部署

```bash
# 构建镜像
docker build -t asia-east1-docker.pkg.dev/$PROJECT_ID/fastapi-repo/fastapi-backend:v1 .

# 推送镜像
docker push asia-east1-docker.pkg.dev/$PROJECT_ID/fastapi-repo/fastapi-backend:v1

# 部署到 Cloud Run
gcloud run deploy fastapi-backend \
    --image=asia-east1-docker.pkg.dev/$PROJECT_ID/fastapi-repo/fastapi-backend:v1 \
    --platform=managed \
    --region=asia-east1 \
    --allow-unauthenticated \
    --add-cloudsql-instances=$PROJECT_ID:asia-east1:fastapi-mysql \
    --set-env-vars="DATABASE_URL=mysql+pymysql://jwt_user:PASSWORD@/jwt_auth_db?unix_socket=/cloudsql/$PROJECT_ID:asia-east1:fastapi-mysql" \
    --set-env-vars="SECRET_KEY=$(openssl rand -base64 32)" \
    --set-env-vars="ALLOWED_ORIGINS=*"
```

### 步骤 5: 运行数据库迁移

由于 Cloud SQL Unix socket 连接限制，推荐在 Cloud Run 容器内运行迁移：

1. 创建临时迁移端点：
```python
@app.post("/migrate")
async def run_migrations():
    from alembic.config import Config
    from alembic import command
    import os
    import sys
    from pathlib import Path

    backend_dir = str(Path(__file__).resolve().parent.parent)
    sys.path.insert(0, backend_dir)

    alembic_cfg = Config()
    alembic_cfg.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))
    alembic_cfg.set_main_option("script_location", os.path.join(backend_dir, "alembic"))

    command.upgrade(alembic_cfg, "head")
    return {"status": "success"}
```

2. 调用端点执行迁移：
```bash
curl -X POST https://your-service/run.app/migrate
```

3. **重要**：迁移完成后删除此端点！

---

## 遇到的问题与解决方案

### 问题 1: 容器启动失败 - uvicorn: Permission denied

**原因**：Docker 多阶段构建中，Python 包安装在 `/root/.local`，但切换到非 root 用户后无法访问。

**解决方案**：将包安装到系统位置
```dockerfile
# 错误方式
RUN pip install --user -r requirements.txt

# 正确方式
RUN pip install -r requirements.txt
```

### 问题 2: 数据库连接失败 - Can't connect to MySQL server on 'localhost'

**错误日志**：
```
sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (2003,
    "Can't connect to MySQL server on 'localhost' ([Errno 111] Connection refused)")
```

**问题排查过程**：

1. 添加调试端点验证环境变量：
```python
@app.get("/debug")
async def debug():
    return {
        "DATABASE_URL_from_settings": settings.DATABASE_URL[:50] + "...",
        "DATABASE_URL_from_env": os.getenv("DATABASE_URL", "NOT_SET")[:50] + "...",
        "K_SERVICE": os.getenv("K_SERVICE", "NOT_SET"),
    }
```

2. 发现：环境变量正确，但连接仍失败
3. 进一步调试：添加 `_init_db()` 日志
4. 结论：模块加载时 `settings` 被初始化，使用了默认的 localhost 值

**根本原因分析**：

```
时间线分析：
┌─────────────────────────────────────────────────────────────┐
│ 应用启动流程                                                  │
├─────────────────────────────────────────────────────────────┤
│ 1. Python 导入 config.py                                   │
│    └─> settings = Settings() 被执行                        │
│    └─> 此时环境变量可能未就绪，使用默认值 localhost:3306  │
│                                                              │
│ 2. Python 导入 database.py                                 │
│    └─> 如果模块级有 engine = create_engine(...)              │
│        └─> 使用了步骤1中的默认配置创建引擎               │
│                                                              │
│ 3. FastAPI 启动，环境变量已就绪                             │
│    └─> 但 engine 已被创建，无法更新！                      │
└─────────────────────────────────────────────────────────────┘
```

**解决方案演进**：

尝试 1: 使用延迟导入 - ❌ 失败
```python
# 不在模块级导入
def get_engine():
    from app.core.config import settings  # 延迟导入
    return create_engine(settings.DATABASE_URL)
```

尝试 2: 使用 `__getattr__` - ❌ 部分失败
```python
_settings_instance = None
def __getattr__(name):
    if name == 'settings':
        return get_settings()
```
问题：仍然在首次访问时缓存了旧值

尝试 3: 完全重写 - ✅ 成功
```python
# config.py - 纯 Python 实现
def get_env(key: str):
    return os.getenv(key, default)

class Settings:
    def __init__(self):
        # 每次创建实例时都从环境变量读取
        self.DATABASE_URL = get_env('DATABASE_URL')

# database.py - 动态 URL 检测
def _init_db():
    global _last_database_url
    current_url = _get_database_url()
    if current_url != _last_database_url:
        # URL 变化时重新创建引擎
        _engine = create_engine(current_url)
```

### 问题 3: Cloud SQL Unix socket URL 格式错误

**错误格式**：
```
mysql+pymysql://user:pass@/cloudsql/project:region:instance/database
```

**正确格式**：
```
mysql+pymysql://user:pass@/database?unix_socket=/cloudsql/project:region:instance
```

### 问题 4: .env 文件被复制到容器覆盖环境变量

**解决方案**：确保 `.dockerignore` 正确排除 `.env` 文件，且在 `config.py` 中禁用 `.env` 文件读取：
```python
model_config = SettingsConfigDict(
    env_file=None,  # 完全禁用 .env 文件
    case_sensitive=True
)
```

### 问题 5: 数据库表不存在

**原因**：部署后未运行 Alembic 迁移

**解决方案**：创建临时迁移端点（见步骤 5），迁移完成后删除。

---

## 深度问题分析：Python 模块加载顺序问题

### 问题描述的复杂性

这个问题是最棘手的，因为它涉及多个层面：

1. **Python 模块导入机制**
   - 模块首次导入时，所有顶层代码都会被执行
   - 模块对象会被缓存，后续导入不会重新执行

2. **Pydantic Settings 行为**
   - pydantic-settings 在类定义时可能尝试读取环境变量
   - 如果环境变量未就绪，会使用默认值

3. **Cloud Run 容器启动**
   - 环境变量通过特定机制注入
   - 可能与代码导入时序不同步

### 完整解决方案对比

#### ❌ 错误的做法
```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "mysql://localhost:3306/db"  # 默认值

settings = Settings()  # ← 问题：模块导入时执行
```

#### ✅ 正确的做法
```python
# app/core/config.py
import os

def get_env(key: str, default=None):
    """直接读取环境变量"""
    return os.getenv(key, default)

class Settings:
    def __init__(self):
        # 每次实例化时读取
        self.DATABASE_URL = get_env('DATABASE_URL')

def __getattr__(name: str):
    if name == 'settings':
        return Settings()  # 延迟创建实例
```

### 代码级别详解

#### database.py 的 URL 变化检测

```python
# 全局变量
_engine = None
_last_database_url = None

def _init_db():
    global _engine, _last_database_url

    current_url = _get_database_url()

    # 关键：每次调用时检查 URL 是否变化
    if _engine is None or current_url != _last_database_url:
        _engine = create_engine(current_url)
        _SessionLocal = sessionmaker(bind=_engine)
        _last_database_url = current_url
```

**为什么需要检测 URL 变化？**

1. 首次请求可能使用旧 URL 创建引擎
2. 后续请求需要确保使用正确的 URL
3. Cloud Run 可能重新调度容器，环境变量可能更新

---

## 关键配置说明

### 1. DATABASE_URL 格式对比

| 连接方式 | 格式 |
|---------|------|
| TCP (本地开发) | `mysql+pymysql://user:pass@localhost:3306/db` |
| Unix Socket (Cloud Run) | `mysql+pymysql://user:pass@/db?unix_socket=/cloudsql/project:region:instance` |

### 2. Cloud Run 环境变量设置

```bash
# 通过 gcloud 命令设置
gcloud run services update fastapi-backend \
    --update-env-vars="DATABASE_URL=... ALLOWED_ORIGINS=https://myapp.com"

# 或在部署时设置
gcloud run deploy ... \
    --set-env-vars="KEY=VALUE"
```

### 3. .dockerignore 关键配置

必须排除 `.env` 文件，避免容器内本地配置覆盖环境变量：
```
.env
.env.*
```

---

## 未来部署注意事项

### 1. 配置管理

#### ✅ 推荐做法
```bash
# 使用 gcloud secret manager
echo "DATABASE_URL=..." | gcloud secrets create DATABASE_URL --data-file=-

# 部署时引用 secret
gcloud run deploy ... \
    --set-secrets="DATABASE_URL=DATABASE_URL:latest"
```

#### ❌ 避免
- 不要将 `.env` 文件提交到代码仓库
- 不要在代码中硬编码敏感信息

### 2. 数据库迁移

#### 方式 A：在 Cloud Run 中运行（推荐）
```bash
# 创建迁移任务
gcloud run jobs create migrate --image=$IMAGE \
    --set-env-vars="DATABASE_URL=..."

# 执行迁移
gcloud run jobs execute migrate
```

#### 方式 B：临时 API 端点（开发环境）
```python
# 仅用于开发环境，生产环境务必删除
if os.getenv("ENVIRONMENT") == "development":
    @app.post("/migrate")
    async def run_migrations():
        ...
```

### 3. 环境变量管理

创建 `.env.cloudrun` 作为模板：
```bash
# Cloud Run 环境变量模板
DATABASE_URL=mysql+pymysql://user:pass@/db?unix_socket=/cloudsql/PROJECT:REGION:INSTANCE
SECRET_KEY=CHANGE_THIS_IN_PRODUCTION
ALLOWED_ORIGINS=https://your-frontend-domain.com
```

### 4. 部署脚本

使用 [`deploy.sh`](deploy.sh) 简化部署流程：
```bash
chmod +x deploy.sh
./deploy.sh PROJECT_ID REGION SERVICE_NAME
```

### 5. 调试技巧

#### 查看实时日志
```bash
gcloud run logs tails fastapi-backend --region=asia-east1
```

#### 查看特定错误
```bash
gcloud logging read "resource.type=cloud_run_revision" \
    --filter="resource.labels.service_name=fastapi-backend" \
    --limit=50
```

#### 进入容器调试
```bash
gcloud run deploy fastapi-backend \
    --image=$IMAGE \
    --command="/bin/sleep 3600"  # 保持容器运行

# 获取容器名称并连接
gcloud container exec --container CONTAINER_NAME \
    --interactive --tty -- /bin/bash
```

### 6. 成本优化

| 配置选项 | 成本影响 |
|---------|---------|
| **最小实例数** | 设置为 0（按需启动）|
| **最大实例数** | 根据实际流量设置 |
| **内存** | 512MB 通常足够 |
| **CPU** | 1 核通常足够 |
| **Cloud SQL tier** | db-f1-micro（最便宜）|
| **区域** | 选择离用户近的区域 |

---

## 快速参考

### 常用命令

```bash
# 构建并部署（一键）
docker build -t $IMAGE . && docker push $IMAGE && gcloud run deploy $SERVICE --image=$IMAGE

# 查看服务状态
gcloud run services describe $SERVICE --region=$REGION

# 查看服务 URL
gcloud run services describe $SERVICE --region=$REGION --format="value(status.url)"

# 查看日志
gcloud run logs tails $SERVICE --region=$REGION

# 更新环境变量
gcloud run services update $SERVICE --region=$REGION --update-env-vars="KEY=VALUE"

# 删除服务
gcloud run services delete $SERVICE --region=$REGION
```

### 服务 URL

- **服务**: https://fastapi-backend-960418016080.asia-east1.run.app
- **API 文档**: https://fastapi-backend-960418016080.asia-east1.run.app/docs

### 成本估算

| 服务 | 月费用 |
|------|--------|
| Cloud SQL db-f1-micro | ~$8-10 |
| Cloud Run (100k 请求/月) | ~$5-10 |
| **总计** | ~$15-20/月 |

---

## 附录：完整文件列表

### 已创建的部署文件

| 文件 | 用途 |
|------|------|
| [Dockerfile](Dockerfile) | Cloud Run 容器配置 |
| [.dockerignore](.dockerignore) | Docker 构建排除 |
| [deploy.sh](deploy.sh) | 自动部署脚本 |
| [.env.cloudrun](.env.cloudrun) | 环境变量模板 |
| [CLOUD_RUN_DEPLOYMENT.md](CLOUD_RUN_DEPLOYMENT.md) | 原始部署文档 |
| [CLOUD_RUN_DEPLOYMENT_GUIDE.md](CLOUD_RUN_DEPLOYMENT_GUIDE.md) | 本文档 |

### 核心代码修改

| 文件 | 修改内容 |
|------|----------|
| [app/core/config.py](app/core/config.py) | 重写为纯 Python 环境变量读取 |
| [app/core/database.py](app/core/database.py) | 动态读取 DATABASE_URL，检测变化 |
| [alembic/env.py](alembic/env.py) | 优先从环境变量读取 |
| [app/main.py](app/main.py) | 添加迁移端点（调试用） |

---

**文档版本**: 1.1
**最后更新**: 2025-01-XX
**维护者**: Deployment Team

---

## 实战经验总结

### 从本次部署中学到的经验

#### 1. 环境变量 > 配置文件

**教训**：在云环境中，永远不要依赖配置文件

```python
# ❌ 错误：使用 .env 文件
from dotenv import load_dotenv
load_dotenv()  # 在生产环境中可能不可靠

# ✅ 正确：直接读取环境变量
import os
database_url = os.getenv("DATABASE_URL")
```

#### 2. 延迟初始化的重要性

**教训**：任何可能依赖环境变量的组件都应该延迟初始化

```python
# ❌ 错误：模块级初始化
engine = create_engine(settings.DATABASE_URL)  # 模块导入时执行

# ✅ 正确：函数级初始化
def get_engine():
    return create_engine(os.getenv("DATABASE_URL"))
```

#### 3. Cloud SQL 连接格式的陷阱

**教训**：不同的连接方式需要完全不同的 URL 格式

```python
# TCP 连接（本地开发）
mysql+pymysql://user:pass@localhost:3306/db

# Unix Socket（Cloud Run）- 注意路径在 host 部分
mysql+pymysql://user:pass@/db?unix_socket=/cloudsql/project:region:instance

# 错误的 Unix Socket 格式（会连接失败）
mysql+pymysql://user:pass@/cloudsql/project:region:instance/db
```

#### 4. 调试技巧：分阶段验证

**教训**：不要等到最后才测试，每一步都要验证

```
部署测试检查清单：
□ 环境变量是否正确设置？（/debug 端点）
□ 容器是否能启动？（查看日志）
□ 是否能访问数据库？（迁移测试）
□ API 端点是否正常？（功能测试）
```

### 常见错误模式

#### 模式 1：忘记 .dockerignore 排除 .env

```
症状：环境变量设置正确，但应用仍使用旧配置
原因：.env 文件被复制到镜像中
解决：确保 .dockerignore 包含 .env
```

#### 模式 2：Docker 多阶段构建权限问题

```
症状：Permission denied when running uvicorn
原因：pip install --user 安装到 /root/.local
解决：安装到系统位置 /usr/local
```

#### 模式 3：Cloud SQL 连接字符串格式错误

```
症状：Can't connect to MySQL server on 'localhost'
原因：使用了错误的 Unix socket 格式
解决：使用 ?unix_socket= 格式
```

### 性能优化建议

#### 1. 减少容器冷启动时间

```dockerfile
# 使用 .dockerignore 排除不必要的文件
# 减少镜像大小
# 使用缓存优化 Docker 构建
```

#### 2. 合理设置 Cloud Run 参数

```bash
# 最小实例数为 0（完全按需）
--min-instances=0

# 设置合理的并发
--concurrency=80

# 设置超时时间
--timeout=300
```

#### 3. 数据库连接池配置

```python
engine = create_engine(
    database_url,
    pool_pre_ping=True,    # 连接前验证
    pool_recycle=3600,    # 1小时回收连接
    pool_size=5,           # 连接池大小
    max_overflow=10        # 最大溢出
)
```

### 安全最佳实践

#### 1. 敏感信息管理

```bash
# ❌ 不要
--set-env-vars="DATABASE_PASSWORD=secret123"

# ✅ 推荐
echo "secret123" | gcloud secrets create DB_PASSWORD --data-file=-
gcloud run deploy ... --set-secrets="DB_PASSWORD=DB_PASSWORD:latest"
```

#### 2. 最小权限原则

```bash
# 只授予必要的 IAM 权限
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:..." \
    --role="roles/cloudsql.client"
```

#### 3. 网络隔离

```bash
# 使用 VPC 服务隔离
# 配置 Serverless VPC Access
# 限制 Cloud SQL 只允许 Cloud Run 访问
```

---

## 故障排查流程图

```
开始
  │
  ├─→ API 返回错误？
  │   ├─ Yes → 查看日志: gcloud run logs tails $SERVICE
  │   │        └→ 检查错误类型
  │   │
  │   └─ No → 检查网络连接: curl $SERVICE_URL/
  │
  ├─→ 数据库连接错误？
  │   ├─ Yes → 验证 DATABASE_URL 格式
  │   │        检查 --add-cloudsql-instances
  │   │        验证 Cloud SQL 实例状态
  │   │
  │   └─ No → 检查数据库表是否存在
  │
  ├─→ 环境变量问题？
  │   ├─ Yes → 使用 /debug 端点验证
  │   │        检查部署命令中的 --set-env-vars
  │   │
  │   └─ No → 检查应用代码逻辑
  │
  └─→ 容器启动问题？
      ├─ Yes → 检查 Dockerfile 权限
      │        检查 CMD 命令格式
      │        查看启动日志
      │
      └─ No → 检查资源配额
               检查 IAM 权限
```

---

## 参考资源

### 官方文档
- [Cloud Run 文档](https://cloud.google.com/run/docs)
- [Cloud SQL 文档](https://cloud.google.com/sql/docs)
- [Artifact Registry 文档](https://cloud.google.com/artifact-registry/docs)

### 社区资源
- [PyMySQL 文档](https://pymysql.readthedocs.io/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)

### 工具下载
- [gcloud CLI](https://cloud.google.com/sdk/docs/install)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

---

**文档版本**: 1.1
**最后更新**: 2025-01-XX
**维护者**: Deployment Team
