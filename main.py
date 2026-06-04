from api.router.chat_route import router as chat_router
from api.router.set_metadata_route import router as set_metadata_router
from fastapi import FastAPI
app = FastAPI()
app.include_router(chat_router, prefix="/api/ai/v1")
app.include_router(set_metadata_router, prefix="/api/ai/v1")
