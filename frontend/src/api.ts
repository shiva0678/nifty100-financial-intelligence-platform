import axios from 'axios';
import type {
  CompanySummary,
  CompanyDetail,
  CompanyMetrics,
  CompanyScores,
  ListResponse,
} from './types';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 12000,
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error?.response?.data?.error ||
      error?.response?.statusText ||
      error?.message ||
      'API request failed';
    return Promise.reject(new Error(message));
  }
);

export function fetchCompanies(page = 1, pageSize = 20): Promise<ListResponse<CompanySummary>> {
  return apiClient
    .get<ListResponse<CompanySummary>>('/api/companies/', {
      params: { page, page_size: pageSize },
    })
    .then((response) => response.data);
}

export function searchCompanies(query: string, page = 1, pageSize = 50): Promise<ListResponse<CompanySummary>> {
  return apiClient
    .get<ListResponse<CompanySummary>>('/api/search/', {
      params: { q: query, page, page_size: pageSize },
    })
    .then((response) => response.data);
}

export function fetchCompanyDetail(symbol: string): Promise<CompanyDetail> {
  return apiClient.get<CompanyDetail>(`/api/company/${encodeURIComponent(symbol)}/`).then((response) => response.data);
}

export function fetchCompanyMetrics(symbol: string): Promise<CompanyMetrics> {
  return apiClient
    .get<CompanyMetrics>(`/api/company/${encodeURIComponent(symbol)}/metrics/`)
    .then((response) => response.data);
}

export function fetchCompanyScores(symbol: string): Promise<CompanyScores> {
  return apiClient
    .get<CompanyScores>(`/api/company/${encodeURIComponent(symbol)}/score/`)
    .then((response) => response.data);
}

export function fetchCompanyInsights(symbol: string): Promise<{ company: string; pros?: string | null; cons?: string | null }> {
  return apiClient
    .get<{ company: string; pros?: string | null; cons?: string | null }>(
      `/api/company/${encodeURIComponent(symbol)}/insights/`,
    )
    .then((response) => response.data);
}
