# 客服培训机器人

基于 Claude API 的智能客服培训系统，帮助新客服快速掌握产品知识和服务技巧。

## ✨ 功能特性

- 💬 **流式对话** - AI 回复逐字显示，实时交互
- 📚 **知识库问答** - 基于产品知识的智能回答
- ⚡ **快捷问题** - 预设常见问题，快速开始
- 🎯 **精美界面** - 简洁优雅的聊天体验

## 🛠️ 技术栈

- **前端**: HTML + CSS + JavaScript
- **后端**: Python + FastAPI
- **AI API**: 火山引擎 Claude API
- **流式协议**: Server-Sent Events (SSE)

## 📁 项目结构

```
ai-1/
├── README.md              # 项目说明
├── requirements.txt       # Python 依赖
├── .env.example           # 配置示例
├── .env                   # 实际配置（不提交到 git）
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

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制配置示例并填写实际 API 密钥：

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 ANTHROPIC_AUTH_TOKEN
```

### 3. 运行项目

```bash
python src/main.py
```

或者使用启动脚本（Windows）：

```cmd
start.bat
```

### 4. 访问应用

打开浏览器访问：http://localhost:8000

## 📡 API 接口

| 方法 | 接口 | 说明 |
|------|------|------|
| `GET` | `/` | 主页 |
| `POST` | `/api/session` | 创建会话 |
| `POST` | `/api/chat/stream` | 流式对话 |
| `GET` | `/api/knowledge` | 获取知识库 |
| `GET` | `/api/health` | 健康检查 |

## 📚 知识库

知识库使用 Markdown 格式存放于 `knowledge/` 目录。

当前包含飞智手柄产品知识：
- 产品系列介绍
- 常见问题解答
- 客服话术规范

添加新知识只需在 `knowledge/` 目录下创建新的 `.md` 文件即可。

## 🎯 核心特性

### 流式响应

采用 SSE (Server-Sent Events) 协议，实现真正的流式输出：
- AI 回复逐字显示
- 实时打字机效果
- 更好的用户体验

### 会话管理

- 每个用户独立会话
- 对话历史自动管理
- 上下文记忆功能

### 知识库集成

- 自动加载 Markdown 文件
- 支持多文件合并
- 系统提示词动态注入

## 📝 开发说明

### 运行模式

项目直接使用火山引擎 HTTP 接口，无需额外 SDK。

### 配置说明

配置从 `.env` 文件加载，或者通过环境变量设置。

### 调试方式

访问健康检查接口查看状态：
```
http://localhost:8000/api/health
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
