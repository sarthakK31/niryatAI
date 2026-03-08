"use client";
import { useState, useEffect } from "react";
import AuthLayout from "@/components/AuthLayout";
import { markets } from "@/lib/api";
import { Globe2, TrendingUp, Shield, Filter } from "lucide-react";

interface MarketRow {
  country: string;
  hs_code: string;
  avg_growth_5y: number | null;
  volatility: number | null;
  total_import: number | null;
  opportunity_score: number | null;
  ai_summary: string | null;
  risk_score: number | null;
}

export default function MarketsPage() {
  const [data, setData] = useState<MarketRow[]>([]);
  const [hsCodes, setHsCodes] = useState<string[]>([]);
  const [selectedHs, setSelectedHs] = useState<string>("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    markets.hsCodes().then(setHsCodes).catch(console.error);
    markets.top().then((d) => { setData(d); setLoading(false); }).catch(console.error);
  }, []);

  const filterByHs = (code: string) => {
    setSelectedHs(code);
    setLoading(true);
    markets.top(code || undefined).then((d) => { setData(d); setLoading(false); }).catch(console.error);
  };

  const formatImport = (val: number | null) => {
    if (!val) return "—";
    if (val >= 1e9) return `$${(val / 1e9).toFixed(1)}B`;
    if (val >= 1e6) return `$${(val / 1e6).toFixed(0)}M`;
    return `$${val.toLocaleString()}`;
  };

  const scoreColor = (score: number | null) => {
    if (!score) return "text-gray-400";
    if (score >= 0.7) return "text-[var(--success)]";
    if (score >= 0.4) return "text-[var(--accent)]";
    return "text-red-400";
  };

  return (
    <AuthLayout>
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <Globe2 className="text-[var(--accent)]" /> Market Intelligence
            </h1>
            <p className="text-[var(--text-secondary)] mt-1">
              Discover the best export markets for your products
            </p>
          </div>

          {/* HS Code filter */}
          <div className="flex items-center gap-2">
            <Filter size={16} className="text-[var(--text-secondary)]" />
            <select
              value={selectedHs}
              onChange={(e) => filterByHs(e.target.value)}
              className="px-3 py-2 rounded-lg bg-[var(--bg-card)] border border-[var(--border)] text-white text-sm focus:border-[var(--primary-light)] focus:outline-none"
            >
              <option value="">All HS Codes</option>
              {hsCodes.map((code) => (
                <option key={code} value={code}>
                  HS {code}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Top 3 Cards */}
        {!loading && data.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {data.slice(0, 3).map((row, i) => (
              <div
                key={`${row.country}-${row.hs_code}`}
                className="bg-[var(--bg-card)] rounded-xl p-5 border border-[var(--border)] relative overflow-hidden"
              >
                <div className="absolute top-3 right-3 text-5xl font-black text-[var(--border)]">
                  #{i + 1}
                </div>
                <h3 className="text-xl font-bold">{row.country}</h3>
                <p className="text-sm text-[var(--text-secondary)]">HS {row.hs_code}</p>
                <div className="mt-4 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-[var(--text-secondary)]">Opportunity Score</span>
                    <span className={`font-bold ${scoreColor(row.opportunity_score)}`}>
                      {row.opportunity_score?.toFixed(2) ?? "—"}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-[var(--text-secondary)]">Total Import</span>
                    <span className="font-medium">{formatImport(row.total_import)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-[var(--text-secondary)]">5Y Growth</span>
                    <span className="font-medium">
                      {row.avg_growth_5y ? `${(row.avg_growth_5y * 100).toFixed(1)}%` : "—"}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Full Table */}
        <div className="bg-[var(--bg-card)] rounded-xl border border-[var(--border)] overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--border)] text-[var(--text-secondary)]">
                  <th className="text-left px-4 py-3 font-medium">#</th>
                  <th className="text-left px-4 py-3 font-medium">Country</th>
                  <th className="text-left px-4 py-3 font-medium">HS Code</th>
                  <th className="text-right px-4 py-3 font-medium">
                    <div className="flex items-center justify-end gap-1">
                      <TrendingUp size={14} /> Score
                    </div>
                  </th>
                  <th className="text-right px-4 py-3 font-medium">Total Import</th>
                  <th className="text-right px-4 py-3 font-medium">5Y Growth</th>
                  <th className="text-right px-4 py-3 font-medium">
                    <div className="flex items-center justify-end gap-1">
                      <Shield size={14} /> Risk
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={7} className="text-center py-12 text-[var(--text-secondary)]">
                      Loading market data...
                    </td>
                  </tr>
                ) : data.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="text-center py-12 text-[var(--text-secondary)]">
                      No data available for this filter.
                    </td>
                  </tr>
                ) : (
                  data.map((row, i) => (
                    <tr
                      key={`${row.country}-${row.hs_code}`}
                      className="border-b border-[var(--border)] hover:bg-[var(--border)]/20 transition-colors"
                    >
                      <td className="px-4 py-3 text-[var(--text-secondary)]">{i + 1}</td>
                      <td className="px-4 py-3 font-medium">{row.country}</td>
                      <td className="px-4 py-3">{row.hs_code}</td>
                      <td className={`px-4 py-3 text-right font-bold ${scoreColor(row.opportunity_score)}`}>
                        {row.opportunity_score?.toFixed(2) ?? "—"}
                      </td>
                      <td className="px-4 py-3 text-right">{formatImport(row.total_import)}</td>
                      <td className="px-4 py-3 text-right">
                        {row.avg_growth_5y ? `${(row.avg_growth_5y * 100).toFixed(1)}%` : "—"}
                      </td>
                      <td className={`px-4 py-3 text-right ${scoreColor(row.risk_score)}`}>
                        {row.risk_score?.toFixed(2) ?? "—"}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AuthLayout>
  );
}
