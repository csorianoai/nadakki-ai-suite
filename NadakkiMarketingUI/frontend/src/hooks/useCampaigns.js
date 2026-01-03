import { useState, useEffect, useCallback } from "react";

const API_BASE = "/api/v1";

export default function useCampaigns(tenantId) {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchCampaigns = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/campaigns`, { headers: { "X-Tenant-Id": tenantId } });
      const data = await res.json();
      setCampaigns(data.campaigns || []);
    } catch (err) { setError(err.message); }
    finally { setLoading(false); }
  }, [tenantId]);

  const createCampaign = async (data) => {
    const res = await fetch(`${API_BASE}/campaigns`, {
      method: "POST", headers: { "Content-Type": "application/json", "X-Tenant-Id": tenantId },
      body: JSON.stringify(data)
    });
    const newCampaign = await res.json();
    setCampaigns(prev => [newCampaign, ...prev]);
    return newCampaign;
  };

  const updateCampaign = async (id, updates) => {
    const res = await fetch(`${API_BASE}/campaigns/${id}`, {
      method: "PATCH", headers: { "Content-Type": "application/json", "X-Tenant-Id": tenantId },
      body: JSON.stringify(updates)
    });
    const updated = await res.json();
    setCampaigns(prev => prev.map(c => c.id === id ? updated : c));
    return updated;
  };

  const deleteCampaign = async (id) => {
    await fetch(`${API_BASE}/campaigns/${id}`, { method: "DELETE", headers: { "X-Tenant-Id": tenantId } });
    setCampaigns(prev => prev.filter(c => c.id !== id));
  };

  const publishCampaign = async (id) => {
    const res = await fetch(`${API_BASE}/campaigns/${id}/publish`, { method: "POST", headers: { "X-Tenant-Id": tenantId } });
    const published = await res.json();
    setCampaigns(prev => prev.map(c => c.id === id ? published : c));
    return published;
  };

  useEffect(() => { if (tenantId) fetchCampaigns(); }, [tenantId, fetchCampaigns]);

  return { campaigns, loading, error, refresh: fetchCampaigns, createCampaign, updateCampaign, deleteCampaign, publishCampaign };
}
