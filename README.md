<div align="center">

# Zhihu Publisher

**知乎文章自动发布工具 | 一键发布文章到知乎专栏**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/delankesita/zhihu-publisher.svg)](https://github.com/delankesita/zhihu-publisher/stargazers)

[English](#english) | [中文文档](#中文文档)

</div>

---

# 中文文档

## ✨ 功能特点

- 🔥 **全自动发布** - 从热点抓取到文章发布，一条命令搞定
- 📝 **Markdown 支持** - 自动转换为知乎格式
- 🖼️ **图片自动上传** - 本地图片自动上传到知乎图床
- 🎨 **AI 配图** - 集成 AI 图片生成
- 📊 **热点抓取** - 微博、头条、百度热搜一键获取
- 🔄 **多平台同步** - 支持同时发布到公众号 + 知乎

## 📦 安装

### 方式一：pip 安装

```bash
pip install zhihu-publisher
```

### 方式二：从源码安装

```bash
git clone https://github.com/delankesita/zhihu-publisher.git
cd zhihu-publisher
pip install -r requirements.txt
```

## ⚙️ 配置

### 1. 获取知乎 Cookie

1. 登录 [知乎](https://www.zhihu.com)
2. 按 F12 打开开发者工具
3. 切换到 Network 标签
4. 刷新页面，找到任意请求
5. 复制请求头中的 `Cookie` 值

### 2. 配置环境变量

```bash
# Linux/macOS
export ZHIHU_COOKIE="你的Cookie"

# Windows
set ZHIHU_COOKIE=你的Cookie
```

或创建配置文件：

```bash
mkdir -p ~/.config/zhihu-publisher
echo 'ZHIHU_COOKIE=你的Cookie' > ~/.config/zhihu-publisher/.env
```

### 3. 图片生成配置（可选）

如需 AI 配图功能，配置火山引擎 API：

```bash
export DOUBAO_API_KEY="你的API密钥"
```

## 🚀 快速开始

### 一键发布（推荐）

```bash
# 自动抓取热点 → 生成文章 → 发布到知乎
python -m zhihu_publisher auto

# 指定主题
python -m zhihu_publisher auto --topic "AI大模型"

# 仅生成，不发布
python -m zhihu_publisher auto --dry-run
```

### 发布现有文章

```bash
# 发布 Markdown 文件
python -m zhihu_publisher publish article.md

# 带封面图发布
python -m zhihu_publisher publish article.md --cover cover.png

# 保存为草稿
python -m zhihu_publisher publish article.md --draft
```

### 抓取热点

```bash
# 抓取 30 个热点
python -m zhihu_publisher hotspots --limit 30

# 保存为 JSON
python -m zhihu_publisher hotspots --output hotspots.json
```

## 📖 使用示例

### 作为 Python 库使用

```python
from zhihu_publisher import ZhihuPublisher

# 初始化
publisher = ZhihuPublisher(cookie="你的Cookie")

# 发布文章
result = publisher.publish(
    title="我的第一篇知乎文章",
    content="# 标题\n\n这是内容...",
    cover_image="cover.png"
)

if result["success"]:
    print(f"发布成功: {result['url']}")
```

### 定时自动发布

```python
import schedule
from zhihu_publisher import auto_publish

def job():
    auto_publish(topic="AI最新动态")

# 每天早上 9 点发布
schedule.every().day.at("09:00").do(job)

while True:
    schedule.run_pending()
```

### 多平台同步

```bash
# 先发布到公众号
cd wewrite-toolkit && python toolkit/cli.py publish article.md --cover cover.png

# 同一篇文章发布到知乎
cd zhihu-publisher && python -m zhihu_publisher publish ../wewrite-toolkit/output/article.md
```

## 🛠️ 命令行参考

### `zhihu-publisher auto`

全自动写作发布。

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--topic` | 指定主题 | 自动选择 |
| `--limit` | 热点数量 | 30 |
| `--dry-run` | 仅生成不发布 | False |
| `--output` | 输出目录 | ./output |

### `zhihu-publisher publish`

发布已有文章。

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `article` | Markdown 文件路径 | 必填 |
| `--title` | 文章标题 | 从文件提取 |
| `--cover` | 封面图片路径 | 无 |
| `--column` | 专栏 ID | 无 |
| `--draft` | 保存为草稿 | False |

### `zhihu-publisher hotspots`

抓取热点话题。

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--limit` | 数量 | 20 |
| `--output` | 输出文件 | stdout |

## 📁 项目结构

```
zhihu-publisher/
├── zhihu_publisher/          # 主包
│   ├── __init__.py
│   ├── publisher.py          # 发布核心逻辑
│   ├── converter.py          # Markdown 转换
│   ├── image_upload.py       # 图片上传
│   ├── hotspots.py           # 热点抓取
│   └── cli.py                # 命令行入口
├── auto_publish.py           # 全自动脚本
├── publish.py                # 独立发布脚本
├── config.example.yaml       # 配置模板
├── requirements.txt          # 依赖
└── README.md                 # 文档
```

## 🔧 高级配置

### 配置文件

创建 `~/.config/zhihu-publisher/config.yaml`：

```yaml
# 知乎配置
zhihu:
  cookie: "${ZHIHU_COOKIE}"
  default_column: ""  # 默认专栏 ID

# 图片生成
image:
  provider: "doubao"  # doubao | openai
  api_key: "${DOUBAO_API_KEY}"

# 热点抓取
hotspots:
  sources:
    - weibo
    - toutiao
    - baidu
  limit: 30

# 发布设置
publish:
  draft: false
  can_comment: true
  auto_cover: true
```

### 环境变量

| 变量 | 说明 | 必需 |
|------|------|------|
| `ZHIHU_COOKIE` | 知乎 Cookie | ✅ |
| `DOUBAO_API_KEY` | 火山引擎 API Key（AI 配图） | ❌ |
| `OPENAI_API_KEY` | OpenAI API Key（AI 配图备选） | ❌ |

## ⚠️ 注意事项

1. **Cookie 安全**：Cookie 包含敏感信息，请勿泄露或上传到公开仓库
2. **发布频率**：建议每天发布不超过 5 篇，避免触发反垃圾机制
3. **内容审核**：知乎有严格的内容审核，请确保文章符合社区规范
4. **图片格式**：支持 jpg、png、gif，单张不超过 5MB

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 License

本项目采用 [MIT](LICENSE) 许可证。

## 🙏 致谢

- [wewrite-toolkit](https://github.com/oaker-io/wewrite) - 公众号写作工具
- 知乎社区

---

# English

## Features

- 🔥 **Fully Automated** - From trending topics to article publishing in one command
- 📝 **Markdown Support** - Auto-convert to Zhihu format
- 🖼️ **Auto Image Upload** - Upload local images to Zhihu CDN
- 🎨 **AI Image Generation** - Integrated AI cover image generation
- 📊 **Trending Topics** - Fetch hot topics from Weibo, Toutiao, Baidu
- 🔄 **Multi-platform Sync** - Publish to WeChat MP + Zhihu simultaneously

## Installation

```bash
pip install zhihu-publisher
```

## Quick Start

```bash
# Set cookie
export ZHIHU_COOKIE="your_cookie_here"

# Auto publish
python -m zhihu_publisher auto

# Publish existing article
python -m zhihu_publisher publish article.md --cover cover.png
```

## License

[MIT](LICENSE)

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给一个 Star！**

Made with ❤️ by [delankesita](https://github.com/delankesita)

</div>
