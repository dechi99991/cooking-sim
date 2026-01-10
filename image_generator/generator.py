"""Gemini APIを使用した画像生成"""
import asyncio
import base64
import json
import time
from pathlib import Path
from datetime import datetime

from . import config
from .prompts import build_prompt
from .extractor import ItemInfo, extract_all_items


def load_manifest() -> dict:
    """マニフェストを読み込み"""
    if config.MANIFEST_PATH.exists():
        with open(config.MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_manifest(manifest: dict):
    """マニフェストを保存"""
    with open(config.MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def get_output_path(item_name: str, category: str) -> Path:
    """出力ファイルパスを取得"""
    # ファイル名をサニタイズ（日本語OK、特殊文字除去）
    safe_name = item_name.replace("/", "_").replace("\\", "_").replace(":", "_")
    return config.OUTPUT_DIR / category / f"{safe_name}.png"


def is_generated(item_name: str, category: str, manifest: dict) -> bool:
    """既に生成済みかチェック"""
    if category not in manifest:
        return False
    return item_name in manifest[category]


class ImageGenerator:
    """Gemini APIを使用した画像生成クラス"""

    def __init__(self):
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        # google-genai ライブラリを使用
        try:
            from google import genai
        except ImportError:
            raise ImportError(
                "google-genai library is not installed. "
                "Please install it with: pip install google-genai"
            )
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.model = config.GEMINI_MODEL
        self._last_request_time = 0

    async def _rate_limit_wait(self):
        """レート制限のための待機"""
        elapsed = time.time() - self._last_request_time
        if elapsed < config.RATE_LIMIT_DELAY:
            wait_time = config.RATE_LIMIT_DELAY - elapsed
            print(f"  [Rate limit] Waiting {wait_time:.1f}s...")
            await asyncio.sleep(wait_time)
        self._last_request_time = time.time()

    async def generate_single(
        self,
        item: ItemInfo,
        dry_run: bool = False
    ) -> tuple[bool, str]:
        """
        単一アイテムの画像を生成

        Returns:
            (success: bool, message: str)
        """
        prompt = build_prompt(item.name, item.category, item.subcategory)
        output_path = get_output_path(item.name, item.category)

        if dry_run:
            return True, f"[DRY RUN] Would generate: {output_path}"

        # 出力ディレクトリ確保
        output_path.parent.mkdir(parents=True, exist_ok=True)

        await self._rate_limit_wait()

        from google.genai import types

        for attempt in range(config.MAX_RETRIES):
            try:
                # Gemini API呼び出し（画像生成）
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[prompt],
                    config=types.GenerateContentConfig(
                        response_modalities=["TEXT", "IMAGE"]
                    )
                )

                # 画像データ抽出
                for part in response.parts:
                    if part.inline_data is not None:
                        # PIL Image として取得して保存
                        image = part.as_image()
                        image.save(str(output_path))
                        return True, f"Generated: {output_path}"

                return False, f"No image in response for {item.name}"

            except Exception as e:
                error_msg = str(e)
                if attempt < config.MAX_RETRIES - 1:
                    print(f"  [Retry {attempt + 1}/{config.MAX_RETRIES}] {error_msg}")
                    await asyncio.sleep(config.RETRY_DELAY)
                else:
                    return False, f"Failed after {config.MAX_RETRIES} attempts: {error_msg}"

        return False, "Unknown error"

    async def generate_batch(
        self,
        items: list[ItemInfo],
        manifest: dict,
        skip_existing: bool = True,
        dry_run: bool = False
    ) -> tuple[int, int, list[str]]:
        """
        バッチ生成

        Returns:
            (success_count, fail_count, error_messages)
        """
        success_count = 0
        fail_count = 0
        errors = []

        total = len(items)
        for i, item in enumerate(items, 1):
            # 既存チェック
            if skip_existing and is_generated(item.name, item.category, manifest):
                print(f"[{i}/{total}] SKIP (exists): {item.name}")
                continue

            print(f"[{i}/{total}] Generating: {item.name}...")
            success, message = await self.generate_single(item, dry_run=dry_run)

            if success:
                print(f"  {message}")
                success_count += 1

                # マニフェスト更新
                if not dry_run:
                    if item.category not in manifest:
                        manifest[item.category] = {}
                    manifest[item.category][item.name] = {
                        "path": str(get_output_path(item.name, item.category).relative_to(config.OUTPUT_DIR)),
                        "generated_at": datetime.now().isoformat(),
                        "subcategory": item.subcategory
                    }
                    save_manifest(manifest)
            else:
                print(f"  ERROR: {message}")
                fail_count += 1
                errors.append(f"{item.name}: {message}")

        return success_count, fail_count, errors


async def generate_category(
    category: str,
    skip_existing: bool = True,
    dry_run: bool = False,
    limit: int | None = None
) -> tuple[int, int]:
    """カテゴリ全体を生成"""
    all_items = extract_all_items()
    if category not in all_items:
        raise ValueError(f"Unknown category: {category}")

    items = all_items[category]
    if limit:
        items = items[:limit]

    print(f"\n=== Generating {category} ({len(items)} items) ===\n")

    manifest = load_manifest()
    generator = ImageGenerator()

    success, fail, errors = await generator.generate_batch(
        items, manifest, skip_existing=skip_existing, dry_run=dry_run
    )

    print(f"\n=== Results: {success} success, {fail} failed ===")
    if errors:
        print("\nErrors:")
        for err in errors:
            print(f"  - {err}")

    return success, fail


async def generate_all(
    skip_existing: bool = True,
    dry_run: bool = False
) -> dict[str, tuple[int, int]]:
    """全カテゴリを生成"""
    results = {}
    for category in config.CATEGORIES:
        success, fail = await generate_category(
            category, skip_existing=skip_existing, dry_run=dry_run
        )
        results[category] = (success, fail)
    return results


async def generate_single_item(
    item_name: str,
    category: str,
    dry_run: bool = False
) -> bool:
    """単一アイテムを生成"""
    all_items = extract_all_items()
    if category not in all_items:
        raise ValueError(f"Unknown category: {category}")

    # アイテムを検索
    item = None
    for i in all_items[category]:
        if i.name == item_name:
            item = i
            break

    if not item:
        raise ValueError(f"Item not found: {item_name} in {category}")

    print(f"\n=== Generating single item: {item_name} ===\n")

    manifest = load_manifest()
    generator = ImageGenerator()

    success, message = await generator.generate_single(item, dry_run=dry_run)
    print(message)

    if success and not dry_run:
        if category not in manifest:
            manifest[category] = {}
        manifest[category][item_name] = {
            "path": str(get_output_path(item_name, category).relative_to(config.OUTPUT_DIR)),
            "generated_at": datetime.now().isoformat(),
            "subcategory": item.subcategory
        }
        save_manifest(manifest)

    return success
