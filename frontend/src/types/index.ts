// src/types/index.ts
export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export interface RepoContext {
  url: string;
  name: string;
  description: string;
  stars: number;
  forks: number;
  issues: number;
  languages: Record<string, number>;
  contributors: number;
  lastUpdated: string;
  dependencies: string[];
}
