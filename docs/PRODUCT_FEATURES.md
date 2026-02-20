# Enterprise Knowledge Platform (EKP)

## 产品功能文档 v0.1.0

---

## 一、产品概述

**Enterprise Knowledge Platform (EKP)** 是一个企业级知识库问答平台，基于 RAG（检索增强生成）技术，支持员工通过自然语言查询内部制度、流程文档，实现智能问答。

### 核心价值

- 📄 **智能文档处理**：自动解析PDF、Word、TXT、Markdown等多种格式文档
- 🔍 **语义检索**：基于向量相似度的语义搜索，而非简单关键词匹配
- 💬 **智能问答**：结合大语言模型生成准确、有依据的回答
- 🏢 **企业级架构**：微服务架构，支持高可用、可扩展部署

---

## 二、系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户界面层                                │
│                   (Web / API / CLI)                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API 网关层                                │
│              FastAPI (AI) + Spring Boot (Biz)                   │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  AI Service   │    │  Biz Service  │    │   Message     │
│   (Python)    │    │    (Java)     │    │    Queue      │
│               │    │               │    │   (Kafka)     │
│ • 文档处理    │    │ • 用户管理    │    │               │
│ • 向量检索    │    │ • 订单管理    │    │               │
│ • RAG问答     │    │ • 工单系统    │    │               │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        数据存储层                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ PostgreSQL  │  │    Redis    │  │   Vector    │             │
│  │  (业务数据) │  │   (缓存)    │  │   Store     │             │
│  │             │  │             │  │  (pgvector) │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 三、技术栈

### AI 服务 (ekp-ai-service)

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11 | 运行环境 |
| FastAPI | 0.109.0 | Web框架 |
| SQLAlchemy | 2.0.25 | ORM |
| LangChain | 0.1.0 | LLM编排 |
| Sentence-Transformers | 2.3.1 | 嵌入模型 |
| pgvector | 0.2.4 | 向量存储 |
| PyPDF | 4.0.1 | PDF解析 |

### 业务服务

| 技术 | 版本 | 用途 |
|------|------|------|
| Java | 21 | 运行环境 |
| Spring Boot | 3.2.2 | Web框架 |
| Spring Data JPA | 3.2.2 | 数据访问 |
| Flyway | 10.4.1 | 数据库迁移 |
| PostgreSQL | 42.7.1 | 数据库驱动 |

### 基础设施

| 技术 | 版本 | 用途 |
|------|------|------|
| PostgreSQL | 16 + pgvector | 关系数据库 + 向量存储 |
| Redis | 7-alpine | 缓存 |
| Kafka | 3.7.0 | 消息队列 |
| Docker | - | 容器化 |

---

## 四、核心功能模块

### 4.1 文档管理模块

#### 功能描述
支持企业文档的上传、解析、切块和向量化存储。

#### 支持的文档格式
- PDF (.pdf)
- Word (.docx) - 计划中
- 文本文件 (.txt)
- Markdown (.md)

#### API 接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/documents` | 上传文档 |
| GET | `/api/v1/documents` | 获取文档列表 |
| GET | `/api/v1/documents/{id}` | 获取文档详情 |
| DELETE | `/api/v1/documents/{id}` | 删除文档 |

#### 文档处理流程

```
上传文档 → 格式验证 → 文件存储 → 状态记录
                                    ↓
                              文档解析
                                    ↓
                              文本切块
                                    ↓
                              向量嵌入
                                    ↓
                              向量存储
```

### 4.2 智能问答模块

#### 功能描述
基于RAG技术，实现文档知识库的智能问答。

#### API 接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/qa` | 提交问题 |
| GET | `/api/v1/qa/{session_id}` | 获取问答详情 |
| GET | `/api/v1/qa/history/list` | 获取问答历史 |

#### RAG 流程

```
用户问题 → 问题嵌入 → 向量检索 → 构建上下文 → LLM生成 → 返回答案
                         ↓
                    Top-K 相关文档块
```

#### 请求示例

```json
POST /api/v1/qa
{
    "question": "公司的请假制度是怎样的？",
    "document_ids": [1, 2, 3],
    "top_k": 5
}
```

#### 响应示例

```json
{
    "session_id": 1,
    "question": "公司的请假制度是怎样的？",
    "answer": "根据公司规定，员工享有以下假期类型...",
    "sources": [
        {
            "chunk_id": 101,
            "document_id": 1,
            "document_title": "员工手册.pdf",
            "content": "员工享有年假、病假、事假...",
            "relevance_score": 0.89
        }
    ],
    "model_used": "gpt-3.5-turbo",
    "tokens_used": 256,
    "response_time_ms": 1200
}
```

### 4.3 文本切块服务

#### 功能描述
将长文本按照语义边界切分成适合向量化的文本块。

#### 切块策略
- **固定大小切块**：按字符数切分，支持重叠
- **语义边界优先**：优先在段落、句子边界切分
- **中文优化**：针对中文标点符号优化

#### 配置参数

| 参数 | 默认值 | 描述 |
|------|--------|------|
| chunk_size | 1000 | 每块最大字符数 |
| chunk_overlap | 200 | 块之间的重叠字符数 |

### 4.4 向量检索服务

#### 功能描述
基于pgvector实现高效的向量相似度检索。

#### 检索能力
- **向量相似度搜索**：使用余弦相似度
- **文档过滤**：支持按文档ID过滤
- **混合检索**：向量检索 + 关键词检索（计划中）

#### 性能指标

