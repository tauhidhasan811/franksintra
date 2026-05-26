from api.router.chat_route import router as chat_router
from fastapi import FastAPI
app = FastAPI()
app.include_router(chat_router, prefix="/api/ai/v1")
