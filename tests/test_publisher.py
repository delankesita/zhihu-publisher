"""
测试 Publisher 模块
"""

import pytest
from zhihu_publisher.publisher import ZhihuPublisher, ZhihuError


def test_publisher_init_without_cookie():
    """测试没有 Cookie 时初始化失败"""
    with pytest.raises(ZhihuError) as exc_info:
        ZhihuPublisher(cookie="")
    
    assert "Cookie" in str(exc_info.value)


def test_publisher_init_with_cookie():
    """测试有 Cookie 时初始化成功"""
    publisher = ZhihuPublisher(cookie="test_cookie=123")
    assert publisher.cookie == "test_cookie=123"


def test_markdown_to_html():
    """测试 Markdown 转换"""
    publisher = ZhihuPublisher(cookie="test=1")
    
    md = """# 标题

这是正文。

## 二级标题

- 列表项 1
- 列表项 2
"""
    
    html = publisher.markdown_to_html(md, upload_images=False)
    
    assert "<h1>标题</h1>" in html
    assert "<h2>二级标题</h2>" in html
    assert "<ul>" in html
    assert "<li>" in html


def test_retry_decorator():
    """测试重试装饰器"""
    from zhihu_publisher.publisher import retry
    
    call_count = 0
    
    @retry(max_retries=3, delay=0.1)
    def failing_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("Temporary error")
        return "success"
    
    result = failing_function()
    assert result == "success"
    assert call_count == 3
