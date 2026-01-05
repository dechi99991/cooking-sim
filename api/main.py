"""FastAPI アプリケーション"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router

app = FastAPI(
    title="cooking-sim API",
    description="一人暮らしサバイバルゲーム API",
    version="1.0.0",
)

# CORS設定（開発用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(router)


@app.get("/")
def root():
    """ヘルスチェック"""
    return {"status": "ok", "message": "cooking-sim API is running"}


@app.get("/health")
def health():
    """ヘルスチェック"""
    from .session import get_session_count
    return {
        "status": "ok",
        "active_sessions": get_session_count(),
    }
