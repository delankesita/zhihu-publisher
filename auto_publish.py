#!/usr/bin/env python3
"""
知乎全自动写作发布工具

整合 wewrite-toolkit 的热点抓取、文章写作能力，一键发布到知乎。

Usage:
    python3 auto_publish.py                    # 自动选题
    python3 auto_publish.py --topic "AI大模型"  # 指定主题
    python3 auto_publish.py --dry-run          # 只生成不发布
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 路径配置
SKILL_DIR = Path(__file__).parent
WEWRITE_DIR = SKILL_DIR.parent / "wewrite-toolkit"
OUTPUT_DIR = SKILL_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def fetch_hotspots(limit: int = 30) -> list[dict]:
    """抓取热点"""
    print("📊 抓取热点...")
    result = subprocess.run(
        ["python3", str(WEWRITE_DIR / "scripts/fetch_hotspots.py"), "--limit", str(limit)],
        capture_output=True,
        text=True,
        cwd=str(WEWRITE_DIR),
    )
    if result.returncode != 0:
        print(f"[error] 抓取热点失败: {result.stderr}")
        return []
    
    data = json.loads(result.stdout)
    print(f"✅ 已抓取 {data['count']} 个热点 (来源: {', '.join(data['sources'])})")
    return data.get("items", [])


def select_topic(hotspots: list[dict], topic_hint: str = None) -> dict:
    """选择主题（简化版：直接返回最热的）"""
    if topic_hint:
        # 匹配用户指定的主题
        for item in hotspots:
            if topic_hint.lower() in item["title"].lower():
                return item
        # 没匹配到，创建自定义主题
        return {
            "title": topic_hint,
            "source": "用户指定",
            "hot": 0,
            "url": "",
            "description": "",
        }
    
    # 返回最热的
    return hotspots[0] if hotspots else {"title": "AI大模型最新进展", "source": "默认"}


def generate_article_prompt(topic: dict) -> str:
    """生成文章写作 prompt（调用 OpenClaw LLM）"""
    return f"""请根据以下热点写一篇知乎文章：

**热点主题**: {topic['title']}
**来源**: {topic.get('source', '综合')}
**热度**: {topic.get('hot', 0)}

**写作要求**:
1. 标题：20-28 字，吸引眼球但不标题党
2. 字数：1500-2500 字
3. 结构：痛点型框架
   - 开头：痛点共鸣
   - H2：问题分析
   - H2：解决方案
   - H2：实操案例
   - 结尾：行动引导
4. 去 AI 痕迹：
   - 禁用：首先、其次、总之、综上所述、作为一个、让我们
   - 加入口语：说实话、讲真、你猜怎么着
   - 段落长短交替，打破匀称节奏
5. 金句：每个 H2 段落结尾放一句精炼总结（≤20 字）
6. 格式：纯 Markdown，H1 写标题

请直接输出文章内容，从 H1 标题开始。"""


def call_llm(prompt: str) -> str:
    """调用 OpenClaw LLM（通过 gateway）"""
    import requests
    
    # 调用本地 gateway
    try:
        resp = requests.post(
            "http://localhost:5000/v1/chat/completions",
            json={
                "model": "default",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
            timeout=120,
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[warn] Gateway 调用失败: {e}")
    
    # Fallback：返回模板
    return """# 一个值得深思的话题

## 这个问题比想象中复杂

说实话，最近看到一个数据挺有意思的。

很多人都在讨论这个话题，但真正理解的人并不多。

**关键在于，这背后的逻辑其实很简单**。

## 为什么大多数人会错过机会

讲真，很多时候我们不是不知道，而是不敢行动。

- 第一个原因：信息差
- 第二个原因：认知差
- 第三个原因：执行力

我觉得最重要的是第三点。

## 如何抓住这个机会

1. **建立信息渠道** - 关注行业动态
2. **深度思考** - 不要人云亦云
3. **快速试错** - 小成本验证

## 写在最后

机会永远留给有准备的人。

你对这个话题怎么看？欢迎评论区讨论。
"""


def generate_cover(topic: dict) -> Path:
    """生成封面图"""
    print("🎨 生成封面图...")
    cover_path = OUTPUT_DIR / "cover.png"
    
    result = subprocess.run(
        [
            "python3",
            str(WEWRITE_DIR / "toolkit/image_gen.py"),
            "--prompt", f"科技感封面图，主题：{topic['title']}",
            "--output", str(cover_path),
            "--size", "cover",
        ],
        capture_output=True,
        text=True,
        cwd=str(WEWRITE_DIR),
    )
    
    if result.returncode == 0 and cover_path.exists():
        print(f"✅ 封面图已生成: {cover_path}")
        return cover_path
    else:
        # 创建默认封面
        print("[warn] 封面生成失败，使用默认封面")
        from PIL import Image, ImageDraw, ImageFont
        
        img = Image.new("RGB", (900, 383), color="#1a1a2e")
        draw = ImageDraw.Draw(img)
        img.save(cover_path)
        return cover_path


def save_article(content: str) -> Path:
    """保存文章"""
    today = datetime.now().strftime("%Y-%m-%d")
    article_path = OUTPUT_DIR / f"{today}-zhihu.md"
    article_path.write_text(content, encoding="utf-8")
    print(f"✅ 文章已保存: {article_path}")
    return article_path


def publish_to_zhihu(article_path: Path, cover_path: Path, dry_run: bool = False) -> bool:
    """发布到知乎"""
    if dry_run:
        print("🔍 [dry-run] 跳过发布")
        return True
    
    print("📤 发布到知乎...")
    result = subprocess.run(
        [
            "python3",
            str(SKILL_DIR / "publish.py"),
            str(article_path),
            "--cover", str(cover_path),
        ],
        capture_output=True,
        text=True,
    )
    
    if result.returncode == 0:
        print("✅ 发布成功")
        return True
    else:
        print(f"[error] 发布失败: {result.stderr}")
        return False


def main():
    parser = argparse.ArgumentParser(description="知乎全自动写作发布")
    parser.add_argument("--topic", type=str, help="指定主题")
    parser.add_argument("--limit", type=int, default=30, help="热点数量")
    parser.add_argument("--dry-run", action="store_true", help="只生成不发布")
    args = parser.parse_args()

    print("=" * 50)
    print("🚀 知乎全自动写作发布")
    print("=" * 50)

    # Step 1: 抓热点
    hotspots = fetch_hotspots(args.limit)
    
    # Step 2: 选主题
    topic = select_topic(hotspots, args.topic)
    print(f"📝 选题: {topic['title']} (来源: {topic['source']})")
    
    # Step 3: 写文章
    print("✍️ 生成文章...")
    prompt = generate_article_prompt(topic)
    content = call_llm(prompt)
    article_path = save_article(content)
    
    # Step 4: 生成封面
    cover_path = generate_cover(topic)
    
    # Step 5: 发布
    publish_to_zhihu(article_path, cover_path, args.dry_run)
    
    print("=" * 50)
    print("✅ 完成！")
    print(f"📄 文章: {article_path}")
    print(f"🖼️ 封面: {cover_path}")


if __name__ == "__main__":
    main()
