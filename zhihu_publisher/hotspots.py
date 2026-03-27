"""
热点抓取模块
从微博、头条、百度等平台抓取热搜话题
"""

import json
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from functools import wraps

import requests

logger = logging.getLogger(__name__)


def retry_on_failure(max_retries: int = 2, delay: float = 1.0):
    """失败重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (attempt + 1))
            logger.warning(f"{func.__name__} 失败: {last_error}")
            return []
        return wrapper
    return decorator


class HotspotFetcher:
    """热点抓取器"""
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
    }
    
    TIMEOUT = 10
    
    def __init__(self, timeout: int = None):
        self.timeout = timeout or self.TIMEOUT
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    
    @retry_on_failure()
    def fetch_weibo(self) -> List[Dict]:
        """抓取微博热搜"""
        resp = self.session.get(
            "https://weibo.com/ajax/side/hotSearch",
            headers={**self.HEADERS, "Referer": "https://weibo.com/"},
            timeout=self.timeout,
        )
        data = resp.json()
        items = []
        
        for entry in data.get("data", {}).get("realtime", []):
            note = entry.get("note", "")
            if not note:
                continue
            items.append({
                "title": note,
                "source": "微博",
                "hot": entry.get("num", 0),
                "url": f"https://s.weibo.com/weibo?q=%23{note}%23",
                "description": entry.get("label_name", ""),
                "rank": len(items) + 1,
            })
        
        logger.info(f"微博热搜: {len(items)} 条")
        return items
    
    @retry_on_failure()
    def fetch_toutiao(self) -> List[Dict]:
        """抓取今日头条热榜"""
        resp = self.session.get(
            "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc",
            headers=self.HEADERS,
            timeout=self.timeout,
        )
        data = resp.json()
        items = []
        
        for entry in data.get("data", []):
            title = entry.get("Title", "")
            if not title:
                continue
            items.append({
                "title": title,
                "source": "今日头条",
                "hot": int(entry.get("HotValue", 0) or 0),
                "url": entry.get("Url", ""),
                "description": "",
                "rank": len(items) + 1,
            })
        
        logger.info(f"今日头条热榜: {len(items)} 条")
        return items
    
    @retry_on_failure()
    def fetch_baidu(self) -> List[Dict]:
        """抓取百度热搜"""
        resp = self.session.get(
            "https://top.baidu.com/api/board?platform=wise&tab=realtime",
            headers=self.HEADERS,
            timeout=self.timeout,
        )
        data = resp.json()
        items = []
        
        for card in data.get("data", {}).get("cards", []):
            top_content = card.get("content", [])
            if not top_content:
                continue
            
            entries = top_content[0].get("content", []) if isinstance(top_content[0], dict) else top_content
            
            for entry in entries:
                word = entry.get("word", "")
                if not word:
                    continue
                items.append({
                    "title": word,
                    "source": "百度",
                    "hot": int(entry.get("hotScore", 0) or 0),
                    "url": entry.get("url", ""),
                    "description": entry.get("desc", ""),
                    "rank": len(items) + 1,
                })
        
        logger.info(f"百度热搜: {len(items)} 条")
        return items
    
    @retry_on_failure()
    def fetch_douyin(self) -> List[Dict]:
        """抓取抖音热点"""
        try:
            # 抖音热点需要特殊处理，这里使用备用 API
            resp = self.session.get(
                "https://api.vvhan.com/api/hotlist/douyinHot",
                headers=self.HEADERS,
                timeout=self.timeout,
            )
            data = resp.json()
            items = []
            
            if data.get("success"):
                for entry in data.get("data", []):
                    items.append({
                        "title": entry.get("title", ""),
                        "source": "抖音",
                        "hot": entry.get("hot_value", 0),
                        "url": entry.get("url", ""),
                        "description": "",
                        "rank": len(items) + 1,
                    })
            
            logger.info(f"抖音热点: {len(items)} 条")
            return items
        except Exception:
            return []
    
    def fetch_all(
        self,
        sources: List[str] = None,
        limit: int = 30,
        deduplicate: bool = True
    ) -> Dict:
        """
        从所有平台抓取热点
        
        Args:
            sources: 数据源列表，默认全部
            limit: 每个平台的最大数量
            deduplicate: 是否去重
            
        Returns:
            热点数据
        """
        sources = sources or ["weibo", "toutiao", "baidu", "douyin"]
        
        fetch_methods = {
            "weibo": self.fetch_weibo,
            "toutiao": self.fetch_toutiao,
            "baidu": self.fetch_baidu,
            "douyin": self.fetch_douyin,
        }
        
        all_items = []
        sources_ok = []
        sources_fail = []
        
        for source in sources:
            if source in fetch_methods:
                try:
                    items = fetch_methods[source]()[:limit]
                    if items:
                        sources_ok.append(source)
                        all_items.extend(items)
                    else:
                        sources_fail.append(source)
                except Exception as e:
                    logger.warning(f"{source} 抓取失败: {e}")
                    sources_fail.append(source)
        
        # 去重
        if deduplicate:
            seen = set()
            unique_items = []
            for item in all_items:
                title = item["title"].strip()
                if title and title not in seen:
                    seen.add(title)
                    unique_items.append(item)
            all_items = unique_items
        
        # 按热度排序
        all_items.sort(key=lambda x: x.get("hot", 0), reverse=True)
        
        tz = timezone(timedelta(hours=8))
        
        return {
            "timestamp": datetime.now(tz).isoformat(),
            "sources": sources_ok,
            "sources_failed": sources_fail,
            "count": len(all_items),
            "items": all_items,
        }


def fetch_hotspots(
    sources: List[str] = None,
    limit: int = 30
) -> Dict:
    """抓取热点的便捷函数"""
    fetcher = HotspotFetcher()
    return fetcher.fetch_all(sources=sources, limit=limit)


def get_trending_topics(limit: int = 10) -> List[str]:
    """获取热门话题标题列表"""
    data = fetch_hotspots(limit=limit)
    return [item["title"] for item in data.get("items", [])[:limit]]


if __name__ == "__main__":
    # 测试
    import sys
    
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        data = fetch_hotspots(limit=limit)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        data = fetch_hotspots(limit=limit)
        print(f"\n📊 热点抓取结果 ({data['count']} 条)")
        print(f"来源: {', '.join(data['sources'])}")
        print("-" * 50)
        
        for i, item in enumerate(data["items"][:limit], 1):
            print(f"{i:2d}. [{item['source']}] {item['title']}")
            if item.get("hot"):
                print(f"    热度: {item['hot']:,}")
