#發行通行證
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from models import User

import os
from dotenv import load_dotenv
# 讀取 .env 檔案
load_dotenv()

# ---------------- 第一層（密碼層）----------------------- #
# 設定「密碼雜湊策略管理器」，來源為 passlib
pwd_context = CryptContext(
    schemes=["bcrypt"], #「我這個系統目前只允許用 bcrypt 這種算法來做密碼 hash」
    deprecated="auto"   # 如果某種 hash 演算法「過時或不建議使用」，自動標記為 deprecated
)

#  hash password 這是註冊時用的 把 明碼 → hash
def hash_password(password: str):
    return pwd_context.hash(password)

# verify password 把使用者輸入的明碼 和 資料庫 hash 的密碼做比對
def verify_password(
    plain_password: str,
    hashed_password: str
):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )

# ---------------- WT Token 的產生 + 驗證 -------------- #
# 一開始開發可以這樣寫
# SECRET_KEY = "your-secret-key-change-in-production"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小時 # token 幾分鐘後過期

# 從環境變數中安全地抓取，如果抓不到，才用後面的字串當備用（通常用於本地測試防呆）
SECRET_KEY = os.getenv("SECRET_KEY", "temporary-local-dev-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))


## 產生 JWT
def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(  # 設定過期時間 (現在時間 + 24小時)
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({                       # 塞進 payload
        "exp": expire
    })

    return jwt.encode(                       # ncode 成 token
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

## 「解 JWT」函式
def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except JWTError:
        return None
    

# -------------- 建立 get_current_user 取得當前使用者 ---------------# 

# 建立 token 提取器
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 無效或已過期"
        )

    user_id = payload.get("sub")

    user = db.query(User).filter(
        User.id == int(user_id)
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="使用者不存在"
        )

    return user