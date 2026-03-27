---
name: zhihu-auto-publish
description: |
  【知乎全自动写作发布】从热点选题 → 文章生成 → 发布知乎，一条龙全自动。
  
  **触发词**：写知乎、发布知乎、知乎文章、知乎专栏、同步知乎
  
  **⚠️ 重要：必须执行 exec_shell 命令，禁止生成代码**
version: 2.0.0
author: OpenClaw
tags: [zhihu, publishing, automation, wewrite]
---

# 知乎全自动写作发布

## 一键执行

当用户说"写一篇知乎文章"时，直接执行：

```bash
cd /workspace/projects/workspace/skills/zhihu-publisher && python3 auto_publish.py --topic "用户指定的主题（可选）"
```

## 完整流程

### Step 1: 抓热点

```bash
cd /workspace/projects/workspace/skills/wewrite-toolkit && python3 scripts/fetch_hotspots.py --limit 30
```

输出：30 个热点（微博 + 头条 + 百度）

### Step 2: 选主题

从热点中选择与用户领域相关的主题，或用户指定主题。

### Step 3: 写文章

用 wewrite 的写作规范生成文章：
- 1500-2500 字
- 去 AI 痕迹
- 金句 + 案例支撑

### Step 4: 生成封面

```bash
cd /workspace/projects/workspace/skills/wewrite-toolkit && python3 toolkit/image_gen.py --prompt "封面描述" --output /workspace/projects/workspace/skills/zhihu-publisher/output/cover.png --size cover
```

### Step 5: 发布知乎

```bash
cd /workspace/projects/workspace/skills/zhihu-publisher && python3 publish.py output/article.md --cover output/cover.png
```

## 已配置账号

- 知乎专栏：需配置 Cookie（首次使用需登录获取）

## 输出目录

```
/workspace/projects/workspace/skills/zhihu-publisher/output/
├── article.md    # 生成的文章
├── cover.png     # 封面图
└── images/       # 内文配图
```

## 配置知乎 Cookie

```bash
mkdir -p ~/.config/zhihu-publisher
echo 'ZHIHU_COOKIE=your_cookie_here' > ~/.config/zhihu-publisher/.env
```

获取方法：登录知乎 → F12 → Network → 复制 Cookie

## 同时发布公众号 + 知乎

```bash
# 发布到公众号
cd /workspace/projects/workspace/skills/wewrite-toolkit && python3 toolkit/cli.py publish output/yinfu/article.md --cover output/yinfu/cover.png

# 同一篇文章发布到知乎
cd /workspace/projects/workspace/skills/zhihu-publisher && python3 publish.py output/article.md
```
