# 從 SQLAlchemy 引入需要的功能，包括創建資料庫引擎
from sqlalchemy import create_engine
# 從 SQLAlchemy 引入 ORM 工具，用於定義基礎類和創建會話
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine(
    'sqlite:///campus_events.db',
    connect_args={"check_same_thread": False} # 這是給 SQLite 專用的，讓 FastAPI 的多執行緒可以安全運作
    )
# 創建 Base 類，所有的 ORM 類將繼承這個類
Base = declarative_base()

Session = sessionmaker(autocommit=False, autoflush=False,bind=engine) # 創建 Session 類，並將其與資料庫引擎綁定
# session = Session() # 創建 Session 實例，用於管理資料庫事務 

def get_db():
    db = Session()
    try:
        yield db # 只要把 db 借出去
    finally:
        db.close() # 不管外面的 API 執行成功還是噴錯死掉，finally 100% 絕對會執行！