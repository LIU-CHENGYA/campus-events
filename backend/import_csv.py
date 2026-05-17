import csv
from datetime import datetime
from collections import defaultdict
from sqlalchemy.orm import Session
from database import Session, Base, engine
import models
import schemas

# 確保資料表都已經建立
Base.metadata.create_all(bind=engine)

def load_tags_mapping(tags_csv_path: str) -> dict:
    """
    讀取 event_tags.csv，整理成 { event_url: ["標籤1", "標籤2"] } 的字典
    """
    tags_map = defaultdict(list)
    try:
        with open(tags_csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row.get("event_url")
                tag_name = row.get("tag")
                if url and tag_name:
                    tags_map[url].append(tag_name.strip())
    except Exception as e:
        print(f"讀取標籤 CSV 失敗: {e}")
    return tags_map

def get_or_create_tag(db: Session, tag_name: str) -> models.Tag:
    """
    檢查資料庫內有沒有這個標籤，有就直接用，沒有就新建一個
    """
    db_tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
    if not db_tag:
        db_tag = models.Tag(name=tag_name)
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)
    return db_tag

def parse_slots(slots_str: str) -> int:
    """
    清洗人數欄位，把 "130 人" 轉換成整數 130
    """
    if not slots_str:
        return 0
    # 移除 "人" 字和空白
    cleaned = slots_str.replace("人", "").replace(" ", "")
    try:
        return int(cleaned)
    except ValueError:
        return 0

def parse_start_time(time_range_str: str) -> datetime:
    """
    將 "2026-06-08 12:20:00 ~ 14:00:00" 拆開並轉換成開始時間的 datetime 物件
    """
    if not time_range_str:
        return None
    try:
        # 拿前半段的開始時間
        start_time_str = time_range_str.split("~")[0].strip()
        return datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return None

def import_data(events_csv_path: str, tags_csv_path: str):
    db: Session = Session()
    print("正在預載入標籤對應表...")
    tags_map = load_tags_mapping(tags_csv_path)
    
    print("開始解析並匯入活動資料...")
    try:
        with open(events_csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            for index, row in enumerate(reader, start=1):
                event_url = row.get("event_url")
                if not event_url:
                    continue
                
                # 檢查是否已經匯入過（避免重複匯入相同網址的活動）
                exists = db.query(models.Event).filter(models.Event.event_url == event_url).first()
                if exists:
                    print(f"第 {index} 筆活動已存在資料庫，跳過。")
                    continue

                # 1. 解析人數與時間
                max_slots = parse_slots(row.get("capacity"))
                remaining_slots = parse_slots(row.get("remaining_slots"))
                start_time = parse_start_time(row.get("session_time"))

                # 2. 轉換與對齊欄位至 Pydantic Schema (EventCreate)
                try:
                    event_data = schemas.EventCreate(
                        event_url=event_url,
                        title=row.get("activity_name_event_page") or row.get("session_name"),
                        type=row.get("activity_type"),
                        start_time=start_time,
                        organizer_unit=row.get("organizer_unit"),
                        organizer_contact=row.get("organizer_contact"),
                        reg_time_display=row.get("registration_time"),
                        registration_type=row.get("registration_type"),
                        target_audience=row.get("target_audience"),
                        max_slots=max_slots,
                        current_slots=max_slots - remaining_slots,
                        is_free=row.get("tag_free") == "True",
                        has_food=row.get("tag_food") == "True",
                        description=row.get("session_content") or row.get("activity_content")
                    )
                except Exception as ve:
                    print(f"❌ 第 {index} 筆資料驗證失敗，原因: {ve}")
                    continue

                # 3. 轉成 SQLAlchemy Model 物件
                db_event = models.Event(**event_data.model_dump())

                # 🌟 4. 處理多對多標籤的神奇魔法！
                # 找出這筆活動在 event_tags.csv 裡對應的所有標籤名稱
                csv_tags = tags_map.get(event_url, [])
                for tag_name in csv_tags:
                    # 去資料庫撈取或建立這個標籤物件
                    tag_obj = get_or_create_tag(db, tag_name)
                    # 直接 append 到活動的 tags 列表裡！SQLAlchemy 會自動幫你寫入中間表 eventTag！
                    db_event.tags.append(tag_obj)

                db.add(db_event)
                
                if index % 50 == 0:
                    db.commit()  # 每 50 筆分批存檔一次，效能更好
                    print(f"已處理 {index} 筆...")

            db.commit()  # 提交剩餘的所有資料
            print("🎉 所有活動與標籤關聯已完美匯入完成！")
            
    except Exception as e:
        print(f"💥 匯入過程中發生嚴重錯誤: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # 請確保這兩個路徑與你的 CSV 檔案存放位置一致
    import_data(
        events_csv_path="../data/events_processed.csv", 
        tags_csv_path="../data/event_tags.csv"
    )