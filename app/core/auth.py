"""
认证中间件：验证 JWT Token 并获取当前用户
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.security import decode_access_token
from app.core.database import get_db
from app.schemas.user import UserResponse
from app.crud import user as crud_user

# HTTP Bearer Token 方案
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    从 JWT Token 中获取当前用户
    
    Args:
        credentials: HTTP Authorization Header 中的凭证
        db: 数据库会话
        
    Returns:
        UserResponse: 当前用户信息
        
    Raises:
        HTTPException: Token 无效或用户不存在时抛出 401 异常
    """
    token = credentials.credentials
    
    # 解码 token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 从 payload 中获取用户 ID
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 从数据库获取用户
    user = crud_user.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email
    )


# 可选的用户依赖（不强制要求登录）
async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserResponse | None:
    """
    可选的获取当前用户（不强制要求登录）
    
    Returns:
        UserResponse | None: 用户信息或 None
    """
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
