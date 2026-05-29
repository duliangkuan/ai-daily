import { getSql } from "@/lib/db";
import NeonBackground from "@/components/NeonBackground";
import { CloudIcon } from "@/components/Icons";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "今日 AI 日报 · 研究Agent的云",
};

export default async function Today() {
  let edition = "";
  let htmlBody = "";
  try {
    const sql = getSql();
    const rows = (await sql`
      select edition, html from digests order by id desc limit 1
    `) as { edition: string; html: string }[];
    if (rows.length) {
      edition = rows[0].edition;
      htmlBody = rows[0].html;
    }
  } catch {
    htmlBody = "";
  }

  return (
    <main className="relative min-h-screen px-4 py-10">
      <NeonBackground />

      <div className="mx-auto max-w-3xl">
        <a
          href="/"
          className="mb-6 inline-flex items-center gap-2 text-sm text-white/60 hover:text-white"
        >
          <CloudIcon size={18} /> 研究Agent的云 · AI 日报
        </a>

        {htmlBody ? (
          <article className="digest glass rounded-2xl px-6 py-8 sm:px-10 sm:py-10">
            <div className="mb-6 border-b border-white/10 pb-5">
              <div className="text-xs uppercase tracking-[0.18em] text-neon-cyan">
                今日日报
              </div>
              <h1 className="mt-1 text-2xl font-bold text-white">{edition}</h1>
            </div>
            <div dangerouslySetInnerHTML={{ __html: htmlBody }} />
          </article>
        ) : (
          <div className="glass rounded-2xl px-8 py-16 text-center text-white/60">
            今天的日报还在路上，稍后再来看看 ✦
          </div>
        )}
      </div>
    </main>
  );
}
