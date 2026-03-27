---
name: zhihu-publisher
description: |
  【知乎文章自动发布】整合微信公众号内容，自动发布到知乎专栏。
  
  **触发词**：知乎、发布知乎、推送到知乎、知乎专栏、同步知乎
  
  支持功能：从公众号文章同步、Markdown 转换、图片上传、封面设置。
version: 1.0.0
author: OpenClaw
tags: [zhihu, publishing, wechat, sync]
---

# 知乎文章自动发布技能

## 功能特点

- ✅ 从微信公众号同步文章到知乎
- ✅ Markdown 自动转换为知乎格式
- ✅ 图片自动上传到知乎图床
- ✅ 支持草稿/直接发布模式

## 安装依赖

```bash
pip install requests pillow markdown
```

## 配置

```bash
mkdir -p ~/.config/zhihu-publisher
cat > ~/.config/zhihu-publisher/.env << 'EOF'
ZHIHU_COOKIE=your_cookie_here
EOF
chmod 600 ~/.config/zhihu-publisher/.env
```

## 使用方法

### 发布文章

```bash
python /workspace/projects/workspace/skills/zhihu-publisher/publish.py article.md
```

### 从公众号同步

```bash
# 同步 wewrite 输出的文章到知乎
python /workspace/projects/workspace/skills/zhihu-publisher/publish.py /workspace/projects/workspace/skills/wewrite-toolkit/output/yinfu/*.md
```

## 完整流程

1. 在公众号写文章 → wewrite 推送草稿箱
2. 同一篇文章 → zhihu-publisher 发布到知乎
3. 实现一稿多平台发布

## 相关技能

- `wewrite`: 微信公众号文章发布
- `feedgrab`: 多平台内容抓取
