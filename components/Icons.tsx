import type { SVGProps } from "react";

/**
 * 霓虹线性图标组 — 青→紫渐变描边 + 发光。
 * 每个图标自带唯一 gradient id，避免多实例冲突。
 */

type IconProps = SVGProps<SVGSVGElement> & { size?: number };

const base = (size: number) => ({
  width: size,
  height: size,
  viewBox: "0 0 24 24",
  fill: "none",
  strokeWidth: 1.6,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
  style: { filter: "drop-shadow(0 0 6px rgba(34,211,238,0.45))" },
});

function Grad({ id }: { id: string }) {
  return (
    <defs>
      <linearGradient id={id} x1="0" y1="0" x2="24" y2="24" gradientUnits="userSpaceOnUse">
        <stop stopColor="#22d3ee" />
        <stop offset="0.5" stopColor="#818cf8" />
        <stop offset="1" stopColor="#d946ef" />
      </linearGradient>
    </defs>
  );
}

/** 云 — logo */
export function CloudIcon({ size = 24, ...p }: IconProps) {
  const id = "g-cloud";
  return (
    <svg {...base(size)} {...p}>
      <Grad id={id} />
      <path
        d="M7 18a4 4 0 0 1-.5-7.97A5.5 5.5 0 0 1 17 9.5a3.5 3.5 0 0 1-.5 8.5H7Z"
        stroke={`url(#${id})`}
      />
    </svg>
  );
}

/** 雷达/扫描 — 广撒网抓取 */
export function RadarIcon({ size = 24, ...p }: IconProps) {
  const id = "g-radar";
  return (
    <svg {...base(size)} {...p}>
      <Grad id={id} />
      <path d="M12 21a9 9 0 1 0-9-9" stroke={`url(#${id})`} />
      <path d="M12 17a5 5 0 1 0-5-5" stroke={`url(#${id})`} opacity="0.75" />
      <circle cx="12" cy="12" r="1.6" fill={`url(#${id})`} stroke="none" />
      <path d="M12 12 19 5" stroke={`url(#${id})`} />
    </svg>
  );
}

/** 漏斗 — AI 精选去噪（1400→160） */
export function FunnelIcon({ size = 24, ...p }: IconProps) {
  const id = "g-funnel";
  return (
    <svg {...base(size)} {...p}>
      <Grad id={id} />
      <path d="M3 5h18l-7 8v6l-4 2v-8L3 5Z" stroke={`url(#${id})`} />
    </svg>
  );
}

/** 信封 — 早晚两推直达 */
export function MailIcon({ size = 24, ...p }: IconProps) {
  const id = "g-mail";
  return (
    <svg {...base(size)} {...p}>
      <Grad id={id} />
      <rect x="3" y="5" width="18" height="14" rx="2.5" stroke={`url(#${id})`} />
      <path d="m4 7 8 6 8-6" stroke={`url(#${id})`} />
    </svg>
  );
}

/** 对勾 — 订阅成功 */
export function CheckIcon({ size = 24, ...p }: IconProps) {
  const id = "g-check";
  return (
    <svg {...base(size)} {...p}>
      <Grad id={id} />
      <circle cx="12" cy="12" r="9" stroke={`url(#${id})`} />
      <path d="m8 12 2.5 2.5L16 9" stroke={`url(#${id})`} />
    </svg>
  );
}

/** GitHub logo（填充版，跟随 currentColor） */
export function GithubIcon({ size = 24, ...p }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" {...p}>
      <path d="M12 .5A11.5 11.5 0 0 0 .5 12a11.5 11.5 0 0 0 7.86 10.92c.58.1.79-.25.79-.56v-2c-3.2.7-3.88-1.37-3.88-1.37-.53-1.34-1.29-1.7-1.29-1.7-1.05-.72.08-.7.08-.7 1.16.08 1.77 1.2 1.77 1.2 1.03 1.77 2.7 1.26 3.36.96.1-.75.4-1.26.73-1.55-2.56-.29-5.25-1.28-5.25-5.69 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.18 1.18a11 11 0 0 1 5.8 0c2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.23 2.76.11 3.05.74.81 1.19 1.84 1.19 3.1 0 4.42-2.69 5.39-5.26 5.68.41.36.78 1.06.78 2.14v3.17c0 .31.21.67.8.56A11.5 11.5 0 0 0 23.5 12 11.5 11.5 0 0 0 12 .5Z" />
    </svg>
  );
}

/** 星标 */
export function StarIcon({ size = 24, ...p }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" {...p}>
      <path d="M12 2.5l2.9 5.88 6.5.94-4.7 4.58 1.11 6.47L12 17.9l-5.81 3.06 1.11-6.47-4.7-4.58 6.5-.94L12 2.5Z" />
    </svg>
  );
}

/** 爱心 — 赞赏 */
export function HeartIcon({ size = 24, ...p }: IconProps) {
  const id = "g-heart";
  return (
    <svg {...base(size)} {...p}>
      <Grad id={id} />
      <path
        d="M12 20s-7-4.35-9.2-8.6C1.4 8.5 2.7 5.5 5.6 5.5c1.8 0 3 .9 3.9 2.1.9-1.2 2.1-2.1 3.9-2.1 2.9 0 4.2 3 2.8 5.9C19 15.65 12 20 12 20Z"
        stroke={`url(#${id})`}
      />
    </svg>
  );
}
