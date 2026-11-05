"""最小化的 DeepSeek 连通性测试：发一句话，看能不能收到回复。"""
import json
import time
import urllib.error
import urllib.request

from app.core.config import settings

key = settings.DEEPSEEK_API_KEY
if not key:
    print("KEY 为空")
    raise SystemExit(1)

body = json.dumps(
    {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "只回复两个字：收到"}],
        "max_tokens": 20,
        "stream": False,
    }
).encode("utf-8")

req = urllib.request.Request(
    "https://api.deepseek.com/chat/completions",
    data=body,
    headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    },
)

t0 = time.time()
try:
    with urllib.request.urlopen(req, timeout=40) as resp:
        data = json.load(resp)
    print("HTTP 200，耗时 %.1fs" % (time.time() - t0))
    print("回复:", data["choices"][0]["message"]["content"])
    print("用量:", data["usage"])
except urllib.error.HTTPError as e:
    print("HTTP", e.code, e.read().decode("utf-8", "ignore")[:300])
except Exception as e:
    print("失败:", type(e).__name__, str(e)[:200])
