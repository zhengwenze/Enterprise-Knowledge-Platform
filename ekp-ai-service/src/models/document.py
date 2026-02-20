from sqlalchemy import Column, BigInteger, String, Text, Integer, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from src.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True)
    role = Column(String(20), default="USER")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    documents = relationship("Document", back_populates="creator")
    qa_sessions = relationship("QASession", back_populates="user")


class Document(Base):
    __tablename__ = "documents"

    id = Column(BigInteger, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    file_path = Column(String(500))
    file_size = Column(BigInteger)
    file_type = Column(String(50))
    status = Column(String(20), default="PENDING")
    error_message = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by = Column(BigInteger, ForeignKey("users.id"))

    creator = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    vectors = relationship("DocumentVector", back_populates="document", cascade="all, delete-orphan")
    qa_sessions = relationship("QASession", back_populates="document")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(BigInteger, primary_key=True, index=True)
    document_id = Column(BigInteger, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    token_count = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())

    document = relationship("Document", back_populates="chunks")
    vector = relationship("DocumentVector", back_populates="chunk", uselist=False)


class DocumentVector(Base):
    __tablename__ = "document_vectors"

    id = Column(BigInteger, primary_key=True, index=True)
    document_id = Column(BigInteger, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_id = Column(BigInteger, ForeignKey("document_chunks.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1024))
    created_at = Column(DateTime, server_default=func.now())

    document = relationship("Document", back_populates="vectors")
    chunk = relationship("DocumentChunk", back_populates="vector")


class QASession(Base):
    __tablename__ = "qa_sessions"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    document_id = Column(BigInteger, ForeignKey("documents.id"))
    question = Column(Text, nullable=False)
    answer = Column(Text)
    model_used = Column(String(100))
    tokens_used = Column(Integer)
    response_time_ms = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="qa_sessions")
    document = relationship("Document", back_populates="qa_sessions")
    sources = relationship("QASource", back_populates="session", cascade="all, delete-orphan")


class QASource(Base):
    __tablename__ = "qa_sources"

    id = Column(BigInteger, primary_key=True, index=True)
    session_id = Column(BigInteger, ForeignKey("qa_sessions.id", ondelete="CASCADE"), nullable=False)
    chunk_id = Column(BigInteger, ForeignKey("document_chunks.id"), nullable=False)
    relevance_score = Column(Float)
    created_at = Column(DateTime, server_default=func.now())

    session = relationship("QASession", back_populates="sources")
