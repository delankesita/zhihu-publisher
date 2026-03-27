---
name: zhihu-publisher
description: |
  【知乎文章自动发布】自动发布文章到知乎专栏，支持 Markdown 转换、图片上传、封面设置。
  
  **触发词**：知乎、发布知乎、推送到知乎、知乎专栏、知乎文章
  
  支持功能：Markdown 转知乎格式、图片自动上传、封面图设置、草稿/发布模式。
version: 1.0.0
author: OpenClaw
tags: [zhihu, publishing, article, automation]
---

# 知乎文章自动发布技能

## 功能特点

- ✅ Markdown 自动转换为知乎编辑器格式
- ✅ 图片自动上传到知乎图床
- ✅ 支持设置封面图
- ✅ 支持草稿/直接发布模式
- ✅ 支持选择专栏发布

## 安装依赖

```bash
pip install requests pillow markdown
```

## 配置

### 1. 获取知乎 Cookie

1. 登录知乎网页版
2. 打开浏览器开发者工具（F12）
3. 切换到 Network 标签
4. 刷新页面，找到任意请求
5. 复制请求头中的 `Cookie` 值

### 2. 创建配置文件

```bash
mkdir -p ~/.config/zhihu-publisher
cat > ~/.config/zhihu-publisher/.env << 'EOF'
ZHIHU_COOKIE=your_cookie_here
ZHIHU_XSRF_TOKEN=your_xsrf_token_here
EOF
chmod 600 ~/.config/zhihu-publisher/.env
```

## 使用方法

### 命令行发布

```bash
# 发布文章
python /workspace/projects/workspace/skills/zhihu-publisher/publish.py article.md

# 发布到指定专栏
python /workspace/projects/workspace/skills/zhihu-publisher/publish.py article.md --column "专栏ID"

# 保存为草稿
python /workspace/projects/workspace/skills/zhihu-publisher/publish.py article.md --draft

# 设置封面图
python /workspace/projects/workspace/skills/zhihu-publisher/publish.py article.md --cover cover.png
```

### Python 调用

```python
from zhihu_publisher import ZhihuPublisher

# 初始化
publisher = ZhihuPublisher(cookie="your_cookie")

# 发布文章
result = publisher.publish(
    title="文章标题",
    content="# 正文内容\n支持 Markdown 格式",
    cover_image="cover.png",  # 可选
    column_id="专栏ID",  # 可选
    draft=False  # True 保存草稿
)

print(f"文章链接: {result['url']}")
```

## API 说明

### 发布文章

```python
POST https://zhuanlan.zhihu.com/api/articles

Headers:
  Cookie: <your_cookie>
  x-xsrftoken: <xsrf_token>
  Content-Type: application/json

Body:
{
  "title": "文章标题",
  "content": "文章内容（HTML格式）",
  "draft": false,
  "can_comment": true,
  "image_url": "封面图URL（可选）",
  "column": "专栏ID（可选）"
}
```

### 上传图片

```python
POST https://zhuanlan.zhihu.com/api/images

Headers:
  Cookie: <your_cookie>
  x-xsrftoken: <xsrf_token>
  Content-Type: multipart/form-data

Body:
  image: <图片文件>

Response:
{
  "src": "https://picx.zhimg.com/..."
}
```

## Markdown 转换规则

| Markdown | 知乎格式 |
|----------|---------|
| `# 标题` | `<h1>标题</h1>` |
| `## 标题` | `<h2>标题</h2>` |
| `**粗体**` | `<strong>粗体</strong>` |
| `*斜体*` | `<em>斜体</em>` |
| `[链接](url)` | `<a href="url">链接</a>` |
| `![图片](path)` | 上传图片后替换为知乎图片链接 |
| `` `代码` `` | `<code>代码</code>` |
| ```代码块``` | `<pre><code>代码块</code></pre>` |

## 注意事项

1. **Cookie 有效期**：知乎 Cookie 有效期约 30 天，过期需重新获取
2. **图片限制**：单张图片不超过 5MB，支持 jpg/png/gif
3. **发布频率**：建议间隔 10 秒以上，避免触发限制
4. **内容审核**：知乎会自动审核内容，敏感内容可能被拦截

## 错误处理

| 错误码 | 说明 | 解决方案 |
|--------|------|---------|
| 401 | Cookie 过期 | 重新获取 Cookie |
| 403 | 无权限 | 检查专栏权限 |
| 429 | 请求过于频繁 | 降低发布频率 |
| 500 | 服务器错误 | 稍后重试 |

## 示例流程

```bash
# 1. 准备文章（Markdown 格式）
cat > article.md << 'EOF'
# 我的第一篇知乎文章

这是正文内容，支持 **粗体** 和 *斜体*。

## 二级标题

- 列表项 1
- 列表项 2

![示例图片](./image.png)

\`\`\`python
print("Hello, Zhihu!")
\`\`\`
EOF

# 2. 发布文章
python /workspace/projects/workspace/skills/zhihu-publisher/publish.py article.md --cover cover.png

# 3. 查看结果
# 输出: 文章已发布: https://zhuanlan.zhihu.com/p/xxxxxx
```

## 相关链接

- 知乎专栏 API 文档：https://www.zhihu.com/api
- GitHub 仓库：https://github.com/your-username/zhihu-publisher
