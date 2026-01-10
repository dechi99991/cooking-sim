"""設定ファイル"""
import os
from pathlib import Path

# Gemini API設定
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash-image"  # Gemini 画像生成モデル

# パス設定
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "frontend" / "public" / "assets" / "items"
MANIFEST_PATH = PROJECT_ROOT / "image_generator" / "manifest.json"

# 画像設定
IMAGE_SIZE = 32
IMAGE_FORMAT = "png"

# レート制限設定
RATE_LIMIT_DELAY = 4.0  # 秒（15 RPM = 4秒間隔）
MAX_RETRIES = 3
RETRY_DELAY = 10.0  # リトライ時の待機秒数

# カテゴリ設定
CATEGORIES = ["ingredients", "relics", "recipes", "provisions"]
