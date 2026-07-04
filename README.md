# 客服培训机器人

基于 Claude API 的智能客服培训系统，参考飞智科技 Agent 开发思路。

## 功能特性

- 💬 **自由问答** - 基于产品知识的智能问答
- 🎯 **场景模拟** - 预设客服场景演练
- 🎭 **角色扮演** - AI 扮演客户进行对话练习
- 📚 **知识库管理** - 支持 Markdown 格式的产品知识

## 技术栈

- **前端**: HTML + CSS + JavaScript
- **后端**: Python + FastAPI
- **AI**: Claude API (火山引擎)

## 项目结构

```
ai-1/
├── README.md              # 本文件
├── 项目规划.md            # 项目规划文档
├── 需求文档.md            # 详细需求文档
├── CLAUDE.md              # Claude Code 指导
├── requirements.txt       # Python 依赖
├── .env.example           # 配置示例
├── knowledge/             # 知识库目录
│   └── 产品知识库.md      # 飞智手柄产品知识
└── src/
    ├── main.py            # FastAPI 主入口
    ├── api_client.py      # Claude API 封装
    ├── knowledge.py       # 知识库管理
    ├── chat_manager.py    # 对话会话管理
    ├── prompts.py         # Prompt 模板
    └── templates/
        └── index.html     # 前端页面
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

Claude Code 会自动使用 `settings.json` 中的配置，无需额外设置。

如需手动配置，复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
# 编辑 .env 文件
```

### 3. 运行项目

```bash
python src/main.py
```

### 4. 访问应用

打开浏览器访问：http://localhost:8000

## API 接口

- `GET /` - 主页
- `POST /api/session` - 创建会话
- `POST /api/chat` - 发送消息
- `GET /api/knowledge` - 获取知识库
- `GET /api/scenarios` - 获取场景列表
- `POST /api/knowledge/reload` - 重新加载知识库
- `GET /api/health` - 健康检查

## 版本规划

- **版本一（当前）**: 基础原型 - 自由问答 + 场景模拟
- **版本二**: 完整功能版 - 测评系统 + 进度追踪
- **版本三**: 企业级版 - 多人管理 + 数据分析

## 许可证

MIT
