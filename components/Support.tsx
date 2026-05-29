"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { GithubIcon, StarIcon, HeartIcon, CheckIcon } from "@/components/Icons";
import { REPO_URL, REWARD_QR } from "@/lib/config";

const STAR_POINTS = [
  "完整源码公开，前后端一把梭",
  "MIT 许可，可自由 fork 自部署",
  "Next.js + Tailwind 构建，持续迭代",
];

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  show: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, delay: i * 0.1, ease: [0.22, 1, 0.36, 1] as const },
  }),
};

export default function Support() {
  const [qrOk, setQrOk] = useState(true);

  return (
    <section className="mx-auto max-w-5xl px-6 py-20">
      <motion.h2
        variants={fadeUp}
        initial="hidden"
        whileInView="show"
        viewport={{ once: true }}
        className="mb-4 text-center text-3xl font-bold text-white sm:text-4xl"
      >
        喜欢的话，<span className="text-gradient">支持一下</span>
      </motion.h2>
      <motion.p
        variants={fadeUp}
        initial="hidden"
        whileInView="show"
        viewport={{ once: true }}
        custom={1}
        className="mb-12 text-center text-white/55"
      >
        这是一个独立开发者的项目，你的每一个 Star 和赞赏都是继续做下去的动力。
      </motion.p>

      <div className="grid gap-6 md:grid-cols-2">
        {/* GitHub Star */}
        <motion.a
          href={REPO_URL}
          target="_blank"
          rel="noopener noreferrer"
          variants={fadeUp}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
          className="glass glass-hover group flex flex-col rounded-2xl p-8"
        >
          <div className="flex flex-col items-center text-center">
            <span className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-white/5 text-white">
              <GithubIcon size={30} />
            </span>
            <h3 className="mb-2 text-xl font-semibold text-white">在 GitHub 点个 Star</h3>
            <p className="text-sm leading-relaxed text-white/55">
              这是一个独立开发者的开源项目，整套抓取、精选、推送的代码全部公开。你的每一个 Star，都是我继续把它做得更好的动力。
            </p>
          </div>

          <ul className="my-6 space-y-3">
            {STAR_POINTS.map((p) => (
              <li key={p} className="flex items-center gap-3 text-sm text-white/75">
                <CheckIcon size={18} />
                <span>{p}</span>
              </li>
            ))}
          </ul>

          <div className="mb-6 flex items-center gap-2 overflow-x-auto rounded-xl border border-white/10 bg-black/40 px-4 py-3 font-mono text-xs text-neon-cyan/90">
            <span className="select-none text-white/30">$</span>
            <span className="whitespace-nowrap">git clone {REPO_URL}.git</span>
          </div>

          <span className="btn-neon mt-auto inline-flex items-center justify-center gap-2 rounded-xl px-6 py-3 text-sm font-semibold text-ink-900">
            <StarIcon size={18} />
            Star on GitHub
          </span>
        </motion.a>

        {/* 微信赞赏 */}
        <motion.div
          variants={fadeUp}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
          custom={1}
          className="glass glass-hover flex flex-col items-center rounded-2xl p-8 text-center"
        >
          <span className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-white/5">
            <HeartIcon size={30} />
          </span>
          <h3 className="mb-2 text-xl font-semibold text-white">请作者喝杯咖啡</h3>
          <p className="mb-5 text-sm leading-relaxed text-white/55">
            服务对你有帮助？微信扫码随意赞赏，金额不限，心意最重。
          </p>

          {qrOk ? (
            <div className="overflow-hidden rounded-2xl shadow-[0_0_36px_rgba(34,211,238,0.22)]">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={REWARD_QR}
                alt="微信赞赏码"
                width={232}
                height={232}
                className="h-[232px] w-[232px] object-contain"
                onError={() => setQrOk(false)}
              />
            </div>
          ) : (
            <div className="flex h-[232px] w-[232px] flex-col items-center justify-center rounded-2xl border border-dashed border-white/20 text-center text-xs text-white/35">
              <span className="mb-1 text-2xl">⌁</span>
              赞赏码待上传
              <br />
              (public/reward-qr.jpg)
            </div>
          )}
          <p className="mt-3 text-xs text-white/35">微信扫一扫</p>
        </motion.div>
      </div>
    </section>
  );
}
