"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CodeIcon, TeachIcon, HandshakeIcon } from "@/components/Icons";
import { WECHAT_QR, WECHAT_ID } from "@/lib/config";

const CHANNELS = ["企业微信", "飞书", "钉钉", "邮件", "公众号", "网页"];

const SERVICES = [
  {
    title: "定制资讯系统",
    Icon: CodeIcon,
    desc: "你看到的这套 AI 日报，就是我搭的。任意领域都能定制同款——金融、医疗、政策法规、行业竞品、舆情监控……全球信源实时抓取，AI 逐条分析精选，每天定时为你报道。",
    points: [
      "任意领域 · 全球信源实时抓取",
      "AI 实时分析 + 智能精选去噪",
      "每日定时自动报道，无需人工",
      "企业微信 / 飞书 / 邮件 / 公众号多渠道直达",
    ],
  },
  {
    title: "授课服务",
    Icon: TeachIcon,
    desc: "面向团队和个人的 AI 实战培训：Claude Code / Agent 开发、提示工程、AI 内容与资讯生产工作流，理论加上能直接复用的工程实践。",
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
    <section id="collaborate" className="mx-auto max-w-5xl scroll-mt-24 px-6 py-24">
      {/* 高亮外框：渐变光环 + 辉光，让整块更醒目 */}
      <motion.div
        variants={fadeUp}
        initial="hidden"
        whileInView="show"
        viewport={{ once: true }}
        className="relative rounded-[28px] p-[1.5px]"
        style={{
          background: "linear-gradient(135deg, #22d3ee, #818cf8 45%, #d946ef)",
          boxShadow: "0 0 60px rgba(34,211,238,0.22), 0 0 120px rgba(217,70,239,0.12)",
        }}
      >
        <div className="bg-deepspace relative overflow-hidden rounded-[27px] px-6 py-14 sm:px-12">
          {/* 角落辉光球 */}
          <div className="glow-orb -right-10 -top-10 h-48 w-48" style={{ background: "#22d3ee" }} />
          <div className="glow-orb -bottom-12 -left-10 h-48 w-48" style={{ background: "#d946ef" }} />

          <div className="relative">
            <div className="mb-5 flex justify-center">
              <span className="glass inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-xs text-white/80">
                <span className="h-2 w-2 animate-pulse rounded-full bg-neon-cyan" />
                可定制 · 同款系统
              </span>
            </div>

            <h2 className="text-center text-3xl font-bold leading-tight text-white sm:text-5xl">
              想要一套<span className="text-gradient">专属的资讯日报</span>？<br className="hidden sm:block" />
              找我合作
            </h2>
            <p className="mx-auto mt-5 max-w-2xl text-center text-base leading-relaxed text-white/60 sm:text-lg">
              我帮你定制化搭建<span className="text-white/85">任意领域的资讯系统</span>：实时抓取 + AI 分析 + 每日报道，
              一键推送到<span className="text-white/85">企业微信、飞书</span>等团队渠道。也提供 AI 实战授课。
            </p>

            {/* 支持渠道 chips */}
            <div className="mx-auto mt-7 flex max-w-3xl flex-wrap justify-center gap-2.5">
              {CHANNELS.map((c) => (
                <span
                  key={c}
                  className="glass rounded-full px-4 py-1.5 text-sm text-white/70"
                >
                  {c}
                </span>
              ))}
            </div>

            {/* 服务卡 */}
            <div className="mt-12 grid gap-6 md:grid-cols-2">
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
            <div className="mt-12 flex flex-col items-center">
              <button
                type="button"
                onClick={() => setShowQr((v) => !v)}
                aria-expanded={showQr}
                className="btn-neon inline-flex items-center justify-center gap-2 rounded-xl px-10 py-4 text-base font-semibold text-ink-900"
              >
                <HandshakeIcon size={20} />
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
            </div>
          </div>
        </div>
      </motion.div>
    </section>
  );
}
