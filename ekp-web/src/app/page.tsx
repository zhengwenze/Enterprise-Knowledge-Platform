'use client';

import { useQuery } from '@tanstack/react-query';
import { FileText, MessageSquare, Database, Activity } from 'lucide-react';
import { API_ENDPOINTS } from '@/lib/api';
import type { HealthStatus } from '@/types';

async function fetchHealth(): Promise<HealthStatus> {
  const response = await fetch(API_ENDPOINTS.health.ai);
  if (!response.ok) throw new Error('Health check failed');
  return response.json();
}

export default function HomePage() {
  const { data: healthData, isLoading } = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchInterval: 30000,
  });

  const stats = [
    { label: '文档总数', value: '0', icon: FileText, color: 'bg-blue-500' },
    { label: '问答会话', value: '0', icon: MessageSquare, color: 'bg-green-500' },
    { label: '向量数量', value: '0', icon: Database, color: 'bg-purple-500' },
    { label: '系统状态', value: healthData?.status === 'healthy' ? '正常' : '检查中...', icon: Activity, color: 'bg-orange-500' },
  ];

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">企业知识库平台</h1>
        <p className="mt-2 text-slate-600">基于 RAG 技术的智能问答系统</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div
              key={stat.label}
              className="rounded-xl bg-white p-6 shadow-sm border border-slate-200"
            >
              <div className="flex items-center gap-4">
                <div className={`rounded-lg p-3 ${stat.color}`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
                <div>
                  <p className="text-sm text-slate-500">{stat.label}</p>
                  <p className="text-2xl font-semibold text-slate-900">
                    {isLoading && stat.label === '系统状态' ? '...' : stat.value}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl bg-white p-6 shadow-sm border border-slate-200">
          <h2 className="text-lg font-semibold text-slate-900">快速开始</h2>
          <div className="mt-4 space-y-3">
            <a
              href="/documents"
              className="flex items-center gap-3 rounded-lg border border-slate-200 p-4 hover:bg-slate-50 transition-colors"
            >
              <FileText className="h-5 w-5 text-blue-500" />
              <div>
                <p className="font-medium text-slate-900">上传文档</p>
                <p className="text-sm text-slate-500">上传 PDF、TXT 等格式文档</p>
              </div>
            </a>
            <a
              href="/qa"
              className="flex items-center gap-3 rounded-lg border border-slate-200 p-4 hover:bg-slate-50 transition-colors"
            >
              <MessageSquare className="h-5 w-5 text-green-500" />
              <div>
                <p className="font-medium text-slate-900">开始问答</p>
                <p className="text-sm text-slate-500">基于知识库进行智能问答</p>
              </div>
            </a>
          </div>
        </div>

        <div className="rounded-xl bg-white p-6 shadow-sm border border-slate-200">
          <h2 className="text-lg font-semibold text-slate-900">系统架构</h2>
          <div className="mt-4 space-y-2 text-sm text-slate-600">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-green-500"></span>
              <span>AI Service (FastAPI) - 端口 8000</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-green-500"></span>
              <span>Biz Service (Spring Boot) - 端口 8080</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-green-500"></span>
              <span>PostgreSQL + pgvector - 端口 5432</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-green-500"></span>
              <span>Redis - 端口 6379</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-green-500"></span>
              <span>Kafka - 端口 9092</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
