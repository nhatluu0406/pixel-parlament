"use client";

import { useEffect, useState, useRef } from "react";
import OfficeCanvas, { AgentData } from "@/components/OfficeCanvas";
import LiveTerminal, { LogMessage } from "@/components/LiveTerminal";
import Link from "next/link";

export default function Home() {
  const [agents, setAgents] = useState<AgentData[]>([]);
  const [logs, setLogs] = useState<LogMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [chatMessages, setChatMessages] = useState<{role: string, text: string}[]>([]);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const res = await fetch("http://localhost:8080/api/agents");
        if (!res.ok) return;
        const data = await res.json();
        setAgents(data.map((a: any) => ({ 
            id: String(a.id), 
            name: a.name, 
            state: a.status || "idle" 
        })));
      } catch (e) {
        console.error("Failed to fetch agents", e);
      }
    };
    fetchAgents();

    const ws = new WebSocket("ws://localhost:8080/ws");
    ws.onopen = () => {
      setIsConnected(true);
      setLogs(p => [...p, { id: Date.now(), agent_id: "SYSTEM", action: "CONNECT", message: "Parliament Link Online.", timestamp: new Date().toLocaleTimeString() }]);
    };
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLogs(p => [...p, { id: Date.now(), agent_id: data.agent_id || "?", action: data.action || "INFO", message: data.message || "", timestamp: new Date().toLocaleTimeString() }].slice(-50));
        if (data.agent_id && data.agent_id !== "SYSTEM") {
          setAgents(prev => prev.map(a => a.id === String(data.agent_id) ? { ...a, state: data.sprite_state || "idle" } : a));
        }
        if (data.action === "MANAGER_RESPONSE") {
          setChatMessages(p => [...p, { role: "director", text: data.message }]);
        }
      } catch {}
    };
    ws.onclose = () => setIsConnected(false);
    return () => ws.close();
  }, []);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    const msg = chatInput;
    setChatMessages(p => [...p, { role: "user", text: msg }]);
    setChatInput("");
    setIsProcessing(true);
    try {
      await fetch("http://localhost:8080/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg }),
      });
    } catch {
      setChatMessages(p => [...p, { role: "system", text: "Lỗi kết nối." }]);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div style={{
      display: "flex",
      flexDirection: "row",
      width: "100vw",
      height: "100vh",
      overflow: "hidden",
      background: "#000",
      margin: 0,
      padding: 0,
      boxSizing: "border-box",
    }}>
      {/* LEFT: Office (70%) */}
      <div style={{
        width: "70%",
        height: "100%",
        position: "relative",
        overflow: "hidden",
        borderRight: "3px solid #333c57",
        flexShrink: 0,
        boxSizing: "border-box",
      }}>
        <OfficeCanvas agents={agents} />

        {/* Chat Dialogue Box */}
        <div style={{
          position: "absolute",
          bottom: 16,
          left: "50%",
          transform: "translateX(-50%)",
          width: "92%",
          zIndex: 50,
          boxSizing: "border-box",
        }}>
          <div style={{
            background: "rgba(10, 12, 20, 0.95)",
            border: "3px solid #f4b41b",
            borderRadius: 8,
            padding: 12,
            boxShadow: "4px 4px 0 rgba(0,0,0,0.6)",
          }}>
            {/* Chat History Area */}
            <div style={{
              height: 100,
              overflowY: "auto",
              marginBottom: 10,
              fontSize: 16,
              lineHeight: 1.6,
            }}>
              {chatMessages.length === 0 ? (
                <p style={{ color: "#888", fontStyle: "italic", margin: 0 }}>Trao đổi với The Director...</p>
              ) : (
                chatMessages.map((m, i) => (
                  <div key={i} style={{ marginBottom: 10 }}>
                    <span style={{
                      fontWeight: 700,
                      fontSize: 14,
                      color: m.role === "user" ? "#5b6ee1" : "#f4b41b",
                      textTransform: "uppercase",
                    }}>
                      {m.role === "user" ? "BẠN: " : "DIRECTOR: "}
                    </span>
                    <span style={{ color: "#e0e0e0", marginLeft: 8 }}>{m.text}</span>
                  </div>
                ))
              )}
              <div ref={chatEndRef} />
            </div>
            {/* Input */}
            <form onSubmit={handleSend} style={{ display: "flex", gap: 12, borderTop: "1px solid #444", paddingTop: 12 }}>
              <input
                type="text"
                value={chatInput}
                onChange={e => setChatInput(e.target.value)}
                disabled={isProcessing}
                placeholder="Nhập nội dung trao đổi..."
                style={{
                  flex: 1,
                  background: "transparent",
                  border: "none",
                  outline: "none",
                  color: "#fff",
                  fontSize: 16,
                }}
              />
              <button
                type="submit"
                disabled={isProcessing}
                style={{
                  background: isProcessing ? "#555" : "#5b6ee1",
                  color: "#fff",
                  border: "2px solid #333",
                  padding: "8px 24px",
                  cursor: isProcessing ? "not-allowed" : "pointer",
                  fontSize: 16,
                  fontWeight: 700,
                  textTransform: "uppercase",
                }}
              >
                GỬI
              </button>
            </form>
          </div>
        </div>

        {/* Nav */}
        <div style={{ position: "absolute", top: 12, right: 12, zIndex: 30 }}>
          <Link href="/admin" style={{
            background: "#5b6ee1",
            color: "#fff",
            border: "2px solid #333",
            padding: "8px 16px",
            fontSize: 16,
            textDecoration: "none",
            fontWeight: 700,
            textTransform: "uppercase",
          }}>
            Cấu hình
          </Link>
        </div>
      </div>

      {/* RIGHT: Activity Logs (30%) */}
      <div style={{
        width: "30%",
        height: "100%",
        overflow: "hidden",
        flexShrink: 0,
        boxSizing: "border-box",
      }}>
        <LiveTerminal logs={logs} />
      </div>

      {/* Connection HUD */}
      <div style={{
        position: "fixed",
        top: 8,
        right: 8,
        zIndex: 100,
        display: "flex",
        alignItems: "center",
        gap: 6,
        background: "rgba(0,0,0,0.8)",
        padding: "3px 8px",
        border: "1px solid #444",
        borderRadius: 4,
      }}>
        <span style={{ fontSize: 7, color: "#777", textTransform: "uppercase", letterSpacing: 2 }}>Link</span>
        <div style={{
          width: 7,
          height: 7,
          borderRadius: "50%",
          background: isConnected ? "#5cce84" : "#b13e53",
          boxShadow: isConnected ? "0 0 6px #5cce84" : "0 0 6px #b13e53",
        }} />
      </div>
    </div>
  );
}
