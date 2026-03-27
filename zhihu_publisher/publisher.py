"""
知乎文章自动发布工具
支持 Markdown 转换、图片上传、自动发布
"""

import os
import re
import json
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from functools import wraps

import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def retry(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (backoff ** attempt)
                        logger.warning(
                            f"Attempt {attempt + 1} failed: {e}. "
                            f"Retrying in {wait_time:.1f}s..."
                        )
                        time.sleep(wait_time)
            raise last_exception
        return wrapper
    return decorator


class ZhihuError(Exception):
    """知乎 API 错误"""
    def __init__(self, message: str, code: int = None, response: dict = None):
        self.message = message
        self.code = code
        self.response = response
        super().__init__(self.message)


class ZhihuPublisher:
    """知乎文章发布器"""
    
    API_BASE = "https://zhuanlan.zhihu.com/api"
    
    def __init__(
        self,
        cookie: str = None,
        xsrf_token: str = None,
        timeout: int = 30
    ):
        """
        初始化发布器
        
        Args:
            cookie: 知乎 Cookie（可从环境变量 ZHIHU_COOKIE 获取）
            xsrf_token: XSRF Token（可从 Cookie 中自动提取）
            timeout: 请求超时时间（秒）
        """
        self.cookie = cookie or os.environ.get("ZHIHU_COOKIE", "")
        if not self.cookie:
            raise ZhihuError("请设置 ZHIHU_COOKIE 环境变量或传入 cookie 参数")
        
        self.xsrf_token = xsrf_token or self._extract_xsrf_token(self.cookie)
        self.timeout = timeout
        
        self.session = requests.Session()
        self.session.headers.update({
            "Cookie": self.cookie,
            "x-xsrftoken": self.xsrf_token,
            "x-zse-83": "3_2.0",
            "Origin": "https://zhuanlan.zhihu.com",
            "Referer": "https://zhuanlan.zhihu.com/write",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
        })
        
        logger.info("ZhihuPublisher 初始化成功")
    
    def _extract_xsrf_token(self, cookie: str) -> str:
        """从 Cookie 中提取 XSRF Token"""
        for pattern in [r'xsrf_token=([^;]+)', r'_xsrf=([^;]+)', r'XSRF-TOKEN=([^;]+)']:
            match = re.search(pattern, cookie)
            if match:
                return match.group(1)
        logger.warning("无法从 Cookie 中提取 XSRF Token，可能导致请求失败")
        return ""
    
    @retry(max_retries=3, delay=1.0)
    def _request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """发送请求"""
        kwargs.setdefault("timeout", self.timeout)
        
        response = self.session.request(method, url, **kwargs)
        
        if response.status_code == 401:
            raise ZhihuError("认证失败，请检查 Cookie 是否有效", 401)
        elif response.status_code == 403:
            raise ZhihuError("请求被拒绝，可能触发反爬机制", 403)
        elif response.status_code == 429:
            raise ZhihuError("请求过于频繁，请稍后重试", 429)
        elif response.status_code >= 500:
            raise ZhihuError(f"服务器错误: {response.status_code}", response.status_code)
        
        try:
            return response.json()
        except json.JSONDecodeError:
            raise ZhihuError(f"响应解析失败: {response.text[:200]}")
    
    @retry(max_retries=3, delay=2.0)
    def upload_image(self, image_path: str) -> str:
        """
        上传图片到知乎图床
        
        Args:
            image_path: 图片路径
            
        Returns:
            图片 URL
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise ZhihuError(f"图片不存在: {image_path}")
        
        # 检查文件大小（知乎限制 5MB）
        file_size = image_path.stat().st_size
        if file_size > 5 * 1024 * 1024:
            raise ZhihuError(f"图片过大（{file_size / 1024 / 1024:.1f}MB），超过 5MB 限制")
        
        logger.info(f"正在上传图片: {image_path.name}")
        
        url = f"{self.API_BASE}/images"
        with open(image_path, 'rb') as f:
            files = {'image': (image_path.name, f, 'image/png')}
            headers = self.session.headers.copy()
            headers.pop("Content-Type", None)  # 让 requests 自动设置
            
            response = self.session.post(url, files=files, headers=headers, timeout=self.timeout)
        
        if response.status_code == 200:
            data = response.json()
            image_url = data.get('src', '')
            logger.info(f"图片上传成功: {image_url}")
            return image_url
        else:
            raise ZhihuError(f"图片上传失败: {response.status_code} - {response.text[:200]}")
    
    def markdown_to_html(
        self,
        content: str,
        image_dir: str = None,
        upload_images: bool = True
    ) -> str:
        """
        将 Markdown 转换为知乎支持的 HTML
        
        Args:
            content: Markdown 内容
            image_dir: 图片目录（用于上传本地图片）
            upload_images: 是否上传本地图片
            
        Returns:
            HTML 内容
        """
        # 处理代码块（优先处理，避免被其他规则干扰）
        content = re.sub(
            r'```(\w*)\n(.*?)```',
            r'<pre><code class="\1">\2</code></pre>',
            content,
            flags=re.DOTALL
        )
        content = re.sub(r'`([^`]+)`', r'<code>\1</code>', content)
        
        # 处理标题
        content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
        content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
        
        # 处理粗体和斜体
        content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
        content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)
        
        # 处理链接
        content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', content)
        
        # 处理图片
        def replace_image(match):
            alt_text = match.group(1)
            img_path = match.group(2)
            
            if not img_path.startswith(('http://', 'https://')):
                if upload_images:
                    # 本地图片，上传到知乎
                    if image_dir:
                        full_path = Path(image_dir) / img_path
                    else:
                        full_path = Path(img_path)
                    
                    if full_path.exists():
                        try:
                            img_url = self.upload_image(str(full_path))
                            return f'<img src="{img_url}" alt="{alt_text}">'
                        except Exception as e:
                            logger.warning(f"图片上传失败: {e}")
            
            return match.group(0)
        
        content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image, content)
        
        # 处理列表
        content = re.sub(r'^- (.+)$', r'<li>\1</li>', content, flags=re.MULTILINE)
        content = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', content, flags=re.MULTILINE)
        
        # 包装列表
        def wrap_lists(text):
            lines = text.split('\n')
            result = []
            in_list = False
            
            for line in lines:
                if '<li>' in line:
                    if not in_list:
                        result.append('<ul>')
                        in_list = True
                    result.append(line)
                else:
                    if in_list:
                        result.append('</ul>')
                        in_list = False
                    result.append(line)
            
            if in_list:
                result.append('</ul>')
            
            return '\n'.join(result)
        
        content = wrap_lists(content)
        
        # 处理段落
        lines = content.split('\n')
        processed_lines = []
        in_block = False
        
        for line in lines:
            stripped = line.strip()
            
            # 检查是否是块级元素
            if stripped.startswith(('<h1', '<h2', '<h3', '<ul', '<ol', '<pre', '<img', '<li', '<p')):
                in_block = True
                processed_lines.append(line)
            elif stripped.endswith(('</h1>', '</h2>', '</h3>', '</ul>', '</ol>', '</pre>', '</li>', '</p>')):
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
        can_comment: bool = True,
        topics: List[str] = None
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
            topics: 文章话题标签
            
        Returns:
            发布结果
        """
        logger.info(f"正在发布文章: {title}")
        
        # 转换 Markdown 为 HTML
        if not content.strip().startswith('<'):
            content = self.markdown_to_html(content)
        
        # 上传封面图
        image_url = None
        if cover_image and Path(cover_image).exists():
            try:
                image_url = self.upload_image(cover_image)
            except Exception as e:
                logger.warning(f"封面上传失败: {e}")
        
        # 构建请求数据
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
        
        if topics:
            data["topics"] = topics
        
        # 发送请求
        url = f"{self.API_BASE}/articles"
        result = self._request("POST", url, json=data)
        
        if "id" in result:
            article_id = result["id"]
            article_url = f"https://zhuanlan.zhihu.com/p/{article_id}"
            logger.info(f"文章发布成功: {article_url}")
            
            return {
                "success": True,
                "id": article_id,
                "url": article_url,
                "title": title,
                "draft": draft
            }
        else:
            error_msg = result.get("error", {}).get("message", str(result))
            raise ZhihuError(f"发布失败: {error_msg}", response=result)
    
    def get_columns(self) -> List[Dict]:
        """获取用户的专栏列表"""
        url = "https://www.zhihu.com/api/me/columns"
        result = self._request("GET", url)
        return result.get("data", [])
    
    def get_article(self, article_id: str) -> Dict:
        """获取文章详情"""
        url = f"{self.API_BASE}/articles/{article_id}"
        return self._request("GET", url)
    
    def update_article(
        self,
        article_id: str,
        title: str = None,
        content: str = None,
        **kwargs
    ) -> Dict:
        """更新文章"""
        url = f"{self.API_BASE}/articles/{article_id}"
        
        data = {}
        if title:
            data["title"] = title
        if content:
            data["content"] = self.markdown_to_html(content) if not content.startswith('<') else content
        data.update(kwargs)
        
        return self._request("PATCH", url, json=data)
    
    def delete_article(self, article_id: str) -> bool:
        """删除文章"""
        url = f"{self.API_BASE}/articles/{article_id}"
        try:
            self._request("DELETE", url)
            logger.info(f"文章已删除: {article_id}")
            return True
        except Exception as e:
            logger.error(f"删除失败: {e}")
            return False


def load_config() -> Dict[str, str]:
    """加载配置文件"""
    config_paths = [
        Path.home() / ".config" / "zhihu-publisher" / ".env",
        Path.home() / ".config" / "zhihu-publisher" / "config.yaml",
        Path.cwd() / ".env",
        Path.cwd() / "config.yaml",
    ]
    
    config = {}
    
    for path in config_paths:
        if path.exists():
            logger.debug(f"加载配置文件: {path}")
            
            if path.suffix == ".yaml":
                try:
                    import yaml
                    with open(path, 'r', encoding='utf-8') as f:
                        yaml_config = yaml.safe_load(f)
                        if yaml_config:
                            # 展开嵌套配置
                            for key, value in yaml_config.get("zhihu", {}).items():
                                config[f"zhihu_{key}"] = value
                except ImportError:
                    pass
            else:
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            config[key.strip()] = value.strip().strip('"').strip("'")
    
    # 展开环境变量
    for key, value in config.items():
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            config[key] = os.environ.get(env_var, "")
    
    return config


# 便捷函数
def publish_article(
    title: str,
    content: str,
    cookie: str = None,
    **kwargs
) -> Dict[str, Any]:
    """发布文章的便捷函数"""
    publisher = ZhihuPublisher(cookie=cookie)
    return publisher.publish(title, content, **kwargs)
