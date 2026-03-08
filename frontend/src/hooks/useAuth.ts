"use client";
import { useState, useEffect } from "react";

interface User {
  id: string;
  email: string;
  full_name: string;
  company_name: string | null;
  hs_codes: string[] | null;
  state: string | null;
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem("niryat_user");
    if (stored) {
      setUser(JSON.parse(stored));
    }
    setLoading(false);
  }, []);

  const login = (token: string, userData: User) => {
    localStorage.setItem("niryat_token", token);
    localStorage.setItem("niryat_user", JSON.stringify(userData));
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem("niryat_token");
    localStorage.removeItem("niryat_user");
    setUser(null);
    window.location.href = "/login";
  };

  return { user, loading, login, logout };
}
