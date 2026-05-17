from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
# 引入基礎建設
from database import get_db
from models import User
import schemas
from auth import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter(
    prefix="/users", 
    tags=["users 模組"]
    )

# 註冊 API
@router.post("/register", response_model=schemas.UserResponse)
def register(user_data:schemas.UserCreate,db: Session = Depends(get_db)):

    ## 檢查 student_id 是否重複
    existing_user = db.query(User).filter(
        User.student_id == user_data.student_id
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="學號已被註冊"
        ) 

    ##  hash password + 建立 user 
    hashed_pw = hash_password(user_data.password)

    new_user = User(
        student_id=user_data.student_id,
        name=user_data.name,
        avatar_url=user_data.avatar_url,
        hashed_password=hashed_pw
    )

    ## 存進 DB
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# 登入 API
@router.post("/login", response_model=schemas.Token)
def login( user_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db) ):

    # 找 user
    user = db.query(User).filter(
        User.student_id == user_data.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="帳號或密碼錯誤"
        )
    
    # 驗證密碼
    if not verify_password(
        user_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="帳號或密碼錯誤"
        )
    
    # 產 JWT
    token = create_access_token(
        data={
            "sub": str(user.id)
        }
    )

    # 回傳 token
    return {
        "access_token": token,
        "token_type": "bearer"
    }