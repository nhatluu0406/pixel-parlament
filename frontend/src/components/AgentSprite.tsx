"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";

interface AgentSpriteProps {
  id: string;
  name: string;
  role?: string;
  state: string;
  initialPosition: { x: number; y: number };
}

// Sprite sheet: 1024x1024, 4 cols x 4 rows, each cell = 256x256
// Columns: 0=Front, 1=Back, 2=Right, 3=Left
// Rows: 0=Director, 1=Code Ninja, 2=Web Scout, 3=Sys Admin
const CELL = 256;
const DISPLAY_SIZE = 96; // px displayed on screen

export default function AgentSprite({ id, name, state, initialPosition }: AgentSpriteProps) {
  const [pos, setPos] = useState(initialPosition);
  const [facingRight, setFacingRight] = useState(true);
  const [isWalking, setIsWalking] = useState(false);
  const [col, setCol] = useState(0); // sprite column (direction frame)

  const row = (parseInt(id) - 1) % 4; // sprite row (character)

  // Frame selection based on direction and state
  useEffect(() => {
    if (state === "working") {
      setCol(1); // Back frame when working at desk
    } else if (isWalking) {
      setCol(facingRight ? 2 : 3); // Right or Left
    } else {
      setCol(0); // Front when idle
    }
  }, [state, isWalking, facingRight]);

  // Wander logic for idle state
  useEffect(() => {
    if (state !== "idle") {
      setIsWalking(false);
      return;
    }

    const wander = () => {
      const newX = Math.max(5, Math.min(90, pos.x + (Math.random() - 0.5) * 20));
      const newY = Math.max(20, Math.min(75, pos.y + (Math.random() - 0.5) * 15));
      setFacingRight(newX > pos.x);
      setIsWalking(true);
      setPos({ x: newX, y: newY });
      setTimeout(() => setIsWalking(false), 2000);
    };

    const interval = setInterval(wander, 5000 + Math.random() * 5000);
    return () => clearInterval(interval);
  }, [state, pos.x, pos.y]);

  // Move to desk when working
  useEffect(() => {
    if (state === "working") {
      const deskPositions = [
        { x: 28, y: 40 },
        { x: 58, y: 40 },
        { x: 28, y: 66 },
        { x: 58, y: 66 },
      ];
      const desk = deskPositions[row % deskPositions.length];
      setFacingRight(desk.x > pos.x);
      setIsWalking(true);
      setPos(desk);
      setTimeout(() => setIsWalking(false), 2000);
    }
  }, [state, row]);

  // Calculate background-position in pixels
  // We scale the sheet so each cell = DISPLAY_SIZE
  // Total sheet display size = DISPLAY_SIZE * 4
  const sheetDisplaySize = DISPLAY_SIZE * 4;
  const bgX = -(col * DISPLAY_SIZE);
  const bgY = -(row * DISPLAY_SIZE);

  return (
    <motion.div
      animate={{ left: `${pos.x}%`, top: `${pos.y}%` }}
      transition={{ duration: 2, ease: "easeInOut" }}
      style={{ position: "absolute" }}
      className="flex flex-col items-center z-20 -translate-x-1/2 -translate-y-1/2 cursor-pointer group"
    >
      {/* Status Bubble */}
      <AnimatePresence>
        {state !== "idle" && (
          <motion.div
            initial={{ opacity: 0, y: 5, scale: 0.7 }}
            animate={{ opacity: 1, y: -12, scale: 1 }}
            exit={{ opacity: 0, y: 5, scale: 0.7 }}
            className="absolute -top-14 bg-white border-2 border-black px-3 py-1 rounded-lg shadow-lg z-30 whitespace-nowrap"
          >
            <span className="text-xs text-black font-bold uppercase">
              {state === "thinking" && "💡 Đang suy nghĩ..."}
              {state === "working" && "⌨️ Đang làm việc..."}
              {state === "voting" && "🗳️ Đang bỏ phiếu..."}
            </span>
            <div className="absolute -bottom-[6px] left-1/2 -translate-x-1/2 w-[8px] h-[8px] bg-white border-b-2 border-r-2 border-black rotate-45" />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Sprite from office_sprites.png */}
      <motion.div
        animate={
          state === "working"
            ? { y: [0, -3, 0] }
            : isWalking
            ? { y: [0, -2, 0, -2, 0] }
            : {}
        }
        transition={{ repeat: Infinity, duration: state === "working" ? 0.4 : 0.6 }}
      >
        <div
          style={{
            width: DISPLAY_SIZE,
            height: DISPLAY_SIZE,
            backgroundImage: "url(/office_sprites_clean.png)",
            backgroundSize: `${sheetDisplaySize}px ${sheetDisplaySize}px`,
            backgroundPosition: `${bgX}px ${bgY}px`,
            backgroundRepeat: "no-repeat",
            imageRendering: "pixelated",
          }}
        />
      </motion.div>

      {/* Name Tag */}
      <div className="mt-0 bg-black/85 px-3 py-1 rounded border border-gray-500 text-sm text-white font-bold whitespace-nowrap uppercase tracking-wide">
        {name}
      </div>
    </motion.div>
  );
}
