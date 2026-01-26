"""
初始化示例用户到数据库
"""
from app.core.database import SessionLocal, init_db
from app.core.security import get_password_hash
from app.crud import user as crud_user
from app.schemas.user import UserCreate


def init_sample_users():
    """创建示例用户"""
    # 初始化数据库表
    init_db()
    
    db = SessionLocal()
    
    try:
        sample_users = [
            {
                "username": "john",
                "email": "john@example.com",
                "password": "password123"
            },
            {
                "username": "jane",
                "email": "jane@example.com",
                "password": "password456"
            },
            {
                "username": "alice",
                "email": "alice@example.com",
                "password": "password789"
            }
        ]
        
        for user_data in sample_users:
            # 检查用户是否已存在
            existing_user = crud_user.get_user_by_username(db, user_data["username"])
            if existing_user:
                print(f"用户 {user_data['username']} 已存在，跳过")
                continue
            
            # 加密密码
            hashed_password = get_password_hash(user_data["password"])
            
            # 创建用户
            user_create = UserCreate(
                username=user_data["username"],
                email=user_data["email"],
                password=hashed_password
            )
            
            new_user = crud_user.create_user(db, user_create)
            print(f"创建用户: {new_user.username} (ID: {new_user.id})")
        
        print("\n 示例用户初始化完成！")
        print("\n可用账户：")
        print("  john / password123")
        print("  jane / password456")
        print("  alice / password789")
        
    except Exception as e:
        print(f"初始化失败: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    init_sample_users()
