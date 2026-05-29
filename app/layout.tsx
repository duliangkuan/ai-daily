import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "研究Agent的云 · AI 日报订阅",
  description:
    "每天扫描 65 个全球 AI 信源、1400+ 条资讯，AI 精选出最值得读的 160 条，早晚两次直达你的邮箱。",
  openGraph: {
    title: "研究Agent的云 · AI 日报订阅",
    description:
      "每天 65 信源 → 1400+ 条 → AI 精选 160 条，早晚直达邮箱。",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}
