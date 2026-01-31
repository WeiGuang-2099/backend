# 三层架构设计文档

本项目采用标准的三层架构（Three-tier Architecture）设计，实现了关注点分离和高内聚低耦合。

## 架构层次

```
┌─────────────────────────────────────────┐
│         API Layer (表现层)               │
│  app/api/routes/                        │
│  - 处理HTTP请求和响应                    │
│  - 参数验证和异常转换                    │
│  - 不包含业务逻辑                        │
└──────────────┬──────────────────────────┘
               │ 依赖
               ↓
┌─────────────────────────────────────────┐
│     Service Layer (业务逻辑层)           │
│  app/services/                          │
│  - 处理业务逻辑                          │
│  - 数据验证和转换                        │
│  - 不直接操作数据库                      │
└──────────────┬──────────────────────────┘
               │ 依赖
               ↓
┌─────────────────────────────────────────┐
│   Repository Layer (数据访问层)          │
│  app/user_repo/ (或 app/repositories/)  │
│  - 数据库CRUD操作                        │
│  - SQL查询封装                           │
│  - 不包含业务逻辑                        │
└─────────────────────────────────────────┘
```

## 各层职责

### 1. API Layer (表现层)
**位置**: `app/api/routes/`

**职责**:
- 处理HTTP请求和响应
- 请求参数验证（通过Pydantic模型）
- 调用Service层方法
- 将Service层异常转换为HTTP异常
- **不应该**: 包含业务逻辑或直接访问数据库

**示例** (`app/api/routes/users.py`):
```python
@router.post("/get", response_model=UserResponse)
async def get_user(
    request: UserIdRequest = Body(...),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """API层只负责请求处理"""
    user = user_service.get_user_by_id(db, request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### 2. Service Layer (业务逻辑层)
**位置**: `app/services/`

**职责**:
- 实现业务逻辑
- 数据验证和转换
- 调用Repository层进行数据操作
- 处理复杂的业务流程
- 抛出业务异常（如`ValueError`）
- **不应该**: 直接操作数据库或处理HTTP请求

**示例** (`app/services/user_service.py`):
```python
@staticmethod
def create_user(db: Session, user_create: UserCreate) -> UserResponse:
    """Service层处理业务逻辑"""
    # 业务逻辑：检查用户名是否已存在
    existing_user = user_repo.get_user_by_username(db, user_create.username)
    if existing_user:
        raise ValueError(f"用户名 '{user_create.username}' 已存在")
    
    # 业务逻辑：密码加密
    hashed_password = get_password_hash(user_create.password)
    user_create.password = hashed_password
    
    # 调用Repository层
    created_user = user_repo.create_user(db, user_create)
    return UserResponse(...)
```

### 3. Repository Layer (数据访问层)
**位置**: `app/user_repo/` (或 `app/repositories/`)

**职责**:
- 封装所有数据库操作
- 执行CRUD操作
- 构建和执行SQL查询
- **不应该**: 包含业务逻辑

**示例** (`app/user_repo/user.py`):
```python
def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Repository层只负责数据库操作"""
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate) -> User:
    """Repository层只负责数据库操作"""
    db_user = User(
        username=user.username,
        email=user.email,
        password=user.password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

## 数据流向

### 请求流程（Request Flow）
```
HTTP Request 
    ↓
API Layer (routes)
    ↓ 调用
Service Layer (services)
    ↓ 调用
Repository Layer (repositories)
    ↓ 访问
Database
```

### 响应流程（Response Flow）
```
Database
    ↓ 返回数据
Repository Layer (返回 Model 对象)
    ↓ 返回数据
Service Layer (转换为 Schema 对象)
    ↓ 返回数据
API Layer (返回 HTTP Response)
    ↓
HTTP Response
```

## 优势

1. **关注点分离**: 每层只负责自己的职责
2. **易于测试**: 可以独立测试每一层
3. **易于维护**: 业务逻辑集中在Service层
4. **可扩展性**: 容易添加新功能或修改现有功能
5. **代码复用**: Service层可以被多个API端点调用
6. **易于理解**: 清晰的架构层次便于新成员理解代码

## 依赖规则

- API层 **只能** 依赖 Service层
- Service层 **只能** 依赖 Repository层
- Repository层 **只能** 依赖 Model层（数据库模型）
- **禁止**跨层依赖（如API层直接调用Repository层）
- **禁止**反向依赖（如Repository层依赖Service层）

## 文件组织

```
app/
├── api/
│   └── routes/          # API层：HTTP路由处理
│       ├── auth.py      # 认证相关路由
│       └── users.py     # 用户相关路由
├── services/            # Service层：业务逻辑
│   └── user_service.py  # 用户业务逻辑
├── user_repo/           # Repository层：数据访问
│   └── user.py          # 用户数据访问
├── models/              # Model层：数据库模型
│   └── user.py          # 用户数据模型
└── schemas/             # Schema层：数据验证
    └── user.py          # 用户请求/响应模型
```

## 示例：完整的请求处理流程

以"创建用户"为例：

1. **API层** (`routes/auth.py`):
   ```python
   @router.post("/register")
   async def register(user: UserCreate, db: Session = Depends(get_db)):
       try:
           new_user = user_service.register_user(db, user)
           # ... 生成token和返回
       except ValueError as e:
           raise HTTPException(status_code=400, detail=str(e))
   ```

2. **Service层** (`services/user_service.py`):
   ```python
   def register_user(db: Session, user_create: UserCreate):
       # 检查用户名是否存在（业务逻辑）
       if user_repo.get_user_by_username(db, user_create.username):
           raise ValueError("用户名已存在")
       
       # 密码加密（业务逻辑）
       user_create.password = get_password_hash(user_create.password)
       
       # 调用Repository层
       return user_repo.create_user(db, user_create)
   ```

3. **Repository层** (`user_repo/user.py`):
   ```python
   def create_user(db: Session, user: UserCreate):
       db_user = User(**user.dict())
       db.add(db_user)
       db.commit()
       db.refresh(db_user)
       return db_user
   ```

## 最佳实践

1. **保持层次清晰**: 不要在API层写业务逻辑
2. **使用依赖注入**: 通过FastAPI的`Depends`机制注入依赖
3. **统一异常处理**: Service层抛出业务异常，API层转换为HTTP异常
4. **使用Schema进行验证**: 利用Pydantic模型进行数据验证
5. **避免循环依赖**: 遵循单向依赖原则
6. **编写清晰的注释**: 说明每层的职责和方法的用途

## 未来扩展

当项目规模增大时，可以考虑：

- 引入 **DTO层** (Data Transfer Objects): 在Service层和Repository层之间传递数据
- 引入 **Domain层**: 实现领域驱动设计（DDD）
- 引入 **Cache层**: 在Service层和Repository层之间添加缓存
- 引入 **Event层**: 实现事件驱动架构
