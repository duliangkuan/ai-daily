<div align="center">

# ☁️ 研究Agent的云 · AI 日报

**每天扫描 70+ 个全球 AI 信源，DeepSeek 智能精选，早晚两次直达你的邮箱。**

不再错过，也不被信息淹没。

<br/>

[![Live](https://img.shields.io/badge/live-ai.dufengyun.xyz-22d3ee?style=flat-square)](https://ai.dufengyun.xyz)
[![Deploy](https://img.shields.io/badge/deploy-Vercel-black?style=flat-square&logo=vercel)](https://vercel.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat-square&logo=next.js)](https://nextjs.org)
[![Tailwind](https://img.shields.io/badge/Tailwind-3-38bdf8?style=flat-square&logo=tailwindcss)](https://tailwindcss.com)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](./LICENSE)

[**🌐 在线访问**](https://ai.dufengyun.xyz) · [**📰 看今日全文**](https://ai.dufengyun.xyz/today) · [**✉️ 订阅日报**](https://ai.dufengyun.xyz/#subscribe)

</div>

---

## ✨ 这是什么

「研究Agent的云 · AI 日报」是一个**全自动的 AI 资讯精选 + 多渠道分发系统**。一个暗色霓虹风格的订阅站，访客留个邮箱，就能每天早晚收到 AI 圈的精选要闻——由 AI 从全球 70+ 信源里替你读完、筛好、送达。

## 🔭 它怎么运作

```
        70+ 全球 AI 信源                  AI 精选去噪              三个出口
 ┌────────────────────────────┐      ┌──────────────┐      ┌─────────────────────┐
 │ OpenAI · Anthropic · arXiv │      │              │  ──▶ │ 📰 网页全文 /today    │
 │ HuggingFace · 各大 newsletter ──▶ │  DeepSeek 打分 │  ──▶ │ 📱 微信公众号草稿箱    │
 │ TechCrunch · 量子位 · 雷峰网 │      │ 1400+ → ~160 │  ──▶ │ ✉️  邮件(早 8 / 晚 9) │
 └────────────────────────────┘      └──────────────┘      └─────────────────────┘
```

- **抓取 + 精选**：基于开源项目 [TrendRadar](https://github.com/sansan0/TrendRadar) 多源抓取，DeepSeek 逐条打分，砍掉营销稿与重复，只留最值得读的
- **网页全文**：每天的完整日报存入数据库，`/today` 实时呈现（AI 洞察在顶、可点链接在底）
- **微信公众号**：精简简报自动推进草稿箱，作者审阅后一键发布
- **邮件**：订阅者每天早晚收到通知，一键直达当日全文

> 上游抓取引擎 TrendRadar 为第三方开源项目，遵循其自身协议，不包含在本仓库内。

## 🎨 功能

- 🌌 **暗色霓虹落地页** —— 渐变流光、漂浮辉光、数据滚动计数、信源墙
- ✉️ **邮箱订阅** —— 订阅即时发欢迎信，退订一键生效
- 📊 **实时数据后台** —— `/admin` 查看订阅人数、新增、退订明细
- 🔄 **飞书多维表格实时同步** —— 订阅者数据自动同步，随时在飞书查看
- 📱 **三渠道分发** —— 网页 / 公众号 / 邮件，一份内容多处触达

## 🚀 本地运行

```bash
npm install
npm run dev      # http://localhost:3000
```

环境变量见 [`.env.example`](./.env.example)：`DATABASE_URL`(Neon)、`DM_*`(邮件)、`FEISHU_*`(飞书同步)等。

## 🛠️ 技术栈

`Next.js 14` · `TypeScript` · `Tailwind CSS` · `Framer Motion` · `Neon Postgres` · `Vercel`

---

## 💛 支持 & 联系

如果这个项目对你有帮助，欢迎 Star ⭐、关注公众号、加群交流，或请作者喝杯咖啡 ☕

<div align="center">

<table>
<tr>
<td align="center" width="25%"><b>📢 公众号</b><br/><sub>研究Agent的云</sub></td>
<td align="center" width="25%"><b>💬 个人微信</b><br/><sub>加我好友</sub></td>
<td align="center" width="25%"><b>👥 交流群</b><br/><sub>fengyun-publish</sub></td>
<td align="center" width="25%"><b>☕ 赞赏</b><br/><sub>请作者喝咖啡</sub></td>
</tr>
<tr>
<td align="center"><img src="public/qr-mp.jpg" width="170" alt="公众号二维码"/></td>
<td align="center"><img src="public/qr-wechat.jpg" width="170" alt="个人微信二维码"/></td>
<td align="center"><img src="public/qr-group.jpg" width="170" alt="交流群二维码"/></td>
<td align="center"><img src="public/reward-qr.jpg" width="170" alt="赞赏码"/></td>
</tr>
</table>

<sub>⏳ 群二维码 7 天有效（6 月 5 日前），过期请扫个人微信拉你进群</sub>

</div>

## 📄 License

[MIT](./LICENSE) © 风云
