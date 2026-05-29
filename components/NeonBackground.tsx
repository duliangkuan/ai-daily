"use client";

import { motion } from "framer-motion";

/** 深空底 + 发光网格 + 漂浮霓虹球 */
export default function NeonBackground() {
  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden bg-deepspace">
      <div className="absolute inset-0 grid-overlay" />

      <motion.div
        className="glow-orb"
        style={{ width: 420, height: 420, left: "-6%", top: "8%", background: "#22d3ee" }}
        animate={{ y: [0, -30, 0], opacity: [0.35, 0.55, 0.35] }}
        transition={{ duration: 9, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="glow-orb"
        style={{ width: 480, height: 480, right: "-8%", top: "2%", background: "#8b5cf6" }}
        animate={{ y: [0, 28, 0], opacity: [0.3, 0.5, 0.3] }}
        transition={{ duration: 11, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="glow-orb"
        style={{ width: 520, height: 520, left: "35%", bottom: "-18%", background: "#d946ef" }}
        animate={{ y: [0, -22, 0], opacity: [0.22, 0.4, 0.22] }}
        transition={{ duration: 13, repeat: Infinity, ease: "easeInOut" }}
      />
    </div>
  );
}
