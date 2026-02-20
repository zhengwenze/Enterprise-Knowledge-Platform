import { create } from 'zustand';
import type { QASession, Document } from '@/types';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: QASession['sources'];
  isLoading?: boolean;
}

interface AppState {
  documents: Document[];
  setDocuments: (documents: Document[]) => void;
  addDocument: (document: Document) => void;
  removeDocument: (id: number) => void;
  
  messages: Message[];
  addMessage: (message: Message) => void;
  updateMessage: (id: string, content: string, sources?: QASession['sources']) => void;
  clearMessages: () => void;
  
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  
  selectedDocuments: number[];
  setSelectedDocuments: (ids: number[]) => void;
  toggleDocument: (id: number) => void;
}

export const useAppStore = create<AppState>((set) => ({
  documents: [],
  setDocuments: (documents) => set({ documents }),
  addDocument: (document) => set((state) => ({ 
    documents: [...state.documents, document] 
  })),
  removeDocument: (id) => set((state) => ({ 
    documents: state.documents.filter((d) => d.id !== id) 
  })),
  
  messages: [],
  addMessage: (message) => set((state) => ({ 
    messages: [...state.messages, message] 
  })),
  updateMessage: (id, content, sources) => set((state) => ({
    messages: state.messages.map((m) => 
      m.id === id ? { ...m, content, sources, isLoading: false } : m
    ),
  })),
  clearMessages: () => set({ messages: [] }),
  
  isLoading: false,
  setIsLoading: (loading) => set({ isLoading: loading }),
  
  selectedDocuments: [],
  setSelectedDocuments: (ids) => set({ selectedDocuments: ids }),
  toggleDocument: (id) => set((state) => ({
    selectedDocuments: state.selectedDocuments.includes(id)
      ? state.selectedDocuments.filter((d) => d !== id)
      : [...state.selectedDocuments, id],
  })),
}));
