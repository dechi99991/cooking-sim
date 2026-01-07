"""FastAPI アプリケーション"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

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

# フロントエンドの静的ファイル配信
FRONTEND_DIR = Path(__file__).parent.parent / "frontend" / "dist"

if FRONTEND_DIR.exists():
    # 静的アセット（CSS, JS）
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")

    @app.get("/")
    def serve_frontend():
        """フロントエンドのindex.htmlを返す"""
        return FileResponse(FRONTEND_DIR / "index.html")

    @app.get("/{path:path}")
    def serve_spa(path: str):
        """SPA用: 存在しないパスはindex.htmlにフォールバック"""
        file_path = FRONTEND_DIR / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIR / "index.html")
else:
    @app.get("/")
    def root():
        """ヘルスチェック（フロントエンドなし）"""
        return {"status": "ok", "message": "cooking-sim API is running"}


@app.get("/health")
def health():
    """ヘルスチェック"""
    from .session import get_session_count
    return {
        "status": "ok",
        "active_sessions": get_session_count(),
    }
