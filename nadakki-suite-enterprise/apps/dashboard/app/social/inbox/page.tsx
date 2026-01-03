"use client";
import { useState } from "react";

const mockMessages = [
  { id: 1, platform: "instagram", user: "@maria_garcia", avatar: "👩", message: "Me encanta este producto! Donde puedo comprarlo?", time: "Hace 5 min", status: "unread", sentiment: "positive" },
  { id: 2, platform: "facebook", user: "Carlos Rodriguez", avatar: "👨", message: "Tuve un problema con mi pedido #12345", time: "Hace 12 min", status: "unread", sentiment: "negative" },
  { id: 3, platform: "x", user: "@tech_lover", avatar: "🧑", message: "Increible la nueva funcionalidad! 🔥", time: "Hace 25 min", status: "read", sentiment: "positive" },
  { id: 4, platform: "linkedin", user: "Ana Martinez", avatar: "👩‍💼", message: "Interesada en partnership para nuestra empresa", time: "Hace 1 hora", status: "read", sentiment: "neutral" },
  { id: 5, platform: "tiktok", user: "@viral_content", avatar: "🎵", message: "Podemos hacer una colaboracion?", time: "Hace 2 horas", status: "read", sentiment: "positive" },
];

export default function SocialInboxPage() {
  const [messages, setMessages] = useState(mockMessages);
  const [selectedMessage, setSelectedMessage] = useState<any>(null);
  const [filter, setFilter] = useState("all");
  const [reply, setReply] = useState("");

  const platformIcons: Record<string, string> = { instagram: "📸", facebook: "📘", x: "🐦", linkedin: "💼", tiktok: "🎵" };
  const sentimentColors: Record<string, string> = { positive: "#22c55e", negative: "#ef4444", neutral: "#64748b" };

  const filteredMessages = filter === "all" ? messages : messages.filter(m => m.status === filter);
  const unreadCount = messages.filter(m => m.status === "unread").length;

  const sendReply = () => {
    if (reply && selectedMessage) {
      alert(`Respuesta enviada a ${selectedMessage.user}: "${reply}"`);
      setReply("");
    }
  };

  const generateAIReply = () => {
    setReply("¡Hola! Gracias por contactarnos. Estaremos encantados de ayudarte. Un miembro de nuestro equipo se pondrá en contacto contigo en breve. 🙌");
  };

  return (
    <div style={{ padding: 40, backgroundColor: "#0a0f1c", minHeight: "100vh" }}>
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 32, fontWeight: 800, color: "#f8fafc", margin: 0 }}>📬 Social Inbox</h1>
        <p style={{ color: "#94a3b8", marginTop: 8 }}>{unreadCount} mensajes sin leer • Bandeja unificada</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "350px 1fr", gap: 24, height: "calc(100vh - 200px)" }}>
        {/* Messages List */}
        <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, overflow: "hidden", display: "flex", flexDirection: "column" }}>
          <div style={{ padding: 16, borderBottom: "1px solid rgba(51,65,85,0.5)" }}>
            <div style={{ display: "flex", gap: 8 }}>
              {["all", "unread", "read"].map(f => (
                <button key={f} onClick={() => setFilter(f)} style={{
                  padding: "6px 12px", backgroundColor: filter === f ? "#8b5cf6" : "transparent",
                  border: "none", borderRadius: 6, color: "white", cursor: "pointer", fontSize: 13
                }}>
                  {f === "all" ? "Todos" : f === "unread" ? `Sin leer (${unreadCount})` : "Leídos"}
                </button>
              ))}
            </div>
          </div>
          
          <div style={{ flex: 1, overflow: "auto" }}>
            {filteredMessages.map(msg => (
              <div key={msg.id} onClick={() => { setSelectedMessage(msg); setMessages(prev => prev.map(m => m.id === msg.id ? {...m, status: "read"} : m)); }}
                style={{
                  padding: 16, borderBottom: "1px solid rgba(51,65,85,0.3)", cursor: "pointer",
                  backgroundColor: selectedMessage?.id === msg.id ? "rgba(139,92,246,0.1)" : msg.status === "unread" ? "rgba(59,130,246,0.05)" : "transparent"
                }}>
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <span style={{ fontSize: 28 }}>{msg.avatar}</span>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <p style={{ color: "#f8fafc", fontSize: 14, fontWeight: 600, margin: 0 }}>{msg.user}</p>
                      <span style={{ fontSize: 16 }}>{platformIcons[msg.platform]}</span>
                    </div>
                    <p style={{ color: "#94a3b8", fontSize: 13, margin: "4px 0", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{msg.message}</p>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <span style={{ color: "#64748b", fontSize: 11 }}>{msg.time}</span>
                      <span style={{ width: 8, height: 8, borderRadius: "50%", backgroundColor: sentimentColors[msg.sentiment] }} />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Message Detail */}
        <div style={{ backgroundColor: "rgba(30,41,59,0.5)", borderRadius: 16, display: "flex", flexDirection: "column" }}>
          {selectedMessage ? (
            <>
              <div style={{ padding: 24, borderBottom: "1px solid rgba(51,65,85,0.5)" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                  <span style={{ fontSize: 48 }}>{selectedMessage.avatar}</span>
                  <div>
                    <h3 style={{ color: "#f8fafc", fontSize: 18, margin: 0 }}>{selectedMessage.user}</h3>
                    <p style={{ color: "#64748b", fontSize: 13, margin: "4px 0 0 0" }}>{platformIcons[selectedMessage.platform]} {selectedMessage.platform} • {selectedMessage.time}</p>
                  </div>
                  <div style={{ marginLeft: "auto", backgroundColor: `${sentimentColors[selectedMessage.sentiment]}20`, padding: "6px 12px", borderRadius: 20 }}>
                    <span style={{ color: sentimentColors[selectedMessage.sentiment], fontSize: 12, fontWeight: 600 }}>
                      {selectedMessage.sentiment === "positive" ? "😊 Positivo" : selectedMessage.sentiment === "negative" ? "😟 Negativo" : "😐 Neutral"}
                    </span>
                  </div>
                </div>
              </div>
              
              <div style={{ flex: 1, padding: 24, overflow: "auto" }}>
                <div style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: 16, borderRadius: 12 }}>
                  <p style={{ color: "#f8fafc", fontSize: 15, lineHeight: 1.6, margin: 0 }}>{selectedMessage.message}</p>
                </div>
              </div>

              <div style={{ padding: 24, borderTop: "1px solid rgba(51,65,85,0.5)" }}>
                <div style={{ display: "flex", gap: 12, marginBottom: 12 }}>
                  <button onClick={generateAIReply} style={{ padding: "8px 16px", backgroundColor: "rgba(139,92,246,0.2)", border: "none", borderRadius: 8, color: "#8b5cf6", cursor: "pointer", fontWeight: 600 }}>
                    🤖 Generar con IA
                  </button>
                  <button style={{ padding: "8px 16px", backgroundColor: "rgba(255,255,255,0.1)", border: "none", borderRadius: 8, color: "white", cursor: "pointer" }}>📋 Plantillas</button>
                </div>
                <div style={{ display: "flex", gap: 12 }}>
                  <textarea value={reply} onChange={(e) => setReply(e.target.value)} placeholder="Escribe tu respuesta..."
                    style={{ flex: 1, padding: 12, backgroundColor: "rgba(0,0,0,0.3)", border: "1px solid rgba(51,65,85,0.5)", borderRadius: 8, color: "#f8fafc", resize: "none", minHeight: 60 }}
                  />
                  <button onClick={sendReply} style={{ padding: "0 24px", backgroundColor: "#22c55e", border: "none", borderRadius: 8, color: "white", fontWeight: 600, cursor: "pointer" }}>
                    Enviar →
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", color: "#64748b" }}>
              <div style={{ textAlign: "center" }}>
                <p style={{ fontSize: 48, margin: "0 0 16px 0" }}>📬</p>
                <p>Selecciona un mensaje para ver los detalles</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
