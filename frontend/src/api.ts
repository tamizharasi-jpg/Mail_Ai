import Constants from "expo-constants";

export type Analysis = {
  spam: { label: string; probability: number; riskLevel: string };
  phishing: { risk: string; probability: number };
  category: { label: string; probability: number };
  priority: { label: string; probability: number; reasons?: string[] };
  intent: { label: string; actionRequired: boolean; confidence: number };
  entities: Record<string, string[]>;
  features: Record<string, string | number | string[]>;
  explanation: { type: string; direction: string; text: string }[];
  summary: string;
  responseRecommendation: string;
  suggestedResponse: string;
  modelVersion: string;
};

export type RecordItem = { id: string; sender: string; subject: string; source_name: string; created_at: string; analysis: Analysis };

const baseUrl = String(Constants.expoConfig?.extra?.backendUrl ?? process.env.EXPO_PUBLIC_BACKEND_URL ?? "").replace(/\/$/, "");

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}/api${path}`, options);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail || "The intelligence service is unavailable.");
  return payload as T;
}

export function analyzeEmail(input: { sender: string; subject: string; body: string; client_id: string; source_name?: string }) {
  return request<RecordItem>("/email/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(input) });
}

export async function analyzeFile(asset: { uri: string; name: string; mimeType?: string }, clientId: string) {
  const form = new FormData();
  if (typeof window !== "undefined") {
    const blob = await (await fetch(asset.uri)).blob();
    form.append("file", blob, asset.name);
  } else {
    form.append("file", { uri: asset.uri, name: asset.name, type: asset.mimeType || "application/octet-stream" } as unknown as Blob);
  }
  return request<RecordItem>(`/email/analyze-file?client_id=${encodeURIComponent(clientId)}`, { method: "POST", body: form });
}

export function getHistory(clientId: string, search = "") {
  return request<RecordItem[]>(`/email/history?client_id=${encodeURIComponent(clientId)}&search=${encodeURIComponent(search)}`);
}

export function saveFeedback(id: string, clientId: string, field: string, correctedValue: string) {
  return request<{ status: string }>(`/email/${id}/feedback`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ client_id: clientId, field, corrected_value: correctedValue }) });
}