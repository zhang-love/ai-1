# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**项目名称：** 产品客服培训机器人
**项目描述：** 基于 Claude API 的智能客服培训系统，帮助新客服快速掌握产品知识和服务技巧。

## Project Status

正在开发版本一：基础原型（MVP）

## Project Structure

```
ai-1/
├── README.md              # 项目说明
├── 项目规划.md            # 项目规划文档
├── 需求文档.md            # 详细需求文档（含代码实现要点）
├── CLAUDE.md              # 本文件
├── knowledge/             # 知识库目录
│   └── 产品知识库.md      # 飞智手柄产品知识
└── src/                   # 源代码
    ├── main.py            # FastAPI 主入口
    ├── api_client.py      # Claude API 封装
    ├── knowledge.py       # 知识库管理
    ├── chat_manager.py    # 对话会话管理
    ├── prompts.py         # Prompt 模板
    ├── templates/
    │   └── index.html     # 前端页面
    └── static/            # 静态资源
├── requirements.txt       # Python 依赖
└── .env.example           # 配置示例
```

## Tech Stack

- **前端：** HTML + CSS + JavaScript
- **后端：** Python + FastAPI
- **AI API：** 火山引擎 Claude API（已在 settings.json 配置）
- **存储：** 本地 JSON 文件

## Key Implementation Points

### 1. 环境变量读取
Claude Code 会自动将 settings.json 中的 `env` 配置注入到运行环境，Python 使用 `os.getenv()` 读取。

### 2. API 客户端
使用官方 `anthropic` Python SDK，配置 `base_url` 和 `timeout`。

### 3. 知识库
读取 knowledge/ 目录下的 Markdown 文件，支持多文件合并。

### 4. 会话管理
每个用户独立会话，历史记录限制条数避免上下文过长。

## Development Guidelines

1. 先实现 MVP 版本，再逐步完善
2. 保持代码简洁，易于理解和扩展
3. 使用中文注释和文档
4. 优先实现核心功能
5. 按照需求文档中的代码示例进行开发

## API Configuration

使用火山引擎的 Claude API，配置在用户的 settings.json 中：
- ANTHROPIC_BASE_URL: https://ark.cn-beijing.volces.com/api/coding
- 模型: claude-opus-4-8-1m

## Current Phase

**Phase 1: 基础原型开发**
- [x] 创建项目文档
- [ ] 搭建项目结构
- [ ] 实现基础对话功能
- [ ] 集成知识库
- [ ] 测试验证

