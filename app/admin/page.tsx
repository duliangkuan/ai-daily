import { getSql } from "@/lib/db";
import NeonBackground from "@/components/NeonBackground";

export const dynamic = "force-dynamic";
export const metadata = { title: "订阅后台 · 研究Agent的云" };

type Stat = { active: number; unsub: number; total: number; today: number };
type Row = {
  email: string;
  status: string;
  created_at: string;
  welcomed_at: string | null;
};

function fmt(ts: string | null) {
  if (!ts) return "—";
  const d = new Date(ts);
  return d.toLocaleString("zh-CN", { timeZone: "Asia/Shanghai", hour12: false });
}

export default async function Admin() {
  let stat: Stat = { active: 0, unsub: 0, total: 0, today: 0 };
  let rows: Row[] = [];
  let err = "";
  try {
    const sql = getSql();
    const s = (await sql`
      select
        count(*) filter (where status='active')::int as active,
        count(*) filter (where status='unsubscribed')::int as unsub,
        count(*)::int as total,
        count(*) filter (where status='active' and created_at >= now() - interval '24 hours')::int as today
      from subscribers
    `) as Stat[];
    stat = s[0] ?? stat;
    rows = (await sql`
      select email, status, created_at, welcomed_at
      from subscribers order by id desc limit 200
    `) as Row[];
  } catch (e) {
    err = String(e);
  }

  const cards = [
    { label: "在订阅", value: stat.active, color: "#22d3ee" },
    { label: "近 24h 新增", value: stat.today, color: "#8b5cf6" },
    { label: "已退订", value: stat.unsub, color: "#d946ef" },
    { label: "总记录", value: stat.total, color: "#94a3b8" },
  ];

  return (
    <main className="relative min-h-screen px-4 py-10">
      <NeonBackground />
      <div className="mx-auto max-w-4xl">
        <div className="mb-8 flex items-baseline justify-between">
          <h1 className="text-2xl font-bold text-white">📊 订阅后台</h1>
          <span className="text-xs text-white/40">研究Agent的云 · AI 日报</span>
        </div>

        {err ? (
          <div className="glass rounded-2xl p-8 text-center text-neon-magenta">
            读取数据失败：{err}
          </div>
        ) : (
          <>
            <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
              {cards.map((c) => (
                <div key={c.label} className="glass rounded-2xl px-5 py-7 text-center">
                  <div className="text-4xl font-bold" style={{ color: c.color }}>
                    {c.value}
                  </div>
                  <div className="mt-2 text-sm text-white/55">{c.label}</div>
                </div>
              ))}
            </div>

            <div className="glass overflow-hidden rounded-2xl">
              <div className="border-b border-white/10 px-5 py-3 text-sm text-white/60">
                最近 {rows.length} 条订阅记录
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-white/40">
                      <th className="px-5 py-3 font-normal">邮箱</th>
                      <th className="px-5 py-3 font-normal">状态</th>
                      <th className="px-5 py-3 font-normal">订阅时间</th>
                      <th className="px-5 py-3 font-normal">欢迎信</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((r, i) => (
                      <tr key={i} className="border-t border-white/5 text-white/80">
                        <td className="px-5 py-2.5">{r.email}</td>
                        <td className="px-5 py-2.5">
                          <span
                            className="rounded-full px-2 py-0.5 text-xs"
                            style={{
                              background:
                                r.status === "active"
                                  ? "rgba(34,211,238,.15)"
                                  : "rgba(217,70,239,.15)",
                              color: r.status === "active" ? "#22d3ee" : "#d946ef",
                            }}
                          >
                            {r.status === "active" ? "在订阅" : "已退订"}
                          </span>
                        </td>
                        <td className="px-5 py-2.5 text-white/55">{fmt(r.created_at)}</td>
                        <td className="px-5 py-2.5 text-white/40">
                          {r.welcomed_at ? "已发" : "—"}
                        </td>
                      </tr>
                    ))}
                    {rows.length === 0 && (
                      <tr>
                        <td colSpan={4} className="px-5 py-10 text-center text-white/40">
                          还没有订阅者
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </main>
  );
}
