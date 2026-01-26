"""
认证相关路由：登录、注册、获取当前用户信息
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.schemas.user import UserLogin, UserCreate, UserResponse, TokenResponse
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.auth import get_current_user
from app.crud import user as crud_user

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册
    
    Args:
        user: 用户注册信息
        db: 数据库会话
        
    Returns:
        TokenResponse: 包含 access_token 和用户信息
        
    Raises:
        HTTPException: 用户名或邮箱已存在时返回 400
    """
    # 检查用户名是否已存在
    if crud_user.get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # 检查邮箱是否已存在
    if crud_user.get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # 对密码进行哈希加密
    hashed_password = get_password_hash(user.password)
    
    # 创建新用户（替换明文密码为哈希密码）
    user_data = user.model_copy()
    user_data.password = hashed_password
    new_user = crud_user.create_user(db, user_data)
    
    # 生成 JWT Token
    access_token = create_access_token(data={"sub": new_user.id, "username": new_user.username})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email
        )
    )


@router.post("/login", response_model=TokenResponse)
async def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录
    
    Args:
        user_login: 登录凭证（用户名和密码）
        db: 数据库会话
        
    Returns:
        TokenResponse: 包含 access_token 和用户信息
        
    Raises:
        HTTPException: 凭证无效时返回 401
    """
    # 查找用户
    user = crud_user.get_user_by_username(db, user_login.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # 验证密码
    if not verify_password(user_login.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # 生成 JWT Token
    access_token = create_access_token(data={"sub": user.id, "username": user.username})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """
    获取当前登录用户的信息（需要认证）
    
    Args:
        current_user: 通过 JWT Token 解析出的当前用户
        
    Returns:
        UserResponse: 当前用户信息
    """
    return current_user


@router.post("/logout")
async def logout(current_user: UserResponse = Depends(get_current_user)):
    """
    用户登出（前端需要删除本地存储的 token）
    
    注意：JWT 是无状态的，服务端不需要做任何处理，
    只需前端删除存储的 token 即可
    
    Returns:
        dict: 成功消息
    """
    return {"message": "Logout successful"}
