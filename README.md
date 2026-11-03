# BidSentry 标书哨兵

上传招标文件 + 投标文件，逐条核查资格项/废标项/格式项，输出带原文页码引用的风险清单。

> 当前进度：Day 2（骨架 + 九张表 + PDF 上传与页面级解析）。

## 快速开始

```bash
# 1. 装依赖
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env

# 2. 起 Postgres（Docker Desktop 已装好）
docker compose -f docker-compose.dev.yml up -d

#    注意：容器映射到本机 5433，不是 5432。
#    本机已装的 PostgreSQL 18 占着 5432，两个都绑 5432 时连接会静默落到本机那个库上。


# 3. 建表 + 起服务
alembic upgrade head
uvicorn app.main:app --reload
```

打开 http://127.0.0.1:8000/docs ，`GET /health` 返回 `{"status":"ok"}`。

## Day 1 验收

- [ ] `docker compose -f docker-compose.dev.yml ps` 里 postgres 是 healthy
- [ ] `alembic upgrade head` 无报错
- [ ] `\dt` 能看到 9 张表：tenants users tenders documents doc_pages clauses segments findings jobs
- [ ] `/docs` 能打开，`/health` 返回 ok
- [ ] `data/samples/` 里有 5 份真实招标 PDF

## 目录

```
app/core/     config（唯一读环境变量处）、logging、security（Day 2 再实现）
app/db/       base / session / models（九张表）
alembic/      env.py 已接 settings.DATABASE_URL
data/         samples（招标文件样本）、uploads（本地存储，不进 git）
docs/devlog/  每天一篇
```

## 国内网络

docker.io 直连不通。`~/.docker/daemon.json` 里已配了 registry-mirrors：

```json
"registry-mirrors": ["https://docker.1panel.live", "https://docker.m.daocloud.io", "https://hub.rat.dev"]
```

改完要 `docker desktop restart` 才生效。哪个镜像挂了就换一个，三个里通常有一个能用。

## 约定

- 连接串必须是 `postgresql+psycopg://`（psycopg3），不是 `postgresql://`
- 分类/状态字段一律 String，不用 PG 原生 enum
- 业务表都带 `tenant_id`，Day 29 做隔离时才不用改表
