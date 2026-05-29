"use client";

import { motion } from "framer-motion";
import NeonBackground from "@/components/NeonBackground";
import CountUp from "@/components/CountUp";
import SubscribeForm from "@/components/SubscribeForm";
import Support from "@/components/Support";
import { CloudIcon, RadarIcon, FunnelIcon, MailIcon, GithubIcon } from "@/components/Icons";
import { REPO_URL } from "@/lib/config";
import type { ComponentType, SVGProps } from "react";

const SOURCES_A = [
  "OpenAI", "Anthropic", "Google DeepMind", "HuggingFace", "NVIDIA",
  "AWS ML", "smol.ai", "Latent Space", "Import AI", "arXiv",
  "Cursor", "Perplexity", "TechCrunch", "MIT Tech Review", "The Batch",
];
const SOURCES_B = [
  "量子位", "机器之心", "新智元", "晚点 LatePost", "Founder Park",
  "数字生命卡兹克", "通义千问", "Kimi", "智谱", "MiniMax",
  "r/LocalLLaMA", "Hacker News", "a16z", "36氪", "硅星人",
];

const STATS = [
  { to: 65, suffix: "", label: "全球 AI 信源" },
  { to: 1400, suffix: "+", label: "每日扫描资讯" },
  { to: 160, suffix: "", label: "AI 精选条目" },
  { to: 2, suffix: " 次", label: "早晚直达邮箱" },
];

const STEPS: {
  no: string;
  title: string;
  desc: string;
  Icon: ComponentType<SVGProps<SVGSVGElement> & { size?: number }>;
}[] = [
  {
    no: "01",
    title: "广撒网 · 抓取",
    desc: "每天定时扫描 65 个全球顶级 AI 信源——OpenAI、Anthropic、arXiv、量子位、卡兹克…… 一条不漏。",
    Icon: RadarIcon,
  },
  {
    no: "02",
    title: "AI 精选 · 去噪",
    desc: "DeepSeek 给 1400+ 条资讯逐条打分，砍掉营销稿和重复信息，只留最值得你花时间读的那 160 条。",
    Icon: FunnelIcon,
  },
  {
    no: "03",
    title: "早晚两推 · 直达",
    desc: "早 8 点看当下热点，晚 9 点收当日全景汇总，外加一段 AI 深度分析，准时躺进你的邮箱。",
    Icon: MailIcon,
  },
];

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  show: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, delay: i * 0.08, ease: [0.22, 1, 0.36, 1] as const },
  }),
};

