"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";

/**
 * 订阅邮件样张 —— 1:1 还原订阅者真实收到的邮件
 * （欢迎信 + 每天早晚两封通知）。邮件本体为通知式：
 * 一键直达当日全文 /today，正文不堆新闻（投递更稳）。
 */

type Sample = {
  tag: string;
  subject: string;
  badge: string;
  lines: string[];
};

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  show: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, delay: i * 0.1, ease: [0.22, 1, 0.36, 1] as const },
  }),
};

function buildSamples(dateLabel: string): Sample[] {
  return [
    {
      tag: "订阅当下 · 即时送达",
      subject: "欢迎订阅 AI 日报 ✦",
      badge: "🎉 欢迎订阅！",
      lines: [
        "你已成功订阅，以后每天「早 8 点」与「晚 9 点」各收到一封 AI 精选日报。",
        "今天的这份已经为你备好，点下面直接看 👇",
      ],
    },
    {
      tag: "每天早 8:00",
      subject: `【AI 日报】早报 · ${dateLabel}`,
      badge: `早报 · ${dateLabel} 已更新`,
      lines: ["今天的 AI 精选已经准备好，点下面查看 👇"],
    },
    {
      tag: "每天晚 21:00",
      subject: `【AI 日报】晚报 · ${dateLabel}`,
      badge: `晚报 · ${dateLabel} 已更新`,
      lines: ["今天的 AI 精选已经准备好（含当日全景汇总 + AI 深度分析），点下面查看 👇"],
    },
  ];
}

/** 单封邮件样张 —— 还原 send_digest / lib/mail 的真实排版 */
function MailCard({ sample }: { sample: Sample }) {
  return (
    <div className="glass flex h-full flex-col overflow-hidden rounded-2xl">
      {/* 邮件客户端头：发件人 + 主题 */}
      <div className="border-b border-white/8 bg-white/[0.02] px-4 py-3">
        <div className="text-[11px] uppercase tracking-wider text-neon-cyan/80">
          {sample.tag}
        </div>
        <div className="mt-1.5 flex items-baseline gap-2 text-xs text-white/40">
          <span className="shrink-0">发件人</span>
          <span className="truncate text-white/70">研究Agent的云 &lt;daily@mail.dufengyun.xyz&gt;</span>
        </div>
        <div className="mt-1 truncate text-sm font-medium text-white/85">
          {sample.subject}
        </div>
      </div>

      {/* 邮件正文：1:1 还原真实邮件（深色头 + 白底 + 渐变按钮）；flex 撑满使多卡等高 */}
      <div className="flex flex-1 flex-col bg-[#f4f5f7] p-3">
        <div className="mx-auto flex w-full max-w-[420px] flex-1 flex-col overflow-hidden rounded-lg bg-white">
          <div
            className="px-5 py-5 text-white"
            style={{ background: "linear-gradient(90deg,#0a0a1a,#1a1040)" }}
          >
            <div className="text-[11px] tracking-[0.18em] text-[#22d3ee]">
              研究 AGENT 的云 · AI 日报
            </div>
            <div className="mt-1.5 text-[17px] font-bold">{sample.badge}</div>
          </div>
          <div className="flex flex-1 flex-col px-5 py-5">
            {/* 正文文字区：flex-1 撑开，把按钮顶到底部，多卡按钮对齐 */}
            <div className="flex-1">
              {sample.lines.map((line, i) => (
                <p
                  key={i}
                  className={`text-[13.5px] leading-relaxed ${
                    i === sample.lines.length - 1 ? "mb-5 text-[#6b7280]" : "mb-2.5 text-[#1f2937]"
                  }`}
                >
                  {line}
                </p>
              ))}
            </div>
            <div className="text-center">
              <a
                href="/today"
                className="inline-block rounded-[10px] px-6 py-2.5 text-[13.5px] font-bold text-[#08081a] transition-transform hover:scale-[1.03]"
                style={{ background: "linear-gradient(90deg,#22d3ee,#8b5cf6)" }}
              >
                阅读今日 AI 日报 →
              </a>
            </div>
          </div>
          <div className="border-t border-[#eee] px-5 py-3 text-center text-[11px] leading-relaxed text-[#9aa0a6]">
            每天早晚各一封。不想再收到？<span className="text-[#7c83ff]">点此退订</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function EmailPreview() {
  // 用真实当天日期让样张更贴近实际；客户端挂载后再更新，避免水合不一致
  const [dateLabel, setDateLabel] = useState("2026-05-31");
  useEffect(() => {
    const d = new Date();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    setDateLabel(`${d.getFullYear()}-${m}-${day}`);
  }, []);

  const samples = buildSamples(dateLabel);

  return (
    <section className="mx-auto max-w-6xl px-6 py-20">
      <motion.h2
        variants={fadeUp}
        initial="hidden"
        whileInView="show"
        viewport={{ once: true }}
        className="mb-4 text-center text-3xl font-bold text-white sm:text-4xl"
      >
        你会收到<span className="text-gradient">什么样的邮件</span>
      </motion.h2>
      <motion.p
        variants={fadeUp}
        initial="hidden"
        whileInView="show"
        viewport={{ once: true }}
        custom={1}
        className="mx-auto mb-12 max-w-2xl text-center text-white/55"
      >
        订阅后立即收到一封欢迎信，之后每天早晚各一封精选通知。
        邮件简洁不打扰，一键直达当日全文，下面是真实样张 👇
      </motion.p>

      <div className="grid items-stretch gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {samples.map((s, i) => (
          <motion.div
            key={s.subject}
            variants={fadeUp}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true }}
            custom={i}
            className="h-full"
          >
            <MailCard sample={s} />
          </motion.div>
        ))}
      </div>

      <p className="mt-8 text-center text-xs text-white/35">
        * 完整日报（AI 深度分析 + 精选条目）在网页全文实时呈现，邮件仅作每日提醒，随时可一键退订。
      </p>
    </section>
  );
}
