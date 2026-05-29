"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CheckIcon } from "@/components/Icons";

type Status = "idle" | "loading" | "success" | "error";

export default function SubscribeForm() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [msg, setMsg] = useState("");

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (status === "loading") return;

    const ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    if (!ok) {
      setStatus("error");
      setMsg("邮箱格式好像不对，再检查一下～");
      return;
    }

    setStatus("loading");
    setMsg("");
    try {
      const res = await fetch("/api/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      const data = await res.json();
      if (res.ok) {
        setStatus("success");
        setMsg(data.message || "订阅成功！明天早上开始，日报准时到达你的邮箱 ✦");
      } else {
        setStatus("error");
        setMsg(data.message || "出了点小问题，稍后再试一下");
      }
    } catch {
      setStatus("error");
      setMsg("网络开小差了，稍后再试");
    }
  }

  return (
    <div className="w-full max-w-xl">
      <AnimatePresence mode="wait">
        {status === "success" ? (
          <motion.div
            key="success"
            initial={{ opacity: 0, scale: 0.92 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass rounded-2xl px-6 py-7 text-center"
          >
            <div className="mb-3 flex justify-center">
              <CheckIcon size={40} />
            </div>
            <p className="text-lg font-medium text-neon-cyan">{msg}</p>
          </motion.div>
        ) : (
          <motion.form
            key="form"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            onSubmit={onSubmit}
            className="flex flex-col gap-3 sm:flex-row"
          >
            <input
              type="email"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                if (status === "error") setStatus("idle");
              }}
              placeholder="输入你的邮箱，每天早晚收到精选 AI 日报"
              className="input-neon h-14 flex-1 rounded-xl px-5 text-base text-white placeholder:text-white/35"
            />
            <button
              type="submit"
              disabled={status === "loading"}
              className="btn-neon h-14 rounded-xl px-7 text-base font-semibold text-ink-900 disabled:opacity-70"
            >
              {status === "loading" ? "订阅中…" : "✦ 立即订阅"}
            </button>
          </motion.form>
        )}
      </AnimatePresence>

      {status === "error" && (
        <motion.p
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-3 text-sm text-neon-magenta"
        >
          {msg}
        </motion.p>
      )}

      {status !== "success" && (
        <p className="mt-4 text-center text-xs text-white/35 sm:text-left">
          完全免费 · 随时可退订 · 我们不会把你的邮箱用于任何别的用途
        </p>
      )}
    </div>
  );
}
