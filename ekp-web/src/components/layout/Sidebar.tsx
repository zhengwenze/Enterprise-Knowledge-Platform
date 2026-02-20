'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { FileText, MessageSquare, Home } from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { href: '/', label: '首页', icon: Home },
  { href: '/documents', label: '文档管理', icon: FileText },
  { href: '/qa', label: '智能问答', icon: MessageSquare },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r bg-slate-900 text-white">
      <div className="flex h-full flex-col">
        <div className="flex h-16 items-center border-b border-slate-700 px-6">
          <h1 className="text-xl font-bold">EKP</h1>
          <span className="ml-2 text-sm text-slate-400">知识库平台</span>
        </div>
        
        <nav className="flex-1 space-y-1 p-4">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-slate-700 text-white'
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                )}
              >
                <Icon className="h-5 w-5" />
                {item.label}
              </Link>
            );
          })}
        </nav>
        
        <div className="border-t border-slate-700 p-4">
          <div className="rounded-lg bg-slate-800 p-4">
            <p className="text-xs text-slate-400">Enterprise Knowledge</p>
            <p className="text-xs text-slate-400">Platform v0.1.0</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
