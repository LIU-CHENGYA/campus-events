# campus-events

```markdown
#  Campus-Events 
## 說明
這是一個基於 **FastAPI** 框架開發的後端練習專案，核心功能圍繞在「學生註冊、登入驗證」與「JWT 安全認證機制」。本專案嚴格遵循 RESTful API 設計規範，並整合了 SQLAlchemy ORM 進行資料庫管理。

## Tech Stack
* **Backend Framework:** FastAPI
* **Database ORM:** SQLAlchemy
* **Database:** SQLite (本地測試)
* **Security & Auth:** JWT (JSON Web Tokens), OAuth2 (Password Bearer)
* **Data Validation:** Pydantic (Schemas)

---

## 📂 專案目錄結構
```text
backend/
├── app/
│   ├── models.py          # SQLAlchemy 資料庫模型 (DB Models)
│   ├── schemas.py         # Pydantic 資料型態驗證 (Schemas)
│   ├── database.py        # 資料庫連線設定 (Engine, Session)
│   ├── auth.py            # JWT Token 產生與驗證安全核心
│   └── routers/
│       └── users.py       # 使用者相關 API 路由 (註冊、登入)
├── main.py                # 應用程式主入口
├── requirements.txt       # Python 套件依賴清單
├── .env.example           # 環境變數設定範本
└── .gitignore             # Git 忽略設定 (已排除 venv, __pycache__, .env)

```

---

## 🚀 本地開發環境架構與啟動指南

想要在本機執行此專案，請依照以下步驟進行設定：

### 1. 複製專案與建立虛擬環境

首先將專案 clone 至本地，並切換至 `backend` 目錄下建立 Python 虛擬環境：

```bash
# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境 (Windows Git Bash)
source venv/Scripts/activate

# 啟動虛擬環境 (Mac / Linux)
# source venv/bin/activate

```

### 2. 安裝相依套件

確保虛擬環境啟動後（終端機前方出現 `(venv)`），執行以下指令一鍵安裝所有後端套件：

```bash
pip install -r requirements.txt

```

### 3. 設定環境變數 (.env)

本專案不將機密金鑰（如 `SECRET_KEY`）直接寫死在程式碼中。請複製 `.env.example` 並重新命名為 `.env`：

```bash
cp .env.example .env

```

打開 `.env` 檔案，並填入您自訂的安全性設定：

```ini
SECRET_KEY=填入您在本地生成的隨機安全密鑰
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

```

> 💡 **如何生成安全密鑰？** 可以在終端機執行以下指令快速生成：
> `python -c "import secrets; print(secrets.token_hex(32))"`

### 4. 啟動伺服器

```bash
uvicorn main:app --reload

```

啟動成功後，伺服器將運行於 `http://127.0.0.1:8000`。

---
