'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { useDocuments } from '@/hooks/useApi';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Send, Loader2, Bot, User, FileText, ChevronDown } from 'lucide-react';
import { API_ENDPOINTS } from '@/lib/api';
import type { QASession, QASource } from '@/types';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: QASource[];
  isLoading?: boolean;
}

export default function QAPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedDocs, setSelectedDocs] = useState<number[]>([]);
  const [showDocSelector, setShowDocSelector] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  
  const { data: documents } = useDocuments();

  const scrollToBottom = useCallback(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
    };

    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: '',
      isLoading: true,
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(API_ENDPOINTS.qa.ask, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: input.trim(),
          document_ids: selectedDocs.length > 0 ? selectedDocs : undefined,
          top_k: 5,
        }),
      });

      if (!response.ok) throw new Error('Failed to get answer');

      const data: QASession = await response.json();
      
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantMessage.id
            ? {
                ...m,
                content: data.answer,
                sources: data.sources,
                isLoading: false,
              }
            : m
        )
      );
    } catch (error) {
      console.error('QA error:', error);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantMessage.id
            ? {
                ...m,
                content: '抱歉，获取答案时出现错误，请稍后重试。',
                isLoading: false,
              }
            : m
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  const toggleDocument = (docId: number) => {
    setSelectedDocs((prev) =>
      prev.includes(docId)
        ? prev.filter((id) => id !== docId)
        : [...prev, docId]
    );
  };

  return (
    <div className="flex h-[calc(100vh-0px)]">
      <div className="flex-1 flex flex-col">
        <div className="p-6 border-b bg-white">
          <h1 className="text-2xl font-bold text-slate-900">智能问答</h1>
          <p className="text-slate-600 mt-1">基于知识库的 RAG 智能问答系统</p>
        </div>

        <ScrollArea className="flex-1 p-6" ref={scrollRef}>
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-500">
              <Bot className="h-16 w-16 mb-4 text-slate-300" />
              <p className="text-lg font-medium">开始对话</p>
              <p className="text-sm mt-1">输入问题，获取基于知识库的智能回答</p>
            </div>
          ) : (
            <div className="space-y-6 max-w-4xl mx-auto">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-4 ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.role === 'assistant' && (
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                      <Bot className="h-4 w-4 text-blue-600" />
                    </div>
                  )}
                  <div
                    className={`max-w-[80%] rounded-lg p-4 ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-white border border-slate-200'
                    }`}
                  >
                    {message.isLoading ? (
                      <div className="flex items-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>正在思考...</span>
                      </div>
                    ) : (
                      <>
                        <p className="whitespace-pre-wrap">{message.content}</p>
                        {message.sources && message.sources.length > 0 && (
                          <div className="mt-4 pt-4 border-t border-slate-200">
                            <p className="text-sm font-medium text-slate-700 mb-2">
                              参考来源：
                            </p>
                            <div className="space-y-2">
                              {message.sources.map((source, index) => (
                                <div
                                  key={index}
                                  className="text-sm bg-slate-50 rounded p-2"
                                >
                                  <div className="flex items-center gap-2">
                                    <FileText className="h-3 w-3 text-slate-400" />
                                    <span className="font-medium text-slate-700">
                                      {source.document_title}
                                    </span>
                                    <Badge variant="outline" className="text-xs">
                                      {(source.relevance_score * 100).toFixed(0)}%
                                    </Badge>
                                  </div>
                                  <p className="mt-1 text-slate-600 line-clamp-2">
                                    {source.content}
                                  </p>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                  {message.role === 'user' && (
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center">
                      <User className="h-4 w-4 text-slate-600" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </ScrollArea>

        <div className="p-6 border-t bg-white">
          <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
            <div className="flex gap-3">
              <div className="relative flex-1">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="输入您的问题..."
                  disabled={isLoading}
                  className="pr-24"
                />
                {selectedDocs.length > 0 && (
                  <Badge className="absolute right-3 top-1/2 -translate-y-1/2">
                    {selectedDocs.length} 个文档
                  </Badge>
                )}
              </div>
              <Button type="submit" disabled={isLoading || !input.trim()}>
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </div>
          </form>
        </div>
      </div>

      <div className="w-72 border-l bg-white flex flex-col">
        <div className="p-4 border-b">
          <Button
            variant="outline"
            className="w-full justify-between"
            onClick={() => setShowDocSelector(!showDocSelector)}
          >
            <span>选择文档范围</span>
            <ChevronDown
              className={`h-4 w-4 transition-transform ${
                showDocSelector ? 'rotate-180' : ''
              }`}
            />
          </Button>
        </div>
        
        {showDocSelector && (
          <ScrollArea className="flex-1 p-4">
            <div className="space-y-2">
              {documents && documents.length > 0 ? (
                documents.map((doc) => (
                  <div
                    key={doc.id}
                    className={`flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-colors ${
                      selectedDocs.includes(doc.id)
                        ? 'bg-blue-50 border border-blue-200'
                        : 'hover:bg-slate-50 border border-transparent'
                    }`}
                    onClick={() => toggleDocument(doc.id)}
                  >
                    <FileText className="h-4 w-4 text-slate-400" />
                    <span className="text-sm truncate flex-1">{doc.title}</span>
                    {selectedDocs.includes(doc.id) && (
                      <Badge variant="secondary" className="text-xs">已选</Badge>
                    )}
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-500 text-center py-4">
                  暂无文档
                </p>
              )}
            </div>
          </ScrollArea>
        )}
        
        {!showDocSelector && (
          <div className="flex-1 p-4">
            <div className="rounded-lg bg-slate-50 p-4">
              <p className="text-sm font-medium text-slate-700">使用说明</p>
              <ul className="mt-2 text-sm text-slate-600 space-y-1">
                <li>• 输入问题进行问答</li>
                <li>• 可选择特定文档范围</li>
                <li>• 系统会检索相关内容</li>
                <li>• 显示答案和参考来源</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
