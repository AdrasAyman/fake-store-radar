import type { components } from "./types";

export type Candidate = components["schemas"]["CandidateOut"];
export type CandidatePage = components["schemas"]["CandidatePage"];
export type Brand = components["schemas"]["BrandOut"];

const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

export interface CandidateFilters {
  brand_id?: number;
  status?: string;
  match_reason?: string;
  q?: string;
  limit?: number;
  offset?: number;
}

async function get<T>(path: string, params?: Record<string, unknown>): Promise<T> {
  const url = new URL(BASE + path);
  for (const [key, value] of Object.entries(params ?? {})) {
    if (value !== undefined && value !== "" && value !== null) {
      url.searchParams.set(key, String(value));
    }
  }

  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export const fetchCandidates = (filters: CandidateFilters) =>
  get<CandidatePage>("/candidates", filters);

export const fetchBrands = () => get<Brand[]>("/brands");