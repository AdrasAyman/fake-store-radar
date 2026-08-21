import { useState } from "react";
import { QueryClient, QueryClientProvider, useQuery } from "@tanstack/react-query";
import { fetchBrands, fetchCandidates } from "./api/client";
import "./App.css";

const queryClient = new QueryClient();

const STATUSES = ["pending", "crawled", "scored", "dismissed"];

function Dashboard() {
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("");
  const [brandId, setBrandId] = useState("");
  const [matchReason, setMatchReason] = useState("");

  const brands = useQuery({ queryKey: ["brands"], queryFn: fetchBrands });

  const filters = {
    q: q || undefined,
    status: status || undefined,
    brand_id: brandId ? Number(brandId) : undefined,
    match_reason: matchReason || undefined,
    limit: 100,
  };

  const candidates = useQuery({
    queryKey: ["candidates", filters],
    queryFn: () => fetchCandidates(filters),
    refetchInterval: 15000,
  });

  const brandName = (id: number | null) =>
    brands.data?.find((b) => b.id === id)?.name ?? "—";

  return (
    <div className="shell">
      <header className="masthead">
        <div>
          <p className="eyebrow">Certificate Transparency monitor</p>
          <h1>Fake Store Radar</h1>
        </div>
        <p className="count">
          {candidates.data ? `${candidates.data.total} flagged` : "—"}
        </p>
      </header>

      <div className="filters">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Filter by domain"
        />
        <select value={brandId} onChange={(e) => setBrandId(e.target.value)}>
          <option value="">All brands</option>
          {brands.data?.map((b) => (
            <option key={b.id} value={b.id}>{b.name}</option>
          ))}
        </select>
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">Any status</option>
          {STATUSES.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <select value={matchReason} onChange={(e) => setMatchReason(e.target.value)}>
          <option value="">Any match type</option>
          <option value="permutation">Permutation</option>
          <option value="keyword">Keyword</option>
        </select>
      </div>

      {candidates.isPending && <p className="note">Loading…</p>}

      {candidates.isError && (
        <p className="note error">
          Can't reach the API. Check that uvicorn is running on port 8000.
        </p>
      )}

      {candidates.data?.items.length === 0 && (
        <p className="note">No domains match these filters.</p>
      )}

      {!!candidates.data?.items.length && (
        <table>
          <thead>
            <tr>
              <th>Domain</th>
              <th>Brand</th>
              <th>Matched by</th>
              <th>Status</th>
              <th>Risk</th>
              <th>First seen</th>
            </tr>
          </thead>
          <tbody>
            {candidates.data.items.map((c) => (
              <tr key={c.id}>
                <td className="domain">{c.domain}</td>
                <td>{brandName(c.brand_id)}</td>
                <td>
                  <span className={c.match_reason.startsWith("permutation")
                    ? "tag tag-perm" : "tag"}>
                    {c.match_reason}
                  </span>
                </td>
                <td>{c.status}</td>
                <td>{c.risk_score ?? "—"}</td>
                <td>{new Date(c.first_seen_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Dashboard />
    </QueryClientProvider>
  );
}