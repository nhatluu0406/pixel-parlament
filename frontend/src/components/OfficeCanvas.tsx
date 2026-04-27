"use client";

import AgentSprite from "./AgentSprite";

export interface AgentData {
  id: string;
  name: string;
  state: string;
}

interface OfficeCanvasProps {
  agents: AgentData[];
}

// Starting positions spread across the office
const INITIAL_POSITIONS = [
  { x: 35, y: 35 },
  { x: 65, y: 35 },
  { x: 35, y: 60 },
  { x: 65, y: 60 },
];

export default function OfficeCanvas({ agents }: OfficeCanvasProps) {
  return (
    <div style={{ width: "100%", height: "100%", position: "relative", overflow: "hidden", background: "#1a1c2c" }}>
      {/* Background */}
      <img
        src="/office_bg.png"
        alt="Office"
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          objectFit: "cover",
          opacity: 0.65,
          pointerEvents: "none",
          userSelect: "none",
        }}
      />
      <div style={{ position: "absolute", inset: 0, background: "rgba(0,0,0,0.25)", pointerEvents: "none" }} />

      {/* Agents */}
      <div style={{ position: "relative", width: "100%", height: "100%", zIndex: 10 }}>
        {agents.map((agent, index) => (
          <AgentSprite
            key={agent.id}
            id={agent.id}
            name={agent.name}
            state={agent.state}
            initialPosition={INITIAL_POSITIONS[index % INITIAL_POSITIONS.length]}
          />
        ))}
      </div>

      {/* HQ Banner */}
      <div style={{ position: "absolute", top: 12, left: 12, zIndex: 30, pointerEvents: "none" }}>
        <div style={{
          background: "rgba(0,0,0,0.9)",
          border: "2px solid white",
          padding: "6px 10px",
          boxShadow: "3px 3px 0 rgba(0,0,0,0.5)",
        }}>
          <span style={{ color: "#5cce84", fontSize: 11, fontFamily: "var(--font-press-start), monospace", letterSpacing: -1 }}>PIXEL PARLAMENT</span>
        </div>
      </div>

      {/* HUD */}
      <div style={{
        position: "absolute",
        bottom: 8,
        left: 12,
        zIndex: 30,
        background: "rgba(0,0,0,0.8)",
        padding: "3px 8px",
        border: "1px solid #333",
        fontSize: 8,
        color: "#f4b41b",
      }}>
        ACTIVE: {agents.length}
      </div>
    </div>
  );
}
