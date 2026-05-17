from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

# 引入基礎建設
from database import get_db
import models
import schemas

router = APIRouter(
    prefix="/comments",
    tags=["comments 留言模組"]  # 這是給 Swagger UI 文件的分類標籤
    )

@router.get("/",response_model=List[schemas.CommentResponse])
async def get_all_comments(db: Session = Depends(get_db)):
    comments = db.query(models.Comment).all()
    return comments


