# Cosmray Backend

基于 FastAPI + MySQL + Neo4j 的 AI 数字人平台后端，采用三层架构设计，支持数字人管理、实时流式对话和知识图谱。

## 快速开始

### 一键启动 (推荐)

```powershell
# Windows
.\start.ps1
```

自动完成：启动 MySQL 容器、安装依赖、运行数据库迁移、初始化示例用户、启动服务。

### 手动启动

```bash
# 1. 启动 MySQL
docker-compose up -d

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env

# 4. 数据库迁移
alembic upgrade head

# 5. (可选) 初始化示例用户
python init_sample_users.py

# 6. 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 访问服务

| 地址 | 说明 |
|------|------|
| http://localhost:8000 | API 根路径 |
| http://localhost:8000/docs | Swagger 文档 |
| http://localhost:8000/redoc | ReDoc 文档 |

### 停止服务

```powershell
docker-compose down
```

## 项目结构

```
backend/
├── app/
│   ├── main.py                    # 应用入口
│   ├── api/routes/                # API 层 - HTTP 路由
│   │   ├── auth.py                # 认证端点
│   │   ├── users.py               # 用户管理
│   │   ├── agents.py              # 数字人 CRUD
│   │   ├── chat.py                # 对话与 SSE 流式响应
│   │   ├── knowledge.py           # 文档上传与知识图谱
│   │   └── items.py               # 示例 CRUD
│   ├── core/                      # 核心配置
│   │   ├── config.py              # 环境变量配置
│   │   ├── database.py            # MySQL + Cloud SQL 连接
│   │   ├── security.py            # JWT + bcrypt 工具
│   │   ├── auth.py                # 认证中间件
│   │   ├── exceptions.py          # 自定义异常
│   │   └── handlers.py            # 全局异常处理
│   ├── models/                    # 数据库模型 (SQLAlchemy)
│   │   ├── user.py                # 用户
│   │   ├── agent.py               # 数字人 (含 JSON 字段)
│   │   ├── conversation.py        # 对话与消息
│   │   ├── knowledge.py           # 知识文档元数据
│   │   └── item.py                # 示例模型
│   ├── schemas/                   # Pydantic 验证模型
│   │   ├── user.py
│   │   ├── agent.py
│   │   ├── conversation.py
│   │   ├── knowledge.py
│   │   ├── item.py
│   │   └── response.py            # 通用响应包装
│   ├── services/                  # 业务逻辑层
│   │   ├── user_service.py
│   │   ├── agent_service.py
│   │   ├── chat_service.py        # 对话编排
│   │   ├── knowledge_service.py   # 文档处理
│   │   └── llm_service.py         # OpenAI / LangChain 集成
│   ├── repositories/              # 数据访问层
│   │   ├── conversation_repo.py
│   │   ├── document_repo.py
│   │   └── knowledge_repo.py
│   ├── agent_repo/
│   │   └── agent.py
│   └── user_repo/
│       └── user.py
├── alembic/                       # 数据库迁移
├── alembic.ini
├── docker-compose.yml             # MySQL 本地开发
├── Dockerfile                     # Cloud Run 多阶段构建
├── deploy.sh                      # GCP Cloud Run 部署脚本
├── requirements.txt
├── init_sample_users.py
├── .env.example
└── README.md
```

## 三层架构

```
API Layer (routes/)  -->  Service Layer (services/)  -->  Repository Layer (repositories/)
  HTTP 请求处理            业务逻辑 + DB 会话管理         数据访问 + CRUD
