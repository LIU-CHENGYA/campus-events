from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List,Optional
from auth import get_current_user

# 引入基礎建設
from database import get_db
import models
import schemas

router = APIRouter(
    prefix="/events",
    tags=["event 活動模組"]  # 這是給 Swagger UI 文件的分類標籤
    )

#獲取全部活動列表，輸入文字、日期、類別 搜尋活動列表
@router.get("/",response_model=List[schemas.EventResponse]) #「等一下不管廚房噴出什麼，最後一定要打包成一個『裝滿 TagResponse 的陣列』送給客人
async def get_event_all(
    keyword: Optional[str] = None,
    date: Optional[str] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db)):
    # 3. 資料庫撈資料邏輯
    if keyword:
        events = db.query(models.Event).filter(models.Event.title.like(f"%{keyword}%")).all()
    elif date:
        events = db.query(models.Event).filter(models.Event.start_time == date).all()
    elif type:
        events = db.query(models.Event).filter(models.Event.type == type).all()
    else:
        events = db.query(models.Event).all() #FastAPI 就會自動幫你開啟會話、借你使用 db、並在 API 結束時幫你關閉

    # 4. 把結果送出去（FastAPI 會自動用 TagResponse 幫你打包）
    return events


#取得單一活動 
@router.get("/{id}",response_model=schemas.EventResponse) # 拿掉 List，只回傳單一物件
async def get_event_by_id(id:int ,db: Session = Depends(get_db)):
    events = db.query(models.Event).filter(models.Event.id == id).first()
    return events

#查看該活動的留言
@router.get("/{id}/comments",response_model=List[schemas.CommentResponse])
async def get_event_comments(id:int,db: Session = Depends(get_db)):
    # 要撈出所有 event_id 等於網址 id 的留言
    comments = db.query(models.Comment).filter(models.Comment.event_id == id).all()
    return comments

#新增留言
@router.post("/{id}/comments",response_model=schemas.CommentResponse)
async def get_event(id:int, comment_in: schemas.CommentCreate,db: Session = Depends(get_db),current_user: models.User = Depends(get_current_user)):
    new_comment = models.Comment(
        content = comment_in.content,
        user_id = current_user.id,
        event_id=id
    )
    db.add(new_comment)
    db.commit()
    # 4. 刷新這個物件，讓它取得資料庫自動生成的 id 和時間
    db.refresh(new_comment)
    return new_comment
#送出報名
@router.post("/{id}/register",response_model=schemas.RegistrationResponse)
async def get_event(id:int,reg_in:schemas.RegistrationCreate,db: Session = Depends(get_db),current_user: models.User = Depends(get_current_user)):
    #建立一個 Python 資料庫物件
    new_reg = models.Registration(
        user_id = current_user.id,
        event_id=id
    )
    db.add(new_reg)
    db.commit()
    # 4. 刷新這個物件，讓它取得資料庫自動生成的 id 和時間
    db.refresh(new_reg)
    return new_reg



