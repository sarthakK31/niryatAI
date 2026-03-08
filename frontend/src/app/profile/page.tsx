"use client";
import { useState, useEffect } from "react";
import AuthLayout from "@/components/AuthLayout";
import { profile as profileApi } from "@/lib/api";
import { User, Save, Plus, X } from "lucide-react";

interface ProfileData {
  id: string;
  email: string;
  full_name: string;
  company_name: string | null;
  hs_codes: string[] | null;
  state: string | null;
}

export default function ProfilePage() {
  const [data, setData] = useState<ProfileData | null>(null);
  const [form, setForm] = useState({
    full_name: "",
    company_name: "",
    state: "",
  });
  const [hsCodes, setHsCodes] = useState<string[]>([]);
  const [newHsCode, setNewHsCode] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    profileApi.get().then((d: ProfileData) => {
      setData(d);
      setForm({
        full_name: d.full_name,
        company_name: d.company_name || "",
        state: d.state || "",
      });
      setHsCodes(d.hs_codes || []);
    }).catch(console.error);
  }, []);

  const addHsCode = () => {
    const code = newHsCode.trim();
    if (code && !hsCodes.includes(code)) {
      setHsCodes((prev) => [...prev, code]);
      setNewHsCode("");
    }
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
      setData(updated);
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
              className="w-full px-4 py-2.5 rounded-lg bg-[var(--bg-dark)] border border-[var(--border)] text-white focus:border-[var(--primary-light)] focus:outline-none"
            />
          </div>

          {/* Company */}
          <div>
            <label className="block text-sm text-[var(--text-secondary)] mb-1">Company Name</label>
            <input
              type="text"
              value={form.company_name}
              onChange={(e) => setForm((p) => ({ ...p, company_name: e.target.value }))}
              className="w-full px-4 py-2.5 rounded-lg bg-[var(--bg-dark)] border border-[var(--border)] text-white focus:border-[var(--primary-light)] focus:outline-none"
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
              className="w-full px-4 py-2.5 rounded-lg bg-[var(--bg-dark)] border border-[var(--border)] text-white focus:border-[var(--primary-light)] focus:outline-none"
            />
          </div>

          {/* HS Codes */}
          <div>
            <label className="block text-sm text-[var(--text-secondary)] mb-1">
              Your Product HS Codes
            </label>
            <p className="text-xs text-[var(--text-secondary)] mb-2">
              Add the HS codes for the products you export or want to export. This helps us
              personalize market recommendations.
            </p>
            <div className="flex flex-wrap gap-2 mb-3">
              {hsCodes.map((code) => (
                <span
                  key={code}
                  className="inline-flex items-center gap-1 px-3 py-1 bg-[var(--primary)] rounded-full text-sm"
                >
                  HS {code}
                  <button
                    onClick={() => removeHsCode(code)}
                    className="hover:text-red-300 transition-colors"
                  >
                    <X size={14} />
                  </button>
                </span>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={newHsCode}
                onChange={(e) => setNewHsCode(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addHsCode())}
                placeholder="e.g. 0901"
                className="flex-1 px-4 py-2.5 rounded-lg bg-[var(--bg-dark)] border border-[var(--border)] text-white focus:border-[var(--primary-light)] focus:outline-none"
              />
              <button
                onClick={addHsCode}
                className="px-4 py-2.5 rounded-lg bg-[var(--border)] hover:bg-[var(--primary)] text-white transition-colors"
              >
                <Plus size={20} />
              </button>
            </div>
          </div>

          {/* Save */}
          {message && (
            <div
              className={`px-4 py-2 rounded-lg text-sm ${
                message.includes("success")
                  ? "bg-green-900/30 border border-green-700 text-green-300"
                  : "bg-red-900/30 border border-red-700 text-red-300"
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
