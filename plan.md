**Enterprise Knowledge Platform 企业知识库 + 订单工单一体化平台**计划框架，计划中不写具体代码，只做“任务粒度 + GitHub 活跃 + 简历展示”层面优化

1. 原计划的主要问题
阶段划分偏“跑流水账”，缺少“可交付里程碑”
很多天是“写接口、写配置、写测试”，但缺少明确的“可演示成果节点”，招聘方一眼看不出你做到什么程度。
项目范围偏“教学 demo”，而不是“企业级系统”
真正的企业 RAG 系统，难点在：
多种文档格式 & 复杂结构的切块策略
混合检索 + 重排序 + 多路召回
可观测性：trace、监控、缓存命中率、检索质量评估
原计划对这些生产关键点涉及较少。
GitHub 活跃度和简历展示点不够突出
没有刻意设计“能写进简历的数字与亮点”，比如：
多少文档 / 多少向量 / QPS / 延迟 / 检索准确率 / 成本优化比例
这些才是面试官关心的“生产级”证据。
2. 优化方向
把 365 天重新划分为 4 个“可独立交付”的大阶段，每个阶段都有：
明确的“可演示成果”
对应的简历写法
GitHub release 和文档产出
把“任务清单”从“写代码 → 写测试”升级为“解决一个具体工程问题”，例如：
Day X：实现混合检索（BM25 + 向量）并对比效果
Day Y：实现 Query 改写 + 多轮对话管理
Day Z：实现缓存策略，把 token 成本降低 30%
为每一周设计“简历数字”目标，例如：
文档处理吞吐：X 篇 / 分钟
检索延迟：P95 < X ms
缓存命中率 > X%
告警恢复时间 < X 分钟
二、优化后的整体结构（先看大局）
1. 四大阶段 + 里程碑
   timeline
    title 365天开发阶段（优化版）
    section 第一阶段：本地可演示的 RAG 平台 (月1-3)
        第1月 : 环境与基础架构 + 单服务 RAG 原型
        第2月 : 多服务拆分 + 事件驱动 + 基础监控
        第3月 : MVP 发布：完整问答系统 + 压测报告
    section 第二阶段：生产级 RAG + 业务系统 (月4-6)
        第4月 : 企业级文档治理 + 多策略切块与检索
        第5月 : 订单/工单业务系统 + Kafka 事件流
        第6月 : 云原生部署 + CI/CD + 基础 MLOps
    section 第三阶段：工程化打磨与优化 (月7-9)
        第7月 : 可观测性建设（监控、日志、追踪）
        第8月 : 安全加固 + 多租户 + 权限模型
        第9月 : 性能优化 + 成本优化 + 压测报告
    section 第四阶段：求职冲刺 (月10-12)
        第10月 : 项目整理 + 文档 + Demo 视频
        第11月 : 技术博客 + 开源贡献
        第12月 : 简历精修 + 模拟面试 + 秋招投递
