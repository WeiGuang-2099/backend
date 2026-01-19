<!--
 * @Author: yuheng li a1793138
 * @Date: 2026-01-19 19:34:55
 * @LastEditors: yuheng 
 * @LastEditTime: 2026-01-20 09:58:21
 * @FilePath: \task-all\backend\README.md
 * @Description: 
 * 
 * Copyright (c) ${2024} by ${yuheng li}, All Rights Reserved. 
-->
# FastAPI Backend

基础的FastAPI后端项目结构

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
│   │       └── items.py     # 示例路由
│   ├── core/                # 核心配置
│   │   ├── __init__.py
│   │   └── config.py        # 配置文件
│   ├── models/              # 数据库模型
│   │   └── __init__.py
│   └── schemas/             # Pydantic模型
│       ├── __init__.py
│       └── item.py          # 示例schema
├── requirements.txt         # 依赖包
├── .env.example            # 环境变量示例
└── README.md               # 项目说明
```

## 快速开始

1. **安装依赖**
```bash
cd backend
pip install -r requirements.txt
```

2. **配置环境变量**
```bash
cp .env.example .env
# 根据需要修改.env文件
```

3. **运行服务**
```bash
# 方式1：使用uvicorn命令
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 方式2：直接运行main.py
python -m app.main
```

4. **访问API文档**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API示例

### Items API

- `GET /api/v1/items/` - 获取所有items
- `GET /api/v1/items/{item_id}` - 获取指定item
- `POST /api/v1/items/` - 创建新item
- `PUT /api/v1/items/{item_id}` - 更新item
- `DELETE /api/v1/items/{item_id}` - 删除item

### 创建item示例

```bash
curl -X POST "http://localhost:8000/api/v1/items/" \
  -H "Content-Type: application/json" \
  -d '{"name":"测试商品","description":"这是一个测试","price":99.99}'
```

## 目录说明

- **app/main.py**: FastAPI应用主入口，配置CORS、路由等
- **app/core/config.py**: 配置管理，使用pydantic-settings
- **app/api/routes/**: API路由模块
- **app/models/**: 数据库模型（如使用SQLAlchemy）
- **app/schemas/**: Pydantic数据验证模型

