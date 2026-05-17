from fastapi import FastAPI
# 1. 引入你在 database.py 寫好的 engine 和 Base 祖先
from database import Base, engine 
# 2. 【超級重要】一定要把 models 引入進來，Base 才能感應到有哪些表要蓋！
import models
from routers import events,user,registrations,comments
Base.metadata.create_all(bind=engine)

app = FastAPI(title='ntu-event',version="1.0.0")

app.include_router(events.router)
app.include_router(user.router)
app.include_router(registrations.router)
app.include_router(comments.router)

@app.get('/',tags=['root'])
async def root():
    return {"message":"fastapi is running"}