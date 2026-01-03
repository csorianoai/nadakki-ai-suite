"use client";
export default function LibraryPromptsPage() {
  const prompts = [
    { name: "Product Launch Post", category: "Social", uses: 234, rating: 4.9 },
    { name: "Welcome Email Sequence", category: "Email", uses: 189, rating: 4.7 },
    { name: "Ad Copy Generator", category: "Ads", uses: 456, rating: 4.8 },
    { name: "Blog Outline Creator", category: "Content", uses: 123, rating: 4.6 },
  ];

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 32 }}>
        <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>📝 Prompt Library</h1>
        <button style={{ padding: "12px 24px", backgroundColor: "#22c55e", border: "none", borderRadius: 10, color: "white", fontWeight: 600, cursor: "pointer" }}>
          + Nuevo Prompt
        </button>
      </div>
      
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {prompts.map((p, i) => (
          <div key={i} style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 12, padding: 20, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <h4 style={{ color: "#f8fafc", margin: "0 0 4px 0" }}>{p.name}</h4>
              <span style={{ color: "#8b5cf6", fontSize: 12 }}>{p.category}</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
              <span style={{ color: "#f59e0b" }}>⭐ {p.rating}</span>
              <span style={{ color: "#64748b", fontSize: 13 }}>{p.uses} usos</span>
              <button style={{ padding: "8px 16px", backgroundColor: "#8b5cf6", border: "none", borderRadius: 8, color: "white", cursor: "pointer" }}>Usar</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