2. 每日执行节奏（优化版）
早晨（30–45 分钟）：推进一个“小而完整”的功能或修复
例如：
实现一种新的切块策略，对比前后检索效果
为某个接口加缓存 + 压测对比
晚间（30–45 分钟）：测试 + 文档 + 重构 + 小优化
写/补单元测试
更新 API 文档
写简短的技术笔记（可放到 docs/notes）
每周固定仪式：
周五：合并本周功能 → 创建 release
周末：写本周总结 + 下周计划 + 更新 GitHub Project
三、第一阶段（月1-3）：本地可演示的 RAG 平台
目标
做到：一台笔记本上 docker-compose up 就能演示完整流程
上传文档 → 自动切块 → 向量化 → 问答
有基础的监控指标和日志
有压测报告和简单的性能数据
第 1 月：环境 + 单服务 RAG 原型
重点：先跑通一条链，再谈扩展。
第 1 周：项目骨架与开发环境
Day 1：
任务：
创建 3 个仓库：ekp-ai、ekp-biz、ekp-infra
写好 README：项目背景、技术栈、目标
提交示例：feat: initialize project structure and README
Day 2：
任务：
设计整体架构图（用 Mermaid 或 draw.io）
明确服务边界：AI 服务负责 RAG，Java 服务负责业务和用户
提交示例：docs: add system architecture diagram
Day 3：
任务：
配置 Python 虚拟环境 + 基础依赖（FastAPI、Pydantic、日志）
写一个“健康检查”接口：/health
提交示例：build: configure Python development environment
Day 4：
任务：
初始化 Spring Boot 项目（只引入 web、data-jpa、validation）
写一个 /health 接口
提交示例：build: configure Spring Boot project
Day 5：
任务：
编写 docker-compose.yml：
PostgreSQL（带 pgvector）
Redis
一个简单的 Kafka（可用轻量镜像）
写一个一键启动脚本：up-dev.sh
提交示例：feat: add Docker Compose for development environment
Day 6：
任务：
设计核心表：用户、文档、文档块、问答会话
编写 SQL migration 脚本
提交示例：feat: add database schema for core entities
Day 7：
任务：
设计核心 API 列表：
/api/v1/documents（上传、列表）
/api/v1/qa（问答）
写成 OpenAPI 文档
提交示例：docs: add OpenAPI specification for REST API
第 2 周：文档摄入 + 切块 + 向量化
目标：做到“上传一篇 PDF → 能按语义块检索”。
Day 8：
任务：
实现文档上传接口（只存文件 + 写数据库记录）
设计文件存储结构（本地或 S3/GCS）
提交示例：feat: implement document upload API
Day 9：
任务：
选定 1–2 种切块策略：
按固定 token 数切块
按段落/章节切块（参考行业实践）
实现一个 ChunkerService，对纯文本做切块
提交示例：feat: implement text chunking service
Day 10：
任务：
引入 PDF/Word 解析工具（如 unstructured / PyMuPDF）
实现“文档 → 文本 → 切块”的完整流水线
提交示例：feat: add document parsing and chunking pipeline
Day 11：
任务：
集成嵌入模型（如 bge-large-zh 或类似）
实现 EmbeddingService：对文本块生成向量
提交示例：feat: integrate embedding model for document chunks
Day 12：
任务：
在 PostgreSQL 中启用 pgvector
创建 document_chunks 表，包含向量列
实现向量插入与查询函数
提交示例：feat: integrate pgvector for vector storage
Day 13：
任务：
实现简单的向量检索：
输入：问题文本
输出：Top-K 最相关的文档块
用 SQL 完成“余弦相似度”检索
提交示例：feat: implement vector similarity search
Day 14：
任务：
搭建一个最小 LLM 接口：
本地小模型或调用云 API
实现“检索结果 → 拼接 prompt → 生成答案”
提交示例：feat: add LLM-based answer generation
第 3 周：Java 业务系统初步 + 事件驱动
目标：让 RAG 服务变成“业务系统里的一个模块”。
Day 15：
任务：
设计用户表、角色表
实现用户注册、登录接口（暂不加密也没关系）
提交示例：feat: implement user registration and login APIs
Day 16：
任务：
设计订单/工单表
实现 CRUD 接口
提交示例：feat: implement order and ticket management APIs
Day 17：
任务：
引入 Kafka（或 Redis Streams）做事件总线
实现“订单创建 → 发送事件”
提交示例：feat: integrate Kafka for event-driven architecture
Day 18：
任务：
引入 Redis 做缓存：
缓存用户会话
缓存热点问题答案
提交示例：feat: add Redis caching for session and hot queries
Day 19：
任务：
在 Java 侧实现一个 AIServiceClient，调用 Python 的 RAG 接口
实现“工单创建 → 调用 RAG → 自动回答”
提交示例：feat: integrate RAG service into ticket workflow
Day 20：
任务：
用事件驱动实现：
订单状态变更 → 发送事件 → 通知服务
写一个简单的消费者，打印日志即可
提交示例：feat: add event-driven notification for order status
Day 21：
任务：
写单元测试 / 集成测试
写本周总结 + 下周计划
提交示例：test: add integration tests for core services
第 4 周：MVP 打磨 + 性能基线
目标：有一个“可演示、可压测”的版本。
Day 22：
任务：
用 JMeter / Locust 对问答接口做压测
记录：QPS、P95 延迟、错误率
提交示例：perf: run load tests on QA endpoint and record baseline
Day 23：
任务：
分析瓶颈：
数据库查询
向量检索
LLM 调用
做第一轮优化（索引、缓存等）
提交示例：perf: optimize slow queries and add indexes
Day 24：
任务：
加上基本的访问日志
引入 Prometheus + Grafana（或对应云监控）
提交示例：feat: add basic monitoring with Prometheus and Grafana
Day 25：
任务：
为关键业务加异常处理和统一错误返回
写一份简单的 API 文档
提交示例：feat: add error handling and API documentation
Day 26：
任务：
编写“演示脚本”：
步骤 1：上传 3–5 篇文档
步骤 2：问几个典型问题
步骤 3：展示答案 + 来源文档
提交示例：docs: add demo script and sample data
Day 27：
任务：
整理 README：
快速开始
架构图
API 文档链接
提交示例：docs: update README with quickstart and architecture
Day 28：
任务：
编写第一阶段总结：
已完成功能
性能数据
不足之处
发布 v0.1.0
提交示例：release: v0.1.0 MVP release
四、第二阶段（月4-6）：生产级 RAG + 业务系统
目标
把系统从“本地 demo”变成“云上可部署的生产系统”
引入企业级 RAG 实践：
多种切块策略对比
混合检索 + 重排序
可观测性和 MLOps（prompt 版本、追踪、评估）
第 4 月：企业级 RAG 能力升级
重点任务（按周拆）：
第 1 周：
支持更多文档格式（PDF、Word、网页）
实现多种切块策略，对比检索效果
第 2 周：
实现混合检索：向量 + BM25
加入重排序（Reranking）
第 3 周：
实现 Query 改写，支持多轮对话
对话历史管理（Redis）
第 4 周：
搭建评估集：人工标注 Q&A
计算检索准确率、召回率等指标
每周至少一个 release：v0.2.0、v0.3.0 等。
第 5 月：订单/工单业务系统 + Kafka 事件流
重点任务：
第 1 周：
完善订单状态机（新建 → 支付 → 发货 → 完成/退款）
用 Kafka 做事件驱动，保证最终一致性
第 2 周：
实现分布式事务 / 本地消息表等模式
用 Redis 做幂等处理
第 3 周：
引入 Spring Boot Admin + 健康检查
配置日志收集（ELK 或 Loki）
第 4 周：
对业务系统压测
优化热点接口
第 6 月：云原生部署 + CI/CD + MLOps
重点任务：
第 1 周：
编写 Dockerfile，对 AI 服务和 Java 服务做镜像
编写 Helm Chart 或 K8s YAML
第 2 周：
在 AWS/GCP 上创建 K8s 集群
部署数据库、Redis、Kafka
第 3 周：
配置 GitHub Actions：
自动测试 → 构建 → 推镜像 → 部署
实现滚动更新
第 4 周：
搭建基础 MLOps：
模型版本管理
Prompt 版本管理
简单的自动化评估流水线
五、第三阶段（月7-9）：工程化打磨与优化
目标
把“能用”变成“好用、可维护、可扩展”
在简历上写出具体优化数字
第 7 月：可观测性建设
第 1 周：
统一日志格式
实现请求 ID，在日志中串联调用链
第 2 周：
在 Prometheus 中定义核心指标：
请求 QPS、延迟分布
缓存命中率
LLM token 使用量
第 3 周：
在 Grafana 中制作仪表板
配置告警规则（错误率、延迟过高）
第 4 周：
引入分布式追踪（如 Jaeger / Tempo）
记录端到端 RAG 延迟
第 8 月：安全加固 + 多租户
第 1 周：
引入 JWT / OAuth2
实现基于角色的访问控制
第 2 周：
实现多租户（不同公司/部门数据隔离）
在数据库设计中加入 tenant_id
第 3 周：
加上接口限流、防刷
实现审计日志
第 4 周：
做一次安全自查：XSS、CSRF、SQL 注入等
记录修复过程
第 9 月：性能 & 成本优化
第 1 周：
对热点接口做缓存策略优化
对高频查询做 SQL 优化
第 2 周：
实现 LLM 调用的分层模型：
高频问题用小模型
复杂问题用大模型
第 3 周：
实现静态问答缓存
统计 token 成本下降比例
第 4 周：
编写性能优化报告
发布 v1.0.0 版本
六、第四阶段（月10-12）：求职冲刺
第 10 月：项目整理 + 文档 + Demo
第 1 周：
整理 3 个仓库：
统一 README 结构
补充架构图、部署图
第 2 周：
编写 3–5 篇技术博客：
RAG 架构设计
事件驱动微服务
MLOps 实践
第 3 周：
录制演示视频（5–10 分钟）
准备 PPT 版“项目介绍”
第 4 周：
把项目整理成简历里的核心项目段落（见下一节）
第 11 月：开源贡献 + 技术影响力
第 1–2 周：
向相关开源项目提 PR（如 Spring Boot、FastAPI、LangChain 等）
至少 2–3 个被合并的 PR
第 3–4 周：
参与社区讨论
把你的踩坑经验整理成博客 / GitHub Issue
第 12 月：简历精修 + 模拟面试
第 1 周：
根据项目成果，精修简历：
数字化成果
技术难点与解决方案
第 2–3 周：
模拟面试：
系统设计
项目深挖
行为面试
第 4 周：
正式投递，准备秋招/春招
七、简历展示模板（优化版）
项目名称
Enterprise Knowledge Platform（企业知识库 + 订单工单一体化平台）
角色与时间
角色：后端 & AI 平台工程师（个人项目）
时间：2026.03 – 2027.02（12 个月）
技术栈
AI 栈：Python 3.11, FastAPI, PyTorch, LangChain, pgvector, Redis
Java 栈：Java 21, Spring Boot 3, Spring Security, Kafka, MySQL, Redis
基础设施：Docker, Kubernetes, GitHub Actions, Prometheus, Grafana, AWS/GCP
项目简述
设计并实现一个企业级知识库问答平台，支持员工通过自然语言查询内部制度、流程文档，结合 RAG 技术在测试集上将答案准确率从 55% 提升到 83%。
构建订单、支付、工单等业务微服务，使用 Kafka 实现事件驱动架构，实现订单创建 → 支付 → 工单创建的异步流程，在压测环境下系统吞吐从 120 QPS 提升到 350 QPS。
将 RAG 服务部署到 Kubernetes 集群，集成 Prometheus + Grafana 监控，对问答延迟、向量命中率、模型调用错误率进行实时可视化。
在 AWS/GCP 上搭建 EKS + RDS + S3 + Kafka 的完整基础设施，使用 GitHub Actions 实现自动测试、构建镜像、滚动部署，部署频率从每周 1 次提高到每日 1 次。
关键数字（示例）
文档处理：支持 PDF / Word / HTML 多格式，处理速度 10 篇/分钟
向量检索：基于 pgvector，P95 检索延迟 < 50ms，Top-10 命中率 85%
并发能力：压测环境支持 500 并发用户，问答接口 P95 延迟 < 800ms
成本优化：通过分层模型 + 静态缓存，LLM token 成本降低约 40%
可观测性：端到端 trace + 监控，平均故障恢复时间 < 5 分钟
八、GitHub 活跃度设计要点
每天至少 1 次有意义的提交
不写空提交，每个提交都对应一个“小功能 / 小修复 / 小优化”。
每周 1 个 release
版本号：v0.1.0、v0.2.0 … v1.0.0
每个版本有清晰的 CHANGELOG。
每个仓库至少包含：
README（架构、快速开始）
docs/ 目录：设计文档、API 文档、运维手册
scripts/ 目录：一键部署、备份恢复脚本
.github/ 目录：CI/CD 配置