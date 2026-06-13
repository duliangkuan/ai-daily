"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CodeIcon, TeachIcon, HandshakeIcon } from "@/components/Icons";
import { WECHAT_QR, WECHAT_ID } from "@/lib/config";

const SERVICES = [
  {
    title: "定制开发",
    Icon: CodeIcon,
    desc: "AI 公众号 / 短视频自动化流水线、Agent 工作流、数据抓取与精选系统、网站与小程序——从 0 到 1 帮你跑通可上线的产品。",
    points: ["端到端落地，不止给方案", "AI 内容流水线 / Agent / 全栈", "可交付源码，长期可维护"],
  },
  {
    title: "授课服务",
    Icon: TeachIcon,
    desc: "面向团队和个人的 AI 实战培训：Claude Code / Agent 开发、提示工程、AI 内容生产工作流，理论加上能直接复用的工程实践。",
    points: ["企业内训 / 一对一陪跑", "Claude Code 与 Agent 实战", "可复用的工程模板与方法论"],
  },
];

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  show: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, delay: i * 0.1, ease: [0.22, 1, 0.36, 1] as const },
  }),
};

export default function Collaborate() {
  const [showQr, setShowQr] = useState(false);
  const [qrOk, setQrOk] = useState(true);

  return (
    <section id="collaborate" className="mx-auto max-w-5xl scroll-mt-24 px-6 py-20">
      <motion.h2
        variants={fadeUp}
        initial="hidden"
        whileInView="show"
        viewport={{ once: true }}
        className="mb-4 text-center text-3xl font-bold text-white sm:text-4xl"
      >
        有需求？<span className="text-gradient">找我合作</span>
      </motion.h2>
      <motion.p
        variants={fadeUp}
        initial="hidden"
        whileInView="show"
        viewport={{ once: true }}
        custom={1}
        className="mb-12 text-center text-white/55"
      >
        这套日报系统就是独立开发跑通的。我同样承接 AI 相关的<span className="text-white/80">定制开发</span>与<span className="text-white/80">授课服务</span>，欢迎扫码聊聊。
      </motion.p>

      <div className="grid gap-6 md:grid-cols-2">
        {SERVICES.map((s, i) => (
          <motion.div
            key={s.title}
            variants={fadeUp}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true }}
            custom={i}
            className="glass glass-hover flex flex-col rounded-2xl p-8"
          >
            <div className="flex flex-col items-center text-center">
              <span className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-white/5">
                <s.Icon size={30} />
              </span>
              <h3 className="mb-2 text-xl font-semibold text-white">{s.title}</h3>
              <p className="text-sm leading-relaxed text-white/55">{s.desc}</p>
            </div>
            <ul className="mt-6 space-y-3">
              {s.points.map((p) => (
                <li key={p} className="flex items-center gap-3 text-sm text-white/75">
                  <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-neon-cyan shadow-[0_0_8px_rgba(34,211,238,0.7)]" />
                  <span>{p}</span>
                </li>
              ))}
            </ul>
          </motion.div>
        ))}
      </div>

      {/* 找我合作 CTA + 微信二维码 */}
      <motion.div
        variants={fadeUp}
        initial="hidden"
        whileInView="show"
        viewport={{ once: true }}
        custom={2}
        className="mt-10 flex flex-col items-center"
      >
        <button
          type="button"
          onClick={() => setShowQr((v) => !v)}
          aria-expanded={showQr}
          className="btn-neon inline-flex items-center justify-center gap-2 rounded-xl px-8 py-3.5 text-sm font-semibold text-ink-900"
        >
          <HandshakeIcon size={18} />
          找我合作 · 微信扫码
        </button>

        <AnimatePresence initial={false}>
          {showQr && (
            <motion.div
              initial={{ opacity: 0, y: 12, height: 0 }}
              animate={{ opacity: 1, y: 0, height: "auto" }}
              exit={{ opacity: 0, y: 12, height: 0 }}
              transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
              className="overflow-hidden"
            >
              <div className="glass mt-8 flex flex-col items-center rounded-2xl p-8 text-center">
                {qrOk ? (
                  <div className="overflow-hidden rounded-2xl shadow-[0_0_36px_rgba(34,211,238,0.22)]">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={WECHAT_QR}
                      alt="作者个人微信二维码"
                      width={232}
                      height={232}
                      className="h-[232px] w-[232px] object-contain"
                      onError={() => setQrOk(false)}
                    />
                  </div>
                ) : (
                  <div className="flex h-[232px] w-[232px] flex-col items-center justify-center rounded-2xl border border-dashed border-white/20 text-center text-xs text-white/35">
                    <span className="mb-1 text-2xl">⌁</span>
                    微信码待上传
                    <br />
                    (public/qr-wechat.jpg)
                  </div>
                )}
                <p className="mt-4 text-sm text-white/70">微信扫一扫，添加好友聊合作</p>
                <p className="mt-1 flex items-center gap-2 text-xs text-white/45">
                  <span>微信号</span>
                  <span className="select-all font-mono font-semibold text-neon-cyan">{WECHAT_ID}</span>
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </section>
  );
}
