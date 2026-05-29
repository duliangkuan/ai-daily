// 飞书多维表格实时同步:订阅时 upsert 一行,退订时改状态。
// 需要 Vercel 环境变量:FEISHU_APP_ID / FEISHU_APP_SECRET / FEISHU_BITABLE_APP_TOKEN / FEISHU_TABLE_ID

const BASE = "https://open.feishu.cn/open-apis";

let cached: { token: string; exp: number } | null = null;

async function getToken(): Promise<string> {
  if (cached && Date.now() < cached.exp) return cached.token;
  const app_id = process.env.FEISHU_APP_ID;
  const app_secret = process.env.FEISHU_APP_SECRET;
  if (!app_id || !app_secret) throw new Error("缺少 FEISHU_APP_ID / FEISHU_APP_SECRET");
  const r = await fetch(`${BASE}/auth/v3/tenant_access_token/internal`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ app_id, app_secret }),
  });
  const d = await r.json();
  if (d.code !== 0) throw new Error("飞书 token: " + d.msg);
  cached = { token: d.tenant_access_token, exp: Date.now() + (d.expire - 120) * 1000 };
  return cached.token;
}

function tableUrl() {
  const app = process.env.FEISHU_BITABLE_APP_TOKEN;
  const tbl = process.env.FEISHU_TABLE_ID;
  if (!app || !tbl) throw new Error("缺少 FEISHU_BITABLE_APP_TOKEN / FEISHU_TABLE_ID");
  return `${BASE}/bitable/v1/apps/${app}/tables/${tbl}`;
}

async function findRecordId(token: string, email: string): Promise<string | null> {
  const r = await fetch(`${tableUrl()}/records/search`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      filter: {
        conjunction: "and",
        conditions: [{ field_name: "邮箱", operator: "is", value: [email] }],
      },
      automatic_fields: false,
    }),
  });
  const d = await r.json();
  return d?.data?.items?.[0]?.record_id ?? null;
}

/** 订阅时调用:存在则更新状态,不存在则新建一行 */
export async function upsertSubscriber(
  email: string,
  status: "active" | "unsubscribed",
  unsubToken: string,
  source: string
) {
  const token = await getToken();
  const recId = await findRecordId(token, email);
  if (recId) {
    await fetch(`${tableUrl()}/records/${recId}`, {
      method: "PUT",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ fields: { 状态: status } }),
    });
  } else {
    await fetch(`${tableUrl()}/records`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({
        fields: {
          邮箱: email,
          状态: status,
          订阅时间: Date.now(),
          退订token: unsubToken,
          来源: source,
        },
      }),
    });
  }
}
