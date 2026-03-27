"""
命令行入口
"""

import argparse
import json
import os
import sys
from pathlib import Path

from .publisher import ZhihuPublisher, ZhihuError, load_config
from .hotspots import fetch_hotspots


def cmd_publish(args):
    """发布文章命令"""
    # 加载配置
    config = load_config()
    cookie = args.cookie or os.environ.get("ZHIHU_COOKIE") or config.get("zhihu_cookie") or config.get("ZHIHU_COOKIE")
    
    if not cookie:
        print("❌ 错误: 请设置 ZHIHU_COOKIE 环境变量或使用 --cookie 参数")
        return 1
    
    # 读取文章
    article_path = Path(args.article)
    if not article_path.exists():
        print(f"❌ 错误: 文件不存在: {article_path}")
        return 1
    
    content = article_path.read_text(encoding='utf-8')
    
    # 提取标题
    title = args.title
    if not title:
        first_line = content.split('\n')[0]
        title = first_line.lstrip('#').strip()
    
    # 发布
    try:
        publisher = ZhihuPublisher(cookie=cookie)
        result = publisher.publish(
            title=title,
            content=content,
            cover_image=args.cover,
            column_id=args.column,
            draft=args.draft
        )
        
        print(f"\n✅ 发布成功!")
        print(f"   标题: {result['title']}")
        print(f"   链接: {result['url']}")
        if result.get('draft'):
            print(f"   状态: 草稿")
        
        return 0
    except ZhihuError as e:
        print(f"❌ 发布失败: {e.message}")
        return 1
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1


def cmd_auto(args):
    """自动写作发布命令"""
    from .auto_writer import auto_publish
    
    try:
        result = auto_publish(
            topic=args.topic,
            limit=args.limit,
            dry_run=args.dry_run,
            output_dir=args.output
        )
        
        if result.get("success"):
            print("\n✅ 完成!")
            print(f"   文章: {result.get('article_path')}")
            if not args.dry_run:
                print(f"   链接: {result.get('url')}")
            return 0
        else:
            print(f"\n❌ 失败: {result.get('error')}")
            return 1
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1


def cmd_hotspots(args):
    """抓取热点命令"""
    data = fetch_hotspots(limit=args.limit)
    
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"✅ 已保存到: {output_path}")
    else:
        print(f"\n📊 热点抓取结果 ({data['count']} 条)")
        print(f"来源: {', '.join(data['sources'])}")
        print("-" * 50)
        
        for i, item in enumerate(data["items"][:args.limit], 1):
            hot_str = f" (热度: {item['hot']:,})" if item.get("hot") else ""
            print(f"{i:2d}. [{item['source']}] {item['title']}{hot_str}")
    
    return 0


def cmd_columns(args):
    """获取专栏列表命令"""
    config = load_config()
    cookie = args.cookie or os.environ.get("ZHIHU_COOKIE") or config.get("ZHIHU_COOKIE")
    
    if not cookie:
        print("❌ 错误: 请设置 ZHIHU_COOKIE 环境变量")
        return 1
    
    try:
        publisher = ZhihuPublisher(cookie=cookie)
        columns = publisher.get_columns()
        
        if not columns:
            print("暂无专栏")
            return 0
        
        print("\n📚 你的专栏:")
        print("-" * 50)
        for col in columns:
            print(f"  {col.get('title', '未命名')}")
            print(f"  ID: {col.get('id')}")
            print(f"  文章数: {col.get('articlesCount', 0)}")
            print()
        
        return 0
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        prog="zhihu-publisher",
        description="知乎文章自动发布工具"
    )
    parser.add_argument("--version", action="version", version="%(prog)s 2.0.0")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # publish 命令
    publish_parser = subparsers.add_parser("publish", help="发布文章")
    publish_parser.add_argument("article", help="Markdown 文件路径")
    publish_parser.add_argument("--title", help="文章标题")
    publish_parser.add_argument("--cover", help="封面图片路径")
    publish_parser.add_argument("--column", help="专栏 ID")
    publish_parser.add_argument("--draft", action="store_true", help="保存为草稿")
    publish_parser.add_argument("--cookie", help="知乎 Cookie")
    publish_parser.set_defaults(func=cmd_publish)
    
    # auto 命令
    auto_parser = subparsers.add_parser("auto", help="自动写作发布")
    auto_parser.add_argument("--topic", help="指定主题")
    auto_parser.add_argument("--limit", type=int, default=30, help="热点数量")
    auto_parser.add_argument("--dry-run", action="store_true", help="仅生成不发布")
    auto_parser.add_argument("--output", default="./output", help="输出目录")
    auto_parser.set_defaults(func=cmd_auto)
    
    # hotspots 命令
    hotspots_parser = subparsers.add_parser("hotspots", help="抓取热点")
    hotspots_parser.add_argument("--limit", type=int, default=20, help="热点数量")
    hotspots_parser.add_argument("--output", help="保存为 JSON 文件")
    hotspots_parser.set_defaults(func=cmd_hotspots)
    
    # columns 命令
    columns_parser = subparsers.add_parser("columns", help="获取专栏列表")
    columns_parser.add_argument("--cookie", help="知乎 Cookie")
    columns_parser.set_defaults(func=cmd_columns)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 0
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
