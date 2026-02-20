import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { API_ENDPOINTS } from '@/lib/api';
import type { Document, QASession, QARequest, UploadResponse } from '@/types';

async function fetchDocuments(): Promise<Document[]> {
  const response = await fetch(API_ENDPOINTS.documents.list);
  if (!response.ok) throw new Error('Failed to fetch documents');
  return response.json();
}

async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(API_ENDPOINTS.documents.upload, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) throw new Error('Failed to upload document');
  return response.json();
}

async function deleteDocument(id: number): Promise<void> {
  const response = await fetch(API_ENDPOINTS.documents.delete(id), {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete document');
}

export function useDocuments() {
  return useQuery({
    queryKey: ['documents'],
    queryFn: fetchDocuments,
  });
}

export function useUploadDocument() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: uploadDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });
}

export function useDeleteDocument() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: deleteDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });
}

async function askQuestion(request: QARequest): Promise<QASession> {
  const response = await fetch(API_ENDPOINTS.qa.ask, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!response.ok) throw new Error('Failed to get answer');
  return response.json();
}

export function useAskQuestion() {
  return useMutation({
    mutationFn: askQuestion,
  });
}

async function fetchQAHistory(): Promise<QASession[]> {
  const response = await fetch(API_ENDPOINTS.qa.history);
  if (!response.ok) throw new Error('Failed to fetch history');
  return response.json();
}

export function useQAHistory() {
  return useQuery({
    queryKey: ['qa-history'],
    queryFn: fetchQAHistory,
  });
}
