# 贡献指南

感谢你对 Zhihu Publisher 项目的兴趣！欢迎提交 Issue 和 Pull Request。

## 🤔 如何贡献

### 报告 Bug

如果你发现了 Bug，请 [创建 Issue](https://github.com/delankesita/zhihu-publisher/issues/new) 并包含：

1. **问题描述** - 清楚地描述发生了什么问题
2. **复现步骤** - 如何复现这个问题
3. **期望行为** - 你期望发生什么
4. **实际行为** - 实际发生了什么
5. **环境信息** - Python 版本、操作系统等
6. **日志/截图** - 如果有相关的错误日志或截图

### 提出新功能

如果你有新功能的想法：

1. 先 [创建 Issue](https://github.com/delankesita/zhihu-publisher/issues/new) 讨论
2. 说明这个功能的使用场景
3. 等待维护者反馈后再开始实现

### 提交代码

1. **Fork 本仓库**
   ```bash
   git clone https://github.com/你的用户名/zhihu-publisher.git
   cd zhihu-publisher
   ```

2. **创建特性分支**
   ```bash
   git checkout -b feature/AmazingFeature
   ```

3. **安装开发依赖**
   ```bash
   pip install -e ".[dev]"
   ```

4. **编写代码**
   - 遵循 PEP 8 代码规范
   - 添加必要的注释和文档字符串
   - 编写单元测试

5. **运行测试**
   ```bash
   pytest tests/
   ```

6. **代码格式化**
   ```bash
   black zhihu_publisher/
   flake8 zhihu_publisher/
   ```

7. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加了某个功能"
   ```

8. **推送到 GitHub**
   ```bash
   git push origin feature/AmazingFeature
   ```

9. **创建 Pull Request**
   - 前往你的 Fork 页面
   - 点击 "New Pull Request"
   - 填写 PR 描述，说明你的更改

## 📝 代码规范

### Python 代码规范

- 遵循 [PEP 8](https://pep8.org/)
- 使用 4 个空格缩进
- 行长度不超过 100 字符
- 使用有意义的变量名和函数名

### 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/)：

- `feat:` 新功能
- `fix:` Bug 修复
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 其他杂项

示例：
```
feat: 添加定时发布功能
fix: 修复图片上传失败的问题
docs: 更新 README 中的安装说明
```

## 🧪 测试

在提交 PR 之前，请确保：

1. 所有现有测试通过
2. 新功能有对应的测试
3. 测试覆盖率不低于 80%

运行测试：
```bash
pytest tests/ -v --cov=zhihu_publisher
```

## 📚 文档

如果你修改了公共 API，请更新：

- `README.md` 中的使用说明
- 代码中的文档字符串
- 必要时更新 `docs/` 目录下的文档

## ❓ 有问题？

- 查看 [FAQ](https://github.com/delankesita/zhihu-publisher/wiki/FAQ)
- 在 [Discussions](https://github.com/delankesita/zhihu-publisher/discussions) 中提问
- 加入我们的社区

再次感谢你的贡献！🙏