function Marquee({ items, reverse = false }: { items: string[]; reverse?: boolean }) {
  const doubled = [...items, ...items];
  return (
    <div className="marquee-mask overflow-hidden py-2">
      <div
        className={`flex w-max gap-4 ${reverse ? "animate-marquee-slow" : "animate-marquee"}`}
        style={reverse ? { animationDirection: "reverse" } : undefined}
      >
        {doubled.map((s, i) => (
          <span
            key={i}
            className="glass whitespace-nowrap rounded-full px-5 py-2 text-sm text-white/70"
          >
            {s}
          </span>
        ))}
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <main className="relative min-h-screen overflow-x-hidden">
      <NeonBackground />

      {/* 顶部导航 */}
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <div className="flex items-center gap-2">
          <CloudIcon size={24} />
          <span className="font-semibold tracking-wide text-white">研究Agent的云</span>
        </div>
        <div className="flex items-center gap-2">
          <a
            href={REPO_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="glass glass-hover flex items-center gap-1.5 rounded-full px-4 py-2 text-sm text-white/80"
            aria-label="GitHub"
          >
            <GithubIcon size={16} />
            <span className="hidden sm:inline">Star</span>
          </a>
          <a
            href="#subscribe"
            className="glass glass-hover rounded-full px-4 py-2 text-sm text-white/80"
          >
            订阅日报
          </a>
        </div>
      </nav>

      {/* 首屏 Hero */}
      <section className="mx-auto flex max-w-4xl flex-col items-center px-6 pb-10 pt-16 text-center sm:pt-24">
        <motion.div
          variants={fadeUp}
          initial="hidden"
          animate="show"
          className="glass mb-7 inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-xs text-white/70"
        >
          <span className="h-2 w-2 animate-pulse rounded-full bg-neon-cyan" />
          每天早晚，准时送达 · 完全免费
        </motion.div>

        <motion.h1
          variants={fadeUp}
          initial="hidden"
          animate="show"
          custom={1}
          className="text-balance text-5xl font-bold leading-[1.1] tracking-tight sm:text-7xl"
        >
          <span className="text-gradient animate-gradient-x">AI 圈的每一天</span>
          <br />
          <span className="text-white">都帮你读完了</span>
        </motion.h1>

        <motion.p
          variants={fadeUp}
          initial="hidden"
          animate="show"
          custom={2}
          className="mt-6 max-w-2xl text-lg leading-relaxed text-white/60"
        >
          扫描全球 <span className="text-neon-cyan">65 个 AI 信源</span>，AI 精选出最值得读的内容，
          早晚两次直达你的邮箱。不再错过，也不被信息淹没。
        </motion.p>

        <motion.div
          id="subscribe"
          variants={fadeUp}
          initial="hidden"
          animate="show"
          custom={3}
          className="mt-10 flex w-full scroll-mt-24 justify-center"
        >
          <SubscribeForm />
        </motion.div>
      </section>

      {/* 数据指标 */}
      <section className="mx-auto max-w-5xl px-6 py-14">
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {STATS.map((s, i) => (
            <motion.div
              key={s.label}
              variants={fadeUp}
              initial="hidden"
              whileInView="show"
              viewport={{ once: true }}
              custom={i}
              className="glass glass-hover rounded-2xl px-5 py-7 text-center"
            >
              <div className="text-4xl font-bold text-gradient sm:text-5xl">
                <CountUp to={s.to} suffix={s.suffix} />
              </div>
              <div className="mt-2 text-sm text-white/55">{s.label}</div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* 信源墙 */}
      <section className="py-10">
        <p className="mb-6 text-center text-sm uppercase tracking-[0.2em] text-white/35">
          覆盖的部分信源
        </p>
        <div className="space-y-3">
          <Marquee items={SOURCES_A} />
          <Marquee items={SOURCES_B} reverse />
        </div>
      </section>

      {/* 怎么运作 */}
      <section className="mx-auto max-w-6xl px-6 py-20">
        <motion.h2
          variants={fadeUp}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
          className="mb-14 text-center text-3xl font-bold text-white sm:text-4xl"
        >
          它是怎么<span className="text-gradient">运作</span>的
        </motion.h2>
        <div className="grid gap-6 md:grid-cols-3">
          {STEPS.map((step, i) => (
            <motion.div
              key={step.no}
              variants={fadeUp}
              initial="hidden"
              whileInView="show"
              viewport={{ once: true }}
              custom={i}
              className="glass glass-hover relative rounded-2xl p-7"
            >
              <div className="mb-5 flex items-center justify-between">
                <span className="glass flex h-12 w-12 items-center justify-center rounded-xl">
                  <step.Icon size={26} />
                </span>
                <span className="font-mono text-2xl font-bold text-white/15">{step.no}</span>
              </div>
              <h3 className="mb-3 text-xl font-semibold text-white">{step.title}</h3>
              <p className="text-sm leading-relaxed text-white/55">{step.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* 支持一下：GitHub Star + 微信赞赏 */}
      <Support />

      {/* 末尾 CTA */}
      <section className="mx-auto max-w-3xl px-6 pb-24 pt-6 text-center">
        <motion.div
          variants={fadeUp}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
          className="glass rounded-3xl px-8 py-12"
        >
          <h2 className="text-3xl font-bold text-white sm:text-4xl">
            从今晚开始，<span className="text-gradient">把 AI 日报交给我们</span>
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-white/55">
            一个邮箱，每天早晚两封精选。省下你刷信息流的两小时。
          </p>
          <div className="mt-8 flex justify-center">
            <SubscribeForm />
          </div>
        </motion.div>
      </section>

      {/* 页脚 */}
      <footer className="border-t border-white/5 px-6 py-10 text-center text-sm text-white/35">
        <div className="flex items-center justify-center gap-2 text-white/55">
          <CloudIcon size={18} />
          <span>研究Agent的云 · AI 日报</span>
        </div>
        <p className="mt-2">每天扫描 65 信源 · DeepSeek 智能精选 · 早晚直达邮箱</p>
      </footer>
    </main>
  );
}
