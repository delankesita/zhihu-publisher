#!/usr/bin/env python3
"""
知乎文章自动发布工具
支持 Markdown 转换、图片上传、自动发布
"""

import os
import re
import json
import argparse
import requests
from pathlib import Path
from typing import Optional, Dict, Any
import base64
import hashlib
import time


class ZhihuPublisher:
    """知乎文章发布器"""
    
    def __init__(self, cookie: str, xsrf_token: str = None):
        """
        初始化发布器
        
        Args:
            cookie: 知乎 Cookie
            xsrf_token: XSRF Token（可从 Cookie 中提取）
        """
        self.cookie = cookie
        self.xsrf_token = xsrf_token or self._extract_xsrf_token(cookie)
        self.base_url = "https://zhuanlan.zhihu.com/api"
        self.headers = {
            "Cookie": cookie,
            "x-xsrftoken": self.xsrf_token,
            "x-zse-83": "3_2.0",
            "Origin": "https://zhuanlan.zhihu.com",
            "Referer": "https://zhuanlan.zhihu.com/write",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _extract_xsrf_token(self, cookie: str) -> str:
        """从 Cookie 中提取 XSRF Token"""
        match = re.search(r'xsrf_token=([^;]+)', cookie)
        if match:
            return match.group(1)
        match = re.search(r'_xsrf=([^;]+)', cookie)
        if match:
            return match.group(1)
        return ""
    
    def upload_image(self, image_path: str) -> str:
        """
        上传图片到知乎图床
        
        Args:
            image_path: 图片路径
            
        Returns:
            图片 URL
        """
        url = f"{self.base_url}/images"
        
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = self.session.post(url, files=files)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('src', '')
        else:
            raise Exception(f"图片上传失败: {response.status_code} - {response.text}")
    
    def markdown_to_html(self, content: str, image_dir: str = None) -> str:
        """
        将 Markdown 转换为知乎支持的 HTML
        
        Args:
            content: Markdown 内容
            image_dir: 图片目录（用于上传本地图片）
            
        Returns:
            HTML 内容
        """
        # 处理标题
        content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
        content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
        
        # 处理粗体和斜体
        content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
        content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)
        
        # 处理链接
        content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', content)
        
        # 处理代码块
        content = re.sub(r'```(\w*)\n(.*?)```', r'<pre><code class="\1">\2</code></pre>', content, flags=re.DOTALL)
        content = re.sub(r'`([^`]+)`', r'<code>\1</code>', content)
        
        # 处理图片
        def replace_image(match):
            alt_text = match.group(1)
            img_path = match.group(2)
            
            # 如果是本地图片，上传到知乎
            if not img_path.startswith(('http://', 'https://')):
                if image_dir:
                    full_path = os.path.join(image_dir, img_path)
                else:
                    full_path = img_path
                
                if os.path.exists(full_path):
                    try:
                        img_url = self.upload_image(full_path)
                        return f'<img src="{img_url}" alt="{alt_text}">'
                    except Exception as e:
                        print(f"图片上传失败: {e}")
            
            return match.group(0)
        
        content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image, content)
        
        # 处理列表
        content = re.sub(r'^- (.+)$', r'<li>\1</li>', content, flags=re.MULTILINE)
        content = re.sub(r'(<li>.*</li>\n?)+', r'<ul>\g<0></ul>', content)
        
        # 处理段落
        lines = content.split('\n')
        processed_lines = []
        in_block = False
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('<h1', '<h2', '<h3', '<ul', '<ol', '<pre', '<img', '<li')):
                in_block = True
                processed_lines.append(line)
            elif stripped.endswith(('</h1>', '</h2>', '</h3>', '</ul>', '</ol>', '</pre>', '</li>')):
                in_block = False
                processed_lines.append(line)
            elif stripped == '':
                processed_lines.append('')
            elif not in_block:
                processed_lines.append(f'<p>{stripped}</p>')
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def publish(
        self,
        title: str,
        content: str,
        cover_image: str = None,
        column_id: str = None,
        draft: bool = False,
        can_comment: bool = True
    ) -> Dict[str, Any]:
        """
        发布文章到知乎
        
        Args:
            title: 文章标题
            content: 文章内容（Markdown 或 HTML）
            cover_image: 封面图片路径
            column_id: 专栏 ID
            draft: 是否保存为草稿
            can_comment: 是否允许评论
            
        Returns:
            发布结果
        """
        url = f"{self.base_url}/articles"
        
        # 转换 Markdown 为 HTML
        if not content.startswith('<'):
            content = self.markdown_to_html(content)
        
        # 上传封面图
        image_url = None
        if cover_image and os.path.exists(cover_image):
            image_url = self.upload_image(cover_image)
        
        data = {
            "title": title,
            "content": content,
            "draft": draft,
            "can_comment": can_comment,
        }
        
        if image_url:
            data["image_url"] = image_url
        
        if column_id:
            data["column"] = column_id
        
        response = self.session.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "id": result.get("id"),
                "url": f"https://zhuanlan.zhihu.com/p/{result.get('id')}",
                "title": title
            }
        else:
            return {
                "success": False,
                "error": f"发布失败: {response.status_code} - {response.text}"
            }
    
    def get_columns(self) -> list:
        """获取用户的专栏列表"""
        url = "https://www.zhihu.com/api/me/columns"
        response = self.session.get(url)
        
        if response.status_code == 200:
            return response.json().get("data", [])
        return []


def load_config() -> Dict[str, str]:
    """加载配置文件"""
    config_paths = [
        Path.home() / ".config" / "zhihu-publisher" / ".env",
        Path.cwd() / ".env",
    ]
    
    for path in config_paths:
        if path.exists():
            config = {}
            with open(path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip().strip('"').strip("'")
            return config
    return {}


def main():
    parser = argparse.ArgumentParser(description="知乎文章发布工具")
    parser.add_argument("article", help="文章文件路径（Markdown 格式）")
    parser.add_argument("--title", help="文章标题（默认从文件第一行提取）")
    parser.add_argument("--cover", help="封面图片路径")
    parser.add_argument("--column", help="专栏 ID")
    parser.add_argument("--draft", action="store_true", help="保存为草稿")
    parser.add_argument("--cookie", help="知乎 Cookie（或设置 ZHIHU_COOKIE 环境变量）")
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config()
    
    # 获取 Cookie
    cookie = args.cookie or os.environ.get("ZHIHU_COOKIE") or config.get("ZHIHU_COOKIE")
    if not cookie:
        print("错误: 请设置 ZHIHU_COOKIE 环境变量或使用 --cookie 参数")
        return 1
    
    # 读取文章
    article_path = Path(args.article)
    if not article_path.exists():
        print(f"错误: 文件不存在: {article_path}")
        return 1
    
    content = article_path.read_text(encoding='utf-8')
    
    # 提取标题
    title = args.title
    if not title:
        first_line = content.split('\n')[0]
        title = re.sub(r'^#+\s*', '', first_line).strip()
    
    # 发布文章
    publisher = ZhihuPublisher(cookie=cookie)
    
    print(f"正在发布文章: {title}")
    
    result = publisher.publish(
        title=title,
        content=content,
        cover_image=args.cover,
        column_id=args.column,
        draft=args.draft
    )
    
    if result["success"]:
        print(f"✓ 发布成功!")
        print(f"  文章链接: {result['url']}")
        return 0
    else:
        print(f"✗ {result['error']}")
        return 1


if __name__ == "__main__":
    exit(main())
