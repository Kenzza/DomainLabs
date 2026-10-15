const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export interface HealthResponse {
  status: string;
}

export interface AnalyzeRequest {
  target: string;
  checks?: string[];
}

export interface AnalyzeResponse {
  target: {
    input: string;
    normalized_host: string;
    normalized_url: string;
  };
  started_at: string;
  completed_at: string;
  checks: Record<string, {
    status: string;
    data: any;
    message?: string;
  }>;
}

export async function checkHealth(): Promise<HealthResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/health`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (!res.ok) {
      throw new Error(`Health check gagal dengan status ${res.status}`);
    }
    return res.json();
  } catch (err: any) {
    throw new Error(err.message || "Gagal terhubung ke backend (Offline / Cold Start).");
  }
}

export async function analyzeTarget(req: AnalyzeRequest): Promise<AnalyzeResponse> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(req),
    });
  } catch (err: any) {
    throw new Error("Tidak dapat terhubung ke server backend. Pastikan layanan backend aktif.");
  }

  if (!res.ok) {
    if (res.status === 422) {
      const errorData = await res.json().catch(() => ({}));
      const detail = errorData.detail;
      if (Array.isArray(detail)) {
        const msgs = detail.map((d: any) => d.msg || JSON.stringify(d)).join(", ");
        throw new Error(`Validasi input ditolak: ${msgs}`);
      }
      throw new Error("Input target tidak valid atau ditolak oleh policy keamanan.");
    }

    if (res.status === 429) {
      const retryAfter = res.headers.get("Retry-After");
      throw new Error(`Terlalu banyak permintaan (Rate Limited). ${retryAfter ? `Silakan coba lagi dalam ${retryAfter} detik.` : 'Silakan coba beberapa saat lagi.'}`);
    }

    if (res.status >= 500) {
      throw new Error(`Kesalahan server internal (${res.status}). Layanan backend sedang mengalami kendala.`);
    }

    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Analisis gagal dengan status ${res.status}`);
  }

  return res.json();
}
