"use client";
import { useState, useEffect, useRef } from "react";
import AuthLayout from "@/components/AuthLayout";
import { profile as profileApi, hsCodes as hsCodesApi } from "@/lib/api";
import { User, Save, Plus, X, Search } from "lucide-react";

interface ProfileData {
  id: string;
  email: string;
  full_name: string;
  company_name: string | null;
  hs_codes: string[] | null;
  state: string | null;
}

interface HsSearchResult {
  hs_code: string;
  product_description: string | null;
}

export default function ProfilePage() {
  const [data, setData] = useState<ProfileData | null>(null);
  const [form, setForm] = useState({
    full_name: "",
    company_name: "",
    state: "",
  });
  const [hsCodes, setHsCodes] = useState<string[]>([]);
  const [hsDescriptions, setHsDescriptions] = useState<Record<string, string>>({});
  const [newHsCode, setNewHsCode] = useState("");
  const [searchResults, setSearchResults] = useState<HsSearchResult[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const dropdownRef = useRef<HTMLDivElement>(null);
  const searchTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    profileApi.get().then((d: ProfileData) => {
      setData(d);
      setForm({
        full_name: d.full_name,
        company_name: d.company_name || "",
        state: d.state || "",
      });
      setHsCodes(d.hs_codes || []);
      // Fetch descriptions for existing codes
      if (d.hs_codes && d.hs_codes.length > 0) {
        hsCodesApi.descriptions(d.hs_codes).then(setHsDescriptions).catch(console.error);
      }
    }).catch(console.error);
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const handleSearchInput = (value: string) => {
    setNewHsCode(value);
    if (searchTimeout.current) clearTimeout(searchTimeout.current);
    if (value.trim().length < 2) {
      setSearchResults([]);
      setShowDropdown(false);
      return;
    }
    searchTimeout.current = setTimeout(() => {
      hsCodesApi.search(value.trim()).then((results: HsSearchResult[]) => {
        setSearchResults(results);
        setShowDropdown(results.length > 0);
      }).catch(console.error);
    }, 300);
  };

  const addHsCode = (code: string, description?: string | null) => {
    const trimmed = code.trim();
    if (trimmed && !hsCodes.includes(trimmed)) {
      setHsCodes((prev) => [...prev, trimmed]);
      if (description) {
        setHsDescriptions((prev) => ({ ...prev, [trimmed]: description }));
      }
    }
    setNewHsCode("");
    setShowDropdown(false);
    setSearchResults([]);
  };

  const removeHsCode = (code: string) => {
    setHsCodes((prev) => prev.filter((c) => c !== code));
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage("");
    try {
      const updated = await profileApi.update({
        full_name: form.full_name,
        company_name: form.company_name || undefined,
        hs_codes: hsCodes.length > 0 ? hsCodes : undefined,
        state: form.state || undefined,
      });
      console.log("[DEBUG] Updated profile:", updated);
      setData(updated);
      setHsCodes(updated.hs_codes || []);
      // Refresh descriptions
      if (updated.hs_codes && updated.hs_codes.length > 0) {
        hsCodesApi.descriptions(updated.hs_codes).then(setHsDescriptions).catch(console.error);
      }
      // Update localStorage
      localStorage.setItem("niryat_user", JSON.stringify(updated));
      setMessage("Profile updated successfully!");
    } catch (err) {
      setMessage("Failed to update profile.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <AuthLayout>
      <div className="max-w-2xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <User className="text-[var(--primary-light)]" /> Profile
          </h1>
          <p className="text-[var(--text-secondary)] mt-1">
            Manage your account and export preferences
          </p>
        </div>

        <div className="bg-[var(--bg-card)] rounded-xl p-8 border border-[var(--border)] space-y-6">
          {/* Email (read-only) */}
          <div>
            <label className="block text-sm text-[var(--text-secondary)] mb-1">Email</label>
            <input
              type="email"
              value={data?.email || ""}
              disabled
              className="w-full px-4 py-2.5 rounded-lg bg-[var(--bg-dark)] border border-[var(--border)] text-[var(--text-secondary)] cursor-not-allowed"
            />
          </div>

          {/* Full Name */}
          <div>
            <label className="block text-sm text-[var(--text-secondary)] mb-1">Full Name</label>
            <input
              type="text"
              value={form.full_name}
              onChange={(e) => setForm((p) => ({ ...p, full_name: e.target.value }))}
              className="w-full px-4 py-2.5 rounded-lg bg-[var(--bg-dark)] border border-[var(--border)] text-[var(--text-primary)] focus:border-[var(--primary-light)] focus:outline-none"
            />
          </div>

          {/* Company */}
          <div>
            <label className="block text-sm text-[var(--text-secondary)] mb-1">Company Name</label>
            <input
              type="text"
              value={form.company_name}
              onChange={(e) => setForm((p) => ({ ...p, company_name: e.target.value }))}
              className="w-full px-4 py-2.5 rounded-lg bg-[var(--bg-dark)] border border-[var(--border)] text-[var(--text-primary)] focus:border-[var(--primary-light)] focus:outline-none"
            />
          </div>

          {/* State */}
          <div>
            <label className="block text-sm text-[var(--text-secondary)] mb-1">State</label>
            <input
              type="text"
              value={form.state}
              onChange={(e) => setForm((p) => ({ ...p, state: e.target.value }))}
              placeholder="e.g. Maharashtra"
              className="w-full px-4 py-2.5 rounded-lg bg-[var(--bg-dark)] border border-[var(--border)] text-[var(--text-primary)] focus:border-[var(--primary-light)] focus:outline-none"
            />
          </div>

          {/* HS Codes */}
          <div>
            <label className="block text-sm text-[var(--text-secondary)] mb-1">
              Your Product HS Codes
            </label>
            <p className="text-xs text-[var(--text-secondary)] mb-2">
              Search by product name or HS code to find and add your export products.
            </p>

            {/* HS Code badges with descriptions */}
            <div className="flex flex-wrap gap-2 mb-3">
              {hsCodes.map((code) => (
                <span
                  key={code}
                  className="inline-flex items-center gap-1 px-3 py-1.5 bg-[var(--primary)] rounded-full text-sm"
                >
                  <span className="font-medium">HS {code}</span>
                  {hsDescriptions[code] && (
                    <span className="text-blue-200 text-xs ml-0.5">
                      &middot; {hsDescriptions[code]}
                    </span>
                  )}
                  <button
                    onClick={() => removeHsCode(code)}
                    className="hover:text-red-300 transition-colors ml-1"
                  >
                    <X size={14} />
                  </button>
                </span>
              ))}
            </div>

            {/* Search input with autocomplete */}
            <div className="relative" ref={dropdownRef}>
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-secondary)]" />
                  <input
                    type="text"
                    value={newHsCode}
                    onChange={(e) => handleSearchInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        if (searchResults.length > 0) {
                          addHsCode(searchResults[0].hs_code, searchResults[0].product_description);
                        } else if (newHsCode.trim()) {
                          addHsCode(newHsCode);
                        }
                      }
                    }}
                    onFocus={() => { if (searchResults.length > 0) setShowDropdown(true); }}
                    placeholder="Search by product name or HS code..."
                    className="w-full pl-9 pr-4 py-2.5 rounded-lg bg-[var(--bg-dark)] border border-[var(--border)] text-[var(--text-primary)] focus:border-[var(--primary-light)] focus:outline-none"
                  />
                </div>
                <button
                  onClick={() => {
                    if (searchResults.length > 0) {
                      addHsCode(searchResults[0].hs_code, searchResults[0].product_description);
                    } else if (newHsCode.trim()) {
                      addHsCode(newHsCode);
                    }
                  }}
                  className="px-4 py-2.5 rounded-lg bg-[var(--border)] hover:bg-[var(--primary)] text-[var(--text-primary)] hover:text-white transition-colors"
                >
                  <Plus size={20} />
                </button>
              </div>

              {/* Autocomplete dropdown */}
              {showDropdown && searchResults.length > 0 && (
                <div className="absolute z-50 w-full mt-1 bg-[var(--bg-card)] border border-[var(--border)] rounded-lg shadow-xl max-h-60 overflow-y-auto">
                  {searchResults.map((result) => (
                    <button
                      key={result.hs_code}
                      onClick={() => addHsCode(result.hs_code, result.product_description)}
                      disabled={hsCodes.includes(result.hs_code)}
                      className="w-full text-left px-4 py-2.5 hover:bg-[var(--border)]/40 transition-colors flex items-center justify-between gap-3 disabled:opacity-40 disabled:cursor-not-allowed"
                    >
                      <div className="min-w-0">
                        <span className="font-medium text-sm">HS {result.hs_code}</span>
                        {result.product_description && (
                          <span className="text-xs text-[var(--text-secondary)] ml-2">
                            {result.product_description}
                          </span>
                        )}
                      </div>
                      {hsCodes.includes(result.hs_code) && (
                        <span className="text-xs text-[var(--text-secondary)] shrink-0">Added</span>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Save */}
          {message && (
            <div
              className={`px-4 py-2 rounded-lg text-sm ${
                message.includes("success")
                  ? "bg-[var(--success-bg)] border border-[var(--success-border)] text-[var(--success-text)]"
                  : "bg-[var(--error-bg)] border border-[var(--error-border)] text-[var(--error-text)]"
              }`}
            >
              {message}
            </div>
          )}

          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center gap-2 px-6 py-2.5 rounded-lg bg-[var(--primary)] hover:bg-[var(--primary-light)] text-white font-medium transition-colors disabled:opacity-50"
          >
            <Save size={18} />
            {saving ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </div>
    </AuthLayout>
  );
}
