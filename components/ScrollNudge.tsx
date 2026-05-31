"use client";

import { useEffect } from "react";

/**
 * 移动端首屏修复。
 *
 * 首页大量板块用 Framer Motion 的 whileInView(滚动进视口才从 opacity:0 渐显),
 * 依赖 IntersectionObserver。部分移动端浏览器在首次加载时不会触发首屏内/附近
 * 元素的初始 intersection 回调,导致这些板块永久卡在 opacity:0 ——
 * 表现为"主页显示不全"。带 #hash 访问时浏览器会自动滚动到锚点,
 * 那一次滚动恰好唤醒了观察器,整页就正常 —— 这正是用户观察到的现象。
 *
 * 这里在挂载后(等首帧布局稳定)做一次极小的滚动往返(0→1→0),用户无感,
 * 等效于 hash 的那次自动滚动,主动唤醒所有观察器。不改动任何动画设计。
 */
export default function ScrollNudge() {
  useEffect(() => {
    let raf = 0;
    let timer = 0;
    raf = requestAnimationFrame(() => {
      // 仅在停在顶部且页面可滚动时微调,避免打扰带 #hash 的正常定位
      if (
        window.scrollY === 0 &&
        document.documentElement.scrollHeight > window.innerHeight
      ) {
        window.scrollTo(0, 1);
        // 隔几十毫秒再回顶,确保观察器已在 y=1 处完成一次重算后才复位
        timer = window.setTimeout(() => window.scrollTo(0, 0), 60);
      }
    });
    return () => {
      cancelAnimationFrame(raf);
      clearTimeout(timer);
    };
  }, []);

  return null;
}
