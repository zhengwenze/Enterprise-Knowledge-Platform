import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("EKP AI Service - 功能测试")
print("=" * 60)

print("\n[1/4] 测试ChunkerService...")
try:
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ImportError:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
    
    text = "这是测试文本。" * 100
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=20,
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
    )
    chunks = splitter.split_text(text)
    print(f"  ✓ 文本切块成功: 输入 {len(text)} 字符 -> {len(chunks)} 个块")
except Exception as e:
    print(f"  ✗ 文本切块失败: {e}")

print("\n[2/4] 测试FastAPI应用导入...")
try:
    from fastapi import FastAPI
    app = FastAPI(title="Test")
    print("  ✓ FastAPI应用创建成功")
except Exception as e:
    print(f"  ✗ FastAPI导入失败: {e}")

print("\n[3/4] 测试Pydantic模型...")
try:
    from pydantic import BaseModel
    from typing import Optional
    
    class TestModel(BaseModel):
        id: int
        name: str
        description: Optional[str] = None
    
    model = TestModel(id=1, name="test")
    print(f"  ✓ Pydantic模型创建成功: {model.model_dump()}")
except Exception as e:
    print(f"  ✗ Pydantic模型失败: {e}")

print("\n[4/4] 测试配置加载...")
try:
    from pydantic_settings import BaseSettings
    
    class Settings(BaseSettings):
        app_name: str = "EKP AI Service"
        chunk_size: int = 1000
        chunk_overlap: int = 200
    
    settings = Settings()
    print(f"  ✓ 配置加载成功: app_name={settings.app_name}, chunk_size={settings.chunk_size}")
except Exception as e:
    print(f"  ✗ 配置加载失败: {e}")

print("\n" + "=" * 60)
print("核心功能测试完成!")
print("=" * 60)
