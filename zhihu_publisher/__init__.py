"""
Zhihu Publisher - 知乎文章自动发布工具

Usage:
    from zhihu_publisher import ZhihuPublisher, fetch_hotspots, auto_publish
    
    # 发布文章
    publisher = ZhihuPublisher(cookie="your_cookie")
    result = publisher.publish("标题", "# 内容")
    
    # 抓热点
    hotspots = fetch_hotspots(limit=10)
    
    # 自动写作发布
    result = auto_publish(topic="AI大模型")
"""

from .publisher import (
    ZhihuPublisher,
    ZhihuError,
    load_config,
    publish_article,
)

from .hotspots import (
    HotspotFetcher,
    fetch_hotspots,
    get_trending_topics,
)

from .auto_writer import auto_publish

__version__ = "2.0.0"
__author__ = "delankesita"
__all__ = [
    # Publisher
    "ZhihuPublisher",
    "ZhihuError",
    "load_config",
    "publish_article",
    
    # Hotspots
    "HotspotFetcher",
    "fetch_hotspots",
    "get_trending_topics",
    
    # Auto Writer
    "auto_publish",
]
