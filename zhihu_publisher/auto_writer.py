"""
自动写作模块
整合热点抓取、AI 写作、自动发布
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from .hotspots import fetch_hotspots
from .publisher import ZhihuPublisher, ZhihuError

logger = logging.getLogger(__name__)

# 默认输出目录
DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent / "output"


def generate_article_prompt(topic: Dict) -> str:
    """生成文章写作 prompt"""
    return f"""请根据以下热点写一篇知乎文章：

**热点主题**: {topic['title']}
**来源**: {topic.get('source', '综合')}
**热度**: {topic.get('hot', 0):,}

**写作要求**:
1. 标题：20-28 字，吸引眼球但不标题党
2. 字数：1500-2500 字
3. 结构：痛点型框架
   - 开头：痛点共鸣（直接描述读者正在经历的问题）
   - H2：问题分析（为什么大多数人会错过）
   - H2：解决方案（核心方法，不超过 3 个要点）
   - H2：实操案例（完整案例走一遍）
   - 结尾：行动引导
4. 去 AI 痕迹：
   - 禁用：首先、其次、总之、综上所述、作为一个、让我们、值得注意的是
   - 加入口语：说实话、讲真、你猜怎么着、我跟你说
   - 段落长短交替，打破匀称节奏
   - 偶尔自嘲或开玩笑
5. 金句：每个 H2 段落结尾放一句精炼总结（≤20 字）
6. 格式：纯 Markdown，H1 写标题

请直接输出文章内容，从 H1 标题开始。"""


def call_llm(prompt: str, timeout: int = 120) -> str:
    """
    调用 LLM 生成文章
    
    优先使用 OpenClaw Gateway，失败则使用模板
    """
    # 方式 1: 调用本地 Gateway
    try:
        import requests
        
        gateway_url = os.environ.get("OPENCLAW_GATEWAY_URL", "http://localhost:5000")
        
        resp = requests.post(
            f"{gateway_url}/v1/chat/completions",
            json={
                "model": "default",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
            timeout=timeout,
        )
        
        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"]
            logger.info("通过 Gateway 生成文章成功")
            return content
    except Exception as e:
        logger.warning(f"Gateway 调用失败: {e}")
    
    # 方式 2: 使用环境变量中的 API
    try:
        import requests
        
        api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("NVIDIA_API_KEY")
        base_url = os.environ.get("OPENAI_BASE_URL") or os.environ.get("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
        
        if api_key:
            resp = requests.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": os.environ.get("MODEL_NAME", "nvidia/llama-3.1-nemotron-70b-instruct"),
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 4000,
                },
                timeout=timeout,
            )
            
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                logger.info("通过 API 生成文章成功")
                return content
    except Exception as e:
        logger.warning(f"API 调用失败: {e}")
    
    # Fallback: 返回模板
    logger.warning("使用模板生成文章")
    return """# 一个值得深思的话题

说实话，最近看到一个数据挺有意思的。

很多人都在讨论这个话题，但真正理解的人并不多。今天就来聊聊我的看法。

## 这个问题比想象中复杂

讲真，很多时候我们不是不知道，而是不敢行动。

为什么会这样？我觉得有三个原因：

- 信息差 - 真正有价值的信息很难获取
- 认知差 - 即使看到了，也不一定能理解
- 执行力差 - 理解了，但迟迟不行动

**最关键的是第三点**。

## 如何抓住机会

1. **建立信息渠道** - 关注行业动态，订阅高质量内容
2. **深度思考** - 不要人云亦云，形成自己的判断
3. **快速试错** - 小成本验证，快速迭代

## 一个真实的案例

我有个朋友，去年开始做副业。一开始也是各种犹豫，后来想通了：与其焦虑，不如行动。

结果呢？半年时间，副业收入已经超过主业了。

**关键在于迈出第一步**。

## 写在最后

机会永远留给有准备的人，但更重要的是：**敢于行动的人**。

