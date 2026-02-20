'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { API_ENDPOINTS } from '@/lib/api';

interface AgentStep {
  thought: string;
  action: string;
  action_input: Record<string, unknown>;
  observation: string;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  steps?: AgentStep[];
  tools_used?: string[];
}

export default function AgentPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState('default');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await fetch(API_ENDPOINTS.agent.query, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: userMessage,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error('Request failed');
      }

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.answer,
          steps: data.steps,
          tools_used: data.tools_used,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: '抱歉，发生了错误，请稍后重试。',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const clearSession = async () => {
    try {
      await fetch(API_ENDPOINTS.agent.session(sessionId), {
        method: 'DELETE',
      });
      setMessages([]);
    } catch (error) {
      console.error('Clear session error:', error);
    }
  };

  return (
    <div className="flex h-[calc(100vh-80px)]">
      <div className="flex-1 flex flex-col">
        <div className="p-4 border-b flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">Agent 智能助手</h1>
            <p className="text-muted-foreground text-sm">
              基于 ReAct 架构的智能对话助手，支持工具调用
            </p>
          </div>
          <Button variant="outline" onClick={clearSession}>
            清空对话
          </Button>
        </div>

        <ScrollArea className="flex-1 p-4" ref={scrollRef}>
          <div className="space-y-4 max-w-4xl mx-auto">
            {messages.length === 0 && (
              <Card className="bg-muted/50">
                <CardContent className="pt-6">
                  <div className="text-center space-y-4">
                    <p className="text-lg font-medium">欢迎使用 Agent 智能助手</p>
                    <p className="text-muted-foreground">
                      我可以帮你搜索知识库、计算、查询时间等
                    </p>
                    <div className="flex flex-wrap justify-center gap-2">
                      <Badge variant="secondary">document_search</Badge>
                      <Badge variant="secondary">calculator</Badge>
                      <Badge variant="secondary">current_time</Badge>
                      <Badge variant="secondary">document_list</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <Card
                  className={`max-w-[80%] ${
                    msg.role === 'user' ? 'bg-primary text-primary-foreground' : ''
                  }`}
                >
                  <CardContent className="pt-4">
                    <p className="whitespace-pre-wrap">{msg.content}</p>

                    {msg.role === 'assistant' && msg.steps && msg.steps.length > 0 && (
                      <div className="mt-4 space-y-2">
                        <Separator />
                        <div className="text-xs text-muted-foreground">
                          推理过程 ({msg.steps.length} 步)
                        </div>
                        {msg.steps.map((step, stepIdx) => (
                          <div
                            key={stepIdx}
                            className="text-xs bg-muted/50 rounded p-2 space-y-1"
                          >
                            {step.thought && (
                              <div>
                                <span className="font-medium">思考: </span>
                                {step.thought}
                              </div>
                            )}
                            {step.action && (
                              <div>
                                <span className="font-medium">行动: </span>
                                <Badge variant="outline" className="text-xs">
                                  {step.action}
                                </Badge>
                              </div>
                            )}
                            {step.observation && (
                              <div>
                                <span className="font-medium">观察: </span>
                                {step.observation}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}

                    {msg.role === 'assistant' && msg.tools_used && msg.tools_used.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {msg.tools_used.map((tool) => (
                          <Badge key={tool} variant="secondary" className="text-xs">
                            {tool}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <Card>
                  <CardContent className="pt-4">
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin h-4 w-4 border-2 border-primary border-t-transparent rounded-full" />
                      <span className="text-muted-foreground">思考中...</span>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        </ScrollArea>

        <div className="p-4 border-t">
          <div className="max-w-4xl mx-auto flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="输入问题，例如：公司请假制度是什么？"
              disabled={loading}
              className="flex-1"
            />
            <Button onClick={sendMessage} disabled={loading || !input.trim()}>
              发送
            </Button>
          </div>
        </div>
      </div>

      <div className="w-80 border-l p-4 hidden lg:block">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">可用工具</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-1">
              <Badge>document_search</Badge>
              <p className="text-xs text-muted-foreground">搜索企业知识库文档</p>
            </div>
            <div className="space-y-1">
              <Badge>document_list</Badge>
              <p className="text-xs text-muted-foreground">获取知识库文档列表</p>
            </div>
            <div className="space-y-1">
              <Badge>calculator</Badge>
              <p className="text-xs text-muted-foreground">执行数学计算</p>
            </div>
            <div className="space-y-1">
              <Badge>current_time</Badge>
              <p className="text-xs text-muted-foreground">获取当前时间</p>
            </div>
          </CardContent>
        </Card>

        <Card className="mt-4">
          <CardHeader>
            <CardTitle className="text-sm">ReAct 架构</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xs text-muted-foreground space-y-2">
              <p>
                <strong>ReAct</strong> = Reasoning + Acting
              </p>
              <p>1. 思考 (Thought): 分析问题</p>
              <p>2. 行动 (Action): 选择工具</p>
              <p>3. 观察 (Observation): 获取结果</p>
              <p>4. 循环直到得出答案</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
