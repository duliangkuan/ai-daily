"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { GithubIcon, StarIcon, HeartIcon } from "@/components/Icons";
import { REPO_URL, REWARD_QR } from "@/lib/config";

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
          className="glass glass-hover group flex flex-col items-center rounded-2xl p-8 text-center"
        >
          <span className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-white/5 text-white">
            <GithubIcon size={30} />
          </span>
          <h3 className="mb-2 text-xl font-semibold text-white">在 GitHub 点个 Star</h3>
          <p className="mb-6 text-sm leading-relaxed text-white/55">
            项目开源，欢迎围观源码。点个 Star 是对作者最轻巧的鼓励。
          </p>
          <span className="btn-neon inline-flex items-center gap-2 rounded-xl px-6 py-3 text-sm font-semibold text-ink-900">
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
