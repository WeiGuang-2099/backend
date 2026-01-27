# Service Layer (业务逻辑层)

## 概述

Service层是三层架构中的业务逻辑层，负责处理所有业务规则和逻辑。

## 职责

- ✅ 实现业务逻辑和业务规则
- ✅ 数据验证和转换
- ✅ 调用Repository层进行数据操作
- ✅ 处理复杂的业务流程
- ✅ 抛出业务异常（如`ValueError`）

- ❌ 不应该直接操作数据库
- ❌ 不应该处理HTTP请求/响应
- ❌ 不应该包含路由逻辑

## 使用方法

### 1. 在API层调用Service

```python
from app.services.user_service import user_service
from app.core.database import get_db

@router.post("/list", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    # 直接调用Service层方法
    return user_service.get_all_users(db)
```

### 2. 处理Service层异常

```python
@router.post("/update", response_model=UserResponse)
async def update_user(request: UserUpdateRequest, db: Session = Depends(get_db)):
    try:
        # Service层可能抛出业务异常
        updated_user = user_service.update_user(db, request.user_id, user_update)
        return updated_user
    except ValueError as e:
        # 将业务异常转换为HTTP异常
        raise HTTPException(status_code=400, detail=str(e))
```

## 现有服务

### UserService

位置: `app/services/user_service.py`

**方法列表**:

- `get_all_users(db)` - 获取所有用户
- `get_user_by_id(db, user_id)` - 根据ID获取用户
- `create_user(db, user_create)` - 创建新用户（包含重复检查和密码加密）
- `register_user(db, user_create)` - 注册新用户（create_user的别名）
- `update_user(db, user_id, user_update)` - 更新用户（包含重复检查和密码加密）
- `delete_user(db, user_id)` - 删除用户
- `authenticate_user(db, username, password)` - 用户认证（验证密码）

## 创建新的Service

```python
"""
Service类的模板
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.your_model import YourSchema
from app.repositories import your_repo


class YourService:
    """业务逻辑服务类"""
    
    @staticmethod
    def your_business_method(db: Session, param: str) -> YourSchema:
        """
        业务方法说明
        
        Args:
            db: 数据库会话
            param: 参数说明
            
        Returns:
            返回值说明
            
        Raises:
            ValueError: 业务异常说明
        """
        # 1. 业务验证
        if not param:
            raise ValueError("参数不能为空")
        
        # 2. 调用Repository层
        result = your_repo.get_data(db, param)
        
        # 3. 业务处理和返回
        return YourSchema.from_orm(result)


# 创建单例实例
your_service = YourService()
```

## 设计原则

1. **单一职责**: 每个Service类只处理一个业务领域
2. **无状态**: Service方法应该是无状态的（使用`@staticmethod`）
3. **异常处理**: 使用`ValueError`等Python内置异常表示业务错误
4. **依赖注入**: 通过参数传递依赖（如`db: Session`）
5. **清晰命名**: 方法名应该清楚地表达业务意图

## 常见业务逻辑示例

### 数据验证
```python
if user_repo.get_user_by_username(db, username):
    raise ValueError("用户名已存在")
```

### 数据转换
```python
hashed_password = get_password_hash(password)
user_create.password = hashed_password
```

### 复杂业务流程
```python
# 1. 验证用户
user = user_repo.get_user_by_id(db, user_id)
if not user:
    return None

# 2. 检查权限
if not user.is_active:
    raise ValueError("用户已被禁用")

# 3. 执行操作
result = user_repo.update_status(db, user_id, new_status)

# 4. 发送通知（可选）
# send_notification(user.email, "状态已更新")

return result
```

## 测试

Service层应该容易测试，因为它不依赖HTTP框架：

```python
def test_create_user_duplicate_username():
    """测试创建用户时用户名重复"""
    db = get_test_db()
    user_create = UserCreate(username="test", email="test@example.com", password="123456")
    
    # 第一次创建应该成功
    user1 = user_service.create_user(db, user_create)
    assert user1 is not None
    
    # 第二次创建相同用户名应该失败
    with pytest.raises(ValueError, match="用户名.*已存在"):
        user_service.create_user(db, user_create)
```
