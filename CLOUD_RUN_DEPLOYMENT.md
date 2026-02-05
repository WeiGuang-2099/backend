# Cloud Run + Cloud SQL Deployment Guide

完整指南：将 FastAPI 后端部署到 Google Cloud Run 并连接 Cloud SQL MySQL。

---

## 前提条件

1. **安装 gcloud CLI**
   ```bash
   # Windows: 下载并安装 Google Cloud SDK
   # macOS: brew install google-cloud-sdk
   # Linux: 按照官方文档安装
   ```

2. **初始化 gcloud**
   ```bash
   gcloud init
   ```

3. **安装 Docker** (用于本地构建镜像)

---

## 步骤 1: 创建 Cloud SQL MySQL 实例

```bash
# 设置变量
PROJECT_ID="your-project-id"
REGION="asia-east1"  # 选择离用户近的区域
INSTANCE_NAME="fastapi-mysql"
DB_NAME="jwt_auth_db"
DB_USER="jwt_user"

# 创建 MySQL 实例 (db-f1-micro 是最便宜的配置)
gcloud sql instances create "$INSTANCE_NAME" \
    --database-version=MYSQL_8_0 \
    --tier=db-f1-micro \
    --region="$REGION" \
    --storage-auto-increase \
    --storage-size=10GB \
    --availability-type=zonal \
    --project="$PROJECT_ID"

# 创建数据库
gcloud sql databases create "$DB_NAME" \
    --instance="$INSTANCE_NAME" \
    --project="$PROJECT_ID"

# 创建数据库用户 (会提示输入密码)
gcloud sql users create "$DB_USER" \
    --instance="$INSTANCE_NAME" \
    --project="$PROJECT_ID"

# 获取实例连接名称 (保存这个值)
gcloud sql instances describe "$INSTANCE_NAME" \
    --format="value(connectionName)" \
    --project="$PROJECT_ID"
# 输出格式: your-project-id:asia-east1:fastapi-mysql
```

---

## 步骤 2: 启用必要的 API

```bash
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    sqladmin.googleapis.com \
    artifactregistry.googleapis.com \
    --project="$PROJECT_ID"
```

---

## 步骤 3: 创建 Artifact Registry 仓库

```bash
REPO_NAME="fastapi-repo"

gcloud artifacts repositories create "$REPO_NAME" \
    --repository-format=docker \
    --location="$REGION" \
    --description="FastAPI Docker repository" \
    --project="$PROJECT_ID"

# 配置 Docker 认证
gcloud auth configure-docker "$REGION-docker.pkg.dev"
```

---

## 步骤 4: 部署到 Cloud Run

### 方式 1: 使用提供的部署脚本 (推荐)

```bash
cd backend
chmod +x deploy.sh

# 运行部署脚本
./deploy.sh PROJECT_ID REGION SERVICE_NAME

# 示例
./deploy.sh my-project-123 asia-east1 fastapi-backend
```

脚本会自动:
1. 验证项目
2. 启用 API
3. 创建 Artifact Registry 仓库
4. 构建 Docker 镜像
5. 推送镜像
6. 部署到 Cloud Run

### 方式 2: 手动部署

```bash
# 1. 设置变量
PROJECT_ID="your-project-id"
REGION="asia-east1"
SERVICE_NAME="fastapi-backend"
REPO_NAME="fastapi-repo"
IMAGE_NAME="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$SERVICE_NAME"

# 2. 构建并推送镜像
docker build -t "$IMAGE_NAME:latest" .
docker push "$IMAGE_NAME:latest"

# 3. 部署 (替换以下变量)
gcloud run deploy "$SERVICE_NAME" \
    --image="$IMAGE_NAME:latest" \
    --platform=managed \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --allow-unauthenticated \
    --add-cloudsql-instances="CONNECTION_NAME" \
    --set-env-vars="DATABASE_URL=mysql+pymysql://jwt_user:YOUR_PASSWORD@/cloudsql/CONNECTION_NAME/jwt_auth_db" \
    --set-env-vars="SECRET_KEY=$(openssl rand -base64 32)" \
    --set-env-vars="ALLOWED_ORIGINS=https://your-frontend.com" \
    --memory=512Mi \
    --cpu=1 \
    --timeout=300
```

---

## 步骤 5: 运行数据库迁移

部署后需要运行 Alembic 迁移来创建数据库表：

```bash
# 方法 1: 使用 Cloud SQL 代理本地运行迁移
gcloud sql connect fastapi-mysql --user=jwt_user --project="$PROJECT_ID"

# 然后在本地运行
cd backend
alembic upgrade head

# 方法 2: 在 Cloud Shell 中运行
gcloud cloud-shell ssh

# 在 Cloud Shell 中
git clone your-repo
cd your-repo/backend
pip install -r requirements.txt
export DATABASE_URL="mysql+pymysql://..."
alembic upgrade head
```

---

## 步骤 6: 验证部署

```bash
# 获取服务 URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(status.url)" \
    --project="$PROJECT_ID")

echo "Service URL: $SERVICE_URL"

# 测试服务
curl "$SERVICE_URL"

# 查看日志
gcloud run logs tails "$SERVICE_NAME" --region="$REGION" --project="$PROJECT_ID"
```

---

## 环境变量说明

| 变量 | 说明 | 必需 |
|------|------|------|
| `DATABASE_URL` | Cloud SQL 连接字符串 | ✅ |
| `SECRET_KEY` | JWT 签名密钥 (32+ 字符) | ✅ |
| `ALLOWED_ORIGINS` | CORS 允许的前端域名 | ✅ |
| `ALGORITHM` | JWT 算法 (默认: HS256) | ❌ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token 过期时间 (默认: 30) | ❌ |

---

## 成本估算 (按月)

| 服务 | 配置 | 成本 |
|------|------|------|
| Cloud SQL | db-f1-micro, 10GB | ~$8-10 |
| Cloud Run | 按请求数计费 | ~$0-20* |
| Artifact Registry | 存储 | ~$0.10/GB |

*Cloud Run 有免费额度: 每月 200 万请求

---

## 常见问题

### 1. 连接 Cloud SQL 超时
确保 Cloud Run 服务和 Cloud SQL 实例在同一区域。

### 2. 数据库迁移失败
检查 `DATABASE_URL` 格式是否正确使用 Unix socket:
```
mysql+pymysql://user:pass@/cloudsql/project:region:instance/dbname
```

### 3. CORS 错误
更新 `ALLOWED_ORIGINS` 包含前端域名:
```bash
gcloud run services update fastapi-backend \
    --update-env-vars="ALLOWED_ORIGINS=['https://myapp.com']"
```

### 4. 查看 Cloud Run 日志
```bash
gcloud run logs tails fastapi-backend --region=asia-east1
```

---

## 有用的命令

```bash
# 列出所有服务
gcloud run services list

# 获取服务详细信息
gcloud run services describe fastapi-backend --region=asia-east1

# 更新环境变量
gcloud run services update fastapi-backend \
    --update-env-vars="SECRET_KEY=new-key"

# 回滚到上一个版本
gcloud run services update-traffic fastapi-backend \
    --to-revisions=LATEST=0

# 删除服务
gcloud run services delete fastapi-backend --region=asia-east1
```

---

## 下一步

1. 配置自定义域名
2. 设置 CI/CD 自动部署
3. 添加监控和告警
4. 配置 Secret Manager 存储敏感信息
