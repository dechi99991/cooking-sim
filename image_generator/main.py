"""画像生成CLI"""
import argparse
import asyncio
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from image_generator import config
from image_generator.extractor import extract_all_items, get_all_item_count
from image_generator.generator import (
    generate_all,
    generate_category,
    generate_single_item,
    load_manifest
)


def cmd_list(args):
    """アイテム一覧を表示"""
    all_items = extract_all_items()

    if args.category:
        if args.category not in all_items:
            print(f"Error: Unknown category '{args.category}'")
            print(f"Available: {', '.join(config.CATEGORIES)}")
            return 1
        categories = {args.category: all_items[args.category]}
    else:
        categories = all_items

    for category, items in categories.items():
        print(f"\n=== {category} ({len(items)} items) ===")
        for item in items:
            subcategory_str = f" [{item.subcategory}]" if item.subcategory else ""
            print(f"  - {item.name}{subcategory_str}")

    return 0


def cmd_status(args):
    """生成状況を表示"""
    manifest = load_manifest()
    counts = get_all_item_count()

    print("\n=== Generation Status ===\n")
    total_items = 0
    total_generated = 0

    for category in config.CATEGORIES:
        item_count = counts.get(category, 0)
        generated = len(manifest.get(category, {}))
        total_items += item_count
        total_generated += generated
        pct = (generated / item_count * 100) if item_count > 0 else 0
        print(f"  {category}: {generated}/{item_count} ({pct:.1f}%)")

    print(f"\n  Total: {total_generated}/{total_items} ({total_generated/total_items*100:.1f}%)")
    return 0


def cmd_generate(args):
    """画像を生成"""
    if not config.GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY environment variable is not set")
        print("Please set it with: export GEMINI_API_KEY=your_api_key")
        return 1

    async def run():
        if args.item:
            # 単一アイテム生成
            if not args.category:
                print("Error: --category is required when using --item")
                return 1
            success = await generate_single_item(
                args.item, args.category, dry_run=args.dry_run
            )
            return 0 if success else 1

        elif args.category:
            # カテゴリ生成
            success, fail = await generate_category(
                args.category,
                skip_existing=not args.regenerate,
                dry_run=args.dry_run,
                limit=args.limit
            )
            return 0 if fail == 0 else 1

        else:
            # 全生成
            results = await generate_all(
                skip_existing=not args.regenerate,
                dry_run=args.dry_run
            )
            total_fail = sum(fail for _, fail in results.values())
            return 0 if total_fail == 0 else 1

    return asyncio.run(run())


def cmd_new_only(args):
    """未生成アイテムのみリスト表示"""
    manifest = load_manifest()
    all_items = extract_all_items()

    new_items = []
    for category, items in all_items.items():
        for item in items:
            if category not in manifest or item.name not in manifest[category]:
                new_items.append((category, item.name))

    if not new_items:
        print("All items have been generated!")
        return 0

    print(f"\n=== New Items ({len(new_items)}) ===\n")
    current_category = None
    for category, name in new_items:
        if category != current_category:
            print(f"\n[{category}]")
            current_category = category
        print(f"  - {name}")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Gemini APIを使用した32x32ドット絵生成ツール"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # list コマンド
    list_parser = subparsers.add_parser("list", help="アイテム一覧を表示")
    list_parser.add_argument("-c", "--category", help="カテゴリを指定")
    list_parser.set_defaults(func=cmd_list)

    # status コマンド
    status_parser = subparsers.add_parser("status", help="生成状況を表示")
    status_parser.set_defaults(func=cmd_status)

    # generate コマンド
    gen_parser = subparsers.add_parser("generate", help="画像を生成")
    gen_parser.add_argument("-c", "--category", help="カテゴリを指定")
    gen_parser.add_argument("-i", "--item", help="アイテム名を指定")
    gen_parser.add_argument("-n", "--limit", type=int, help="生成数を制限")
    gen_parser.add_argument("--regenerate", action="store_true",
                           help="既存ファイルも再生成")
    gen_parser.add_argument("--dry-run", action="store_true",
                           help="実際には生成せずにプレビュー")
    gen_parser.set_defaults(func=cmd_generate)

    # new-only コマンド
    new_parser = subparsers.add_parser("new-only", help="未生成アイテムを表示")
    new_parser.set_defaults(func=cmd_new_only)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