```

- **API 层**: 只负责 HTTP 请求解析和响应
- **Service 层**: 业务逻辑，管理数据库事务
- **Repository 层**: 纯数据访问，不包含业务逻辑

## API 接口

### 认证 `/api/v1/auth`

| 方法 | 端点 | 认证 | 说明 |
|------|------|------|------|
| POST | `/register` | - | 用户注册 |
| POST | `/login` | - | 用户登录，返回 JWT |
| GET | `/me` | Bearer | 获取当前用户信息 |
| POST | `/logout` | Bearer | 登出 |

### 用户 `/api/v1/users`

| 方法 | 端点 | 认证 | 说明 |
|------|------|------|------|
| POST | `/list` | Bearer | 获取用户列表 |
| POST | `/get` | Bearer | 获取指定用户 |
| POST | `/update` | Bearer | 更新用户 |
| POST | `/delete` | Bearer | 删除用户 |

### 数字人 `/api/v1/agents`

| 方法 | 端点 | 认证 | 说明 |
|------|------|------|------|
| POST | `/` | Bearer | 创建数字人 |
| POST | `/list` | Bearer | 获取数字人列表 |
| POST | `/get` | Bearer | 获取指定数字人 |
| POST | `/update` | Bearer | 更新数字人 |
| POST | `/delete` | Bearer | 删除数字人 |

### 对话 `/api/v1/chat`

| 方法 | 端点 | 认证 | 说明 |
|------|------|------|------|
| POST | `/conversations` | Bearer | 创建新对话 |
| POST | `/conversations/list` | Bearer | 获取对话列表 |
| GET | `/conversations/{id}/messages` | Bearer | 获取消息历史 |
| POST | `/conversations/delete` | Bearer | 删除对话 |
| POST | `/conversations/{id}/stream` | Bearer | SSE 流式对话 |

### 知识库 `/api/v1/knowledge`

| 方法 | 端点 | 认证 | 说明 |
|------|------|------|------|
| POST | `/upload` | Bearer | 上传文档 (txt/md, 5MB) |
| POST | `/documents/list` | Bearer | 获取文档列表 |
| POST | `/documents/delete` | Bearer | 删除文档 |
| GET | `/graph/{agent_id}` | Bearer | 获取知识图谱 |
| POST | `/graph/search` | Bearer | 搜索实体 |

## 数据库模型

### User
- id, username, email, full_name, hashed_password
- is_active, is_superuser
- created_at, updated_at

### Agent
- id, user_id (FK)
- name, description, short_description, avatar_url
- agent_type, skills (JSON), permission
- conversation_style, personality
- voice_id, voice_settings (JSON), appearance_settings (JSON)
- temperature, max_tokens, system_prompt
- is_active, created_at, updated_at

### Conversation / Message
- Conversation: id, agent_id, user_id, title, is_active
- Message: id, conversation_id, role (user/assistant/system), content, tokens_used

### KnowledgeDocument
- id, agent_id, user_id
- filename, file_size, status (processing/completed/failed)
- entity_count, created_at

## 技术栈

| 类别 | 技术 |
|------|------|
| Web 框架 | FastAPI 0.109 |
| ORM | SQLAlchemy 2.0 |
| 数据库 | MySQL 8.0 (主库) + Neo4j 5 (知识图谱) |
| 数据库迁移 | Alembic 1.13 |
| 认证 | JWT (python-jose) + bcrypt |
| AI 集成 | LangChain + OpenAI API |
| 实时通信 | SSE (Server-Sent Events) |
| 数据验证 | Pydantic v2 |
| 部署 | Docker + Cloud Run |
| CI/CD | GitHub Actions |

## 数据库迁移

```bash
# 应用所有迁移
alembic upgrade head

# 创建新迁移
alembic revision --autogenerate -m "描述变更"

# 回滚一个版本
alembic downgrade -1

# 查看当前版本
alembic current

# 查看迁移历史
alembic history
```

## 部署

### Docker 本地构建

```bash
docker build -t cosmray-backend .
docker run -p 8000:8000 --env-file .env cosmray-backend
```

### Cloud Run 部署

```bash
./deploy.sh
```

## 环境变量

参考 `.env.example`，主要配置：

```
DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/dbname
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENAI_API_KEY=your-openai-key
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
```

## 示例用户

运行 `python init_sample_users.py` 后可用：

| 用户名 | 密码 |
|--------|------|
| john | password123 |
| jane | password456 |
| alice | password789 |
