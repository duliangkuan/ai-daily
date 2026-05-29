import { neon } from "@neondatabase/serverless";

/**
 * Neon Postgres 客户端（懒加载，避免 build 期因缺 env 报错）。
 * 连接串放在环境变量 DATABASE_URL：
 *   - 本地开发：.env.local
 *   - 线上：Vercel 项目环境变量
 */
export function getSql() {
  const url = process.env.DATABASE_URL;
  if (!url) {
    throw new Error("缺少环境变量 DATABASE_URL（Neon 连接串）");
  }
  return neon(url);
}