| 指标 | 目标值 |
|------|--------|
| P95 检索延迟 | < 50ms |
| Top-10 命中率 | > 85% |

---

## 五、数据模型

### 5.1 核心实体

#### 用户 (users)
| 字段 | 类型 | 描述 |
|------|------|------|
| id | BIGINT | 主键 |
| username | VARCHAR(50) | 用户名 |
| email | VARCHAR(100) | 邮箱 |
| role | VARCHAR(20) | 角色 |
| created_at | DATETIME | 创建时间 |

#### 文档 (documents)
| 字段 | 类型 | 描述 |
|------|------|------|
| id | BIGINT | 主键 |
| title | VARCHAR(255) | 文档标题 |
| file_path | VARCHAR(500) | 文件路径 |
| file_size | BIGINT | 文件大小 |
| file_type | VARCHAR(50) | 文件类型 |
| status | VARCHAR(20) | 状态 |
| created_at | DATETIME | 创建时间 |

#### 文档块 (document_chunks)
| 字段 | 类型 | 描述 |
|------|------|------|
| id | BIGINT | 主键 |
| document_id | BIGINT | 文档ID |
| content | TEXT | 文本内容 |
| chunk_index | INTEGER | 块索引 |
| token_count | INTEGER | Token数量 |

#### 文档向量 (document_vectors)
| 字段 | 类型 | 描述 |
|------|------|------|
| id | BIGINT | 主键 |
| document_id | BIGINT | 文档ID |
| chunk_id | BIGINT | 文档块ID |
| content | TEXT | 文本内容 |
| embedding | VECTOR(1024) | 向量嵌入 |

#### 问答会话 (qa_sessions)
| 字段 | 类型 | 描述 |
|------|------|------|
| id | BIGINT | 主键 |
| user_id | BIGINT | 用户ID |
| question | TEXT | 问题 |
| answer | TEXT | 答案 |
| model_used | VARCHAR(100) | 使用的模型 |
| tokens_used | INTEGER | Token消耗 |
| response_time_ms | INTEGER | 响应时间 |

---

## 六、部署指南

### 6.1 环境要求

- Docker Desktop 4.0+
- Docker Compose 2.0+
- 8GB+ 可用内存
- 20GB+ 磁盘空间

### 6.2 快速启动

```bash
# 1. 克隆项目
git clone https://github.com/zhengwenze/Enterprise-Knowledge-Platform.git
cd Enterprise-Knowledge-Platform

# 2. 构建Java项目
cd ekp-biz-service
mvn clean package -DskipTests

# 3. 启动所有服务
cd ../ekp-infra
docker-compose up -d

# 4. 验证服务状态
docker-compose ps
```

### 6.3 服务端口

| 服务 | 端口 | 描述 |
|------|------|------|
| AI Service | 8000 | FastAPI服务 |
| Biz Service | 8080 | Spring Boot服务 |
| PostgreSQL | 5432 | 数据库 |
| Redis | 6379 | 缓存 |
| Kafka | 9092 | 消息队列 |

### 6.4 健康检查

```bash
# AI Service
curl http://localhost:8000/health
# 响应: {"status":"healthy","service":"ai-service"}

# Biz Service
curl http://localhost:8080/health
# 响应: {"status":"UP"}
```

---

## 七、API 文档

### 7.1 AI Service API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: `ekp-ai-service/openapi.yaml`

### 7.2 主要接口

#### 上传文档
```http
POST /api/v1/documents
Content-Type: multipart/form-data

file: <binary>
```

#### 智能问答
```http
POST /api/v1/qa
Content-Type: application/json

{
    "question": "你的问题",
    "top_k": 5
}
```

---

## 八、开发进度

### 已完成 (Week 1-2)

| 阶段 | 任务 | 状态 |
|------|------|------|
| Week 1 | 项目初始化与架构设计 | ✅ |
| Week 1 | 开发环境配置 | ✅ |
| Week 1 | Docker Compose环境 | ✅ |
| Week 1 | 数据库Schema设计 | ✅ |
| Week 1 | OpenAPI规范 | ✅ |
| Week 2 | 文档上传与存储 | ✅ |
| Week 2 | 文本切块服务 | ✅ |
| Week 2 | PDF解析流水线 | ✅ |
| Week 2 | 嵌入模型集成 | ✅ |
| Week 2 | 向量数据库集成 | ✅ |
| Week 2 | 向量检索服务 | ✅ |
| Week 2 | LLM问答集成 | ✅ |

### 计划中 (Week 3-4)

| 阶段 | 任务 | 优先级 |
|------|------|--------|
| Week 3 | 用户认证系统 | 高 |
| Week 3 | 订单/工单业务 | 高 |
| Week 3 | Kafka事件驱动 | 高 |
| Week 3 | Redis缓存集成 | 高 |
| Week 4 | 压力测试 | 高 |
| Week 4 | 性能优化 | 高 |
| Week 4 | 监控告警 | 中 |
| Week 4 | MVP发布 | 高 |

---

## 九、项目统计

| 指标 | 数值 |
|------|------|
| 代码仓库 | 3 |
| 服务数量 | 5 |
| API接口 | 10+ |
| 数据表 | 6 |
| 服务类 | 7 |
| 代码行数 | ~3,000+ |
| 提交次数 | 10+ |

---

## 十、联系方式

- **GitHub**: https://github.com/zhengwenze/Enterprise-Knowledge-Platform
- **License**: Apache License 2.0

---

*文档版本: v0.1.0*
*最后更新: 2026-02-20*
