export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
export const BIZ_API_URL = process.env.NEXT_PUBLIC_BIZ_URL || 'http://localhost:8080';

export const API_ENDPOINTS = {
  documents: {
    list: `${API_BASE_URL}/api/v1/documents`,
    upload: `${API_BASE_URL}/api/v1/documents`,
    get: (id: number) => `${API_BASE_URL}/api/v1/documents/${id}`,
    delete: (id: number) => `${API_BASE_URL}/api/v1/documents/${id}`,
  },
  qa: {
    ask: `${API_BASE_URL}/api/v1/qa`,
    history: `${API_BASE_URL}/api/v1/qa/history/list`,
    get: (id: number) => `${API_BASE_URL}/api/v1/qa/${id}`,
  },
  agent: {
    query: `${API_BASE_URL}/api/v1/agent/query`,
    queryStream: `${API_BASE_URL}/api/v1/agent/query/stream`,
    session: (sessionId: string) => `${API_BASE_URL}/api/v1/agent/session/${sessionId}`,
    tools: `${API_BASE_URL}/api/v1/agent/tools`,
  },
  health: {
    ai: `${API_BASE_URL}/health`,
    biz: `${BIZ_API_URL}/health`,
  },
} as const;
