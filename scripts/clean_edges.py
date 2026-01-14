import json, re
from urllib.parse import urlsplit, urlunsplit, unquote

INP = "graph.json"
OUT = "graph_clean.json"

KEEP_PREFIXES = (
    "https://www.work.ua/",
    "https://www.work.ua/jobs",
    "https://www.work.ua/articles",
    "https://www.work.ua/news",
    "https://www.work.ua/employer",
)

DROP_PREFIXES = (
    "https://www.work.ua/jobseeker/",
    "https://www.work.ua/dialog/",
    "https://www.work.ua/share",
    "https://www.work.ua/i/",
    "https://www.work.ua/stat/",
    "https://www.work.ua/store/",
    "https://www.work.ua/api/",
)

DROP_EXT_RE = re.compile(r"\.(jpg|jpeg|png|gif|webp|svg|pdf|zip|rar|7z|mp4|mp3|css|js|eps)$", re.I)

def canonical(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    p = urlsplit(url)
    if p.netloc not in ("www.work.ua", "work.ua"):
        return ""
    path = p.path or "/"
    # убираем query+fragment полностью
    clean = urlunsplit((p.scheme or "https", "www.work.ua", path, "", ""))
    if clean.endswith("/") and clean != "https://www.work.ua/":
        clean = clean[:-1]
    return clean

def normalize_jobs(url: str) -> str:
    p = urlsplit(url)
    if not p.path.startswith("/jobs-"):
        return url

    decoded = unquote(p.path)

    def tail_is_keyword(tail: str) -> bool:
        if "+" in tail:
            return True
        if re.search(r"[A-Za-zА-Яа-яІіЇїЄє]", tail):
            return True
        return False

    cur = decoded
    for _ in range(4):  # чуть больше итераций
        if not cur.startswith("/jobs-") or "-" not in cur:
            break
        tail = cur.rsplit("-", 1)[1]
        if tail_is_keyword(tail):
            cur = cur.rsplit("-", 1)[0]
        else:
            break

    out = "https://www.work.ua" + cur
    if out.endswith("/") and out != "https://www.work.ua/":
        out = out[:-1]
    return out

def allowed(url: str) -> bool:
    if not url.startswith("https://www.work.ua/"):
        return False
    for pre in DROP_PREFIXES:
        if url.startswith(pre):
            return False
    if DROP_EXT_RE.search(urlsplit(url).path):
        return False
    return url.startswith(KEEP_PREFIXES)

with open(INP, "r", encoding="utf-8") as f:
    data = json.load(f)

# нормализуем и фильтруем
node_ids = set()
nodes_out = []
id_map = {}  # старый -> новый (после нормализации)

for n in data.get("nodes", []):
    u0 = n.get("id") or n.get("url") or ""
    u = normalize_jobs(canonical(u0))
    if not u or not allowed(u):
        continue
    id_map[u0] = u
    if u not in node_ids:
        node_ids.add(u)
        nodes_out.append({"id": u})

# links: приводим source/target к строкам, нормализуем, фильтруем, дедуп
links_out = []
seen = set()

def as_str(x):
    if isinstance(x, str):
        return x
    if isinstance(x, dict) and "id" in x:
        return x["id"]
    return str(x)

for l in data.get("links", []):
    s0 = as_str(l.get("source"))
    t0 = as_str(l.get("target"))

    s = normalize_jobs(canonical(id_map.get(s0, s0)))
    t = normalize_jobs(canonical(id_map.get(t0, t0)))

    if not s or not t or s == t:
        continue
    if not (allowed(s) and allowed(t)):
        continue

    # node set должен содержать их (если узлы не попали — добавим)
    if s not in node_ids:
        node_ids.add(s); nodes_out.append({"id": s})
    if t not in node_ids:
        node_ids.add(t); nodes_out.append({"id": t})

    key = (s, t)
    if key in seen:
        continue
    seen.add(key)
    links_out.append({"source": s, "target": t})

out = {"nodes": nodes_out, "links": links_out}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False)

print(f"OK: nodes {len(data.get('nodes', []))} -> {len(nodes_out)} | links {len(data.get('links', []))} -> {len(links_out)} | saved {OUT}")
