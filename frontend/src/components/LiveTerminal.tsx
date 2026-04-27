"use client";

import { useEffect, useRef } from "react";

export interface LogMessage {
  id: number;
  agent_id: string;
  action: string;
  message: string;
  timestamp: string;
}

interface LiveTerminalProps {
  logs: LogMessage[];
}

const ACTION_COLORS: Record<string, string> = {
  THINKING: "#5b6ee1",
  WORKING: "#f4b41b",
  DONE: "#5cce84",
  ERROR: "#b13e53",
  PARLIAMENT: "#d95763",
  VOTING: "#df7126",
  CONNECT: "#5cce84",
  DISCONNECT: "#b13e53",
  MANAGER_RESPONSE: "#f4b41b",
};

export default function LiveTerminal({ logs }: LiveTerminalProps) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      height: "100%",
      width: "100%",
      background: "#0c0d14",
      color: "#fff",
      padding: 12,
      boxSizing: "border-box",
      overflow: "hidden",
    }}>
      {/* Header */}
      <div style={{
        borderBottom: "1px solid #222",
        paddingBottom: 8,
        marginBottom: 8,
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        flexShrink: 0,
      }}>
        <span style={{ color: "#f4b41b", fontSize: 10, fontFamily: "var(--font-press-start), monospace", textTransform: "uppercase", letterSpacing: 1 }}>
          Agent Activity Logs
        </span>
        <span style={{ color: "#5cce84", fontSize: 8, animation: "pulse 2s infinite" }}>● LIVE</span>
      </div>

      {/* Log Entries */}
      <div style={{
        flex: 1,
        overflowY: "auto",
        overflowX: "hidden",
        paddingRight: 4,
      }}>
        {logs.length === 0 && (
          <p style={{ color: "#555", fontStyle: "italic", fontSize: 11 }}>Đang chờ tín hiệu từ các Agents...</p>
        )}
        {logs.map((log) => (
          <div key={log.id} style={{
            borderLeft: `2px solid ${ACTION_COLORS[log.action.toUpperCase()] || "#333"}`,
            paddingLeft: 8,
            paddingTop: 4,
            paddingBottom: 4,
            marginBottom: 6,
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8 }}>
              <span style={{
                fontWeight: 700,
                fontSize: 9,
                color: ACTION_COLORS[log.action.toUpperCase()] || "#aaa",
                textTransform: "uppercase",
              }}>
                [{log.agent_id}] {log.action}
              </span>
              <span style={{ fontSize: 7, color: "#555", flexShrink: 0 }}>{log.timestamp}</span>
            </div>
            <p style={{ color: "#999", fontSize: 10, margin: "2px 0 0 0", lineHeight: 1.5, wordBreak: "break-word" }}>
              {log.message}
            </p>
          </div>
        ))}
        <div ref={endRef} />
      </div>

      {/* Footer */}
      <div style={{
        borderTop: "1px solid #222",
        paddingTop: 6,
        marginTop: 6,
        fontSize: 7,
        color: "#444",
        display: "flex",
        justifyContent: "space-between",
        flexShrink: 0,
      }}>
        <span>LINK: ESTABLISHED</span>
        <span>NODE: OK</span>
      </div>
    </div>
  );
}