你对这个话题怎么看？欢迎评论区讨论。
"""


def generate_cover_image(topic: Dict, output_dir: Path) -> Optional[Path]:
    """生成封面图"""
    cover_path = output_dir / "cover.png"
    
    # 尝试使用 wewrite-toolkit 的图片生成
    try:
        wewrite_path = Path(__file__).parent.parent.parent / "wewrite-toolkit"
        if wewrite_path.exists():
            import subprocess
            
            result = subprocess.run(
                [
                    "python3",
                    str(wewrite_path / "toolkit/image_gen.py"),
                    "--prompt", f"科技感封面图，主题：{topic['title']}",
                    "--output", str(cover_path),
                    "--size", "cover",
                ],
                capture_output=True,
                text=True,
                cwd=str(wewrite_path),
            )
            
            if result.returncode == 0 and cover_path.exists():
                logger.info(f"封面图生成成功: {cover_path}")
                return cover_path
    except Exception as e:
        logger.warning(f"wewrite 图片生成失败: {e}")
    
    # Fallback: 创建简单封面
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        img = Image.new("RGB", (900, 383), color="#1a1a2e")
        draw = ImageDraw.Draw(img)
        
        # 绘制标题
        title = topic["title"][:20]
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 170), title, fill="white", font=font)
        
        img.save(cover_path)
        logger.info(f"创建默认封面: {cover_path}")
        return cover_path
    except Exception as e:
        logger.warning(f"创建封面失败: {e}")
    
    return None


def auto_publish(
    topic: str = None,
    limit: int = 30,
    dry_run: bool = False,
    output_dir: str = None
) -> Dict[str, Any]:
    """
    自动写作发布
    
    Args:
        topic: 指定主题（可选）
        limit: 热点数量
        dry_run: 仅生成不发布
        output_dir: 输出目录
        
    Returns:
        结果字典
    """
    output_dir = Path(output_dir or DEFAULT_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 50)
    print("🚀 知乎全自动写作发布")
    print("=" * 50)
    
    # Step 1: 抓热点
    print("\n📊 抓取热点...")
    hotspots_data = fetch_hotspots(limit=limit)
    hotspots = hotspots_data.get("items", [])
    
    if not hotspots:
        return {"success": False, "error": "未能抓取到热点"}
    
    print(f"✅ 已抓取 {hotspots_data['count']} 个热点 (来源: {', '.join(hotspots_data['sources'])})")
    
    # Step 2: 选主题
    selected_topic = None
    if topic:
        # 用户指定主题
        for item in hotspots:
            if topic.lower() in item["title"].lower():
                selected_topic = item
                break
        
        if not selected_topic:
            selected_topic = {
                "title": topic,
                "source": "用户指定",
                "hot": 0,
            }
    else:
        # 自动选择最热的
        selected_topic = hotspots[0]
    
    print(f"📝 选题: {selected_topic['title']} (来源: {selected_topic['source']})")
    
    # Step 3: 写文章
    print("\n✍️ 生成文章...")
    prompt = generate_article_prompt(selected_topic)
    content = call_llm(prompt)
    
    # 保存文章
    today = datetime.now().strftime("%Y-%m-%d")
    article_path = output_dir / f"{today}-zhihu.md"
    article_path.write_text(content, encoding="utf-8")
    print(f"✅ 文章已保存: {article_path}")
    
    # Step 4: 生成封面
    print("\n🎨 生成封面...")
    cover_path = generate_cover_image(selected_topic, output_dir)
    
    # Step 5: 发布
    if dry_run:
        print("\n🔍 [dry-run] 跳过发布")
        return {
            "success": True,
            "article_path": str(article_path),
            "cover_path": str(cover_path) if cover_path else None,
            "topic": selected_topic,
            "dry_run": True,
        }
    
    print("\n📤 发布到知乎...")
    
    # 检查 Cookie
    from .publisher import load_config
    config = load_config()
    cookie = os.environ.get("ZHIHU_COOKIE") or config.get("ZHIHU_COOKIE")
    
    if not cookie:
        return {
            "success": False,
            "error": "请设置 ZHIHU_COOKIE 环境变量",
            "article_path": str(article_path),
        }
    
    try:
        publisher = ZhihuPublisher(cookie=cookie)
        
        # 提取标题
        title = content.split('\n')[0].lstrip('#').strip()
        
        result = publisher.publish(
            title=title,
            content=content,
            cover_image=str(cover_path) if cover_path else None,
        )
        
        return {
            "success": True,
            "article_path": str(article_path),
            "cover_path": str(cover_path) if cover_path else None,
            "topic": selected_topic,
            "url": result.get("url"),
            "id": result.get("id"),
        }
    except ZhihuError as e:
        return {
            "success": False,
            "error": e.message,
            "article_path": str(article_path),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "article_path": str(article_path),
        }


if __name__ == "__main__":
    import sys
    
    result = auto_publish(
        topic=sys.argv[1] if len(sys.argv) > 1 else None,
        dry_run="--dry-run" in sys.argv,
    )
    
    if result.get("success"):
        print("\n✅ 完成!")
        print(f"📄 文章: {result.get('article_path')}")
        if result.get("url"):
            print(f"🔗 链接: {result['url']}")
    else:
        print(f"\n❌ 失败: {result.get('error')}")
        sys.exit(1)
