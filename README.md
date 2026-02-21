# Enterprise Knowledge Platform (EKP)

<div align="center">

![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11-green.svg)
![Java](https://img.shields.io/badge/Java-21-orange.svg)
![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)

**企业级知识库问答平台 - 基于 RAG 技术的智能问答系统**

[快速开始](#-快速开始) · [系统架构](#-系统架构) · [技术栈](#-技术栈) · [核心功能](#-核心功能)

</div>

---

## 📖 项目简介

Enterprise Knowledge Platform (EKP) 是一个企业级知识库问答平台，基于 RAG（检索增强生成）技术构建。系统支持员工通过自然语言查询内部制度、流程文档，实现智能问答，并提供完整的文档管理、智能对话和 Agent 助手功能。

### 🎯 核心特性

| 特性 | 描述 |
|------|------|
| 📄 **智能文档处理** | 自动解析 PDF、Word、TXT、Markdown 等多种格式，支持文档分块和向量化 |
| 🔍 **语义检索** | 基于 pgvector 的向量相似度搜索，支持语义级别的智能匹配 |
| 💬 **智能问答** | 结合大语言模型生成准确回答，支持本地 Ollama 模型部署 |
| 🤖 **ReAct Agent** | 基于工具调用的智能助手，支持多步推理和复杂任务处理 |
| 🏢 **企业级架构** | 微服务架构设计，支持高可用部署和水平扩展 |
| 🎨 **现代前端** | Next.js 15 + Shadcn/ui 响应式界面，支持流式响应 |
| 🔒 **完全本地化** | 支持完全离线部署，无需第三方 API Key |

---

## 🚀 快速开始

### 环境要求

| 依赖 | 版本要求 | 说明 |
|------|----------|------|
| Docker Desktop | 4.0+ | 容器运行环境 |
| Docker Compose | 2.0+ | 容器编排工具 |
| Node.js | 20+ | 前端开发（可选） |
| Ollama | 最新版 | 本地 LLM 模型（可选） |
| 内存 | 8GB+ | 推荐配置 |

### 一键启动（生产模式）

```bash
# 1. 克隆项目
git clone https://github.com/zhengwenze/Enterprise-Knowledge-Platform.git
cd Enterprise-Knowledge-Platform

# 2. 构建Java项目
cd ekp-biz-service && mvn clean package -DskipTests && cd ..

# 3. 启动所有服务
cd ekp-infra && docker-compose up -d

# 4. 访问前端界面
# http://localhost:3000
```

### 本地 LLM 部署（可选）

如需使用本地模型，请安装 Ollama 并下载模型：

```bash
# 安装 Ollama
# Windows: 从 https://ollama.ai 下载安装

# 下载推荐模型
ollama pull qwen2.5:7b

# 验证安装
ollama list
```

### 开发模式启动

```bash
# 1. 启动后端服务
cd ekp-infra && docker-compose up -d postgres redis kafka ai-service biz-service

# 2. 启动前端开发服务器
cd ekp-web && npm install && npm run dev

# 3. 访问前端界面
# http://localhost:3000
```

### 服务端口

| 服务 | 端口 | 说明 | 访问地址 |
|------|------|------|----------|
| **Web (前端)** | 3000 | Next.js 前端界面 | http://localhost:3000 |
| AI Service | 8000 | FastAPI RAG 服务 | http://localhost:8000/docs |
| Biz Service | 8080 | Spring Boot 业务服务 | http://localhost:8080/health |
| PostgreSQL | 5432 | 数据库 (pgvector) | localhost:5432 |
| Redis | 6379 | 缓存服务 | localhost:6379 |
| Kafka | 9092 | 消息队列 | localhost:9092 |

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           前端层 (Next.js 15)                                │
│                        http://localhost:3000                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   首页      │  │  文档管理   │  │  智能问答   │  │ Agent助手   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            ▼                       ▼                       ▼
┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────────────┐
│     AI Service        │ │     Biz Service       │ │       Kafka          │
│      (Python)         │ │        (Java)         │ │     (消息队列)        │
│                       │ │                       │ │                       │
│  • 文档解析处理       │ │  • 用户管理           │ │  • 事件驱动           │
│  • 文本分块切块       │ │  • 订单管理           │ │  • 异步处理           │
│  • 向量嵌入生成       │ │  • 工单系统           │ │  • 解耦服务           │
│  • 语义检索搜索       │ │  • 业务逻辑           │ │                       │
│  • RAG 智能问答       │ │                       │ │                       │
│  • ReAct Agent        │ │                       │ │                       │
└───────────────────────┘ └───────────────────────┘ └───────────────────────┘
            │                       │                       │
            └───────────────────────┼───────────────────────┘
                                    ▼
            ┌───────────────────────────────────────────────────┐
            │         PostgreSQL (pgvector) + Redis             │
            │                                                   │
            │  • 文档存储        • 向量存储 (pgvector)          │
            │  • 会话管理        • 缓存服务 (Redis)             │
            │  • 用户数据        • 分布式锁                     │
            └───────────────────────────────────────────────────┘
```

### RAG 流程

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   用户问题   │───▶│   问题嵌入   │───▶│   向量检索   │───▶│   构建上下文  │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
                                                                  │
┌──────────────┐    ┌──────────────┐    ┌──────────────┐         │
│   返回答案   │◀───│   来源展示   │◀───│   LLM生成    │◀────────┘
└──────────────┘    └──────────────┘    └──────────────┘
```

---

## 💻 技术栈

### 前端 (ekp-web)

| 技术 | 版本 | 用途 |
|------|------|------|
| [Next.js](https://nextjs.org/) | 15 | React 框架 (App Router) |
| [TypeScript](https://www.typescriptlang.org/) | 5.x | 类型安全 |
| [Tailwind CSS](https://tailwindcss.com/) | 4.x | 样式框架 |
| [Shadcn/ui](https://ui.shadcn.com/) | latest | UI 组件库 |
| [Zustand](https://zustand-demo.pmnd.rs/) | 4.x | 状态管理 |
| [TanStack Query](https://tanstack.com/query) | 5.x | 数据请求管理 |
| [Vercel AI SDK](https://sdk.vercel.ai/) | latest | AI 集成 & 流式响应 |

### AI 服务 (ekp-ai-service)

| 技术 | 版本 | 用途 |
|------|------|------|
| [Python](https://www.python.org/) | 3.11 | 运行环境 |
| [FastAPI](https://fastapi.tiangolo.com/) | 0.109.0 | Web 框架 |
| [Sentence-Transformers](https://www.sbert.net/) | 2.3.1 | 嵌入模型 (BAAI/bge-large-zh) |
| [pgvector](https://github.com/pgvector/pgvector) | 0.2.4 | 向量存储 |
| [Ollama](https://ollama.ai/) | - | 本地 LLM 部署 |
| [Redis](https://redis.io/) | - | 缓存 & 工作记忆 |

### 业务服务 (ekp-biz-service)

| 技术 | 版本 | 用途 |
|------|------|------|
| [Java](https://openjdk.org/) | 21 | 运行环境 |
| [Spring Boot](https://spring.io/projects/spring-boot) | 3.2.2 | Web 框架 |
| [Spring Data JPA](https://spring.io/projects/spring-data-jpa) | 3.2.2 | 数据访问 |
| [Flyway](https://flywaydb.org/) | 10.4.1 | 数据库迁移 |

### 基础设施 (ekp-infra)

| 技术 | 用途 |
|------|------|
| [PostgreSQL](https://www.postgresql.org/) + [pgvector](https://github.com/pgvector/pgvector) | 关系数据库 + 向量存储 |
| [Redis](https://redis.io/) | 缓存、会话管理、分布式锁 |
| [Apache Kafka](https://kafka.apache.org/) | 消息队列、事件驱动 |
| [Docker](https://www.docker.com/) | 容器化部署 |

---

## 📁 项目结构

```
EKP/
├── 📁 ekp-web/                    # 前端 (Next.js 15)
│   ├── 📁 src/
│   │   ├── 📁 app/                # 页面路由 (App Router)
│   │   │   ├── 📄 page.tsx        # 首页
│   │   │   ├── 📄 documents/      # 文档管理页面
│   │   │   ├── 📄 qa/             # 智能问答页面
│   │   │   └── 📄 agent/          # Agent 助手页面
│   │   ├── 📁 components/         # UI 组件
│   │   │   ├── 📁 ui/             # Shadcn/ui 组件
│   │   │   └── 📁 layout/         # 布局组件
│   │   ├── 📁 hooks/              # 自定义 Hooks
│   │   ├── 📁 lib/                # 工具函数
│   │   ├── 📁 providers/          # Context Providers
│   │   ├── 📁 store/              # Zustand 状态管理
│   │   └── 📁 types/              # TypeScript 类型定义
│   ├── 📄 Dockerfile
│   ├── 📄 package.json
│   └── 📄 next.config.ts
│
├── 📁 ekp-ai-service/             # AI 服务 (Python FastAPI)
│   ├── 📁 src/
│   │   ├── 📁 api/v1/             # API 端点
│   │   │   ├── 📄 documents.py    # 文档管理 API
│   │   │   ├── 📄 qa.py           # 问答 API
│   │   │   ├── 📄 agent.py        # Agent API
│   │   │   └── 📄 health.py       # 健康检查
│   │   ├── 📁 models/             # SQLAlchemy 数据模型
│   │   ├── 📁 services/           # 业务服务
│   │   │   ├── 📄 document_processor.py   # 文档处理
│   │   │   ├── 📄 embedding_service.py    # 嵌入生成
│   │   │   ├── 📄 vector_store.py         # 向量存储
│   │   │   ├── 📄 retriever_service.py    # 检索服务
│   │   │   ├── 📄 llm_service.py          # LLM 服务
│   │   │   ├── 📄 cache_service.py        # 缓存服务
│   │   │   └── 📄 memory_service.py       # 记忆服务
│   │   ├── 📁 agents/             # ReAct Agent
│   │   │   ├── 📄 react_agent.py  # Agent 核心实现
│   │   │   └── 📁 tools/          # 工具定义
│   │   ├── 📄 main.py             # FastAPI 应用入口
│   │   ├── 📄 config.py           # 配置管理
│   │   └── 📄 database.py         # 数据库连接
│   ├── 📁 tests/                  # 测试文件
│   ├── 📄 Dockerfile
│   ├── 📄 requirements.txt
│   └── 📄 openapi.yaml
│
├── 📁 ekp-biz-service/            # 业务服务 (Java Spring Boot)
│   ├── 📁 src/main/
│   │   ├── 📁 java/com/ekp/
│   │   │   ├── 📄 EkpBizServiceApplication.java
│   │   │   ├── 📁 controller/     # REST 控制器
│   │   │   └── 📁 entity/         # JPA 实体
│   │   └── 📁 resources/
│   │       ├── 📄 application.yml
│   │       └── 📁 db/migration/   # Flyway 迁移脚本
│   ├── 📄 Dockerfile
│   └── 📄 pom.xml
│
├── 📁 ekp-infra/                  # 基础设施
│   ├── 📄 docker-compose.yml      # 容器编排配置
│   ├── 📁 init-db/                # 数据库初始化脚本
│   ├── 📄 up-dev.sh               # 开发环境启动脚本
│   ├── 📄 down-dev.sh             # 开发环境停止脚本
│   ├── 📄 architecture.md         # 架构文档
│   ├── 📄 WEEK1_SUMMARY.md        # 周报
│   └── 📄 WEEK2_SUMMARY.md
│
├── 📁 docs/                       # 项目文档
│   ├── 📄 PRODUCT_FEATURES.md     # 产品功能文档
│   ├── 📄 AGENT_UPGRADE_ROADMAP.md # Agent 升级路线图
│   ├── 📄 LOCAL_DEPLOYMENT.md     # 本地部署指南
│   └── 📄 RAG_OPTIMIZATION.md     # RAG 优化方案
│
├── 📄 README.md                   # 项目说明
├── 📄 plan.md                     # 开发计划
├── 📄 RAG_README.md               # RAG 技术文档
├── 📄 LICENSE                     # Apache 2.0 许可证
└── 📄 .gitignore
```

---

## ⚡ 核心功能

### 1. 文档管理

- **多格式支持**: PDF、TXT、Markdown 格式
- **自动解析**: 智能文档解析和文本提取
- **智能分块**: 基于语义的文档切块策略
- **状态追踪**: 实时显示文档处理状态（PENDING → PROCESSING → COMPLETED）

### 2. 智能问答 (RAG)

- **语义检索**: 基于向量相似度的智能匹配
- **上下文增强**: 检索结果作为 LLM 上下文
- **来源追溯**: 显示答案来源和相关度评分
- **本地模型**: 支持 Ollama 本地模型，无需联网

### 3. ReAct Agent

- **多步推理**: 基于 ReAct 架构的智能助手
- **工具调用**: 支持文档检索、知识库查询等工具
- **推理可视化**: 展示 Agent 的思考和行动过程
- **工作记忆**: 基于 Redis 的会话记忆管理

### 4. 系统监控

- **健康检查**: 各服务健康状态监控
- **日志管理**: 统一日志格式和收集
- **性能指标**: 请求延迟、缓存命中率等

---

## 📊 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| 文档处理 | ~10 篇/分钟 | 取决于文档大小和复杂度 |
| 向量维度 | 1024 | BAAI/bge-large-zh 模型 |
| 检索延迟 | P95 < 100ms | 向量相似度搜索 |
| 问答延迟 | P95 < 3s | 包含 LLM 生成时间 |
| 嵌入模型 | 1024 维 | 中文优化模型 |

---

## 🔧 配置说明

### 环境变量

```bash
# AI Service 配置
USE_LOCAL_LLM=true                    # 使用本地模型
LOCAL_LLM_URL=http://host.docker.internal:11434  # Ollama 地址
LLM_MODEL=qwen2.5:7b                  # LLM 模型名称
EMBEDDING_MODEL=BAAI/bge-large-zh    # 嵌入模型
EMBEDDING_DIMENSION=1024              # 向量维度

# 数据库配置
DATABASE_URL=postgresql://ekp_user:ekp_password@postgres:5432/ekp_db
REDIS_URL=redis://redis:6379/0

# OpenAI 配置（可选）
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
```

### 支持的 LLM 模型

| 模型 | 参数量 | 推荐显存 | 说明 |
|------|--------|----------|------|
| qwen2.5:7b | 7B | 8GB | 推荐，中文优化 |
| qwen2.5:14b | 14B | 16GB | 更强性能 |
| llama3.1:8b | 8B | 8GB | 英文优化 |
| mistral:7b | 7B | 8GB | 通用模型 |

---

## 📚 API 文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 核心 API 端点

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/v1/documents` | 上传文档 |
| GET | `/api/v1/documents` | 文档列表 |
| DELETE | `/api/v1/documents/{id}` | 删除文档 |
| POST | `/api/v1/qa` | 智能问答 |
| POST | `/api/v1/agent/chat` | Agent 对话 |

---

## 🛠️ 开发进度

### ✅ 已完成

- [x] 项目初始化与架构设计
- [x] Docker Compose 开发环境
- [x] 数据库 Schema 设计 (PostgreSQL + pgvector)
- [x] 文档上传与存储
- [x] 文本切块服务
- [x] PDF 解析流水线
- [x] 嵌入模型集成 (Sentence-Transformers)
- [x] 向量数据库集成 (pgvector)
- [x] 向量检索服务
- [x] LLM 问答集成 (Ollama)
- [x] 前端界面开发 (Next.js 15)
- [x] ReAct Agent 智能助手
- [x] Redis 缓存集成
- [x] 本地化部署支持

### 🚧 进行中

- [ ] 用户认证系统
- [ ] 订单/工单业务
- [ ] Kafka 事件驱动
- [ ] 压力测试与性能优化

### 📋 计划中

- [ ] 多租户支持
- [ ] 权限管理系统
- [ ] 监控告警
- [ ] CI/CD 流水线

---

## 📖 文档

| 文档 | 说明 |
|------|------|
| [产品功能文档](docs/PRODUCT_FEATURES.md) | 详细功能说明 |
| [Agent 升级路线图](docs/AGENT_UPGRADE_ROADMAP.md) | Agent 架构演进 |
| [本地化部署指南](docs/LOCAL_DEPLOYMENT.md) | 离线部署方案 |
| [RAG 优化方案](docs/RAG_OPTIMIZATION.md) | RAG 技术优化 |
| [系统架构设计](ekp-infra/architecture.md) | 架构详细说明 |

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 📄 License

本项目采用 [Apache License 2.0](LICENSE) 开源协议。

---

## 📞 联系方式

- **GitHub**: https://github.com/zhengwenze/Enterprise-Knowledge-Platform
- **Issues**: https://github.com/zhengwenze/Enterprise-Knowledge-Platform/issues

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给一个 Star！**

Made with ❤️ by EKP Team

</div>
