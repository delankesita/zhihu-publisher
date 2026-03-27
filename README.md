# Zhihu Publisher - 知乎文章自动发布工具

自动发布文章到知乎专栏，支持从微信公众号同步。

## 功能特点

- ✅ Markdown 自动转换为知乎格式
- ✅ 图片自动上传到知乎图床
- ✅ 支持从微信公众号文章同步
- ✅ 支持草稿/直接发布模式

## 安装

```bash
pip install -r requirements.txt
```

## 配置

1. 登录知乎网页版
2. F12 打开开发者工具 → Network → 复制 Cookie
3. 创建配置文件：

```bash
mkdir -p ~/.config/zhihu-publisher
echo 'ZHIHU_COOKIE=your_cookie_here' > ~/.config/zhihu-publisher/.env
```

## 使用

```bash
# 发布文章
python publish.py article.md

# 保存草稿
python publish.py article.md --draft

# 设置封面
python publish.py article.md --cover cover.png
```

## 整合微信公众号

配合 `wewrite` 技能使用：

```bash
# 1. 用 wewrite 写公众号文章
# 2. 同一篇文章发布到知乎
python publish.py /path/to/wewrite/output/article.md
```

## License

MIT
