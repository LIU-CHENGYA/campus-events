import enum
from sqlalchemy import  Column, Integer, String, DateTime, Enum,ForeignKey,Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base
## models 不需要加 JWT 欄位，JWT 不存在 DB。JWT 是登入時動態產生的
# Define a simple User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    student_id = Column(String,unique=True,nullable=False)
    name = Column(String,nullable=False)
    avatar_url = Column(String)
    hashed_password = Column(String,nullable=False)

### **Event (活動) — 這裡放爬下來的資料**
class Event(Base):
    __tablename__ = "event"

    id = Column(Integer,primary_key=True)
    event_url = Column(String,unique=True)
    title = Column(String)
    type  = Column(String)
    start_time = Column(DateTime)
    organizer_unit = Column(String)
    organizer_contact = Column(String)
    reg_time_display = Column(String)
    registration_type = Column(String)
    target_audience = Column(String)
    max_slots = Column(Integer)
    current_slots = Column(Integer)
    is_free = Column(Boolean)
    has_food = Column(Boolean)
    description = Column(String)
    tags = relationship("Tag", secondary="event_tag") 
    #「未來當我跟你要某個活動的標籤時（例如 event.tags），請你自動幫我透過 eventTag 這張中間橋樑表，去把 tag 表格裡對應的標籤全部撈出來給我。」

### **Tag (標籤)**
class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer,primary_key=True)
    name = Column(String)

### EventTag
class EventTag(Base):
    __tablename__ = "event_tag"

    id = Column(Integer,primary_key=True)
    event_id = Column(Integer,ForeignKey('event.id'))
    tag_id = Column(Integer,ForeignKey('tag.id'))

# . 定義一個 Python 的 Enum 類別
class RegistrationStatus(str, enum.Enum):
    REGISTERED = "registered"  # 已報名
    CANCELLED = "cancelled"    # 已取消

### **Registration (報名紀錄)**
class Registration(Base):
    __tablename__ = "registration"

    id = Column(Integer,primary_key=True)
    user_id = Column(Integer,ForeignKey('users.id'))
    event_id = Column(Integer,ForeignKey('event.id'))
    status = Column(Enum(RegistrationStatus),default=RegistrationStatus.REGISTERED, nullable=False) #- `status` (狀態：已報名、已取消) -> *這能滿足你「查看取消活動」的需求*
    created_at = Column(DateTime,default=func.now())

### **Comment (留言)**
class Comment(Base):
    __tablename__ = "comment"

    id = Column(Integer,primary_key=True)
    user_id = Column(Integer,ForeignKey('users.id'))
    event_id = Column(Integer,ForeignKey('event.id'))
    content = Column(String)
    created_at = Column(DateTime,default=func.now())

