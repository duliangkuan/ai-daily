-- 订阅者表
-- 在 Neon 控制台的 SQL Editor 里执行一次即可。
create table if not exists subscribers (
  id          bigserial primary key,
  email       text not null unique,
  status      text not null default 'active',   -- active | unsubscribed
  unsub_token text not null unique,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now(),
  welcomed_at timestamptz                        -- 已发欢迎信的时间;NULL=待发
);

create index if not exists idx_subscribers_status on subscribers (status);
