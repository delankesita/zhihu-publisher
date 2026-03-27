# Zhihu Publisher - 知乎文章自动发布工具

自动发布文章到知乎专栏的 Python 工具。

## 功能特点

- ✅ Markdown 自动转换为知乎编辑器格式
- ✅ 图片自动上传到知乎图床
- ✅ 支持设置封面图
- ✅ 支持草稿/直接发布模式
- ✅ 支持选择专栏发布

## 安装

```bash
# 克隆仓库
git clone https://github.com/your-username/zhihu-publisher.git
cd zhihu-publisher

# 安装依赖
pip install -r requirements.txt
```

## 配置

### 获取知乎 Cookie

1. 登录知乎网页版
2. 打开浏览器开发者工具（F12）
3. 切换到 Network 标签
4. 刷新页面，找到任意请求
5. 复制请求头中的 `Cookie` 值

### 创建配置文件

```bash
mkdir -p ~/.config/zhihu-publisher
cat > ~/.config/zhihu-publisher/.env << 'EOF'
ZHIHU_COOKIE=your_cookie_here
EOF
chmod 600 ~/.config/zhihu-publisher/.env
```

## 使用方法

### 命令行

```bash
# 发布文章
python publish.py article.md

# 保存为草稿
python publish.py article.md --draft

# 设置封面图
python publish.py article.md --cover cover.png

# 发布到指定专栏
python publish.py article.md --column "专栏ID"
```

### Python API

```python
from publish import ZhihuPublisher

publisher = ZhihuPublisher(cookie="your_cookie")
result = publisher.publish(
    title="文章标题",
    content="# 正文内容",
    cover_image="cover.png"
)
print(result['url'])
```

## License

MIT
