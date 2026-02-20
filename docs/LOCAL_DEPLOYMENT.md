# 本地化 RAG 部署指南（RTX 4060 8GB）

## 系统要求

| 组件 | 要求 |
|------|------|
| GPU | NVIDIA RTX 4060 (8GB) |
| RAM | 16GB+ 推荐 |
| 存储 | 20GB+ 可用空间 |

## 第一步：安装 Ollama

### Windows 安装

1. 下载 Ollama: https://ollama.ai/download
2. 运行安装程序
3. 验证安装:
```powershell
ollama --version
```

## 第二步：下载模型

针对 RTX 4060 8GB 显存，推荐以下模型：

### LLM 模型（问答生成）

```powershell
# 推荐：Qwen2.5 7B（中文支持最好）
ollama pull qwen2.5:7b

# 备选：Llama 3.1 8B（英文更强）
ollama pull llama3.1:8b

# 备选：Mistral 7B（平衡选择）
ollama pull mistral:7b
```

### 视觉模型（图片理解）

```powershell
# 用于处理文档中的图片
ollama pull llava:7b
```

### 模型显存占用参考

| 模型 | 显存占用 | 4060 8GB 兼容性 |
|------|---------|----------------|
| qwen2.5:7b | ~5GB | ✅ 推荐 |
| llama3.1:8b | ~5.5GB | ✅ 可用 |
| mistral:7b | ~4.5GB | ✅ 可用 |
| llava:7b | ~5GB | ✅ 可用 |

## 第三步：验证 Ollama 运行

```powershell
# 测试 LLM
ollama run qwen2.5:7b "你好，请介绍一下自己"

# 测试 API
curl http://localhost:11434/api/generate -d '{"model": "qwen2.5:7b", "prompt": "你好"}'
```

## 第四步：启动 EKP 服务

### 方式一：Docker Compose（推荐）

```powershell
cd d:\AAA_DEV\EKP\ekp-infra

# 确保 Docker Desktop 正在运行
# 构建并启动服务
docker-compose up -d --build
```

### 方式二：本地开发模式

```powershell
# 终端 1: 启动数据库
cd d:\AAA_DEV\EKP\ekp-infra
docker-compose up -d postgres redis

# 终端 2: 启动 AI 服务
cd d:\AAA_DEV\EKP\ekp-ai-service
pip install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 终端 3: 启动前端
cd d:\AAA_DEV\EKP\ekp-web
npm install
npm run dev
```

## 第五步：访问服务

- **前端界面**: http://localhost:3000
- **API 文档**: http://localhost:8000/docs
- **Ollama API**: http://localhost:11434

## 常见问题

### Q: 显存不足怎么办？

A: 使用量化版本的模型：
```powershell
# Q4 量化版本（显存占用更小）
ollama pull qwen2.5:7b-q4_0
```

### Q: 嵌入模型下载慢？

A: 使用国内镜像：
```powershell
# 设置 HuggingFace 镜像
$env:HF_ENDPOINT = "https://hf-mirror.com"
```

### Q: 如何切换到 OpenAI API？

A: 修改 `.env` 文件：
```
USE_LOCAL_LLM=false
OPENAI_API_KEY=your-api-key
```

## 性能优化建议

1. **显存优化**: 使用 `qwen2.5:7b-q4_0` 量化版本
2. **嵌入模型**: 首次运行会自动下载，建议提前下载
3. **并发处理**: 4060 建议单线程处理文档

## 成本对比

| 方案 | 成本 | 性能 |
|------|------|------|
| 本地 Ollama | 免费 | 7B 模型够用 |
| OpenAI GPT-4 | ~$0.03/1K tokens | 最强 |
| DeepSeek API | ~$0.001/1K tokens | 性价比高 |
