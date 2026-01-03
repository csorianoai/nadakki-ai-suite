import { useState, useEffect, useCallback } from "react";

const API_BASE = "/api/v1";

export default function useConnections(tenantId) {
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchConnections = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/connections`, { headers: { "X-Tenant-Id": tenantId } });
      const data = await res.json();
      setConnections(data.connections || []);
    } catch (err) { setError(err.message); }
    finally { setLoading(false); }
  }, [tenantId]);

  const connect = async (platform) => {
    const redirectUri = `${window.location.origin}/oauth/callback`;
    const res = await fetch(`${API_BASE}/connections/${platform}/auth-url?redirect_uri=${encodeURIComponent(redirectUri)}`, { headers: { "X-Tenant-Id": tenantId } });
    const data = await res.json();
    window.location.href = data.auth_url;
  };

  const disconnect = async (id) => {
    await fetch(`${API_BASE}/connections/${id}`, { method: "DELETE", headers: { "X-Tenant-Id": tenantId } });
    setConnections(prev => prev.filter(c => c.id !== id));
  };

  useEffect(() => { if (tenantId) fetchConnections(); }, [tenantId, fetchConnections]);

  return { connections, loading, error, refresh: fetchConnections, connect, disconnect };
}
