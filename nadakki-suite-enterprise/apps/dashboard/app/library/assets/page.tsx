"use client";
export default function LibraryAssetsPage() {
  const assets = [
    { name: "Logo Principal", type: "image", format: "PNG", size: "2.4 MB", uses: 45 },
    { name: "Video Producto", type: "video", format: "MP4", size: "24 MB", uses: 12 },
    { name: "Brand Guidelines", type: "document", format: "PDF", size: "5.1 MB", uses: 8 },
    { name: "Iconos Set", type: "image", format: "SVG", size: "340 KB", uses: 89 },
  ];

  const typeIcons: Record<string, string> = { image: "🖼️", video: "🎬", document: "📄" };

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 32 }}>
        <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>📁 Banco de Assets</h1>
        <button style={{ padding: "12px 24px", backgroundColor: "#8b5cf6", border: "none", borderRadius: 10, color: "white", fontWeight: 600, cursor: "pointer" }}>
          + Subir Asset
        </button>
      </div>
      
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16 }}>
        {assets.map((a, i) => (
          <div key={i} style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, overflow: "hidden" }}>
            <div style={{ height: 120, backgroundColor: "rgba(139,92,246,0.1)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <span style={{ fontSize: 40 }}>{typeIcons[a.type]}</span>
            </div>
            <div style={{ padding: 16 }}>
              <h4 style={{ color: "#f8fafc", margin: "0 0 4px 0" }}>{a.name}</h4>
              <p style={{ color: "#64748b", fontSize: 12, margin: "0 0 8px 0" }}>{a.format} • {a.size}</p>
              <span style={{ color: "#94a3b8", fontSize: 12 }}>{a.uses} usos</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
