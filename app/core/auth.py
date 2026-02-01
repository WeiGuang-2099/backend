"""
认证中间件：验证 JWT Token 并获取当前用户

遵循三层架构原则，使用 Service 层获取用户，不直接依赖数据库。
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_access_token
from app.schemas.user import UserResponse
from app.services.user_service import user_service

# HTTP Bearer Token 方案
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserResponse:
    """
    从 JWT Token 中获取当前用户

    Args:
        credentials: HTTP Authorization Header 中的凭证

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

    # 通过 Service 层获取用户
    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# 可选的用户依赖（不强制要求登录）
async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserResponse | None:
    """
    可选的获取当前用户（不强制要求登录）

    Returns:
        UserResponse | None: 用户信息或 None
    """
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
