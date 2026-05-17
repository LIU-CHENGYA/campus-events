from fastapi import APIRouter, Depends ,HTTPException
from sqlalchemy.orm import Session

# 引入基礎建設
from database import get_db
import schemas
from auth import get_current_user
import models 

router = APIRouter(
    prefix="/registrations",
    tags=["registrations 報名模組"]  # 這是給 Swagger UI 文件的分類標籤
    )

#取消報名
@router.put("/{reg_id}",response_model=schemas.RegistrationResponse)
async def cancel_registration(reg_id:int,db: Session = Depends(get_db),current_user: models.User = Depends(get_current_user)):
        registration = db.query(models.Registration).filter(models.Registration.id == reg_id).first()
        # 這裡可以加個小防呆，萬一找不到這筆報名紀錄，就不要繼續往下跑
        if not registration:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="找不到該筆報名紀錄")

        # 只能取消自己的報名
        if registration.user_id != current_user.id:
            raise HTTPException(
            status_code=403,
            detail="你不能取消別人的報名"
            )
        registration.status = models.RegistrationStatus.CANCELLED
        db.add(registration)
        db.commit()
        db.refresh(registration)
        return registration

