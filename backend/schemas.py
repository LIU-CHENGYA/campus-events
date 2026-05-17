from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Optional
from models import RegistrationStatus

## 1. user 
### 共同基底 放前後端「看得到且不敏感」的欄位
class UserBase(BaseModel):
    student_id : str
    name :str
    avatar_url :Optional[str] = None  # 頭貼預設可以是空的 (Optional)

### 前端輸入(註冊)
class UserCreate(UserBase):
    password :str

#### 增加 登入
class UserLogin(BaseModel):
    student_id: str
    password: str

## 後端輸出
class UserResponse(UserBase):
    id : int
    class Config:
        from_attributes = True  # 讓 Pydantic 可以直接讀取 SQLAlchemy 的 User 物件

# 增加 JWT Token回傳格式
class Token(BaseModel):
    access_token: str
    token_type: str

## 3. tag
class TagBase(BaseModel):
    name : str
class TagCreate(TagBase):
    pass
## 後端輸出
class TagResponse(TagBase):
    id : int
    class Config:
        from_attributes = True 

## 2. Event
### 共同基底 
class EventBase(BaseModel):
    event_url: str
    title: str
    type: Optional[str] = None
    start_time: Optional[datetime] = None  # 如果 CSV 的時間格式偶爾有缺，用 Optional
    organizer_unit: Optional[str] = None
    organizer_contact: Optional[str] = None
    reg_time_display: Optional[str] = None
    registration_type: Optional[str] = None
    target_audience: Optional[str] = None
    max_slots: Optional[int] = None
    current_slots: Optional[int] = None
    is_free: bool = True                    
    has_food: bool = False
    description: Optional[str] = None
### 前端輸入
class EventCreate(EventBase):
    pass
## 後端輸出
class EventResponse(EventBase):
    id : int
    # 告訴 FastAPI：我回傳活動時，要順便附帶一個「這個活動的所有標籤列表」
    tags: list[TagResponse] = []
    class Config:
        from_attributes = True  



## 4. Registration
class RegistrationBase(BaseModel):
    event_id: int
class RegistrationCreate(RegistrationBase):
    pass
class RegistrationResponse(RegistrationBase):
    id : int
    user_id: int
    created_at : datetime
    status: RegistrationStatus  # 回傳時才帶上
    class Config:
        from_attributes = True 


## 5. Comment
class CommentBase(BaseModel):
    event_id: int
    content : str
class CommentCreate(CommentBase):
    pass
class CommentResponse(CommentBase):
    id : int
    user_id: int
    created_at : datetime
    class Config:
        from_attributes = True 
